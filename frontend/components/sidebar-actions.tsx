'use client'

import { IconTrash } from './icons'
import { Tooltip } from './design-system-components/Tooltip'
import { IconFrameButton } from './design-system-components/IconFrameButton'
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
