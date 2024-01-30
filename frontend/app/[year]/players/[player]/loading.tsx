import { Card, LoadingH1, LoadingH2, LoadingRows, LoadingText, Table, TableHeader } from "@/app/shared";

export default function Loading() {
    return <>
        <LoadingH1 />
        <LoadingH2 />
        <LoadingText />
        <Card title="Games Played">
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>G</th><th>A</th><th>GB</th></tr></TableHeader>
                <LoadingRows cols={["w-16", "w-64", "w-8", "w-8", "w-8"]} skeletons={[
                    ["w-8", "w-52", "w-7", "w-7", "w-6"],
                    ["w-8", "w-80", "w-5", "w-4", "w-3"],
                    ["w-8", "w-64", "w-3", "w-8", "w-4"],
                    ["w-8", "w-52", "w-4", "w-4", "w-6"]]} />
            </Table>
        </Card>
    </>
}