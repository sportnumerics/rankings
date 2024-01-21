export async function GET() {
    return Response.json(DIVS);
}

export const DIVS = [
    {
        "name": "NCAA Mens Division I",
        "id": "ml1",
        "sport": "ml",
        "source": "ncaa",
        "div": "1"
    },
    {
        "name": "NCAA Mens Division II",
        "id": "ml2",
        "sport": "ml",
        "source": "ncaa",
        "div": "2"
    },
    {
        "name": "NCAA Mens Division III",
        "id": "ml3",
        "sport": "ml",
        "source": "ncaa",
        "div": "3"
    },
    {
        "name": "NCAA Womens Division I",
        "id": "wl1",
        "sport": "wl",
        "source": "ncaa",
        "div": "1"
    },
    {
        "name": "NCAA Womens Division II",
        "id": "wl2",
        "sport": "wl",
        "source": "ncaa",
        "div": "2"
    },
    {
        "name": "NCAA Womens Division III",
        "id": "wl3",
        "sport": "wl",
        "source": "ncaa",
        "div": "3"
    },
    {
        "name": "MCLA Division I",
        "id": "mcla1",
        "sport": "ml",
        "source": "mcla",
        "div": "1"
    },
    {
        "name": "MCLA Division II",
        "id": "mcla2",
        "sport": "ml",
        "source": "mcla",
        "div": "2"
    },
    {
        "name": "MCLA Division III",
        "id": "mcla3",
        "sport": "ml",
        "source": "mcla",
        "div": "3"
    }
]