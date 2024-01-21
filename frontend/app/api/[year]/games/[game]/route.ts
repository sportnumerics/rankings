import source from "@/app/api/source";

export async function GET(request: Request, { params: { year, game } }: { params: { year: string, game: string}}) {
    const response = await source.get(`${year}/games/${game}.json`);
    return Response.json(JSON.parse(response));
}