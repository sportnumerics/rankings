"use client";

import { useEffect } from "react";

export function useClickOutside(ref: React.RefObject<HTMLElement>, onClickOutside: VoidFunction) {
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (event.target instanceof HTMLElement && ref?.current && !ref.current.contains(event.target)) {
                onClickOutside();
            }
        }

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        }
    }, [ref, onClickOutside]);
}