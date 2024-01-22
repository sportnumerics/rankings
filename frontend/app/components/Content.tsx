import { getDivs } from "../server/divs";
import { getYears } from "../server/years";
import Header from "./Header";

export default async function Content({ children }: { children: React.ReactNode }) {
    const [ years, divs ] = await Promise.all([getYears(), getDivs()]);
    return <div>
        <Header years={years} divs={divs} />
        <div className="mx-auto container px-4">
            {children}
        </div>
    </div>
}