import { datetime } from "../formatting";
import Link from "./Link";

export default function GameDate({ id, date, link, year, hideTime = false }: { id: string, date: string, link: boolean, year: string, hideTime?: boolean }) {
    const dt = datetime(date, hideTime)
    return link ? <Link href={`/${year}/games/${id}`}>{dt}</Link> : dt;
}
