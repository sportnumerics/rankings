'use client';
import { LinkProps as NextLinkProps, default as NextLink } from "next/link";
import { useDataMode, withDataMode } from "../hooks/useDataMode";

interface LinkProps {
    nounderline?: boolean;
}

export default function Link(props: Omit<React.AnchorHTMLAttributes<HTMLAnchorElement>, keyof NextLinkProps> & NextLinkProps & { children?: React.ReactNode } & LinkProps) {
    const { nounderline: _, ...passedProps } = props;
    const dataMode = useDataMode();
    
    // Apply dataMode to href if present and href is a string
    const href = typeof props.href === 'string' ? withDataMode(props.href, dataMode) : props.href;
    
    return <NextLink {...passedProps} href={href} className={`${props.className ?? ""} ${props.nounderline ? "" : "underline"}`} prefetch={false}>{props.children}</NextLink>
}