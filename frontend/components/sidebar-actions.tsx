'use client'

import { IconTrash } from '@cleanlab/design-system/icons'
import { IconFrameButton, Tooltip } from '@cleanlab/design-system/components'
import { HistoryThread } from '@/stores/history-thread-store'
import { useRagAppStore } from '@/providers/rag-app-store-provider'

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
            const assistantId = thread.assistantId
            const threadId = thread.thread?.id
            const localThreadId = thread.localThreadId
            removeHistoryThread({ assistantId, threadId, localThreadId })
          }}
          icon={<IconTrash />}
          aria-label="Delete chat"
        />
      </Tooltip>
    </>
  )
}
