import type { Thread } from '@/client'
import { produce } from 'immer'
import type { StateCreator } from 'zustand'
import type { Prettify } from '@/lib/ts/Prettify'
import type { AssistantId } from './common'

export type HistoryThread = {
  title: string
  assistantId: AssistantId
  snapshot?: {
    user: {
      content: string
      metadata?: any
    }
    assistant: {
      content: string
      metadata?: any
    }
  }
} & (
  | {
      localThreadId?: string
      thread: Thread
    }
  | { localThreadId: string; thread?: Thread }
)

export type History = Record<AssistantId, HistoryThread[]>

export type ThreadHistoryActions = {
  addHistoryThread: (historyThread: HistoryThread) => void
  updateHistoryThread: (options: {
    assistantId: AssistantId
    threadId?: string
    localThreadId?: string
    thread: Partial<HistoryThread>
  }) => void
  removeHistoryThread: (options: {
    assistantId: AssistantId
    threadId?: string
    localThreadId?: string
  }) => void
}

export type ThreadHistoryState = {
  history: History
}

export type ThreadHistorySlice = Prettify<
  ThreadHistoryState & ThreadHistoryActions
>

export const createThreadHistorySlice: StateCreator<ThreadHistorySlice> = (
  set,
  get
) => ({
  history: {},
  addHistoryThread: historyThread => {
    const history = get().history
    const assistantId = historyThread.assistantId
    const nextHistory = produce(history, draft => {
      const threads = (draft[assistantId] = draft[assistantId] || [])
      const existingThreadIndex = threads.findIndex(thread =>
        threadIdsMatch(thread, historyThread)
      )
      if (existingThreadIndex !== -1) {
        threads[existingThreadIndex] = historyThread
      } else {
        threads.push(historyThread)
      }
    })
    set({ history: nextHistory })
  },
  updateHistoryThread: ({
    assistantId,
    threadId,
    localThreadId,
    thread: threadUpdates
  }) => {
    const history = get().history
    const nextHistory = produce(history, draft => {
      const threads = (draft[assistantId] = draft[assistantId] || [])
      const existingThreadIndex = threads.findIndex(thread =>
        idsMatchThread({ thread, localThreadId, threadId })
      )
      threads[existingThreadIndex] = {
        ...threads[existingThreadIndex],
        ...threadUpdates
      }
    })
    set({ history: nextHistory })
  },
  removeHistoryThread: ({ assistantId, threadId, localThreadId }) => {
    const history = get().history
    const nextHistory = produce(history, draft => {
      const threads = (draft[assistantId] = draft[assistantId] || [])
      const existingThreadIndex = threads.findIndex(thread =>
        idsMatchThread({ thread, localThreadId, threadId })
      )
      if (existingThreadIndex !== -1) {
        threads.splice(existingThreadIndex, 1)
      }
    })
    set({ history: nextHistory })
  }
})

export const sameByIdOrLocalId = (
  a: { id?: string; localId?: string },
  b: { id?: string; localId?: string }
) => {
  if (a?.id && a.id === b?.id) return true
  if (a?.localId && a.localId === b?.localId) return true
  return false
}

export const threadIdsMatch = (
  threadA: HistoryThread,
  threadB: HistoryThread
) =>
  sameByIdOrLocalId(
    { id: threadA.thread?.id, localId: threadA.localThreadId },
    { id: threadB.thread?.id, localId: threadB.localThreadId }
  )

export const idsMatchThread = ({
  thread,
  threadId,
  localThreadId
}: {
  thread: HistoryThread
  threadId?: string
  localThreadId?: string
}) =>
  sameByIdOrLocalId(
    {
      id: threadId,
      localId: localThreadId
    },
    {
      id: thread.thread?.id,
      localId: thread.localThreadId
    }
  )

/**
 * Filters out unfinished threads from the history.
 *
 * @param history - The current history object containing threads for each assistant.
 * @returns A new History object with unfinished threads removed.
 *
 * @remarks
 * This function uses Immer's `produce` to create a new immutable state.
 * It removes any thread that doesn't have a valid `id` property.
 * This is useful for cleaning up the history from any incomplete or corrupted thread data.
 */
export const filterUnfinishedThreads = (history: History) => {
  return produce(history, draft => {
    Object.keys(draft).forEach(assistantId => {
      const threads = draft[assistantId]
      threads.forEach((thread, index) => {
        delete thread.localThreadId
        if (!thread.thread?.id) {
          const removedThread = threads.splice(index, 1)[0]
          console.info('removedThread from history sync', removedThread)
        }
      })
    })
  })
}
