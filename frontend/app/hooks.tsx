"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, usePathname } from "next/navigation";
import { Location } from "./navigation";
import { Result, loading, success } from "./Result";

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
    const divResult = usePromise(useCallback(() => fetchDiv(params), [params]));
    const pathname = usePathname();
    if (divResult.loading) {
        return { loading: true };
    }
    const type = getType(pathname);
    const location = {
        div: divResult.error ? undefined : divResult.value,
        ...params,
        type
    }
    return location;
}

function fetchDiv(params: { div?: string, year?: string, team?: string, player?: string }): Promise<Result<string | undefined>> {
    if (params.div) {
        return Promise.resolve(success(params.div));
    }
    const url = getUrl(params);
    if (!url) {
        return Promise.resolve(success(undefined));
    }
    return fetch(url).then(response => response.json());
}

function getUrl({ year, team, player }: { year?: string, team?: string, player?: string }): string | undefined {
    if (!year) {
        return undefined;
    }
    const baseUrl = `/api/${year}/div`;
    if (team) {
        return `${baseUrl}?team=${team}`;
    } else if (player) {
        return `${baseUrl}?player=${player}`;
    } else {
        return undefined;
    }
}

function getType(pathname: string) {
    if (pathname.endsWith('players')) {
        return 'players';
    } else if (pathname.endsWith('teams')) {
        return 'teams';
    } else if (pathname.includes('players')) {
        return 'player';
    } else if (pathname.includes('teams')) {
        return 'team';
    } else if (pathname.includes('games')) {
        return 'game';
    } else {
        return null;
    }
}

export function usePromise<T>(get: () => Promise<T>): Result<T> {
    const [result, setResult] = useState<Result<T>>(loading());

    useEffect(() => {
        get()
            .then(value => setResult(success(value)))
            .catch(error => setResult(error(error)))
    }, [get]);

    return result;
}