import { cache } from 'react'
import { AGILITY_DEFAULT_ASSISTANT_SLUG, getChatPath } from '@/lib/consts'

export const getCurrentAssistantSlug = cache(async function () {
  // Always coerce to the default assistant slug
  return AGILITY_DEFAULT_ASSISTANT_SLUG
})

export const getNewChatPath = cache(async function () {
  return getChatPath()
})
