'use client'

import { cn } from '@cleanlab/design-system/utils'
import { type ComponentProps } from 'react'

import { useSidebar } from '@/lib/hooks/use-sidebar'

export function Sidebar({ className, children }: ComponentProps<'div'>) {
  const { isSidebarOpen, isLoading } = useSidebar()

  return (
    <div
      data-state={isSidebarOpen && !isLoading ? 'open' : 'closed'}
      className={cn(className, 'h-full flex-col bg-surface-0')}
    >
      {children}
    </div>
  )
}
