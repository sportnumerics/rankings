import { GoogleAnalytics } from '@next/third-parties/google';
import Header from './components/Header';
import './globals.css'
import { Fira_Code } from 'next/font/google'
import { getYears, latestYear } from './server/years';
import { getDivs } from './server/divs';
import Footer from './components/Footer';
import classNames from 'classnames';

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
  const [years, divs] = await Promise.all([getYears(), getDivs()]);
  return (
    <html lang="en">
      <body className={classNames(inter.className, 'h-screen')}>
        <div className="h-full flex flex-col">
          <Header years={years} divs={divs} currentYear={latestYear(years)} />
          <div className="mx-auto container px-4 grow">
            {children}
          </div>
          <Footer />
        </div>
      </body>
      <GoogleAnalytics gaId="G-EP0CT5LECX" />
    </html>
  )
}
