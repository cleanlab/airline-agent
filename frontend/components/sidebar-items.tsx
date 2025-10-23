'use client'

import { AnimatePresence, motion } from 'motion/react'
import { SidebarItem } from '@/components/sidebar-item'
import type { HistoryThread } from '../stores/history-thread-store'
import { useMemo } from 'react'
import { SidebarActions } from './sidebar-actions'

interface SidebarItemsProps {
  historyThreads?: HistoryThread[]
  assistantId?: string
  assistantSlug?: string | null | undefined
}

export function SidebarItems({ historyThreads }: SidebarItemsProps) {
  const reversedHistoryThreads = useMemo(
    () => (!historyThreads ? undefined : [...historyThreads].reverse()),
    [historyThreads]
  )
  if (!reversedHistoryThreads?.length) return null

  return (
    <AnimatePresence>
      {reversedHistoryThreads.map(
        (thread, index) =>
          thread && (
            <motion.div
              key={thread.localThreadId || thread.thread?.id}
              exit={{
                opacity: 0,
                height: 0
              }}
            >
              <SidebarItem index={index} thread={thread}>
                <SidebarActions thread={thread} />
              </SidebarItem>
            </motion.div>
          )
      )}
    </AnimatePresence>
  )
}
