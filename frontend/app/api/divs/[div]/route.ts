import { DIVS } from "../route";

export async function GET(request: Request, { params: { div } }: { params: { div: string }}) {
    const division = DIVS.find(d => d.id === div);
    if (!division) {
        return new Response('division not found', { status: 404 });
    }
    return Response.json(division);
}