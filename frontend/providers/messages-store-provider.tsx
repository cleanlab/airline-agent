'use client'

import { type ReactNode, createContext, useContext, useRef } from 'react'
import type { MessagesSlice } from '@/stores/messages-store'
import { createMessagesStore } from '@/stores/messages-store'
import { useStore } from 'zustand'

export type MessagesStoreApi = ReturnType<typeof createMessagesStore>

export const MessagesStoreContext = createContext<MessagesStoreApi | undefined>(
  undefined
)

export interface MessagesStoreProviderProps {
  children: ReactNode
}

export const MessagesStoreProvider = ({
  children
}: MessagesStoreProviderProps) => {
  const storeRef = useRef<MessagesStoreApi>(undefined)
  if (!storeRef.current) {
    storeRef.current = createMessagesStore()
  }

  return (
    <MessagesStoreContext.Provider value={storeRef.current}>
      {children}
    </MessagesStoreContext.Provider>
  )
}

export const useMessagesStore = <T,>(
  selector: (store: MessagesSlice) => T
): T => {
  const messagesStore = useContext(MessagesStoreContext)

  if (!messagesStore) {
    throw new Error(
      `useMessagesStore must be used within MessagesStoreProvider`
    )
  }

  messagesStore.getState()

  return useStore(messagesStore, selector)
}

export const useBareMessagesStore = () => {
  const messagesStore = useContext(MessagesStoreContext)

  if (!messagesStore) {
    throw new Error(
      `useBareMessagesStore must be used within MessagesStoreProvider`
    )
  }

  return messagesStore
}

export const useMessageIsPending = () => {
  return useMessagesStore(state => {
    return !!state.currentThread?.isPending
  })
}
