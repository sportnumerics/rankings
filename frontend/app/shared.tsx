import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import Link from "./components/Link";
import { PropsWithChildren } from "react";
import classNames from "classnames";

export function ExternalLink({ href }: { href: string }) {
    const url = new URL(href);
    return <div className="w-fit">
        <Link className="flex space-x-1" href={href}><span>{url.hostname}</span><ArrowTopRightOnSquareIcon className="h-5 w-5" /></Link>
    </div>;
}

export function Card({ children, title }: PropsWithChildren<{ title?: string }>) {
    return <div className="border rounded my-4 p-4 shadow-md w-fit min-w-48 md:min-w-96 min-h-18">
        {title && <H2>{title}</H2>}
        {children}
    </div>
}

export function Table({ children }: PropsWithChildren<{}>) {
    return <table className="table-fixed">
        {children}
    </table>;
}

export function TableHeader({ children }: PropsWithChildren<{}>) {
    return <thead className="text-left">
        {children}
    </thead>
}

export function H1({ children }: PropsWithChildren<{}>) {
    return <h1 className="text-xl font-extrabold tracking-wider mb-2">{children}</h1>;
}

export function LoadingH1() {
    return <Skeleton className="h-5 w-60 mt-1 mb-2" />
}

export function H2({ children }: PropsWithChildren<{}>) {
    return <h2 className="text-lg font-bold tracking-wider my-2">{children}</h2>;
}

export function LoadingH2() {
    return <Skeleton className="h-4 w-60 my-2" />
}

export function H3({ children }: PropsWithChildren<{}>) {
    return <h3 className="text font-bold tracking-wider my-2">{children}</h3>;
}

export function LoadingText() {
    return <Skeleton className="h-4 w-80 my-1" />
}

export function Skeleton({ className }: { className: string }) {
    return <div className={classNames('animate-pulse rounded bg-slate-200 z-0', className)} />
}

export function LoadingRows({ cols, skeletons }: { cols: string[], skeletons: string[][] }) {
    return <tbody>{skeletons.map((skeleton, i) =>
        <tr key={i}>
            {cols.map((col, j) => <td key={j} className={col}><Skeleton className={classNames("h-4 w-4", skeleton[j])} /></td>)}
        </tr>
    )}
    </tbody>
}

export function Error() {
    return <div>
        <H1>Oops</H1>
        <p>This page has an issue. Please go back.</p>
    </div>
}

export function by<T>(fn: (t: T) => number | undefined, direction: 'asc' | 'desc' = 'desc'): (a: T, b: T) => number {
    return direction === 'asc' ?
        (a, b) => (fn(b) ?? -Infinity) - (fn(a) ?? -Infinity) :
        (a, b) => (fn(a) ?? Infinity) - (fn(b) ?? Infinity);
}