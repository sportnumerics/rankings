import { datetime, twoPlaces } from "@/app/formatting";
import { TeamSummary, getRankedPlayersByTeam, getRankedTeamsByDiv, getTeamSchedule } from "@/app/services/data";
import Link from "next/link";

interface Params {
    year: string;
    id: string;
}

export default async function Page({ params } : { params: Params}) {
    const schedule = await getTeamSchedule(params);
    const teamPromise = getRankedTeamsByDiv({ year: params.year, source: schedule.team.source, div: schedule.team.div });
    const playersPromise = getRankedPlayersByTeam({ year: params.year, team: schedule.team.id });
    const [teams, players] = await Promise.all([teamPromise, playersPromise]);
    const rankedPlayers = Object.values(players);
    rankedPlayers.sort((a, b) => a.rank - b.rank);

    function Opponent(summary: TeamSummary) {
        const opponent = teams[summary.id];
        return <Link href={`/${params.year}/teams/${summary.id}`}>
            <span>{opponent?.rank <= 25 ? opponent.rank : ""}</span>
            <span>{summary.name}</span>
        </Link>
    }

    return <div>
        <h1>{schedule.team.name}</h1>
        <h3><Link href={schedule.team.schedule.url}>External Link</Link></h3>
        <h2>Schedule</h2>
        <table>
            <thead><tr><th>Date</th><th>Opponent</th><th>Result</th></tr></thead>
            <tbody>
                {schedule.games.map(game => <tr>
                    <td>{game.result ? <Link href={`/${params.year}/games/${game.id}`}>{datetime(game.date)}</Link> : datetime(game.date)}</td>
                    <td><Opponent {...game.opponent}/></td>
                    <td>{game.result ? game.result.points_for + "-" + game.result.points_against : ""}</td>
                    </tr>)}
            </tbody>
        </table>
        <h2>Top Scoring Players</h2>
        <table>
            <thead><tr><th>Rank</th><th>Name</th><th>Rating</th></tr></thead>
            <tbody>
                {rankedPlayers.slice(0, 20).map(player => <tr>
                    <td>{player.rank}</td>
                    <td><Link href={`/${params.year}/players/${player.id}`}>{player.name}</Link></td>
                    <td>{twoPlaces(player.points)}</td>
                </tr>)}
            </tbody>
        </table>
    </div>
}