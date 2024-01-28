import { H1, H2, LoadingH1, LoadingH2 } from "../shared";

export default function PageHeading({ heading, subHeading }: { heading: string, subHeading: string }) {
    return <div>
        <H1>{heading}</H1>
        <H2>{subHeading}</H2>
    </div>
}

export function LoadingHeading() {
    return <div>
        <LoadingH1 />
        <LoadingH2 />
    </div>
}