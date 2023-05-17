"use client";

import { useCallback, useMemo, useRef, useState } from "react";
import { default as NextLink } from "next/link";
import { useClickOutside } from "./hooks";
import { Location, linkToDiv, linkToYear } from "./navigation";
import { Division, Year } from "./services/data";
import { Link } from "./shared";
import { Bars3Icon } from "@heroicons/react/24/outline";

type OverlayControlProps = {toggle: VoidFunction, isOpen: boolean};
type OverlayControl = React.FunctionComponent<OverlayControlProps>

export function Header({ location = {}, years = [], divs = [] }: { location: Location, years: Year[], divs: Division[] } = { location: {}, years: [], divs: []}) {
    return <NavBar>
        <Nav>
            <div className="text-2xl font-black tracking-widest italic"><NextLink href="/">S#</NextLink></div>
        </Nav>
        <DropdownNav content="Years">
            {years.map(year => {
                const href = linkToYear(year.id, location);
                const link = href ? <Link href={href} nounderline>{year.id}</Link> : year.id;
                return <DropdownItem key={year.id} content={link} isActive={!href} />;
            })}
        </DropdownNav>
        <DropdownNav content="Division">
            {divs.map(div => {
                const href = linkToDiv(div.id, location);
                const link = href ? <Link href={href} nounderline>{div.name}</Link> : div.name;
                return <DropdownItem key={div.id} content={link} isActive={!href} />
            })}
        </DropdownNav>
    </NavBar>
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
        return <button className="w-full text-left" onClick={toggle} >
            <div className={`leading-8 px-8 py-6 ${activeOrHover(isOpen, "bg-black/10")}`}>{content}</div>
        </button>;
    }, [content]);
    
    return <Overlay Component={DropdownControl}>
        <div className="md:divide-y md:text-black w-full md:w-max">
            {children}
        </div>
    </Overlay>;
}

export function DropdownItem({ content, isActive }: { content: React.ReactNode, isActive?: boolean }) {
    return <div className={`py-4 px-10 first:rounded-t last:rounded-b ${activeOrHover(isActive, "bg-black/10")}`}>{content}</div>;
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