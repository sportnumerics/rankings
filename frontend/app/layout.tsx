import './globals.css'
import { Fira_Code } from 'next/font/google'

const inter = Fira_Code({ subsets: ['latin'] })

export const metadata = {
  title: 'Sportnumerics',
  description: 'NCAA and MCLA Lacrosse Computer Ratings',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
