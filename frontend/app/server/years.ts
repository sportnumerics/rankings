import 'server-only';
import { Year } from "./types";
import source from './source';

export async function getYears(): Promise<Year[]> {
    const availableYears = await source.list('');
    return YEARS.filter(year => availableYears.includes(year.id));
}

export async function getCurrentYear(): Promise<string> {
  const years = await getYears();
  return latestYear(years);
}

export function latestYear(years: Year[]) {
  years.sort((a, b) => Number(b.id) - Number(a.id));
  return years[0].id;
}

const YEARS = [
    {
      "id": "2026"
    },
    {
      "id": "2025"
    },
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