import type { Metadata } from 'next'
import { Sen } from 'next/font/google'
import localFont from 'next/font/local'
import './globals.css'

const sen = Sen({ 
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  display: 'swap',
  variable: '--font-body',
})

const bbhSansBogle = localFont({
  src: '../public/fonts/BBH_Sans_Bogle/BBHSansBogle-Regular.ttf',
  variable: '--font-heading',
  display: 'swap',
  weight: '700',
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
    <html lang="en" className={`${bbhSansBogle.variable} ${sen.variable}`}>
      <body className={sen.className}>{children}</body>
    </html>
  )
}

