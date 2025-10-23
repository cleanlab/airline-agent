import { type RefObject, useCallback } from 'react'
import ResizeObserver from 'resize-observer-polyfill'

import { useIsomorphicLayoutEffect } from './use-isomorphic-layout-effect'

const useResizeObserver = (
  ref: RefObject<HTMLElement>,
  callback: (entry: DOMRectReadOnly) => void
) => {
  const handleResize = useCallback(
    (entries: ResizeObserverEntry[]) => {
      if (!Array.isArray(entries)) {
        return
      }

      const entry = entries[0]

      if (callback) {
        callback(entry.contentRect)
      }
    },
    [callback]
  )

  useIsomorphicLayoutEffect(() => {
    if (!ref.current) {
      return
    }

    let RO: ResizeObserver | null = new ResizeObserver(
      (entries: ResizeObserverEntry[]) => handleResize(entries)
    )

    RO?.observe(ref.current)

    return () => {
      RO?.disconnect()
      RO = null
    }
  }, [ref, handleResize])
}

export { useResizeObserver }
