import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Header } from "@/components/layout/Header"
import { Footer } from "@/components/layout/Footer"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

export const metadata: Metadata = {
  title: {
    default: "Friidrett.live - Norsk Friidrettsstatistikk",
    template: "%s | Friidrett.live",
  },
  description:
    "Komplett statistikk for norsk friidrett - årslister, rekorder, utøverprofiler og stevneresultater.",
  keywords: [
    "friidrett",
    "statistikk",
    "Norge",
    "resultater",
    "rekorder",
    "utøvere",
  ],
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="no">
      <body className={`${inter.variable} font-sans`}>
        <div className="relative flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  )
}
