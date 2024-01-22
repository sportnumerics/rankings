import 'server-only';
import source from "./source";
import { Game } from "./types";

export async function getGame({ year, game }: { year: string, game: string }): Promise<Game> {
    const response = await source.get(`${year}/games/${game}.json`);
    return JSON.parse(response);
}