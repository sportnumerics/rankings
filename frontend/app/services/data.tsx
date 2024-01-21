export * from"../api/types";
import { Division, PlayerStats, RankedPlayerMap, RankedTeamMap, TeamMap, TeamSchedule, Year, Game } from "../api/types";

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

export async function getYears(): Promise<Year[]> {
    return api(`/api/years`);
}

export async function getDivs(): Promise<Division[]> {
    return api(`/api/divs`);
}

export async function getDiv(div: string): Promise<Division> {
    return api(`/api/divs/${div}`);
}

export async function getTeams({ year, div }: { year: string, div: string }): Promise<TeamMap> {
    return api(`/api/${year}/teams?div=${div}`);
}


export async function getRankedTeamsByDiv({ year, div }: { year: string, div: string }): Promise<RankedTeamMap> {
    return api(`/api/${year}/teams?div=${div}`);
}

export async function getTeamSchedule({ year, team }: { year: string, team: string }): Promise<TeamSchedule> {
    return api(`/api/${year}/teams/${team}`);
}

export async function getRankedPlayersByDiv({ year, div }: { year: string, div: string }): Promise<RankedPlayerMap> {
    return api(`/api/${year}/players?div=${div}`);
}

export async function getRankedPlayersByTeam({ year, team }: { year: string, team: string }): Promise<RankedPlayerMap> {
    return api(`/api/${year}/players?team=${team}`);
}

export async function getPlayerStats({ year, player }: { year: string, player: string }): Promise<PlayerStats> {
    return api(`/api/${year}/players/${player}`);
}

export async function getGame({ year, game }: { year: string, game: string }): Promise<Game> {
    return api(`/api/${year}/games/${game}`);
}

async function api<T>(uri: string): Promise<T> {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/${uri}`);
    if (!response.ok) {
        throw new Error(`Problem fetching ${uri}`);
    }
    return await response.json();
}