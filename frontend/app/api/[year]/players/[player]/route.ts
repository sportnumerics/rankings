import source from "@/app/api/source";

export async function GET(request: Request, { params: { year, player } }: { params: { year: string, player: string}}) {
    const response = await source.get(`${year}/players/${player}.json`);
    return Response.json(JSON.parse(response));
}