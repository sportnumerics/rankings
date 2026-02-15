import 'server-only';
import source from "./source";
import Data from './Data';

export interface Game {
    date: string;
    homeTeam: string;
    homeTeamId: string;
    awayTeam: string;
    awayTeamId: string;
    homeDiv?: string;
    sport?: string;
    source?: string;
    result?: {
        homeScore: number;
        awayScore: number;
    };
}

export type GamesByDate = Record<string, Game[]>;

export async function getGames({ year }: { year: string }): Promise<Data<GamesByDate>> {
    return await source.get(`${year}/games.json`);
}
