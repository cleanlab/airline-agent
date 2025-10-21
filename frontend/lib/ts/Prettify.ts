/**
 * Utility type that flattens complex nested type definitions into a cleaner representation.
 * Useful for improving type readability in TypeScript's type system and IDE tooltips.
 *
 * @template T - The type to be prettified
 * @reference https://www.totaltypescript.com/concepts/the-prettify-helper
 *
 * @example
 * type Messy = { a: string } & { b: number } & { c: boolean }
 * type Clean = Prettify<Messy> // { a: string; b: number; c: boolean }
 */
export type Prettify<T> = {
  [K in keyof T]: T[K]
} & {}
