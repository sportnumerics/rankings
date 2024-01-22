import 'server-only';
import { Year } from "./types";

export async function getYears(): Promise<Year[]> {
    return YEARS;
}

const YEARS = [
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