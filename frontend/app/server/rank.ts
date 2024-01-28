import { HasId, HasRanking } from "./types";

export default function rank<T extends HasId>(items: T[], by: (item: T) => number): {[id: string]: (T & HasRanking)} {
    const result = items.slice();
    result.sort((a, b) => by(b) - by(a));
    return Object.fromEntries(result.map((item, i) => [item.id, {...item, rank: i + 1}]))
}