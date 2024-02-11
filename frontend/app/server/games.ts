import 'server-only';
import source from "./source";
import { Game } from "./types";
import Data from './Data';

export async function getGame({ year, game }: { year: string, game: string }): Promise<Data<Game>> {
    return await source.get(`${year}/games/${game}.json`);
}