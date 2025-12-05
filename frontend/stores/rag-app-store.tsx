import type { StateCreator } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import { createStore } from 'zustand/vanilla'
import type { Prettify } from '@/lib/ts/Prettify'
import type { ZustandPersist } from '@/lib/ts/ZustandPersist'
import {
  type ThreadHistorySlice,
  createThreadHistorySlice,
  filterUnfinishedThreads
} from '@/stores/history-thread-store'
import type { ResponseRatingsSlice } from '@/stores/response-ratings-store'
import { createRatingsSlice } from '@/stores/response-ratings-store'

export type RagAppStore = Prettify<ThreadHistorySlice & ResponseRatingsSlice>

const persistState = (stateCreator: StateCreator<RagAppStore>) => {
  return (persist as ZustandPersist<RagAppStore>)(stateCreator, {
    partialize: state => ({
      history: filterUnfinishedThreads(state.history),
      responseRatings: state.responseRatings
    }),
    name: 'ragApp',
    storage: createJSONStorage(() => localStorage),
    version: 2,
    migrate: (persisted: any, version: number) => {
      try {
        if (!persisted) return persisted
        // v1 shape had history as a Record<string, HistoryThread[]>
        if (
          version < 2 &&
          persisted.history &&
          !Array.isArray(persisted.history)
        ) {
          const legacyHistoryObj = persisted.history as Record<string, any[]>
          const flat: any[] = []
          Object.values(legacyHistoryObj || {}).forEach(arr => {
            if (Array.isArray(arr)) {
              arr.forEach(item => {
                if (item && typeof item === 'object') {
                  // Drop assistantId from legacy items
                  delete item.assistantId
                  flat.push(item)
                }
              })
            }
          })
          persisted.history = flat
        }
        // Always run cleanup on load
        if (Array.isArray(persisted.history)) {
          persisted.history = filterUnfinishedThreads(persisted.history)
        }
      } catch {
        // Best-effort migration; if anything fails, return original state
        return persisted
      }
      return persisted
    }
  })
}

export const createRagAppStore = () => {
  return createStore<RagAppStore>(
    persistState((...args) => ({
      ...createThreadHistorySlice(...args),
      ...createRatingsSlice(...args)
    }))
  )
}
