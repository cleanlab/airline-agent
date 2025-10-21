'use client'

import { AGILITY_DEFAULT_ASSISTANT_SLUG } from '../consts'
import { useLocalStorage } from './use-local-storage'

type AppSettings = {
  assistantId: string | null
  orgName: string | null
  iframeSrc: string | null
}

export const useAppSettings = () => {
  const [appSettings, setAppSettings] = useLocalStorage<AppSettings>(
    'appSettings',
    {
      assistantId: AGILITY_DEFAULT_ASSISTANT_SLUG ?? null,
      orgName: null,
      iframeSrc: null
    }
  )

  return [appSettings, setAppSettings] as const
}
