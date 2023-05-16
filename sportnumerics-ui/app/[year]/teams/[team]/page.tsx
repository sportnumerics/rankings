import { datetime, twoPlaces } from "@/app/formatting";
import { TeamSummary, getDivs, getRankedPlayersByTeam, getRankedTeamsByDiv, getTeamSchedule } from "@/app/services/data";
import { Card, Content, ExternalLink, Link, H1, Table, TableHeader, Error, H2 } from "@/app/shared";

interface Params {
    year: string;
    team: string;
}

export default async function Page({ params } : { params: Params}) {
    const schedule = await getTeamSchedule(params);

    if (!schedule) {
        return <Content location={params}><Error /></Content>
    }

    const teamPromise = getRankedTeamsByDiv({ year: params.year, div: schedule.team.div });
    const playersPromise = getRankedPlayersByTeam({ year: params.year, team: schedule.team.id });
    const divsPromise = getDivs();
    const [teams, players, divs] = await Promise.all([teamPromise, playersPromise, divsPromise]);
    if (!teams || !players) {
        return <Content location={params}><Error /></Content>
    }

    const rankedPlayers = Object.values(players);
    rankedPlayers.sort((a, b) => a.rank - b.rank);

    function Opponent(summary: TeamSummary) {
        if (!teams) {
            return <Error />
        }
        const opponent = teams[summary.id];
        return <Link href={`/${params.year}/teams/${summary.id}`} className="space-x-1">
            <span className="text-xs">{opponent?.rank <= 25 ? opponent.rank : ""}</span>
            <span>{summary.name}</span>
        </Link>
    }

    return <Content location={params}>
        <div>
            <H1>{schedule.team.name} ({params.year})</H1>
            <H2>{divs.find(div => div.id === schedule.team.div)?.name}</H2>
            <ExternalLink href={schedule.team.schedule.url} />
        </div>
        <Card title="Schedule">
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>Result</th></tr></TableHeader>
                <tbody>
                    {schedule.games.map(game => <tr>
                        <td className="w-24">{game.result ? <Link href={`/${params.year}/games/${game.id}`}>{datetime(game.date)}</Link> : datetime(game.date)}</td>
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
                    {rankedPlayers.slice(0, 20).map(player => <tr>
                        <td className="w-24">{player.rank}</td>
                        <td className="w-64"><Link href={`/${params.year}/players/${player.id}`}>{player.name}</Link></td>
                        <td className="w-24">{twoPlaces(player.points)}</td>
                    </tr>)}
                </tbody>
            </Table>
        </Card>
        </Content>
}