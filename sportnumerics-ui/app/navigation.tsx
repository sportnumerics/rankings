import { JsxElement } from "typescript";
import { Link } from "./shared";

export interface HasYear {
    year: string
}

export interface HasDivision extends HasYear {
    div: string
}

export interface PlayersList extends HasDivision {
    type: "players"
}

export interface TeamsList extends HasDivision {
    type: "teams"
}

export interface Game extends HasYear {
    game: string
}

export interface Player extends HasYear {
    player: string
}

export interface Team extends HasYear {
    team: string
}

export interface Home {

}

export type Location = PlayersList | TeamsList | Game | Player | Team | Home;

function isPlayersList(location: Location): location is PlayersList {
    return (location as PlayersList).type === "players";
}

function isTeamsList(location: Location): location is TeamsList {
    return (location as TeamsList).type === "teams";
}

function isGame(location: Location): location is Game {
    return (location as Game).game !== undefined;
}

function isPlayer(location: Location): location is Player {
    return (location as Player).player !== undefined;
}

function isTeam(location: Location): location is Team {
    return (location as Team).team !== undefined;
}

function hasYear(location: Location, year: string): location is HasYear {
    return (location as HasYear).year === year;
}

function hasDiv(location: Location, div: string): location is HasDivision {
    return (location as HasDivision).div === div;
}

export function LinkToYear({ year, location } : { year: string, location: Location }) {
    if (hasYear(location, year)) {
        return <>{year}</>;
    } else if (isPlayersList(location)) {
        return <Link href={`/${year}/${location.div}/players`}>{year}</Link>;
    } else if (isTeamsList(location)) {
        return <Link href={`/${year}/${location.div}/teams`}>{year}</Link>
    } else if (isGame(location)) {
        // TODO: home page for year
        return <Link href="/">{year}</Link>;
    } else if (isPlayer(location)) {
        return <Link href={`/${year}/players/${location.player}`}>{year}</Link>
    } else if (isTeam(location)) {
        return <Link href={`/${year}/teams/${location.team}`}>{year}</Link>
    } else {
        return <Link href="/">{year}</Link>;
    }
}

export function LinkToDiv({ div, name, location } : { div: string, name: string, location: Location }) {
    if (hasDiv(location, div)) {
        return <>{name}</>
    } else if (isPlayersList(location)) {
        return <Link href={`/${location.year}/${div}/players`}>{name}</Link>;
    } else if (isTeamsList(location)) {
        return <Link href={`/${location.year}/${div}/teams`}>{name}</Link>;
    } else {
        return <Link href="/">{name}</Link>
    }
}