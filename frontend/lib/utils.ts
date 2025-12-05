import { customAlphabet } from 'nanoid'

export const nanoid = customAlphabet(
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
  7
) // 7-character random string

export function truncateString(str: string, maxLength: number) {
  if ((str?.length ?? 0) <= maxLength) {
    return str
  } else {
    return str.slice(0, maxLength - 3) + '...'
  }
}
