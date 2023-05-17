import { LinkProps as NextLinkProps, default as NextLink } from "next/link";
import { ArrowTopRightOnSquareIcon } from "@heroicons/react/24/outline";
import { Header } from "./client";
import { Location } from "./navigation";
import { getDivs, getYears } from "./services/data";

export function ExternalLink({ href } : { href: string }) {
    const url = new URL(href);
    return <div className="w-fit">
        <Link className="flex space-x-1" href={href}><span>{url.hostname}</span><ArrowTopRightOnSquareIcon className="h-5 w-5"/></Link>
        </div>;
}

interface LinkProps {
    nounderline?: boolean;
}

export function Link(props: Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, keyof NextLinkProps> & NextLinkProps & { children?: React.ReactNode} & LinkProps) {
    const {nounderline: _, ...passedProps} = props;
    return <NextLink {...passedProps} className={`${props.className ?? ""} ${props.nounderline ? "" : "underline"}`}>{props.children}</NextLink>
}

export function Card({ children, title } : {children: React.ReactNode, title: string }) {
    return <div className="border rounded my-4 p-4 shadow-md w-fit">
        <H2>{ title }</H2>
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
    return <h2 className="text-l font-bold tracking-wider mb-2">{ children }</h2>;
}

async function AsyncContent({ children, location = {} }: { children: React.ReactNode, location?: Location }) {
    const yearsPromise = getYears();
    const divsPromise = getDivs();
    const [years, divs] = await Promise.all([yearsPromise, divsPromise]);
    return <div>
        <Header location={location} years={years} divs={divs} />
        <div className="mx-auto container px-4">
            {children}
        </div>
    </div>
}

export function Content({ children, location = {}}: { children: React.ReactNode, location?: Location }) {
    {/* @ts-expect-error Async Server Component */}
    return <AsyncContent location={location}>{children}</AsyncContent>
}

export function Error() {
    return <div>
        <H1>Oops</H1>
        <p>This page has an issue. Please go back.</p>
    </div>
}
