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
