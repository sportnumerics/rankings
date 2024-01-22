import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import Link from "./components/Link";

export function ExternalLink({ href } : { href: string }) {
    const url = new URL(href);
    return <div className="w-fit">
        <Link className="flex space-x-1" href={href}><span>{url.hostname}</span><ArrowTopRightOnSquareIcon className="h-5 w-5"/></Link>
        </div>;
}

export function Card({ children, title } : {children: React.ReactNode, title?: string }) {
    return <div className="border rounded my-4 p-4 shadow-md w-fit">
        {title && <H2>{ title }</H2> }
        { children }
    </div>
}

export function Table({ children }: { children: React.ReactNode }) {
    return <table className="table-fixed">
        { children }
    </table>;
}

export function TableHeader({ children }: { children: React.ReactNode }) {
    return <thead className="text-left">
        { children }
    </thead>
}

export function H1({ children }: { children: React.ReactNode }) {
    return <h1 className="text-xl font-extrabold tracking-wider mb-2">{ children }</h1>;
}

export function H2({ children }: { children: React.ReactNode }) {
    return <h2 className="text-l font-bold tracking-wider my-2">{ children }</h2>;
}

export function Error() {
    return <div>
        <H1>Oops</H1>
        <p>This page has an issue. Please go back.</p>
    </div>
}
