import { LinkProps as NextLinkProps, default as NextLink } from "next/link";

interface LinkProps {
    nounderline?: boolean;
}

export default function Link(props: Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, keyof NextLinkProps> & NextLinkProps & { children?: React.ReactNode} & LinkProps) {
    const {nounderline: _, ...passedProps} = props;
    return <NextLink {...passedProps} className={`${props.className ?? ""} ${props.nounderline ? "" : "underline"}`}>{props.children}</NextLink>
}