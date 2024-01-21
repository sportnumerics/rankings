export async function GET() {
    return Response.json(YEARS);
}

export const YEARS = [
    {
      "id": "2024"
    },
    {
      "id": "2023"
    },
    {
      "id": "2022"
    },
    {
      "id": "2021",
      "unavailable": ["mcla1", "mcla2"]
    }
]