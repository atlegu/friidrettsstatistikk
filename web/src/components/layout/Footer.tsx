import Link from "next/link"

const footerLinks = {
  statistikk: [
    { name: "Årslister", href: "/statistikk/2025" },
    { name: "All-time", href: "/statistikk/all-time" },
    { name: "Rekorder", href: "/statistikk/rekorder" },
  ],
  stevner: [
    { name: "Kalender", href: "/stevner" },
    { name: "Resultater", href: "/stevner/resultater" },
  ],
  om: [
    { name: "Om systemet", href: "/om" },
    { name: "API", href: "/api-docs" },
    { name: "Personvern", href: "/personvern" },
  ],
}

export function Footer() {
  return (
    <footer className="border-t bg-muted/40">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-xl font-bold text-primary">friidrettresultater</span>
              <span className="text-xl font-light">.no</span>
            </Link>
            <p className="mt-4 text-sm text-muted-foreground">
              Norsk friidrettsstatistikk - fra rekrutt til veteran.
            </p>
          </div>

          {/* Statistikk */}
          <div>
            <h3 className="text-sm font-semibold">Statistikk</h3>
            <ul className="mt-4 space-y-2">
              {footerLinks.statistikk.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-primary"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Stevner */}
          <div>
            <h3 className="text-sm font-semibold">Stevner</h3>
            <ul className="mt-4 space-y-2">
              {footerLinks.stevner.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-primary"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Om */}
          <div>
            <h3 className="text-sm font-semibold">Om oss</h3>
            <ul className="mt-4 space-y-2">
              {footerLinks.om.map((link) => (
                <li key={link.name}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-primary"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t pt-8">
          <p className="text-center text-sm text-muted-foreground">
            © Friidrettsresultater.no utviklet av Athlete Mindset Inc. for Norges Friidrettsforbund
          </p>
        </div>
      </div>
    </footer>
  )
}
