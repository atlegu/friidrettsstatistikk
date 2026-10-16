"use client"

import { useFormStatus } from "react-dom"

/**
 * Knapp i et behandlingsskjema (avvik, terminliste). Viser «Lagrer …» mens
 * lagringen pågår og låser alle knappene i skjemaet, så et dobbeltklikk ikke
 * sender samme handling flere ganger.
 */
export function BehandleKnapp({
  formAction,
  children,
  className,
  title,
}: {
  formAction: (formData: FormData) => void | Promise<void>
  children: React.ReactNode
  className?: string
  title?: string
}) {
  const { pending, action } = useFormStatus()
  const denne = pending && action === formAction
  return (
    <button
      formAction={formAction}
      disabled={pending}
      aria-busy={denne}
      title={title}
      className={`${className ?? ""} disabled:cursor-wait disabled:opacity-50`}
    >
      {denne ? "Lagrer …" : children}
    </button>
  )
}
