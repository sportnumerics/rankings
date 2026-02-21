'use server'

import { HasYear } from "../navigation";
import { getDivs } from "../server/divs";
import { getPlayerRatings, rankPlayers } from "../server/players";
import { getRankedTeams } from "../server/teams";
import { Card, H2, H3 } from "../shared";
import LastUpdated from "./LastModified";
import Link from "./Link";
import PageHeading from "./PageHeading";
import { PlayersTable } from "./PlayersCard";
import { TeamsTable } from "./TeamList";

export default async function YearTeams({ params: { year } }: { params: HasYear }) {
    const divs = await getDivs();
    const [{ body: playerMap, lastModified }, ...divisions] = await Promise.all([
        getPlayerRatings({ year }),
        ...divs
            .map(div => getRankedTeams({ year, div: div.id })
                .then(map => ({ ...div, teams: Object.values(map.body) })))]);
    // need div in players
    const players = Object.values(playerMap);
    return <>
        <PageHeading heading={year} subHeading="" />
        {divisions.map(div => {
            if (div.teams.length === 0) {
                return null;
            }
            const divPlayers = Object.values(rankPlayers(players.filter(p => p.team.div === div.id).slice(0, 5)));
            return <Card key={div.id}>
                <H2>{div.name}</H2>
                <div className="flex flex-row">
                    <div>
                        <H3>
                            <Link href={`/${year}/${div.id}/teams`}>Top Teams</Link>
                            <span className="mx-2 text-gray-400">|</span>
                            <Link href={`/${year}/${div.id}/games`}>Upcoming Games</Link>
                        </H3>
                        <TeamsTable teams={div.teams.slice(0, 5)} params={{ year, div: div.id }} />
                    </div>
                    {divPlayers.length > 0 && <div className="hidden md:block">
                        <H3><Link href={`/${year}/${div.id}/players`}>Top Scoring Players</Link></H3>
                        <PlayersTable players={divPlayers} showTeam hideRank params={{ year, div: div.id }} />
                    </div>}
                </div>
            </Card>
        }).filter(Boolean)}
        <LastUpdated lastModified={lastModified} />
    </>
}