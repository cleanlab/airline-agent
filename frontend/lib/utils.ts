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

export const getIsDefaultAssistant = (assistantSlug?: string | null) =>
  assistantSlug === ''

export const IS_PROD = process.env.NEXT_PUBLIC_VERCEL_ENV === 'production'
