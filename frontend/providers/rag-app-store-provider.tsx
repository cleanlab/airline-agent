'use client'

import { type ReactNode, createContext, useContext, useRef } from 'react'
import { type RagAppStore, createRagAppStore } from '@/stores/rag-app-store'
import { useStore } from 'zustand'

export type RagAppStoreApi = ReturnType<typeof createRagAppStore>

export const RagAppStoreContext = createContext<RagAppStoreApi | undefined>(
  undefined
)

export interface RagAppStoreProviderProps {
  children: ReactNode
}

export const RagAppStoreProvider = ({ children }: RagAppStoreProviderProps) => {
  const storeRef = useRef<RagAppStoreApi>(undefined)
  if (!storeRef.current) {
    storeRef.current = createRagAppStore()
  }

  return (
    <RagAppStoreContext.Provider value={storeRef.current}>
      {children}
    </RagAppStoreContext.Provider>
  )
}

export const useRagAppStore = <T,>(selector: (store: RagAppStore) => T): T => {
  const ragappStore = useContext(RagAppStoreContext)

  if (!ragappStore) {
    throw new Error(`useRagAppStore must be used within RagAppStoreProvider`)
  }

  ragappStore.getState()

  return useStore(ragappStore, selector)
}

export const useBareRagAppStore = () => {
  const ragappStore = useContext(RagAppStoreContext)

  if (!ragappStore) {
    throw new Error(
      `useBareRagAppStore must be used within RagAppStoreProvider`
    )
  }

  return ragappStore
}

export const useAssistantHistory = (assistantId?: string) => {
  return useRagAppStore(state => {
    if (!assistantId) return undefined
    return state.history?.[assistantId]
  })
}
