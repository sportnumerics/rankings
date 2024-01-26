'use server'

import { HasYear } from "../navigation";
import { getDivs } from "../server/divs";
import { getPlayerRatings } from "../server/players";
import { getRankedTeams } from "../server/teams";
import { RankedPlayer } from "../server/types";
import { Card, H2 } from "../shared";
import PageHeading from "./PageHeading";
import { PlayersTable } from "./PlayersCard";
import { TeamsTable } from "./TeamList";

export default async function YearTeams({ params: { year } }: { params: HasYear }) {
    const divs = await getDivs();
    const [players, ...divisions] = await Promise.all([getPlayerRatings({ year }), ...divs.map(div => getRankedTeams({ year, div: div.id }).then(map => ({...div, teams: Object.values(map)})))]);
    // need div in players
    return <>
    <PageHeading heading={year} subHeading=""/>
    { divisions.map(div => (div.teams.length > 0 ? <Card key={div.id}>
        <H2>{div.name}</H2>
        <div className="flex-row">
            <TeamsTable teams={div.teams.slice(0, 5)} params={{year, div: div.id}}/>
        </div>
    </Card> : null)).filter(Boolean)}
    </>
}