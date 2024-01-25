import { H1, H2 } from "../shared";

export default function PageHeading({ heading, subHeading }: { heading: string, subHeading: string }) {
    return <div>
        <H1>{heading}</H1>
        <H2>{subHeading}</H2>
    </div>
}