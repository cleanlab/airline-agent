'use client'

import type { ReactNode } from 'react'
import { useMessagesStore } from '@/providers/messages-store-provider'
import { useStreamMessage } from '../lib/hooks/useStreamMessage'
import { ButtonRetryMessage } from './design-system-components/ButtonRetryMessage'

export function RetryButton({}: Readonly<{ error?: ReactNode }>) {
  const isPending = useMessagesStore(state => state.currentThread?.isPending)

  const { retrySendMessage } = useStreamMessage()
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
