import { ClockIcon } from "@heroicons/react/24/outline";
import { Card, H2 } from "../shared";

export default function EmptyCard({ text }: { text: string }) {
    return <Card>
        <div className="flex items-center gap-3"><ClockIcon className="w-12 h-12"/><H2>{text}</H2></div>
    </Card>
}