import { Card, LoadingH1, LoadingH2, LoadingRows, LoadingText, Table, TableHeader } from "@/app/shared";

export default function Loading() {
    return <>
        <div>
            <LoadingH1 />
            <LoadingH2 />
            <LoadingText />
        </div>
        <Card>
            <Table>
                <TableHeader><tr><th>Date</th><th>Opponent</th><th>Result</th></tr></TableHeader>
                <LoadingRows cols={["w-24", "w-64", "w-24"]} skeletons={[["w-8", "w-52", "w-7"], ["w-8", "w-72", "w-9"], ["w-9", "w-48", "w-7"], ["w-8", "w-52", "w-8"]]} />
            </Table>
        </Card>
        </>
}