import YearTeams from "./components/YearTeams";
import { getCurrentYear } from "./server/years";

export const dynamic = 'force-dynamic';
export const revalidate = 600;

export default async function Home() {
  const year = await getCurrentYear();
  return <YearTeams params={{ year }} />
}
