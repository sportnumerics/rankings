'use client';
import { useSearchParams } from 'next/navigation';

export function useDataMode() {
    const searchParams = useSearchParams();
    const dataMode = searchParams.get('dataMode');
    return dataMode === 'parquet' ? 'parquet' : null;
}

export function withDataMode(href: string, dataMode: string | null): string {
    if (!dataMode) return href;
    
    const separator = href.includes('?') ? '&' : '?';
    return `${href}${separator}dataMode=${dataMode}`;
}
