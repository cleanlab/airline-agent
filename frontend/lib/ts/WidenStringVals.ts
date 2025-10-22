/**
 * Takes any `string` or `Record` type and recursively widens any `string`
 * literal values into `strings` leaving all other types intact.
 *
 * @example
 * 'some string const' → string
 * { key0: '#FFFFFF' } → { key0: string }
 * { key0: '#FFFFFF', key1: { key2:'#000000', key3: 10 } }
 *   → { 'key0': string, key1: { key2: string, key3: 10 } }
 */
export type WidenStringVals<T> = T extends string
  ? string
  : T extends Record<string, any>
    ? {
        [K in keyof T]: WidenStringVals<T[K]>
      }
    : T
