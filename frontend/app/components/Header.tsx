'use client';
import { useContext, useMemo } from "react";
import { default as NextLink } from "next/link";
import { useLocation } from "../hooks";
import { HasDivision, HasType, HasYear, linkToDiv, linkToPlayers, linkToTeams, linkToYear } from "../navigation";
import { Bars3Icon, ChevronDownIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import { Division, Year } from "../server/types";
import Overlay, { OverlayContext, OverlayControlProps } from "./Overlay";
import Link from "./Link";

type Props = { years: Year[], divs: Division[] };

export default function Header({ years, divs }: Props) {
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

function NavBar({ children }: { children: React.ReactNode }) {
    return <div className="bg-gradient-to-r from-red-800 to-red-900 mb-8 shadow-xl text-white">
        <div className="hidden md:flex">
            {children}
        </div>
        <Overlay Component={OverlayButton}>
            {children}
        </Overlay>
    </div>
}

function OverlayButton({ toggle }: OverlayControlProps) {
    return <div className="p-3 flex md:hidden">
        <button className="rounded border h-10 w-10" onClick={toggle}>
            <Bars3Icon className="h-8 w-8 m-auto"/>
        </button>
    </div>
}

function Nav({ children, isActive }: { children: React.ReactNode, isActive?: boolean }) {
    return <div className={`leading-8 px-10 py-6 ${activeOrHover(isActive, "bg-black/10")}`}>{children}</div>
}

function DropdownNav({ content, children }: { content: React.ReactNode, children: React.ReactNode }) {
    const MemoizedDropdownControl = useMemo(() => function DropdownControl({ toggle, isOpen }: OverlayControlProps) {
        const Icon = isOpen ? ChevronDownIcon : ChevronRightIcon;
        return <button className="w-full text-left" onClick={toggle} >
            <div className={`leading-8 flex px-8 py-6 ${activeOrHover(isOpen, "bg-black/10")}`}><Icon className="w-6 h-6 m-auto mr-3" />{content}</div>
        </button>;
    }, [content]);

    return <Overlay Component={MemoizedDropdownControl}>
        <div className="md:divide-y md:text-black w-full md:w-max">
            {children}
        </div>
    </Overlay>;
}

function DropdownItem({ children, isActive, href }: { children: React.ReactNode, isActive?: boolean, href?: string | null }) {
    const overlay = useContext(OverlayContext);
    const content = <div className="py-4 px-10">{children}</div>;
    return <div className={`first:rounded-t last:rounded-b ${activeOrHover(isActive, "bg-black/10")}`}>{href ? <Link href={href} nounderline onClick={e => overlay.close()}>{content}</Link> : content}</div>;
}

function activeOrHover(show: boolean | undefined, value: string) {
    return show ? value : "hover:" + value;
}
