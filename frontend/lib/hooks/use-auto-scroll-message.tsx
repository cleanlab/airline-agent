'use client'

import type { RefObject } from 'react'
import { useEffect } from 'react'

const SCROLL_PADDING = 24
const calculateMessageScrollPosition = (
  message: HTMLElement | undefined | null
) => {
  if (!message) {
    return 0
  }
  return message.offsetTop - SCROLL_PADDING
}
const isMessageScrolledIntoView = (
  scrollRef: RefObject<HTMLElement | null>,
  message: HTMLElement | undefined | null
) => {
  if (!message || !scrollRef.current) {
    return false
  }
  const nextTop = calculateMessageScrollPosition(message)
  return nextTop < scrollRef.current?.scrollTop
}
// Rename to scrollMessageIntoView for consistency
const scrollMessageIntoView = (
  scrollRef: RefObject<HTMLElement | null>,
  message: HTMLElement | undefined | null
) => {
  if (
    !message ||
    !scrollRef.current ||
    isMessageScrolledIntoView(scrollRef, message)
  ) {
    return false
  }
  const nextTop = message.offsetTop - SCROLL_PADDING
  if (nextTop < scrollRef.current?.scrollTop) {
    return false
  }
  scrollRef.current?.scrollTo({
    top: nextTop,
    behavior: 'smooth'
  })
  return true
}
/**
 * Auto-scroll messageRef.current into view on first mount and whenever its content changes and it is out of view
 * @param scrollRef ref to the scrollable container
 * @param messageRef ref to the message element to auto-scroll into view
 * @param isEnabled whether the auto-scrolling is enabled
 **/

export const useAutoScrollMessage = (
  scrollRef: RefObject<HTMLElement | null>,
  messageRef: RefObject<HTMLElement | null>,
  isEnabled: boolean
) => {
  // Used to scroll to message when it's first rendered
  useEffect(() => {
    if (!messageRef.current || !isEnabled) {
      return
    }

    scrollMessageIntoView(scrollRef, messageRef.current)
  }, [messageRef, scrollRef, isEnabled])
  // Observes for changes to the message content and scrolls to it if necessary
  useEffect(() => {
    if (!messageRef.current || !isEnabled) {
      return
    }
    const controller = new AbortController()

    const observer = new MutationObserver(() => {
      if (isEnabled && messageRef.current) {
        const didScroll = scrollMessageIntoView(scrollRef, messageRef.current)
        if (!didScroll) {
          // If already scrolled past the message, stop observing for changes
          observer.disconnect()
          controller.abort()
        }
      }
    })
    observer.observe(messageRef.current, {
      childList: true,
      subtree: true
    })
    messageRef.current.addEventListener(
      'scroll',
      () => {
        if (isMessageScrolledIntoView(scrollRef, messageRef.current)) {
          controller.abort()
        }
      },
      { signal: controller.signal }
    )
    const abortListener = () => {
      observer.disconnect()
    }
    controller.signal.addEventListener('abort', abortListener)
    return () => {
      controller?.signal?.removeEventListener('abort', abortListener)
      controller?.abort()
    }
  }, [messageRef, scrollRef, isEnabled])
}
