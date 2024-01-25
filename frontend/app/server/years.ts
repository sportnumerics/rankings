import 'server-only';
import { Year } from "./types";
import source from './source';

export async function getYears(): Promise<Year[]> {
    const availableYears = await source.list('');
    return YEARS.filter(year => availableYears.includes(year.id));
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