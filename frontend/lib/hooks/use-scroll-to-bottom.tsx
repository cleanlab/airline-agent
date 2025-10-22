import { useCallback, useEffect, useRef, useState } from 'react'
import useResizeObserver from './use-resize-observer'

function isScrolledToBottom(
  element: HTMLElement,
  threshold: number = 1
): boolean {
  const { scrollTop, scrollHeight, clientHeight } = element
  // https://stackoverflow.com/a/71076218/2926283
  // NOTE: scrollTop is fractional, while scrollHeight and clientHeight are
  // not, so without this Math.abs() trick then sometimes the result won't
  // work because scrollTop may not be exactly equal to el.scrollHeight -
  // el.clientHeight when scrolled to the bottom.
  return Math.abs(scrollHeight - clientHeight - scrollTop) < threshold
}

export function scrollElementToBottom(
  element: HTMLElement,
  behavior?: ScrollBehavior
) {
  element.scrollTo({
    top: element.scrollHeight,
    behavior: behavior
  })
}

export const useScrollToBottom = () => {
  const scrollRef = useRef<HTMLDivElement>(null)

  const [isAtBottom, setIsAtBottom] = useState(true)

  const scrollToBottom = useCallback(() => {
    if (scrollRef.current) {
      scrollElementToBottom(scrollRef.current)
    }
  }, [])

  const updateIsAtBottom = () => {
    if (scrollRef.current) {
      if (isScrolledToBottom(scrollRef.current)) {
        setIsAtBottom(true)
      } else {
        setIsAtBottom(false)
      }
    }
  }

  // Check isAtBottom when scroll container is resized
  useResizeObserver(scrollRef, updateIsAtBottom)

  // Check isAtBottom when scroll container is scrolled
  useEffect(() => {
    const { current } = scrollRef
    if (current) {
      current.addEventListener('scroll', updateIsAtBottom, {
        passive: true
      })
      return () => {
        current.removeEventListener('scroll', updateIsAtBottom)
      }
    }
  }, [])

  return {
    scrollRef,
    scrollToBottom,
    isAtBottom
  }
}
