// Forked from `merge-props`: https://github.com/andrewbranch/merge-props
// Modified to overwrite duplicate props instead of throwing an error and use `cn` for className merging

import { cn } from './tailwindUtils'

type UnionToIntersection<U> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void
  ? I
  : never

function pushProp(target: { [key: string]: any }, key: string, value: any): void {
  if (key === 'className') {
    target.className = cn(target.className, value)
  } else if (key === 'style') {
    target.style = { ...target.style, ...value }
  } else if (
    typeof value === 'function' &&
    typeof target[key] === 'function' &&
    // This is a lot faster than a regex.
    key[0] === 'o' &&
    key[1] === 'n' &&
    key.charCodeAt(2) >= /* 'A' */ 65 &&
    key.charCodeAt(2) <= /* 'Z' */ 90
  ) {
    const oldFn = target[key]
    target[key] = oldFn
      ? (...args: any[]) => {
          oldFn(...args)
          value(...args)
        }
      : value
  } else if (
    // skip merging undefined values
    value === undefined ||
    // skip if both value are the same primitive value
    (typeof value !== 'object' && value === target[key])
  ) {
    return
  } else {
    if (key in target) {
      console.warn(
        `mergeProps: Overwriting prop: ${key}\n    From: ${target[key]}\n    To:   ${value}`
      )
    }
    target[key] = value
  }
}

/**
 * Merges sets of props together:
 *  - duplicate `className` props get concatenated
 *  - duplicate `style` props get shallow merged (later props have precedence for conflicting rules)
 *  - duplicate functions (to be used for event handlers) get called in order from left to right
 *  - all other are overwritten (later props have precedence)
 * @param props Sets of props to merge together. Later props have precedence.
 */
function mergeProps<T extends Record<string, any>[]>(
  ...props: T
): {
  [K in keyof UnionToIntersection<T[number]>]: K extends 'className'
    ? string
    : K extends 'style'
      ? UnionToIntersection<T[number]>[K]
      : Exclude<Extract<T[number], { [Q in K]: unknown }>[K], undefined>
} {
  if (props.length === 1) {
    return props[0] as any
  }

  return props.reduce((merged, ps: any) => {
    Object.entries(ps).forEach(([key, value]) => {
      pushProp(merged, key, value)
    })
    return merged
  }, {}) as any
}

export { mergeProps }
