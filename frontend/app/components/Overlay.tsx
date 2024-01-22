'use client';
import { useCallback, useRef, useState } from "react";
import { useClickOutside } from "../hooks";

export type OverlayControlProps = {toggle: VoidFunction, isOpen: boolean};
export type OverlayControl = React.FunctionComponent<OverlayControlProps>

export default function Overlay({ Component, children }: { Component: OverlayControl, children: React.ReactNode }) {
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