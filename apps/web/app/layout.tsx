import type { Metadata } from 'next'
import { Inter, Bowlby_One_SC } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800', '900'],
  display: 'swap',
})

const bowlbyOne = Bowlby_One_SC({
  weight: '400',
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-bowlby',
})

export const metadata: Metadata = {
  title: 'Kopitiam Capital',
  description: 'AI-powered pocket analyst for traders',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={bowlbyOne.variable}>
      <body className={inter.className}>{children}</body>
    </html>
  )
}

