'use server'

import { redirect } from 'next/navigation'

export async function refreshHistory(path: string) {
  redirect(path)
}

const KEYS_REQUIRED: readonly string[] = []

export async function getMissingKeys() {
  return KEYS_REQUIRED.map(key => (process.env[key] ? '' : key)).filter(
    key => key !== ''
  )
}
