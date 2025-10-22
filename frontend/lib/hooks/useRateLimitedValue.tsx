import { useRef, useEffect, useState } from 'react'

/**
 * A React hook that rate-limits the updates of a value by queuing changes and releasing them at a specified interval.
 *
 * @template V - The type of the value being rate-limited
 * @param v - The input value to be rate-limited
 * @param wait - The minimum time (in milliseconds) to wait between value updates
 * @returns The rate-limited value, which updates no more frequently than the specified wait time
 *
 * @example
 * ```tsx
 * // Rate limit value updates to once per second
 * const value = "some value";
 * const limitedValue = useRateLimitedValue(value, 1000);
 * ```
 *
 * @description
 * This hook is useful for scenarios where you need to throttle rapid value changes,
 * such as handling frequent user input or API updates. It maintains a queue of changes
 * and processes them according to the specified wait time, ensuring that updates
 * don't occur more frequently than desired.
 */
export const useRateLimitedValue = <V,>(v: V, wait: number) => {
  const [limitedValue, setLimitedValue] = useState(() => v)
  const queue = useRef<V[]>([])
  const [queueHasValues, setQueueHasValues] = useState(false)
  const lastUpdate = useRef(0)

  useEffect(() => {
    if (v === limitedValue) return
    queue.current.push(v)
    if (!queueHasValues) {
      setQueueHasValues(true)
    }
  }, [v])

  useEffect(() => {
    // If queue is Empty, no need to do anything
    if (!queueHasValues) {
      return
    }

    // Updates `limitedValue` to the next value in the queue
    const update = () => {
      if (queue.current.length === 0) {
        setQueueHasValues(false)
        return
      }
      setLimitedValue(queue.current.shift()!)
      lastUpdate.current = Date.now()
      if (queue.current.length === 0) {
        setQueueHasValues(false)
      }
    }

    // If more than wait time has elapsed since last update, update `limitedValue` immediately
    if (lastUpdate.current + wait < Date.now()) {
      update()
      // If queue is empty after update, no need to do anything, return early
      if (queue.current.length === 0) {
        setQueueHasValues(false)
        return
      }
    }

    // Set a timeout to update `limitedValue` after wait time
    let timeout: ReturnType<typeof setTimeout>
    const timeoutCb = () => {
      update()
      // If queue is empty after update, no need to do anything, return early
      if (queue.current.length === 0) {
        setQueueHasValues(false)
        return
      }
      // Otherwise, set a timeout to update `limitedValue` after wait time
      timeout = setTimeout(timeoutCb, wait)
    }
    timeout = setTimeout(timeoutCb, wait)

    // Cleanup function to clear the timeout when component unmounts or when queueHasValues changes
    return () => {
      clearTimeout(timeout)
    }
  }, [queueHasValues])

  return limitedValue
}
