import { DIVS } from "../divs";

export async function GET() {
    return Response.json(DIVS);
}
