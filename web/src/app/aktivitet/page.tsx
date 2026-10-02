import Link from "next/link"
import { Breadcrumbs } from "@/components/ui/breadcrumbs"
import { AktivitetLinje } from "@/components/aktivitet/AktivitetLinje"
import { AlderStolper } from "@/components/aktivitet/AlderStolper"
import {
  ALDERSBAND,
  KATEGORIER,
  endring,
  hentKlubber,
  hentPerAar,
  hentPerAlder,
  lesFiltre,
  tall,
  type Filtre,
} from "@/lib/aktivitet"

export const metadata = {
  title: "Aktivitet og deltakelse",
  description: "Deltakelse i norsk friidrett, fordelt på alder, kjønn og øvelsesgruppe",
}

export const revalidate = 3600

type Sp = Record<string, string | undefined>

function url(f: Filtre, endringer: Partial<Record<keyof Filtre | "visning", string | number | null>>, sp: Sp) {
  const p = new URLSearchParams()
  const verdier: Record<string, string | number | null | undefined> = {
    fra: f.fra, til: f.til, kjonn: f.kjonn, alder: f.alder, kategori: f.kategori,
    visning: sp.visning, ...endringer,
  }
  for (const [k, v] of Object.entries(verdier)) {
    if (v !== null && v !== undefined && v !== "") p.set(k, String(v))
  }
  return `/aktivitet?${p.toString()}`
}

function Chip({ href, aktiv, children, deaktivert }: {
  href?: string; aktiv?: boolean; children: React.ReactNode; deaktivert?: boolean
}) {
  const klasse =
    "inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-[13px] transition-colors " +
    (aktiv
      ? "border-[var(--nfif-navy)] bg-[var(--nfif-navy)] font-semibold text-white"
      : deaktivert
        ? "cursor-not-allowed border-[var(--border-default)] bg-[var(--bg-surface)] text-[var(--text-muted)]"
        : "border-[var(--border-default)] bg-[var(--bg-surface)] text-[var(--text-primary)] hover:border-[var(--nfif-navy-lys)]")
  if (!href || deaktivert) return <span className={klasse}>{children}</span>
  return <Link href={href} className={klasse + " no-underline hover:no-underline"}>{children}</Link>
}

function Flis({ navn, verdi, endringPst, endringTekst }: {
  navn: string; verdi: string; endringPst: number | null; endringTekst: string
}) {
  const farge =
    endringPst === null ? "text-[var(--text-muted)]"
      : endringPst < -1 ? "text-[var(--nfif-rod)]"
        : endringPst > 1 ? "text-[var(--serie-3)]"
          : "text-[var(--text-muted)]"
  const tekst =
    endringPst === null ? "" : Math.abs(endringPst) <= 1 ? "uendret " : `${endringPst > 0 ? "+" : "−"}${Math.abs(endringPst)} % `
  return (
    <div className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] px-[18px] py-4">
      <div className="text-[12px] font-bold uppercase tracking-[0.06em] text-[var(--text-muted)]">{navn}</div>
      <div className="my-0.5 text-[30px] font-black tracking-tight tabular-nums text-[var(--text-primary)]">{verdi}</div>
      <div className={`text-[12.5px] font-bold ${farge}`}>{tekst}{endringTekst}</div>
    </div>
  )
}

function Kort({ tittel, children, className = "" }: { tittel: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] p-5 ${className}`}>
      <h2 className="mb-3 text-[16px] font-bold tracking-tight">{tittel}</h2>
      {children}
    </div>
  )
}

export default async function AktivitetSide({ searchParams }: { searchParams: Promise<Sp> }) {
  const sp = await searchParams
  const naa = new Date()
  // Inneværende sesong er ufullstendig til den er over; standardutvalget
  // slutter derfor på siste hele år.
  const sisteHeleAar = naa.getMonth() >= 10 ? naa.getFullYear() : naa.getFullYear() - 1
  const f = lesFiltre(sp, sisteHeleAar)

  const [rader, alderFra, alderTil, klubber] = await Promise.all([
    hentPerAar(f),
    hentPerAlder(f.fra, f),
    hentPerAlder(f.til, f),
    hentKlubber(f.fra, f.til),
  ])

  const forste = rader[0]
  const siste = rader[rader.length - 1]
  const perDeltaker = (r?: { starter: number; unike: number }) =>
    r && r.unike ? r.starter / r.unike : undefined

  const linjedata = rader.map((r) => ({ aar: r.aar, alle: r.unike, ungdom: f.alder ? null : r.unike_ungdom }))
  const band = ["under13", "13-19", "20-34", "35+"].map((b) => ({
    band: ALDERSBAND[b], fra: alderFra[b] ?? 0, til: alderTil[b] ?? 0,
  }))
  const kjonn = siste ? { menn: siste.menn, kvinner: siste.kvinner } : null
  const kjonnSum = kjonn ? kjonn.menn + kjonn.kvinner : 0
  const visTabell = sp.visning === "tabell"

  const aarValg = [
    { navn: `2019–${sisteHeleAar}`, fra: 2019, til: sisteHeleAar },
    { navn: `2013–${sisteHeleAar}`, fra: 2013, til: sisteHeleAar },
    { navn: `Siste tre år`, fra: sisteHeleAar - 2, til: sisteHeleAar },
    { navn: `Til og med ${naa.getFullYear()}`, fra: 2019, til: naa.getFullYear() },
  ]

  return (
    <div className="container py-6">
      <Breadcrumbs items={[{ label: "Aktivitet" }]} />

      {/* Sidetopp i Norsk Friidretts profil, som paa de andre sidene */}
      <div className="relative -mx-4 overflow-hidden bg-[var(--nfif-navy)] sm:-mx-6 lg:-mx-8">
        <div aria-hidden className="pointer-events-none absolute inset-0 bg-gradient-to-br from-[var(--nfif-navy-dyp)] via-[var(--nfif-navy)] to-[var(--nfif-navy-lys)]" />
        <div className="relative flex flex-col gap-3 px-4 py-6 sm:px-6 md:flex-row md:items-end md:justify-between lg:px-8">
          <div>
            <h1 className="text-[27px] font-black tracking-tight text-white">Aktivitet og deltakelse</h1>
            <p className="mt-1 text-[14.5px] text-[var(--nfif-navy-blekk)]">
              Deltakelse i norsk friidrett, fordelt på alder, kjønn og øvelsesgruppe. Kravspekkens §12.
            </p>
          </div>
          <a
            href={url(f, {}, sp).replace("/aktivitet?", "/aktivitet/eksport?")}
            className="inline-flex items-center justify-center rounded-lg border border-white/25 bg-white/10 px-4 py-2 text-[13px] font-medium text-white no-underline hover:bg-white/20 hover:no-underline"
          >
            Eksporter CSV
          </a>
        </div>
      </div>

      {/* Filtre */}
      <div className="mt-5 space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="w-24 text-[12px] font-bold uppercase tracking-wide text-[var(--text-muted)]">År</span>
          {aarValg.map((v) => (
            <Chip key={v.navn} href={url(f, { fra: v.fra, til: v.til }, sp)} aktiv={f.fra === v.fra && f.til === v.til}>{v.navn}</Chip>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="w-24 text-[12px] font-bold uppercase tracking-wide text-[var(--text-muted)]">Kjønn</span>
          <Chip href={url(f, { kjonn: null }, sp)} aktiv={!f.kjonn}>Alle</Chip>
          <Chip href={url(f, { kjonn: "M" }, sp)} aktiv={f.kjonn === "M"}>Menn</Chip>
          <Chip href={url(f, { kjonn: "F" }, sp)} aktiv={f.kjonn === "F"}>Kvinner</Chip>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="w-24 text-[12px] font-bold uppercase tracking-wide text-[var(--text-muted)]">Alder</span>
          <Chip href={url(f, { alder: null }, sp)} aktiv={!f.alder}>Alle</Chip>
          {Object.entries(ALDERSBAND).map(([k, n]) => (
            <Chip key={k} href={url(f, { alder: k }, sp)} aktiv={f.alder === k}>{n}</Chip>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="w-24 text-[12px] font-bold uppercase tracking-wide text-[var(--text-muted)]">Øvelse</span>
          <Chip href={url(f, { kategori: null }, sp)} aktiv={!f.kategori}>Alle</Chip>
          {Object.entries(KATEGORIER).map(([k, n]) => (
            <Chip key={k} href={url(f, { kategori: k }, sp)} aktiv={f.kategori === k}>{n}</Chip>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="w-24 text-[12px] font-bold uppercase tracking-wide text-[var(--text-muted)]">Krets</span>
          <Chip deaktivert>Hele landet</Chip>
          <span className="text-[12.5px] text-[var(--text-muted)]">
            Kretsdimensjonen krever klubb-til-krets-tilordning fra NFIF. Den kan ikke utledes trygt fra klubbnavn.
          </span>
          <Link href={url(f, { visning: visTabell ? null : "tabell" }, sp)} className="ml-auto text-[13px]">
            {visTabell ? "Vis som graf" : "Vis som tabell"}
          </Link>
        </div>
      </div>

      {rader.length === 0 ? (
        <p className="mt-8 text-center text-[var(--text-muted)]">Ingen aktivitet i utvalget.</p>
      ) : (
        <>
          {/* Fliser */}
          <div className="mt-5 grid gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
            <Flis navn={`Stevner ${siste.aar}`} verdi={tall(siste.stevner)} endringPst={endring(forste.stevner, siste.stevner)} endringTekst={`mot ${forste.aar}`} />
            <Flis navn={`Starter ${siste.aar}`} verdi={tall(siste.starter)} endringPst={endring(forste.starter, siste.starter)} endringTekst={`mot ${forste.aar}`} />
            <Flis navn={`Unike deltakere ${siste.aar}`} verdi={tall(siste.unike)} endringPst={endring(forste.unike, siste.unike)} endringTekst={`mot ${forste.aar}`} />
            <Flis navn="Starter per deltaker" verdi={tall(perDeltaker(siste), 1)} endringPst={endring(perDeltaker(forste), perDeltaker(siste))} endringTekst={`siden ${forste.aar}`} />
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-[1.5fr_1fr]">
            <Kort tittel="Unike deltakere per år">
              <div className="mb-1 flex gap-4 text-[13px] text-[var(--text-secondary)]">
                <span className="flex items-center gap-1.5"><i className="inline-block h-2.5 w-2.5 rounded-full bg-[var(--serie-1)]" /> Alle aldre</span>
                {!f.alder && <span className="flex items-center gap-1.5"><i className="inline-block h-2.5 w-2.5 rounded-full bg-[var(--serie-2)]" /> 13–19 år</span>}
              </div>
              {visTabell ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-[13.5px]">
                    <thead>
                      <tr className="border-b text-left text-[11.5px] uppercase tracking-wide text-[var(--text-muted)]">
                        <th className="py-1.5 pr-3">År</th><th className="py-1.5 pr-3 text-right">Stevner</th><th className="py-1.5 pr-3 text-right">Starter</th>
                        <th className="py-1.5 pr-3 text-right">Unike</th>{!f.alder && <th className="py-1.5 text-right">13–19 år</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {rader.map((r) => (
                        <tr key={r.aar} className="border-b last:border-0">
                          <td className="py-1.5 pr-3 tabular-nums">{r.aar}</td>
                          <td className="py-1.5 pr-3 text-right tabular-nums">{tall(r.stevner)}</td>
                          <td className="py-1.5 pr-3 text-right tabular-nums">{tall(r.starter)}</td>
                          <td className="py-1.5 pr-3 text-right tabular-nums font-semibold">{tall(r.unike)}</td>
                          {!f.alder && <td className="py-1.5 text-right tabular-nums">{tall(r.unike_ungdom)}</td>}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <AktivitetLinje data={linjedata} visUngdom={!f.alder} />
              )}
              <p className="mt-2 text-[12.5px] text-[var(--text-muted)]">
                Unike personer med minst ett godkjent resultat i året. Inneværende sesong er ufullstendig til den er over.
              </p>
            </Kort>

            <div className="grid gap-4">
              <Kort tittel="Aktive klubber">
                <table className="w-full text-[13.5px]">
                  <thead>
                    <tr className="border-b text-left text-[11.5px] uppercase tracking-wide text-[var(--text-muted)]">
                      <th className="py-1.5">År</th><th className="py-1.5 text-right">Alle</th><th className="py-1.5 text-right">Med 20+ resultater</th>
                    </tr>
                  </thead>
                  <tbody>
                    {klubber.slice(-4).map((k) => (
                      <tr key={k.aar} className="border-b last:border-0">
                        <td className="py-1.5 tabular-nums">{k.aar}</td>
                        <td className="py-1.5 text-right tabular-nums">{tall(k.alle)}</td>
                        <td className="py-1.5 text-right tabular-nums font-bold">{tall(k.aktive)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="mt-2 text-[12.5px] text-[var(--text-muted)]">
                  <b>Råtallet overdriver.</b> Klubber med under tjue resultater er i hovedsak skoler og lag innom ett stevne.
                  Kolonnen til høyre er klubber med reell aktivitet.
                </p>
              </Kort>

              {kjonn && kjonnSum > 0 && (
                <Kort tittel={`Kjønnsfordeling ${siste.aar}`}>
                  <div className="flex h-[22px] w-full gap-1 overflow-hidden rounded">
                    <div className="flex items-center rounded bg-[var(--serie-1)] px-2 text-[11.5px] font-bold text-white" style={{ width: `${(kjonn.menn / kjonnSum) * 100}%` }}>Menn {tall(kjonn.menn)}</div>
                    <div className="flex items-center rounded bg-[var(--serie-3)] px-2 text-[11.5px] font-bold text-white" style={{ width: `${(kjonn.kvinner / kjonnSum) * 100}%` }}>Kvinner {tall(kjonn.kvinner)}</div>
                  </div>
                  <div className="mt-1 flex justify-between text-[11px] text-[var(--text-muted)]">
                    <span>{Math.round((kjonn.menn / kjonnSum) * 100)} %</span><span>{Math.round((kjonn.kvinner / kjonnSum) * 100)} %</span>
                  </div>
                </Kort>
              )}

              <Kort tittel="Mest aktive kretser">
                <p className="text-[13px] text-[var(--text-muted)]">
                  Krever klubb-til-krets-tilordning fra NFIF. Kretsdimensjonen er den ene opplysningen vi ikke kan utlede trygt fra dataene selv.
                </p>
              </Kort>
            </div>
          </div>

          {!f.alder && (
            <Kort tittel={`Deltakelse per aldersklasse · ${f.fra} mot ${f.til}`} className="mt-4">
              <div className="mb-1 flex gap-4 text-[13px] text-[var(--text-secondary)]">
                <span className="flex items-center gap-1.5"><i className="inline-block h-2.5 w-2.5 rounded-sm bg-[var(--serie-1)]" /> {f.fra}</span>
                <span className="flex items-center gap-1.5"><i className="inline-block h-2.5 w-2.5 rounded-sm bg-[var(--serie-2)]" /> {f.til}</span>
              </div>
              <AlderStolper data={band} fraAar={f.fra} tilAar={f.til} />
              <p className="mt-2 text-[12.5px] text-[var(--text-muted)]">
                Alder er konkurranseår minus fødselsår, slik norsk friidrett regner aldersklasser.
              </p>
            </Kort>
          )}
        </>
      )}
    </div>
  )
}
