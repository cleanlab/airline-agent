import type { StateCreator } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import { createStore } from 'zustand/vanilla'
import type { Prettify } from '@/lib/ts/Prettify'
import type { ZustandPersist } from '../lib/ts/ZustandPersist'
import {
  type ThreadHistorySlice,
  createThreadHistorySlice,
  filterUnfinishedThreads
} from './history-thread-store'
import type { ResponseRatingsSlice } from './response-ratings-store'
import { createRatingsSlice } from './response-ratings-store'

export type RagAppStore = Prettify<ThreadHistorySlice & ResponseRatingsSlice>

const persistState = (stateCreator: StateCreator<RagAppStore>) => {
  return (persist as ZustandPersist<RagAppStore>)(stateCreator, {
    partialize: state => ({
      history: filterUnfinishedThreads(state.history),
      responseRatings: state.responseRatings
    }),
    name: 'ragApp',
    storage: createJSONStorage(() => localStorage)
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
