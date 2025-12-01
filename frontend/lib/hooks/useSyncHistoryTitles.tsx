'use client'

import { useEffect } from 'react'
import { useShallow } from 'zustand/shallow'

import { useMessagesStore } from '@/providers/messages-store-provider'
import { useRagAppStore } from '@/providers/rag-app-store-provider'
import { idsMatchThread } from '@/stores/history-thread-store'

/**
 * A hook that synchronizes the history title with the first message in a thread.
 * When the first message content changes, it automatically updates the corresponding history thread title.
 *
 * @remarks
 * - The hook watches for changes in the first message of the current thread
 * - If the first message content exists differs from the current history title, it updates the history
 * - Uses both threadId and localThreadId for thread identification
 */
export const useSyncHistoryTitles = () => {
  const [threadId, localThreadId, firstMessage] = useMessagesStore(
    useShallow(state => [
      state.currentThread?.threadId,
      state.currentThread?.localThreadId,
      state.currentThread?.messages?.[0]
    ])
  )
  const historyTitle = useRagAppStore(state => {
    return state?.history?.find(thread =>
      idsMatchThread({ thread, localThreadId, threadId })
    )?.title
  })
  const updateHistoryThread = useRagAppStore(state => state.updateHistoryThread)

  useEffect(() => {
    if (firstMessage?.content && firstMessage?.content !== historyTitle) {
      updateHistoryThread({
        threadId,
        localThreadId,
        thread: { title: firstMessage?.content }
      })
    }
  }, [
    firstMessage?.content,
    historyTitle,
    localThreadId,
    threadId,
    updateHistoryThread
  ])
}
