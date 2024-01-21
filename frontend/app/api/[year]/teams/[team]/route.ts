import source from "@/app/api/source";

export async function GET(request: Request, { params: { year, team } }: { params: { year: string, team: string}}) {
    const response = await source.get(`${year}/schedules/${team}.json`);
    return Response.json(JSON.parse(response));
}