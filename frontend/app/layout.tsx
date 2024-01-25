import Header from './components/Header';
import './globals.css'
import { Fira_Code } from 'next/font/google'
import { getYears, latestYear } from './server/years';
import { getDivs } from './server/divs';

const inter = Fira_Code({ subsets: ['latin'] })

export const metadata = {
  title: 'Sportnumerics',
  description: 'NCAA and MCLA Lacrosse Computer Ratings',
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [ years, divs ] = await Promise.all([getYears(), getDivs()]);
  return (
    <html lang="en">
      <body className={inter.className}>
        <div>
          <Header years={years} divs={divs} currentYear={latestYear(years)} />
          <div className="mx-auto container px-4">
              {children}
          </div>
        </div>
      </body>
    </html>
  )
}
