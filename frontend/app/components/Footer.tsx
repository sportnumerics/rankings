import Image from 'next/image';
import x from '../images/x.svg';
import github from '../images/github.svg';

export default function Footer() {
    return <div className="text-xs container py-10 flex flex-col items-center mx-auto">
        <div className="flex flex-row gap-4">
            <a href="https://x.com/sportnumerics"><Image src={x} alt="Sportnumerics on x" /></a>
            <a href="https://github.com/sportnumerics"><Image src={github} alt="Sportnumerics on github" /></a>
        </div>
    </div>
}