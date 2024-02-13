import { ArrowPathIcon } from "@heroicons/react/24/outline";

export default function Loading() {
    return <div className="w-full h-96 flex">
        <div className="m-auto w-min h-min"><ArrowPathIcon className="h-16 w-16 animate-spin stroke-slate-300" /></div>
    </div>
}