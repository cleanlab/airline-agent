'use client'

import { IconFrameButton, Tooltip } from '@cleanlab/design-system/components'
import { IconTrash } from '@cleanlab/design-system/icons'
import { useRouter } from 'next/navigation'

import { getChatPath } from '@/lib/consts'
import { useMessagesStore } from '@/providers/messages-store-provider'
import {
  useAssistantHistory,
  useRagAppStore
} from '@/providers/rag-app-store-provider'
import {
  type HistoryThread,
  idsMatchThread} from '@/stores/history-thread-store'

export function SidebarActions({ thread }: { thread: HistoryThread }) {
  const removeHistoryThread = useRagAppStore(state => state.removeHistoryThread)
  const history = useAssistantHistory() || []
  const currentThread = useMessagesStore(state => state.currentThread)
  const setCurrentThread = useMessagesStore(state => state.setCurrentThread)
  const router = useRouter()

  return (
    <>
      <Tooltip content="Delete chat">
        <IconFrameButton
          variant="iconOnly"
          size="xSmall"
          className="size-[20px]"
          onClick={() => {
            const threadId = thread.thread?.id
            const localThreadId = thread.localThreadId
            const isDeletingCurrent =
              (!!threadId && threadId === currentThread?.threadId) ||
              (!!localThreadId &&
                localThreadId === currentThread?.localThreadId)

            // Compute remaining threads before removal
            const remaining = history.filter(
              t =>
                !idsMatchThread({
                  thread: t,
                  threadId,
                  localThreadId
                })
            )

            removeHistoryThread({ threadId, localThreadId })

            // If we deleted the active thread, navigate to a safe location
            if (isDeletingCurrent) {
              if (remaining.length > 0) {
                const next =
                  remaining[0].thread?.id ?? remaining[0].localThreadId
                if (next) {
                  router.replace(getChatPath(next))
                } else {
                  router.replace('/')
                }
              } else {
                // Clear the current thread view when no threads remain
                setCurrentThread(undefined)
                router.replace('/')
              }
            }
          }}
          icon={<IconTrash />}
          aria-label="Delete chat"
        />
      </Tooltip>
    </>
  )
}
