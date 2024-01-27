'use server';
import { getDiv } from "@/app/server/divs";
import { getRankedPlayers } from "@/app/server/players";
import { getRankedTeams, getTeam } from "@/app/server/teams";
import { GameResult, TeamSummary } from "@/app/server/types";
import { datetime, twoPlaces } from "@/app/formatting";
import { Card, ExternalLink, H1, Table, TableHeader, H2 } from "@/app/shared";
import Link from "@/app/components/Link";
import PlayersCard from "@/app/components/PlayersCard";

interface Params {
    year: string;
    div: string;
    team: string;
}

export default async function Page({ params } : { params: Params}) {
    const schedule = await getTeam(params);
    const teamPromise = getRankedTeams({ year: params.year, div: schedule.team.div });
    const playersPromise = getRankedPlayers({ year: params.year, team: schedule.team.id });
    const divPromise = getDiv(schedule.team.div);
    const [teams, players, div] = await Promise.all([teamPromise, playersPromise, divPromise]);

    const rankedPlayers = Object.values(players);
    rankedPlayers.sort((a, b) => a.rank - b.rank);

    function Opponent(summary: TeamSummary) {
        const opponent = teams[summary.id];
        return <Link href={`/${params.year}/teams/${summary.id}`} className="space-x-1">
            <span className="text-xs">{opponent?.rank <= 25 ? opponent.rank : ""}</span>
            <span>{summary.name}</span>
        </Link>
    }

    return <>
        <div>
            <H1>{schedule.team.name} ({params.year})</H1>
            <H2>{div.name}</H2>
            <ExternalLink href={schedule.team.schedule.url} />
        </div>
        <Card title="Schedule">
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>Result</th></tr></TableHeader>
                <tbody>
                    {schedule.games.map(game => <tr key={game.id}>
                        <td className="w-24">{game.result ? <Link href={`/${params.year}/games/${game.id}`}>{datetime(game.date)}</Link> : datetime(game.date)}</td>
                        <td className="w-64"><Opponent {...game.opponent}/></td>
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