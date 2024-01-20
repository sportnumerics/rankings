import { datetime, twoPlaces } from "@/app/formatting";
import { TeamSummary, getDiv, getRankedPlayersByTeam, getRankedTeamsByDiv, getTeamSchedule } from "@/app/services/data";
import { Card, Content, ExternalLink, Link, H1, Table, TableHeader, Error, H2 } from "@/app/shared";

interface Params {
    year: string;
    div: string;
    team: string;
}

export default async function Page({ params } : { params: Params}) {
    const schedule = await getTeamSchedule(params);

    if (!schedule) {
        console.error(`No schedule for ${JSON.stringify(params)}`);
        return <Content><Error /></Content>
    }

    const teamPromise = getRankedTeamsByDiv({ year: params.year, div: schedule.team.div });
    const playersPromise = getRankedPlayersByTeam({ year: params.year, team: schedule.team.id });
    const divPromise = getDiv(schedule.team.div);
    const [teams, players, div] = await Promise.all([teamPromise, playersPromise, divPromise]);
    if (!teams || !players || !div) {
        console.error(`No teams, players or division for ${JSON.stringify(params)}`);
        return <Content><Error /></Content>
    }

    const rankedPlayers = Object.values(players);
    rankedPlayers.sort((a, b) => a.rank - b.rank);

    function Opponent(summary: TeamSummary) {
        if (!teams) {
            console.error(`No teams for opponent ${JSON.stringify(summary)}`);
            return <Error />
        }
        const opponent = teams[summary.id];
        return <Link href={`/${params.year}/${params.div}/teams/${summary.id}`} className="space-x-1">
            <span className="text-xs">{opponent?.rank <= 25 ? opponent.rank : ""}</span>
            <span>{summary.name}</span>
        </Link>
    }

    return <Content>
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
                        <td className="w-24">{game.result ? <Link href={`/${params.year}/${params.div}/games/${game.id}`}>{datetime(game.date)}</Link> : datetime(game.date)}</td>
                        <td className="w-64"><Opponent {...game.opponent}/></td>
                        <td className="w-24">{game.result ? game.result.points_for + "-" + game.result.points_against : ""}</td>
                        </tr>)}
                </tbody>
            </Table>
        </Card>
        <Card title="Top Scoring Players">
            <Table>
                <TableHeader><tr><th>Rank</th><th>Name</th><th>Rating</th></tr></TableHeader>
                <tbody>
                    {rankedPlayers.slice(0, 20).map(player => <tr key={player.id}>
                        <td className="w-24">{player.rank}</td>
                        <td className="w-64"><Link href={`/${params.year}/${params.div}/players/${player.id}`}>{player.name}</Link></td>
                        <td className="w-24">{twoPlaces(player.points)}</td>
                    </tr>)}
                </tbody>
            </Table>
        </Card>
        </Content>
}