import { useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useBareRagAppStore } from '@/providers/rag-app-store-provider'
import { useBareMessagesStore } from '@/providers/messages-store-provider'

export function useClearHistory() {
  const ragAppStore = useBareRagAppStore()
  const messagesStore = useBareMessagesStore()
  const router = useRouter()

  const clearHistory = useCallback(() => {
    try {
      localStorage.removeItem('ragApp')
    } catch {}

    try {
      const keysToRemove: string[] = []
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (!key) continue
        if (key.startsWith('cleanlabEnabled:thread:')) {
          keysToRemove.push(key)
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key))
    } catch {}

    try {
      ragAppStore.setState({ history: {}, responseRatings: {} })
    } catch {}
    try {
      messagesStore.getState().resetState()
    } catch {}

    try {
      router.replace('/')
    } catch {}
  }, [ragAppStore, messagesStore, router])

  return clearHistory
}
