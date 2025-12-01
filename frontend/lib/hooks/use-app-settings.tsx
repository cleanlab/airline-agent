'use client'

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
      assistantId: 'default',
      orgName: null,
      iframeSrc: null
    }
  )

  return [appSettings, setAppSettings] as const
}
