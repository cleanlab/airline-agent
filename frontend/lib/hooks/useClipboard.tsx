'use client'
import { useCallback, useRef, useState } from 'react'

export const useClipboard = (timeout: number) => {
  const [hasCopied, setHasCopied] = useState(false)
  const timeoutId = useRef<ReturnType<typeof setTimeout> | null>(null)
  const copyToClipboard = useCallback(
    (value: string) => {
      if (
        typeof window === 'undefined' ||
        !navigator.clipboard?.writeText ||
        !value
      ) {
        return
      }

      if (timeoutId.current !== null) {
        clearTimeout(timeoutId.current)
      }
      navigator.clipboard.writeText(value)
      setHasCopied(true)
      if (timeout) {
        timeoutId.current = setTimeout(() => setHasCopied(false), timeout)
      }
    },
    [timeout]
  )
  return { copyToClipboard, hasCopied }
}
