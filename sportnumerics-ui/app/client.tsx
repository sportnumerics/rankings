"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { default as NextLink } from "next/link";
import { useClickOutside, useLocation, usePromise } from "./hooks";
import { HasDivision, HasType, HasYear, linkToDiv, linkToPlayers, linkToTeams, linkToYear } from "./navigation";
import { getDivs, getYears } from "./services/data";
import { Link } from "./shared";
import { Bars3Icon, ChevronDownIcon, ChevronRightIcon } from "@heroicons/react/24/outline";

type OverlayControlProps = {toggle: VoidFunction, isOpen: boolean};
type OverlayControl = React.FunctionComponent<OverlayControlProps>

export function Header() {
    const { value: years = [] } = usePromise(getYears, []);
    const { value: divs = [] } = usePromise(getDivs, []);
    const location = useLocation();
    const playersHref = linkToPlayers(location);
    const teamsHref = linkToTeams(location);
    const type = (location as HasType).type;
    const division = divs.find(div => div.id === (location as HasDivision).div);
    return <NavBar>
        <Nav>
            <div className="text-2xl font-black tracking-widest italic"><NextLink href="/">S#</NextLink></div>
        </Nav>
        <DropdownNav content={`${(location as HasYear)?.year ?? "Years"}`}>
            {years.map(year => {
                const href = linkToYear(year.id, location);
                return <DropdownItem key={year.id} href={href} isActive={!href} >{year.id}</DropdownItem>;
            })}
        </DropdownNav>
        <DropdownNav content={`${division?.name ?? "Divisions"}`}>
            {divs.map(div => {
                const href = linkToDiv(div.id, location);
                return <DropdownItem key={div.id} href={href} isActive={!href} >{div.name}</DropdownItem>
            })}
        </DropdownNav>
        {type && <DropdownNav content={type === "players" ? "Players" : "Teams"}>
            <DropdownItem isActive={!teamsHref} href={ teamsHref }>Teams</DropdownItem>
            <DropdownItem isActive={!playersHref} href={ playersHref }>Players</DropdownItem>
            </DropdownNav>}
    </NavBar>;
}

export function NavBar({ children }: { children: React.ReactNode }) {
    return <div className="bg-gradient-to-r from-red-800 to-red-900 mb-8 shadow-xl text-white">
        <div className="hidden md:flex">
            {children}
        </div>
        <Overlay Component={({toggle}: OverlayControlProps) => <div className="p-3 flex md:hidden"><button className="rounded border h-10 w-10" onClick={toggle}><Bars3Icon className="h-8 w-8 m-auto"/></button></div>}>
            {children}
        </Overlay>
    </div>
}

export function Nav({ children, isActive }: { children: React.ReactNode, isActive?: boolean }) {
    return <div className={`leading-8 px-10 py-6 ${activeOrHover(isActive, "bg-black/10")}`}>{children}</div>
}

export function DropdownNav({ content, children }: { content: React.ReactNode, children: React.ReactNode }) {
    const DropdownControl = useMemo(() => function ({ toggle, isOpen }: OverlayControlProps) {
        const Icon = isOpen ? ChevronDownIcon : ChevronRightIcon;
        return <button className="w-full text-left" onClick={toggle} >
            <div className={`leading-8 flex px-8 py-6 ${activeOrHover(isOpen, "bg-black/10")}`}><ChevronDownIcon className="w-6 h-6 m-auto mr-3" />{content}</div>
        </button>;
    }, [content]);
    
    return <Overlay Component={DropdownControl}>
        <div className="md:divide-y md:text-black w-full md:w-max">
            {children}
        </div>
    </Overlay>;
}

export function DropdownItem({ children, isActive, href }: { children: React.ReactNode, isActive?: boolean, href?: string | null }) {
    const content = <div className="py-4 px-10">{children}</div>;
    return <div className={`first:rounded-t last:rounded-b ${activeOrHover(isActive, "bg-black/10")}`}>{href ? <Link href={href} nounderline>{content}</Link> : content}</div>;
}

function activeOrHover(show: boolean | undefined, value: string) {
    return show ? value : "hover:" + value;
}


export function Overlay({ Component, children }: { Component: OverlayControl, children: React.ReactNode }) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);
    const close = useCallback(() => setOpen(false), [setOpen]);
    useClickOutside(ref, close);
    const toggle = useCallback(() => setOpen(!open), [setOpen, open]);

    return <div ref={ref} className="w-full md:w-fit">
            <Component toggle={toggle} isOpen={open} />
            {open && <div  className="md:relative md:top-4">
                <div className="md:absolute md:bg-white md:rounded md:shadow-xl">{ children }</div>
            </div>}
        </div>
}