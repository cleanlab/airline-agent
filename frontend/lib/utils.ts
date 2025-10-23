import { customAlphabet } from 'nanoid'
import { AGILITY_DEFAULT_ASSISTANT_SLUG } from './consts'

export const nanoid = customAlphabet(
  '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
  7
) // 7-character random string

export async function fetcher<JSON = any>(
  input: RequestInfo,
  init?: RequestInit
): Promise<JSON> {
  const res = await fetch(input, init)

  if (!res.ok) {
    const json = await res.json()
    if (json.error) {
      const error = new Error(json.error) as Error & {
        status: number
      }
      error.status = res.status
      throw error
    } else {
      throw new Error('An unexpected error occurred')
    }
  }

  return res.json()
}

export function formatDate(input: string | number | Date): string {
  const date = new Date(input)
  return date.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

export const formatNumber = (value: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)

export const runAsyncFnWithoutBlocking = (
  fn: (...args: any) => Promise<any>
) => {
  fn()
}

export const sleep = (ms: number) =>
  new Promise(resolve => setTimeout(resolve, ms))

export const getStringFromBuffer = (buffer: ArrayBuffer) =>
  Array.from(new Uint8Array(buffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')

export enum ResultCode {
  InvalidCredentials = 'INVALID_CREDENTIALS',
  InvalidSubmission = 'INVALID_SUBMISSION',
  UserAlreadyExists = 'USER_ALREADY_EXISTS',
  UnknownError = 'UNKNOWN_ERROR',
  UserCreated = 'USER_CREATED',
  UserLoggedIn = 'USER_LOGGED_IN'
}

export const getMessageFromCode = (resultCode: string) => {
  switch (resultCode) {
    case ResultCode.InvalidCredentials:
      return 'Invalid credentials!'
    case ResultCode.InvalidSubmission:
      return 'Invalid submission, please try again!'
    case ResultCode.UserAlreadyExists:
      return 'User already exists, please log in!'
    case ResultCode.UserCreated:
      return 'User created, welcome!'
    case ResultCode.UnknownError:
      return 'Something went wrong, please try again!'
    case ResultCode.UserLoggedIn:
      return 'Logged in!'
  }
}

type RecordWithStringKey = Record<string | number, any>

export const camelCaseKeys = (
  input: RecordWithStringKey[] | RecordWithStringKey
): any => {
  // if array OR object, recurse. Exclude null because in JS, null is also an object ¯\_(ツ)_/¯
  // function is also type object, but we won't receive those from an API so not checking for that at the moment
  if (typeof input === 'object' && input !== null) {
    if (Array.isArray(input)) {
      return input.map(item => camelCaseKeys(item))
    } else {
      const output: RecordWithStringKey = {}

      // eslint-disable-next-line no-restricted-syntax
      for (const key in input) {
        const camelKey = key.replace(
          /([a-z])_([a-z])/g,
          (_, firstLetter, secondLetter) =>
            `${firstLetter}${secondLetter.toUpperCase()}`
        )

        output[camelKey] = camelCaseKeys(input[key])
      }

      return output
    }
  } else {
    return input
  }
}

export function truncateString(str: string, maxLength: number) {
  if ((str?.length ?? 0) <= maxLength) {
    return str
  } else {
    return str.slice(0, maxLength - 3) + '...'
  }
}

export const getIsDefaultAssistant = (assistantSlug?: string | null) =>
  assistantSlug === AGILITY_DEFAULT_ASSISTANT_SLUG

export const IS_PROD = process.env.NEXT_PUBLIC_VERCEL_ENV === 'production'
