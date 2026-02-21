import 'server-only';
import source from "./source";
import { Game } from "./types";
import Data from './Data';

export interface GameScore {
    // camelCase (frontend-normalized)
    homeScore?: number;
    awayScore?: number;
    // snake_case (raw backend JSON)
    home_score?: number;
    away_score?: number;
    // team schedule style
    points_for?: number;
    points_against?: number;
}

export interface ScheduledGame {
    date: string;
    homeTeam: string;
    homeTeamId: string;
    awayTeam: string;
    awayTeamId: string;
    homeDiv?: string;
    sport?: string;
    source?: string;
    result?: GameScore;
    prediction?: GameScore;
}

export type GamesByDate = Record<string, ScheduledGame[]>;

export async function getGame({ year, game }: { year: string, game: string }): Promise<Data<Game>> {
    return await source.get(`${year}/games/${game}.json`);
}

export async function getGames({ year }: { year: string }): Promise<Data<GamesByDate>> {
    return await source.get(`${year}/games.json`);
}
