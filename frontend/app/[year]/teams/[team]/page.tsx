'use server';
import { getDiv } from "@/app/server/divs";
import { getRankedPlayers } from "@/app/server/players";
import { getRankedTeams, getTeam, getTeamRatings } from "@/app/server/teams";
import { ScheduleGameResult, TeamRating } from "@/app/server/types";
import { Card, ExternalLink, H1, Table, TableHeader, H2, by } from "@/app/shared";
import PlayersCard from "@/app/components/PlayersCard";
import Opponent from "@/app/components/Opponent";
import Rank from "@/app/components/Rank";
import GameDate from "@/app/components/GameLink";
import LastUpdated from "@/app/components/LastModified";
import { ReactElement } from "react";

interface Params {
    year: string;
    div: string;
    team: string;
}

export default async function Page({ params }: { params: Params }) {
    const { body: schedule, lastModified } = await getTeam(params);
    const allTeamsPromise = getTeamRatings({ year: params.year });
    const rankedTeamsPromise = getRankedTeams({ year: params.year, div: schedule.team.div });
    const playersPromise = getRankedPlayers({ year: params.year, team: schedule.team.id });
    const divPromise = getDiv(schedule.team.div);
    const [{ body: teams }, { body: allTeams }, { body: players }, div] = await Promise.all([rankedTeamsPromise, allTeamsPromise, playersPromise, divPromise]);

    const rankedPlayers = Object.values(players);
    rankedPlayers.sort(by(t => t.rank));
    const team = teams[schedule.team.id];

    const games = schedule.games.map(game => {
        const rankedOpponent = teams[game.opponent.id];
        const opponent = rankedOpponent ?? game.opponent;
        const prediction = predict({ team, opponent });
        return {
            ...game,
            knownOpponent: Boolean(allTeams[game.opponent.id]),
            divisional: Boolean(rankedOpponent),
            opponent,
            team,
            year: params.year,
            prediction
        };
    });

    const footnotes: { element: JSX.Element, col: number }[] = [];
    if (games.find(game => game.divisional === false)) {
        footnotes.push({ element: <><sup>†</sup>non-divisional</>, col: 1 });
    }
    if (games.find(game => !game.result && game.prediction)) {
        footnotes.push({ element: <><sup>*</sup>projection</>, col: 2 })
    }

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
                        <td className="w-64"><Opponent opponent={game.opponent} link={game.knownOpponent} year={params.year} home={game.home} divisional={game.divisional} /></td>
                        <td className="w-24"><ResultOrPrediction prediction={game.prediction} result={game.result} /></td>
                    </tr>)}
                    {footnotes
                        ?
                        <tr>
                            {[0, 1, 2]
                                .map(i => <td key={i}>{footnotes.filter(fn => fn.col === i)
                                    .map((fn, j) => <span key={j} className="text-slate-300 italic py-2">{fn.element}</span>)}</td>)}
                        </tr>
                        : null}
                </tbody>
            </Table>
        </Card>
        <PlayersCard title="Top Scoring Players" players={rankedPlayers.slice(0, 20)} params={params} />
        <LastUpdated lastModified={lastModified} />
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

function predict({ team, opponent }: { team: TeamRating, opponent: TeamRating }): ScheduleGameResult | undefined {
    if (team.group && team.group === opponent.group) {
        return {
            points_for: Math.max(0, Math.round(team.offense - opponent.defense)),
            points_against: Math.max(0, Math.round(opponent.offense - team.defense))
        }
    }
    return undefined;
}