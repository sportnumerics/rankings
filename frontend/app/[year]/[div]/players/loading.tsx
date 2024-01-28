import PageHeading, { LoadingHeading } from "@/app/components/PageHeading";
import { LoadingPlayersTable } from "@/app/components/PlayersCard";
import { LoadingTeamsTable, TeamsCard } from "@/app/components/TeamList";
import { HasDivision } from "@/app/navigation";
import { Card } from "@/app/shared";

export default function Loading({ params }: { params: HasDivision }) {
    return <>
        <LoadingHeading />
        <Card>
            <LoadingPlayersTable />
        </Card>
    </>
}