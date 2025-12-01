'use client'

import { IconFrameButton, Tooltip } from '@cleanlab/design-system/components'
import { IconTrash } from '@cleanlab/design-system/icons'

import { useRagAppStore } from '@/providers/rag-app-store-provider'
import { type HistoryThread } from '@/stores/history-thread-store'

export function SidebarActions({ thread }: { thread: HistoryThread }) {
  const removeHistoryThread = useRagAppStore(state => state.removeHistoryThread)

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
            removeHistoryThread({ threadId, localThreadId })
          }}
          icon={<IconTrash />}
          aria-label="Delete chat"
        />
      </Tooltip>
    </>
  )
}
