"use client";

import { DependencyList, useEffect, useState } from "react";
import { useParams, usePathname } from "next/navigation";
import { Location } from "./navigation";

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

export function useLocation(): Location {
    const params = useParams();
    const pathname = usePathname();
    const [type] = pathname.split("/").slice(-1);
    const location = {
        ...params,
        type
    }
    return location;
}

interface Result<T> {
    value?: T;
    error?: any;
    loading: boolean;
}

export function usePromise<T>(get: () => Promise<T>, deps: DependencyList): Result<T> {
    const [result, setResult] = useState<Result<T>>({ loading: true });

    useEffect(() => {
        get()
            .then(value => setResult({value, loading: false }))
            .catch(error => setResult({error, loading: false }))
    }, deps);

    return result;
}