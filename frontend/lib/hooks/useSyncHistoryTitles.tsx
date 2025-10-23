'use client'

import { useEffect } from 'react'
import { useMessagesStore } from '@/providers/messages-store-provider'
import { useRagAppStore } from '@/providers/rag-app-store-provider'
import { idsMatchThread } from '@/stores/history-thread-store'
import { useShallow } from 'zustand/shallow'

/**
 * A hook that synchronizes the history title with the first message in a thread.
 * When the first message content changes, it automatically updates the corresponding history thread title.
 *
 * @param assistantId - The ID of the assistant associated with the thread. Optional.
 *
 * @example
 * ```tsx
 * // In a component
 * useSyncHistoryTitles('assistant-123')
 * ```
 *
 * @remarks
 * - The hook watches for changes in the first message of the current thread
 * - If the first message content exists differs from the current history title, it updates the history
 * - Uses both threadId and localThreadId for thread identification
 */
export const useSyncHistoryTitles = (assistantId?: string) => {
  const [threadId, localThreadId, firstMessage] = useMessagesStore(
    useShallow(state => [
      state.currentThread?.threadId,
      state.currentThread?.localThreadId,
      state.currentThread?.messages?.[0]
    ])
  )
  const historyTitle = useRagAppStore(state => {
    if (!assistantId) return undefined

    return state?.history?.[assistantId]?.find(thread =>
      idsMatchThread({ thread: thread, localThreadId, threadId })
    )?.title
  })
  const updateHistoryThread = useRagAppStore(state => state.updateHistoryThread)

  useEffect(() => {
    if (firstMessage?.content && firstMessage?.content !== historyTitle) {
      updateHistoryThread({
        threadId,
        localThreadId,
        thread: { title: firstMessage?.content },
        assistantId: assistantId ?? ''
      })
    }
  }, [
    assistantId,
    firstMessage?.content,
    historyTitle,
    localThreadId,
    threadId,
    updateHistoryThread
  ])
}
