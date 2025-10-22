/**
 * Prefixes a string type with another string type.
 * @template T - The original string type.
 * @template Prefix - The prefix string type (default is an empty string).
 */
type PrefixString<T extends string, Prefix extends string = ''> = `${Prefix}${T}`

/**
 * Creates a new type by prefixing all keys of an object type with a given prefix.
 * @template T - The original object type.
 * @template Prefix - The prefix string type.
 * @template Val - The value type (default is void, which keeps the original value types).
 */
type PrefixKeys<T extends object, Prefix extends string, Val = void> = {
  [key in keyof T as PrefixString<key & string, Prefix>]: Val extends void ? T[key] : Val
}

/**
 * Suffixes a string type with another string type.
 * @template T - The original string type.
 * @template Suffix - The suffix string type (default is an empty string).
 */
type SuffixString<T extends string, Suffix extends string = ''> = `${T}${Suffix}`

/**
 * Creates a new type by suffixing all keys of an object type with a given suffix.
 * @template T - The original object type.
 * @template Suffix - The suffix string type (default is an empty string).
 * @template Val - The value type (default is void, which keeps the original value types).
 */
type SuffixKeys<T extends object, Suffix extends string = '', Val = void> = {
  [key in keyof T as SuffixString<key & string, Suffix>]: Val extends void ? T[key] : Val
}

/**
Add a string to the beginning of all keys in a string-keyed object
 * @param obj Object to modify the keys of
 * @param suffix String to add to the beginning of the keys
*/
function prefixKeys<T extends object, Prefix extends string>(obj: T, prefix: Prefix) {
  return Object.fromEntries(
    Object.entries(obj).map(([key, val]) => [`${prefix ?? ''}${key}`, val])
  ) as PrefixKeys<T, Prefix>
}

/**
 * Add a string to the end of all keys in a string-keyed object
 * @param obj Object to modify the keys of
 * @param suffix String to add to the end of the keys
 */
function suffixKeys<T extends object, Suffix extends string>(obj: T, suffix: Suffix) {
  return Object.fromEntries(
    Object.entries(obj).map(([key, val]) => [`${key}${suffix ?? ''}`, val])
  ) as SuffixKeys<T, Suffix>
}

/**
 * Creates a new type by adding a prefix and/or suffix to all string values in an object type.
 * @template T - The original object type with string values.
 * @template Prefix - The prefix string type (default is an empty string).
 * @template Suffix - The suffix string type (default is an empty string).
 */
type AffixValues<
  T extends Record<any, string>,
  Prefix extends string = '',
  Suffix extends string = '',
> = {
  [key in keyof T]: `${Prefix}${T[key]}${Suffix}`
}

/**
 * Add a string to the beginning and/or end of all values in a string-keyed object
 * @param obj Object to modify the values of
 * @param prefix String to add to the beginning of the keys
 * @param suffix String to add to the end of the keys
 */
function affixValues<
  T extends Record<string, string>,
  Prefix extends string = '',
  Suffix extends string = '',
>(obj: T, { prefix, suffix }: { prefix?: Prefix; suffix?: Suffix }) {
  return Object.fromEntries(
    Object.entries(obj).map(([key, val]) => [key, `${prefix || ''}${val}${suffix || ''}`])
  ) as AffixValues<T, Prefix, Suffix>
}

export type { AffixValues, PrefixKeys, PrefixString, SuffixKeys, SuffixString }
export { affixValues, prefixKeys, suffixKeys }
