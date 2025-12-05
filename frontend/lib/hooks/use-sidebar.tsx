'use client'

import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from 'react'

const LOCAL_STORAGE_KEY = 'sidebar'

interface SidebarContext {
  isSidebarOpen: boolean
  toggleSidebar: () => void
  isLoading: boolean
}

const SidebarContext = createContext<SidebarContext | undefined>(undefined)

export function useSidebar() {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error('useSidebarContext must be used within a SidebarProvider')
  }
  return context
}

interface SidebarProviderProps {
  children: ReactNode
}

export function SidebarProvider({ children }: SidebarProviderProps) {
  const [isSidebarOpen, setSidebarOpen] = useState(true)
  const [isLoading, setLoading] = useState(true)

  useEffect(() => {
    const value = localStorage.getItem(LOCAL_STORAGE_KEY)
    if (value) {
      setSidebarOpen(JSON.parse(value))
    }
    setLoading(false)
  }, [])

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(value => {
      const newState = !value
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(newState))
      return newState
    })
  }, [])
  const contextValue = useMemo(
    () => ({ isSidebarOpen, toggleSidebar, isLoading }),
    [isSidebarOpen, toggleSidebar, isLoading]
  )
  if (isLoading) {
    return null
  }

  return <SidebarContext value={contextValue}>{children}</SidebarContext>
}
