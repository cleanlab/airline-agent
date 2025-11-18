'use client'

import type { ReactNode } from 'react'
import { useMessagesStore } from '@/providers/messages-store-provider'
import { useStreamMessage } from '../lib/hooks/useStreamMessage'
import { ButtonRetryMessage } from '@cleanlab/design-system/chat'

export function RetryButton({
  cleanlabEnabled = true
}: Readonly<{
  error?: ReactNode
  cleanlabEnabled?: boolean
}>) {
  const isPending = useMessagesStore(state => state.currentThread?.isPending)

  const { retrySendMessage } = useStreamMessage(cleanlabEnabled)
  const retry = () => {
    retrySendMessage()
  }
  if (isPending) {
    return null
  }
  return (
    <div className="mt-2 flex items-center justify-end gap-2">
      <ButtonRetryMessage
        onClick={async () => {
          retry()
        }}
      >
        Resend
      </ButtonRetryMessage>
    </div>
  )
}
