import { by } from "../shared";
import { HasId, HasRanking } from "./types";

export default function rank<T extends HasId>(items: T[], field: (item: T) => number | undefined): { [id: string]: (T & HasRanking) } {
    const result = items.slice();
    result.sort(by(field, 'asc'));
    return Object.fromEntries(result.map((item, i) => [item.id, { ...item, rank: field(item) ? i + 1 : undefined }]))
}