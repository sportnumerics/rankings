'use client';

export interface HasYear {
    year: string
}

export interface HasDivision extends HasYear {
    div: string
}

export interface HasType extends HasDivision {
    type: string
}

export interface PlayersList extends HasType {
    type: "players";
}

export interface TeamsList extends HasType {
    type: "teams";
}

export interface Game extends HasType {
    type: "game";
    game: string;
}

export interface Player extends HasType {
    type: "player";
    player: string;
}

export interface Team extends HasType {
    type: "team";
    team: string;
}

export interface Home {

}

export interface Loading {
    loading: true;
}

export type Location = PlayersList | TeamsList | Game | Player | Team | Home | Loading;

function isPlayersList(location: Location): location is PlayersList {
    return (location as PlayersList).type === "players";
}

function isTeamsList(location: Location): location is TeamsList {
    return (location as TeamsList).type === "teams";
}

export function isGame(location: Location): location is Game {
    return (location as Game).game !== undefined;
}

export function isPlayer(location: Location): location is Player {
    return (location as Player).player !== undefined;
}

export function isTeam(location: Location): location is Team {
    return (location as Team).team !== undefined;
}

function hasYear(location: Location, year?: string): location is HasYear {
    if (year) {
        return (location as HasYear).year === year;
    } else {
        return Boolean((location as HasYear).year);
    }
}

function hasDiv(location: Location, div?: string): location is HasDivision {
    const hasDivision = location as HasDivision;
    if (!hasDivision.year) {
        return false;
    }
    if (div) {
        return hasDivision.div === div;
    } else {
        return Boolean(hasDivision.div);
    }
}

export type LinkComponentProps = { isActive?: boolean }
export type LinkComponent = React.FunctionComponent<LinkComponentProps>

export function linkToYear(year: string, location: Location): string | null {
    if (hasYear(location, year)) {
        return null;
    } else if (isPlayersList(location)) {
        return `/${year}/${location.div}/players`;
    } else if (isTeamsList(location) || isGame(location)) {
        return `/${year}/${location.div}/teams`;
    } else if (isPlayer(location)) {
        return `/${year}/players/${location.player}`;
    } else if (isTeam(location)) {
        return `/${year}/teams/${location.team}`;
    } else {
        return `/${year}`;
    }
}

export function linkToDiv(div: string, location: Location, currentYear: string): string | null {
    if (hasDiv(location, div)) {
        return null;
    } else if (isPlayersList(location)) {
        return `/${location.year}/${div}/players`;
    } else if (hasYear(location)) {
        return `/${location.year}/${div}/teams`;
    } else {
        return `/${currentYear}/${div}/teams`;
    }
}

export function linkToPlayers(location: Location, currentYear: string): string | undefined {
    if (isPlayersList(location)) {
        return undefined;
    } else if (hasYear(location) && hasDiv(location)) {
        return `/${location.year}/${location.div}/players`;
    } else {
        return `/${currentYear}`
    }
}

export function linkToTeams(location: Location, currentYear: string): string | undefined {
    if (isTeamsList(location)) {
        return undefined;
    } else if (hasYear(location) && hasDiv(location)) {
        return `/${location.year}/${location.div}/teams`;
    } else if (hasYear(location)) {
        return `/${location.year}/teams`;
    } else {
        return `/${currentYear}/teams`;
    }
}