'use server';
import { getPlayerStats } from "@/app/server/players";
import { dataModeFromSearch } from "@/app/server/parquet";
import { Card, ExternalLink, H1, H2, Table, TableHeader } from "@/app/shared";
import Link from "@/app/components/Link";
import Opponent from "@/app/components/Opponent";
import { getRankedTeams } from "@/app/server/teams";
import GameDate from "@/app/components/GameLink";
import LastUpdated from "@/app/components/LastModified";
import DataModeFooter from "@/app/components/DataModeFooter";
import { NotFoundError } from "@/app/server/source";

interface Params {
    year: string;
    player: string;
}

export default async function Page({ params, searchParams }: { params: Params, searchParams?: Record<string, string | string[] | undefined> }) {
    const mode = dataModeFromSearch(searchParams);
    let player;
    let lastModified;
    let playerDebug;

    try {
        // First get player with JSON to learn division, then re-fetch with parquet if needed
        let div: string | undefined;
        if (mode === 'parquet') {
            try {
                const jsonPlayer = await getPlayerStats({ ...params, mode: 'json' });
                div = jsonPlayer.body.team.div;
            } catch (jsonErr) {
                // If JSON fetch fails, parquet will also fail without division
                throw jsonErr;
            }
        }
        ({ body: player, lastModified, debug: playerDebug } = await getPlayerStats({ ...params, div, mode }));
    } catch (err) {
        if (err instanceof NotFoundError) {
            return <>
                <H1>Player not found</H1>
                <Card title="No data for this season">
                    <p className="mb-4">We don&apos;t have a profile for this player in {params.year}.</p>
                    <p><Link href={`/${params.year}`}>Browse the {params.year} season</Link></p>
                </Card>
            </>
        }
        throw err;
    }

    const { body: teams } = await getRankedTeams({ div: player.team.div, ...params });

    const stats = player.stats.map(line => {
        const rankedOpponent = teams[line.opponent.id];
        const opponent = rankedOpponent ?? line.opponent;
        return {
            ...line,
            knownOpponent: Boolean(rankedOpponent),
            opponent
        }
    })

    return <>
        <H1>{player.name}</H1>
        <H2><Link href={`/${params.year}/teams/${player.team.id}`}>{player.team.name}</Link></H2>
        {player.external_link && <ExternalLink href={player.external_link} />}
        <Card title="Profile">
            <Table>
                <tbody>
                    {[
                        ['Jersey Number', player.number],
                        ['Position', player.position],
                        ['High School', player.high_school],
                        ['Hometown', player.hometown],
                        ['Class', player.class_year],
                        ['Eligibility', player.eligibility],
                        ['Height', player.height],
                        ['Weight', player.weight]
                    ].filter(v => v[1])
                        .map(([k, v], i) => <tr key={i}><td className="w-40 font-bold">{k}</td><td>{v}</td></tr>)}
                </tbody>
            </Table>
        </Card>
        <Card title="Games Played">
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>G</th><th>A</th><th>GB</th></tr></TableHeader>
                <tbody>
                    {stats.map(line => <tr key={line.game_id}>
                        <td className="w-16"><GameDate id={line.game_id} date={line.date} link={Boolean(line.g || line.a || line.gb)} year={params.year} hideTime /></td>
                        <td className="w-64"><Opponent opponent={line.opponent} link={line.knownOpponent} year={params.year} /></td>
                        <td className="w-8">{line.g}</td>
                        <td className="w-8">{line.a}</td>
                        <td className="w-8">{line.gb}</td>
                    </tr>)}
                </tbody>
            </Table>
        </Card>
        <DataModeFooter mode={mode} debugs={[playerDebug].filter((d): d is NonNullable<typeof d> => Boolean(d))} />
        <LastUpdated lastModified={lastModified} />
    </>
}