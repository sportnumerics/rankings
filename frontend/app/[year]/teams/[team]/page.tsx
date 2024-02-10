'use server';
import { getDiv } from "@/app/server/divs";
import { getRankedPlayers } from "@/app/server/players";
import { getRankedTeams, getTeam } from "@/app/server/teams";
import { ScheduleGameResult, RankedTeam } from "@/app/server/types";
import { Card, ExternalLink, H1, Table, TableHeader, H2, by } from "@/app/shared";
import PlayersCard from "@/app/components/PlayersCard";
import Opponent from "@/app/components/Opponent";
import Rank from "@/app/components/Rank";
import GameDate from "@/app/components/GameLink";

interface Params {
    year: string;
    div: string;
    team: string;
}

export default async function Page({ params }: { params: Params }) {
    const schedule = await getTeam(params);
    const teamPromise = getRankedTeams({ year: params.year, div: schedule.team.div });
    const playersPromise = getRankedPlayers({ year: params.year, team: schedule.team.id });
    const divPromise = getDiv(schedule.team.div);
    const [teams, players, div] = await Promise.all([teamPromise, playersPromise, divPromise]);

    const rankedPlayers = Object.values(players);
    rankedPlayers.sort(by(t => t.rank));
    const team = teams[schedule.team.id];

    const games = schedule.games.map(game => {
        const rankedOpponent = teams[game.opponent.id];
        const opponent = rankedOpponent ?? game.opponent;
        const prediction = predict({ team, opponent });
        return {
            ...game,
            knownOpponent: Boolean(rankedOpponent),
            opponent,
            team,
            year: params.year,
            prediction
        };
    });

    return <>
        <div>
            <H1><Rank rank={team?.rank} />{schedule.team.name} ({params.year})</H1>
            <H2>{div.name}</H2>
            <ExternalLink href={schedule.team.schedule.url} />
        </div>
        <Card title="Schedule">
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>Result</th></tr></TableHeader>
                <tbody>
                    {games.map(game => <tr key={game.opponent.name + game.date}>
                        <td className="w-24"><GameDate id={game.id} link={Boolean(game.result)} date={game.date} year={params.year} /></td>
                        <td className="w-64"><Opponent opponent={game.opponent} link={game.knownOpponent} year={params.year} /></td>
                        <td className="w-24"><ResultOrPrediction prediction={game.prediction} result={game.result} /></td>
                    </tr>)}
                </tbody>
            </Table>
            {games.find(game => game.prediction) ? <div className="text-slate-300 italic p-2 text-end"><sup>*</sup>projection</div> : null}
        </Card>
        <PlayersCard title="Top Scoring Players" players={rankedPlayers.slice(0, 20)} params={params} />
    </>
}

function ResultOrPrediction({ result, prediction }: { result?: ScheduleGameResult, prediction?: ScheduleGameResult }) {
    if (result) {
        return <Result result={result} />
    }
    if (prediction) {
        return <Prediction prediction={prediction} />
    }
    return "";
}

function Result({ result }: { result: ScheduleGameResult }) {
    return <><WinLossTie result={result} /><Score result={result} /></>;
}

function WinLossTie({ result }: { result: ScheduleGameResult }) {
    if (result.points_for > result.points_against) {
        return "W "
    } else if (result.points_for < result.points_against) {
        return "L "
    } else {
        return "T "
    }
}

function Score({ result }: { result: ScheduleGameResult }) {
    return result.points_for + "-" + result.points_against;
}

function Prediction({ prediction }: { prediction: ScheduleGameResult }) {
    return <div className="text-slate-300 italic"><Result result={prediction} /><sup>*</sup></div>
}

function predict({ team, opponent }: { team: RankedTeam, opponent: RankedTeam }): ScheduleGameResult | undefined {
    if (team.group && team.group === opponent.group) {
        return {
            points_for: Math.max(0, Math.round(team.offense - opponent.defense)),
            points_against: Math.max(0, Math.round(opponent.offense - team.defense))
        }
    }
    return undefined;
}