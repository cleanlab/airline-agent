'use client'

import type { ComponentPropsWithoutRef, ComponentPropsWithRef } from 'react'
import { forwardRef } from 'react'

import { ButtonRetryMessage } from './ButtonRetryMessage'
import { MessageInfo } from './MessageInfo'

const MessageError = forwardRef(
  (
    {
      error,
      onRetry,
      retryLabel,
      ...props
    }: {
      error?: string
      onRetry?: () => void
      retryLabel?: string
    } & Partial<ComponentPropsWithoutRef<typeof MessageInfo>>,
    ref: ComponentPropsWithRef<typeof MessageInfo>['ref']
  ) => {
    if (!error) return null
    return (
      <MessageInfo
        ref={ref}
        status="warning"
        description={error}
        actions={
          onRetry ? (
            <ButtonRetryMessage onClick={onRetry}>{retryLabel}</ButtonRetryMessage>
          ) : undefined
        }
        {...props}
      >
        {error}
      </MessageInfo>
    )
  }
)
MessageError.displayName = 'MessageError'

export { MessageError }
