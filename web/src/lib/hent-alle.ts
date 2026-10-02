/**
 * Hent alle radene fra en spørring, ikke bare de første tusen.
 *
 * PostgREST leverer aldri mer enn 1 000 rader, og det sier den ikke fra om:
 * du får tusen rader og ingen feil. Flere sider hentet «alt» i én spørring
 * og regnet nøkkeltall ut fra det de fikk, så de oppga avkortede tall som
 * fakta. Stevnesiden sto med «Resultater 1 000» for Tyrvinglekene, som har
 * 3 299, og utøverprofilen med det samme for de 37 utøverne som har mer
 * enn tusen resultater.
 *
 * Bruk denne der radtallet ikke er kjent på forhånd og alle radene trengs.
 * Skal du bare vise en liste, sett heller en grense og si hvor mange av
 * hvor mange du viser.
 */
const SIDE = 1000

export async function hentAlle<T>(
  /** Kalles per side. Må sette rekkefølge og range(fra, til). */
  hentSide: (
    fra: number,
    til: number
  ) => PromiseLike<{ data: T[] | null; error: { message: string } | null }>,
  /** Navn til loggen når noe feiler. */
  merkelapp: string,
  /** Sikkerhetsventil mot uendelig løkke. */
  maksSider = 10
): Promise<T[]> {
  const alle: T[] = []

  for (let side = 0; side < maksSider; side++) {
    const { data, error } = await hentSide(side * SIDE, side * SIDE + SIDE - 1)

    if (error) {
      console.error(`${merkelapp}: kunne ikke hente side ${side + 1}:`, error.message)
      break
    }
    if (!data?.length) break

    alle.push(...data)
    if (data.length < SIDE) break

    if (side === maksSider - 1) {
      console.warn(
        `${merkelapp}: stoppet på ${maksSider * SIDE} rader. Taket er nådd, ` +
          `så lista kan være avkortet.`
      )
    }
  }

  return alle
}
