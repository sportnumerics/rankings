'use server'

import { HasYear } from "../navigation";
import { getDivs } from "../server/divs";
import { getRankedTeams } from "../server/teams";
import { Card, H2 } from "../shared";
import PageHeading from "./PageHeading";
import { TeamsTable } from "./TeamList";

export default async function YearTeams({ params }: { params: HasYear }) {
    const divs = await getDivs();
    const divisions = await Promise.all(divs.map(div => getRankedTeams({ year: params.year, div: div.id }).then(map => ({...div, teams: Object.values(map)}))));
    return <>
    <PageHeading heading={params.year} subHeading=""/>
    { divisions.map(div => (div.teams.length > 0 ? <Card key={div.id}>
        <H2>{div.name}</H2>
        <TeamsTable teams={div.teams.slice(0, 5)} params={{year: params.year, div: div.id}}/>
    </Card> : null)).filter(Boolean)}
    </>
}