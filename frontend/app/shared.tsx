import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import Link from "./components/Link";
import { PropsWithChildren } from "react";

export function ExternalLink({ href } : { href: string }) {
    const url = new URL(href);
    return <div className="w-fit">
        <Link className="flex space-x-1" href={href}><span>{url.hostname}</span><ArrowTopRightOnSquareIcon className="h-5 w-5"/></Link>
        </div>;
}

export function Card({ children, title } : PropsWithChildren<{ title?: string }>) {
    return <div className="border rounded my-4 p-4 shadow-md w-fit min-w-48 md:min-w-96 min-h-24">
        {title && <H2>{ title }</H2> }
        { children }
    </div>
}

export function Table({ children }: PropsWithChildren<{}>) {
    return <table className="table-fixed">
        { children }
    </table>;
}

export function TableHeader({ children }: PropsWithChildren<{}>) {
    return <thead className="text-left">
        { children }
    </thead>
}

export function H1({ children }: PropsWithChildren<{}>) {
    return <h1 className="text-xl font-extrabold tracking-wider mb-2">{ children }</h1>;
}

export function H2({ children }: PropsWithChildren<{}>) {
    return <h2 className="text-l font-bold tracking-wider my-2">{ children }</h2>;
}

export function Error() {
    return <div>
        <H1>Oops</H1>
        <p>This page has an issue. Please go back.</p>
    </div>
}
