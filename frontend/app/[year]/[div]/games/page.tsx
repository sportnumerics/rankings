'use server';
import { getGames } from "@/app/server/games";
import { H1, Card } from "@/app/shared";
import Link from "@/app/components/Link";
import { NotFoundError } from "@/app/server/source";
import { getDiv } from "@/app/server/divs";
import { notFound } from "next/navigation";

interface Params {
    year: string;
    div: string;
}

const DISPLAY_TIMEZONE = "America/Chicago";

function parseGameDate(dateKey: string): Date | null {
    const direct = new Date(dateKey);
    if (!Number.isNaN(direct.getTime())) return direct;

    const dateOnly = new Date(`${dateKey}T00:00:00`);
    if (!Number.isNaN(dateOnly.getTime())) return dateOnly;

    return null;
}

function dayKeyInTz(date: Date): string {
    return new Intl.DateTimeFormat("en-CA", {
        timeZone: DISPLAY_TIMEZONE,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
    }).format(date);
}

function labelForDay(date: Date, todayKey: string): string {
    const dayKey = dayKeyInTz(date);
    const dayOfWeek = new Intl.DateTimeFormat("en-US", {
        timeZone: DISPLAY_TIMEZONE,
        weekday: "long",
    }).format(date);
    const formattedDate = new Intl.DateTimeFormat("en-US", {
        timeZone: DISPLAY_TIMEZONE,
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(date);

    return dayKey === todayKey
        ? `Today - ${dayOfWeek}, ${formattedDate}`
        : `${dayOfWeek}, ${formattedDate}`;
}

export default async function Page({ params }: { params: Params }) {
    try {
        await getDiv(params.div);
    } catch (err) {
        if (err instanceof NotFoundError) {
            notFound();
        }
        throw err;
    }

    let gamesByDate;

    try {
        ({ body: gamesByDate } = await getGames({ year: params.year }));
    } catch (err) {
        if (err instanceof NotFoundError) {
            return <>
                <H1>Upcoming Games</H1>
                <Card title="No games data available">
                    <p>Games schedule data is not yet available for {params.year}.</p>
                </Card>
            </>;
        }
        throw err;
    }

    const now = new Date();
    const todayKey = dayKeyInTz(now);
    const twoWeeksFromNow = new Date(now.getTime() + (14 * 24 * 60 * 60 * 1000));
    const cutoffKey = dayKeyInTz(twoWeeksFromNow);

    const rows = Object.entries(gamesByDate)
        .flatMap(([dateKey, games]) => {
            const parsedDate = parseGameDate(dateKey);
            if (!parsedDate) return [];

            const dayKey = dayKeyInTz(parsedDate);
            if (dayKey < todayKey || dayKey > cutoffKey) return [];

            return games
                .filter(game => game.homeDiv === params.div)
                .map(game => ({ gameDate: parsedDate, dayKey, game }));
        })
        .sort((a, b) => {
            if (a.dayKey !== b.dayKey) return a.dayKey.localeCompare(b.dayKey);
            return a.gameDate.getTime() - b.gameDate.getTime();
        });

    if (rows.length === 0) {
        return <>
            <H1>Upcoming Games</H1>
            <Card title="No upcoming games">
                <p>No games scheduled for the next two weeks in this division.</p>
            </Card>
        </>;
    }

    return <>
        <H1>Upcoming Games</H1>
        <p className="text-sm text-gray-600 mb-4">Next 14 days</p>

        <div className="overflow-x-auto">
            <table className="min-w-full border border-gray-200 bg-white text-sm">
                <thead>
                    <tr className="bg-gray-50 text-left">
                        <th className="px-3 py-2 border-b">Date</th>
                        <th className="px-3 py-2 border-b">Matchup</th>
                        <th className="px-3 py-2 border-b">Result</th>
                    </tr>
                </thead>
                <tbody>
                    {rows.map(({ gameDate, dayKey, game }, idx) => {
                        const showDate = idx === 0 || rows[idx - 1].dayKey !== dayKey;

                        return <tr key={`${dayKey}-${game.awayTeam || 'away'}-${game.homeTeam || 'home'}-${idx}`} className="align-top">
                            <td className="px-3 py-2 border-b whitespace-nowrap font-medium text-gray-800">
                                {showDate ? labelForDay(gameDate, todayKey) : ""}
                            </td>
                            <td className="px-3 py-2 border-b">
                                {game.awayTeamId ? (
                                    <Link href={`/${params.year}/teams/${game.awayTeamId}`} className="font-semibold">
                                        {game.awayTeam}
                                    </Link>
                                ) : (
                                    <span className="font-semibold">{game.awayTeam}</span>
                                )}
                                <span className="mx-2 text-gray-500">@</span>
                                {game.homeTeamId ? (
                                    <Link href={`/${params.year}/teams/${game.homeTeamId}`} className="font-semibold">
                                        {game.homeTeam}
                                    </Link>
                                ) : (
                                    <span className="font-semibold">{game.homeTeam}</span>
                                )}
                            </td>
                            <td className="px-3 py-2 border-b whitespace-nowrap text-gray-700">
                                {game.result ? `${game.result.awayScore} - ${game.result.homeScore}` : "—"}
                            </td>
                        </tr>;
                    })}
                </tbody>
            </table>
        </div>
    </>;
}
