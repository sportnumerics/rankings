'use server';
import { getGames } from "@/app/server/games";
import { H1, Card } from "@/app/shared";
import Link from "@/app/components/Link";
import { NotFoundError } from "@/app/server/source";
import { getDiv } from "@/app/server/divs";
import { notFound } from "next/navigation";
import { getTeamRatings } from "@/app/server/teams";
import { TeamRating } from "@/app/server/types";

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

function timeLabel(date: Date): string {
    const parts = new Intl.DateTimeFormat("en-US", {
        timeZone: DISPLAY_TIMEZONE,
        hour: "2-digit",
        minute: "2-digit",
        hour12: false,
    }).formatToParts(date);

    const hour = Number(parts.find(part => part.type === "hour")?.value ?? "0");
    const minute = Number(parts.find(part => part.type === "minute")?.value ?? "0");

    if (hour === 0 && minute === 0) {
        return "—";
    }

    return new Intl.DateTimeFormat("en-US", {
        timeZone: DISPLAY_TIMEZONE,
        hour: "numeric",
        minute: "2-digit",
    }).format(date);
}

function scoreString(value?: { awayScore?: number; homeScore?: number; away_score?: number; home_score?: number; points_for?: number; points_against?: number; }) {
    if (!value) return null;

    const away = value.awayScore ?? value.away_score ?? value.points_for;
    const home = value.homeScore ?? value.home_score ?? value.points_against;

    if (away === undefined || home === undefined) return null;
    return `${away}-${home}`;
}

function predictScore(away?: TeamRating, home?: TeamRating) {
    if (!away || !home) return null;
    if (!away.group || !home.group || away.group !== home.group) return null;

    const awayScore = Math.max(0, Math.round(away.offense - home.defense));
    const homeScore = Math.max(0, Math.round(home.offense - away.defense));
    return `${awayScore}-${homeScore}`;
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

    const { body: ratings } = await getTeamRatings({ year: params.year });

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
                .map(game => {
                    const awayRating = ratings[game.awayTeamId];
                    const homeRating = ratings[game.homeTeamId];
                    const projection = predictScore(awayRating, homeRating);
                    return { gameDate: parsedDate, dayKey, game, projection };
                });
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

    const byDay = rows.reduce((acc, row) => {
        if (!acc[row.dayKey]) acc[row.dayKey] = [];
        acc[row.dayKey].push(row);
        return acc;
    }, {} as Record<string, typeof rows>);

    return <>
        <H1>Upcoming Games</H1>
        <p className="text-sm text-gray-600 mb-4">Next 14 days</p>

        {Object.entries(byDay).map(([dayKey, dayRows]) => {
            const dayDate = dayRows[0].gameDate;
            return <Card key={dayKey} title={labelForDay(dayDate, todayKey)} className="w-full max-w-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full table-auto text-sm">
                        <thead className="text-left">
                            <tr>
                                <th className="w-20 pr-2">Time</th>
                                <th className="pr-2">Matchup</th>
                                <th className="w-16">Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dayRows.map(({ game, gameDate, projection }, idx) => {
                                const result = scoreString(game.result as any);
                                return <tr key={`${dayKey}-${game.awayTeam || 'away'}-${game.homeTeam || 'home'}-${idx}`}>
                                    <td className="py-1 pr-2 text-gray-600 whitespace-nowrap">{timeLabel(gameDate)}</td>
                                    <td className="py-1 pr-2 break-words">
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
                                    <td className="py-1 whitespace-nowrap">
                                        {result ? (
                                            <span className="text-gray-900">{result}</span>
                                        ) : projection ? (
                                            <span className="text-slate-400 italic">{projection}<sup>*</sup></span>
                                        ) : (
                                            <span className="text-gray-400">—</span>
                                        )}
                                    </td>
                                </tr>;
                            })}
                        </tbody>
                    </table>
                </div>
            </Card>;
        })}
    </>;
}
