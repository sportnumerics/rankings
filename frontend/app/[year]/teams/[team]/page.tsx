'use server';
import { getDiv } from "@/app/server/divs";
import { getRankedPlayers } from "@/app/server/players";
import { getRankedTeams, getTeam } from "@/app/server/teams";
import { GameResult } from "@/app/server/types";
import { datetime } from "@/app/formatting";
import { Card, ExternalLink, H1, Table, TableHeader, H2 } from "@/app/shared";
import Link from "@/app/components/Link";
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
    rankedPlayers.sort((a, b) => a.rank - b.rank);
    const team = teams[schedule.team.id];

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
                    {schedule.games.map(game => <tr key={game.id}>
                        <td className="w-24"><GameDate id={game.id} link={Boolean(game.result)} date={game.date} year={params.year} /></td>
                        <td className="w-64"><Opponent id={game.opponent.id} name={game.opponent.name} teams={teams} year={params.year} /></td>
                        <td className="w-24"><Result result={game.result} /></td>
                    </tr>)}
                </tbody>
            </Table>
        </Card>
        <PlayersCard players={rankedPlayers.slice(0, 20)} params={params} />
    </>
}

function Result({ result }: { result?: GameResult }) {
    if (!result) {
        return "";
    }
    return <><WinLossTie result={result} /><Score result={result} /></>;
}

function WinLossTie({ result }: { result: GameResult }) {
    if (result.points_for > result.points_against) {
        return "W "
    } else if (result.points_for < result.points_against) {
        return "L "
    } else {
        return "T "
    }
}

function Score({ result }: { result: GameResult }) {
    return result.points_for + "-" + result.points_against;
}