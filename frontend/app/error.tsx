'use client';
import { H1, H2 } from "@/app/shared";
import { FaceFrownIcon } from "@heroicons/react/24/outline";

export default function Error({ error }: { error: Error }) {
    return <div className="container max-w-fit">
        <H1>Oops</H1>
        <div className="flex flex-row items-start my-6">
            <FaceFrownIcon className="h-8 w-8" />
            <div className="mx-6">
                <span>This page has an issue. Please go back.</span>
                {error.message && <div className="text-slate-400 text-xs my-2">Message: {error.message}</div>}
            </div>
            </div>
    </div>
}