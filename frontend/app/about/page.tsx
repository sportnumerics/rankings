import React, { PropsWithChildren } from "react";
import { H1, H2, H3, P } from "../shared";

export default function About() {
    return <>
        <H1>About</H1>
        <P>
            Sportnumerics is run by Will James as a hobby. I don&apos;t have a lot of time to make changes here shoot me a line on Twitter / X <a href="https://x.com/wiggzz">@wiggzz</a> if you have any suggestions or thoughts.
        </P>
        <H2>Methodology</H2>
        <H3>Team Ratings</H3>
        <P>
            Team rankings are based on points scored only. We don&apos;t account for things like momentum, injuries or wins or losses (aside from the information that is built into the scores). Essentially what the algorithm does is attempt to solve the following equations
            <Formula>
                <div>O<sub>x</sub> - D<sub>y</sub> + h = P<sub>xy</sub></div>
                <div>O<sub>y</sub> - D<sub>x</sub> - h = P<sub>yx</sub></div>
            </Formula>
            where O<sub>x</sub> is the offensive rating of team x, D<sub>x</sub> is the defensive rating of team x, h is the home field advantage factor and P<sub>xy</sub> is the actual points scored by team x against team y. The algorithm finds values for O<sub>x</sub> and D<sub>y</sub> which minimize the error in the above equations.
        </P>
        <P>
            This allows us to predict the number of points scored in a given game between two teams, by taking one team&apos;s offensive rating and subtracting the opposing team&apos;s defensive rating, which gives an estimate of how many points one team will score against the other.
        </P>
        <P>
            The overall rating R<sub>x</sub> of a team is determined by adding together their offensive and defensive rating
            <Formula>
                <div>R<sub>x</sub> = O<sub>x</sub> + D<sub>x</sub></div>
            </Formula>
        </P>
        <H3>Player Ratings</H3>
        <P>
            Player rankings are similar. We solve the following equation
            <Formula>
                <div>R<sub>px</sub> + O&apos;<sub>x</sub> - D&apos;<sub>y</sub> = P<sub>pxy</sub></div>
            </Formula>
            where R<sub>px</sub> is the rating of player p on team x, O&apos;<sub>x</sub> is the team x&apos;s offensive rating, D&apos;<sub>y</sub> is the opposing teams defensive rating, and P<sub>pxy</sub> is the number of points player p from team x actually scores against team y. Note that the offensive and defensive ratings (O&apos;<sub>x</sub> and D&apos;<sub>y</sub>) in the player ratings are not related to the offensive and defensive ratings for the team ratings.
        </P>
    </>
}

function Formula({ children }: PropsWithChildren<{}>) {
    return <div className="shadow-inner p-4 m-4 bg-slate-50 rounded">
        {children}
    </div>
}