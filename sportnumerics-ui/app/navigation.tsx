import Link from "next/link"

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

export type LinkComponentProps = {isActive?: boolean}
export type LinkComponent = React.FunctionComponent<LinkComponentProps>

export function linkToYear(year: string, location: Location): string | null {
    if (hasYear(location, year)) {
        return null;
    } else if (isPlayersList(location)) {
        return `/${year}/${location.div}/players`;
    } else if (isTeamsList(location)) {
        return `/${year}/${location.div}/teams`;
    } else if (isGame(location)) {
        // TODO: home page for year
        return "/";
    } else if (isPlayer(location)) {
        return `/${year}/players/${location.player}`
    } else if (isTeam(location)) {
        return `/${year}/teams/${location.team}`
    } else {
        return "/";
    }
}

export function LinkToYear({ year, location, Component } : { year: string, location: Location, Component: LinkComponent }) {
    if (hasYear(location, year)) {
        return <Component isActive />;
    } else if (isPlayersList(location)) {
        return <Link href={`/${year}/${location.div}/players`}><Component /></Link>;
    } else if (isTeamsList(location)) {
        return <Link href={`/${year}/${location.div}/teams`}><Component /></Link>
    } else if (isGame(location)) {
        // TODO: home page for year
        return <Link href="/"><Component /></Link>;
    } else if (isPlayer(location)) {
        return <Link href={`/${year}/players/${location.player}`}><Component /></Link>
    } else if (isTeam(location)) {
        return <Link href={`/${year}/teams/${location.team}`}><Component /></Link>
    } else {
        return <Link href="/"><Component /></Link>;
    }
}

export function linkToDiv(div: string, location: Location): string | null {
    if (hasDiv(location, div)) {
        return null;
    } else if (isPlayersList(location)) {
        return `/${location.year}/${div}/players`;
    } else if (isTeamsList(location)) {
        return `/${location.year}/${div}/teams`;
    } else {
        return "/";
    }
}

export function LinkToDiv({ div, location, Component } : { div: string, location: Location, Component: LinkComponent }) {
    if (hasDiv(location, div)) {
        return <Component isActive />;
    } else if (isPlayersList(location)) {
        return <Link href={`/${location.year}/${div}/players`}><Component /></Link>;
    } else if (isTeamsList(location)) {
        return <Link href={`/${location.year}/${div}/teams`}><Component /></Link>;
    } else {
        return <Link href="/"><Component /></Link>
    }
}