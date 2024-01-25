'use server'
import YearTeams from "./components/YearTeams";
import { getCurrentYear } from "./server/years";

export default async function Home() {
    const year = await getCurrentYear();
    return <YearTeams params={{year}}/>
}
