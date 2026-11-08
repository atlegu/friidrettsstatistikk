import { redirect } from "next/navigation"

/* «Spør AI» er tatt ut av nettstedet 08.11.2026. Koden står igjen, så
 * funksjonen kan komme tilbake som betalt tillegg. Inntil da sendes
 * besøkende til forsiden. */
export default function SporLayout() {
  redirect("/")
}
