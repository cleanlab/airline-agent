type Thread = { id: string }
import { produce } from 'immer'
import type { StateCreator } from 'zustand'
import type { Prettify } from '@/lib/ts/Prettify'

export type HistoryThread = {
  title: string
  cleanlabEnabled?: boolean
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
  messages?: Array<{
    localId?: string
    id?: string
    role: 'user' | 'assistant' | 'tool'
    content: string
    metadata?: any
    isPending?: boolean
    isContentPending?: boolean
    error?: string
  }>
} & (
  | {
      localThreadId?: string
      thread: Thread
    }
  | { localThreadId: string; thread?: Thread }
)

export type History = HistoryThread[]

export type ThreadHistoryActions = {
  addHistoryThread: (historyThread: HistoryThread) => void
  updateHistoryThread: (options: {
    threadId?: string
    localThreadId?: string
    thread: Partial<HistoryThread>
  }) => void
  removeHistoryThread: (options: {
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
  history: [],
  addHistoryThread: historyThread => {
    const history = get().history
    const nextHistory = produce(history, draft => {
      const existingThreadIndex = draft.findIndex(thread =>
        threadIdsMatch(thread, historyThread)
      )
      if (existingThreadIndex !== -1) {
        draft[existingThreadIndex] = historyThread
      } else {
        draft.push(historyThread)
      }
    })
    set({ history: nextHistory })
  },
  updateHistoryThread: ({ threadId, localThreadId, thread: threadUpdates }) => {
    const history = get().history
    const nextHistory = produce(history, draft => {
      const existingThreadIndex = draft.findIndex(thread =>
        idsMatchThread({ thread, localThreadId, threadId })
      )
      if (existingThreadIndex !== -1) {
        draft[existingThreadIndex] = {
          ...draft[existingThreadIndex],
          ...threadUpdates
        }
      }
    })
    set({ history: nextHistory })
  },
  removeHistoryThread: ({ threadId, localThreadId }) => {
    const history = get().history
    const nextHistory = produce(history, draft => {
      const existingThreadIndex = draft.findIndex(thread =>
        idsMatchThread({ thread, localThreadId, threadId })
      )
      if (existingThreadIndex !== -1) {
        draft.splice(existingThreadIndex, 1)
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
 * @param history - The current history array containing threads.
 * @returns A new History array with unfinished threads removed.
 *
 * @remarks
 * This function uses Immer's `produce` to create a new immutable state.
 * It removes any thread that doesn't have a valid `id` property.
 * This is useful for cleaning up the history from any incomplete or corrupted thread data.
 */
export const filterUnfinishedThreads = (history: History) => {
  return produce(history, draft => {
    // Remove local-only ids and drop any unfinished threads
    for (let i = draft.length - 1; i >= 0; i--) {
      const thread = draft[i]
      delete thread.localThreadId
      if (!thread.thread?.id) {
        const removedThread = draft.splice(i, 1)[0]
        console.info('removedThread from history sync', removedThread)
      }
    }
  })
}
