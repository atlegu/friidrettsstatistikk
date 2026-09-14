import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Header } from "@/components/layout/Header"
import { Footer } from "@/components/layout/Footer"
import { Providers } from "@/components/layout/Providers"
import { AuthErrorHandler } from "@/components/auth/AuthErrorHandler"

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
})

export const metadata: Metadata = {
  title: {
    default: "friidrettsresultater.no - Norsk Friidrettsstatistikk",
    template: "%s | friidrettsresultater.no",
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
    <html lang="no" data-density="compact">
      <body className={`${inter.variable} font-sans`}>
        <Providers>
          <AuthErrorHandler />
          <div className="relative flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  )
}
