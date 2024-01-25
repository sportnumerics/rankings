'use client';
import { createContext, useCallback, useContext, useRef, useState } from "react";
import { useClickOutside } from "../hooks";

export type OverlayControlProps = {toggle: VoidFunction, isOpen: boolean};
export type OverlayControl = React.FunctionComponent<OverlayControlProps>

export const OverlayContext = createContext({ close: (parents: boolean) => {}});

export default function Overlay({ Component, children }: { Component: OverlayControl, children: React.ReactNode }) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);
    const close = useCallback(() => setOpen(false), [setOpen]);
    useClickOutside(ref, close);
    const toggle = useCallback(() => setOpen(!open), [setOpen, open]);
    const parent = useContext(OverlayContext);
    const closeFromChild = useCallback((parents: boolean) => {
        close();
        if (parents) {
            parent.close(parents);
        }
    }, [close, parent]);

    return <OverlayContext.Provider value={{close: closeFromChild}}>
        <div ref={ref} className="w-full md:w-fit">
            <Component toggle={toggle} isOpen={open} />
            {open && <div  className="md:relative md:top-4">
                <div className="md:absolute md:bg-white md:rounded md:shadow-xl">{ children }</div>
            </div>}
        </div>
    </OverlayContext.Provider>
}