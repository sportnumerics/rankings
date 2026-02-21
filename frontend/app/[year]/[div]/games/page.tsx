'use server';
import { getGames } from "@/app/server/games";
import { H1, H2, Card } from "@/app/shared";
import Link from "@/app/components/Link";
import { NotFoundError } from "@/app/server/source";
import { getDiv } from "@/app/server/divs";
import { notFound } from "next/navigation";

interface Params {
    year: string;
    div: string;
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
    
    // Get today's date and 2 weeks from now
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Start of day
    const twoWeeksFromNow = new Date(today);
    twoWeeksFromNow.setDate(today.getDate() + 14);
    
    // Filter games to upcoming + today (next 2 weeks) and by division
    const upcomingGames = Object.entries(gamesByDate)
        .map(([date, games]) => {
            const filteredGames = games.filter(game => game.homeDiv === params.div);
            return [date, filteredGames] as [string, typeof games];
        })
        .filter(([_, games]) => games.length > 0)
        .filter(([dateStr]) => {
            const gameDate = new Date(dateStr + 'T00:00:00');
            return gameDate >= today && gameDate <= twoWeeksFromNow;
        })
        .sort(([dateA], [dateB]) => dateA.localeCompare(dateB));
    
    if (upcomingGames.length === 0) {
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
        
        {upcomingGames.map(([date, games]) => {
            const gameDate = new Date(date + 'T00:00:00');
            const isToday = gameDate.toDateString() === today.toDateString();
            const dayOfWeek = gameDate.toLocaleDateString('en-US', { weekday: 'long' });
            const formattedDate = gameDate.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: 'numeric'
            });
            
            return <div key={date} className="mb-6">
                <H2>
                    {isToday && <span className="text-blue-600">Today - </span>}
                    {dayOfWeek}, {formattedDate}
                </H2>
                <div className="space-y-2">
                    {games.map((game, idx) => (
                        <Card key={idx}>
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <Link href={`/${params.year}/teams/${game.awayTeamId}`} className="font-semibold">
                                        {game.awayTeam}
                                    </Link>
                                    <span className="mx-2 text-gray-500">@</span>
                                    <Link href={`/${params.year}/teams/${game.homeTeamId}`} className="font-semibold">
                                        {game.homeTeam}
                                    </Link>
                                </div>
                                {game.result && (
                                    <div className="text-sm text-gray-600">
                                        {game.result.awayScore} - {game.result.homeScore}
                                    </div>
                                )}
                            </div>
                        </Card>
                    ))}
                </div>
            </div>;
        })}
    </>;
}
