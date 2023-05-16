"use client";

import { useRef, useState } from "react";
import { default as NextLink } from "next/link";
import { useClickOutside } from "./hooks";
import { LinkToDiv, LinkToYear, Location } from "./navigation";
import { getDivs, getYears } from "./services/data";

type OverlayItem = (toggle: VoidFunction) => React.ReactNode

const YEARS = ["2023"];

export async function Header({ location = {} }: { location: Location } = { location: {}}) {
    const yearsPromise = getYears();
    const divsPromise = getDivs();
    const [years, divs] = await Promise.all([yearsPromise, divsPromise]);

    return <div className="flex p-6 bg-gradient-to-r from-red-800 to-red-900 mb-8 shadow-xl text-white space-x-8">
        <div className="text-2xl font-black tracking-widest italic"><NextLink href="/">S#</NextLink></div>
        <Overlay item={toggle => <button onClick={toggle} ><div className="leading-8">Years</div></button>}>
            {years.map(year => <div><LinkToYear year={year.id} location={location}/></div>)}
        </Overlay>
        <Overlay item={toggle => <button onClick={toggle} ><div className="leading-8">Divisions</div></button>}>
            {divs.map(div => <div><LinkToDiv div={div.id} name={div.name} location={location}/></div>)}
        </Overlay>
    </div>
}

export function Overlay({ item, children }: { item: OverlayItem, children: React.ReactNode }) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);
    useClickOutside(ref, () => setOpen(false));

    return <div ref={ref}>
        { item(() => setOpen(!open)) }
        {open && <div className="relative">
            <div className="fixed bg-white rounded text-black p-3 shadow-xl">{ children }</div>
        </div>}
    </div>
}