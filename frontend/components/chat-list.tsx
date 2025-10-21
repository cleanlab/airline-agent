'use client'

import { RATE_LIMIT_WAIT_MS } from '@/lib/consts'
import { useRateLimitedValue } from '@/lib/hooks/useRateLimitedValue'
import { useMessagesStore } from '@/providers/messages-store-provider'
import type { StoreMessage } from '@/stores/messages-store'

import logoLightMode from './assets/logo-black.png'
import logoDarkMode from './assets/logo-white.png'
import { cn } from '@/lib/utils/tailwindUtils'
import type { RefObject } from 'react'
import { useEffect, useRef } from 'react'
import { useAutoScrollMessage } from '../lib/hooks/use-auto-scroll-message'
import type { DemoMode } from './chat'
import { RetryButton } from './message'
import { LogoImg } from './design-system-components/LogoImg'
import { logoMetadata } from './design-system-components/logoMetadata'
import { MessageUser } from './design-system-components/MessageUser'
import {
  MessageAssistant,
  MessageAssistantStatus
} from './design-system-components/MessageAssistant'
import { MessageError } from './design-system-components/MessageError'

export interface ChatListProps {
  threadId?: string
  scrollRef: RefObject<HTMLElement | null>
  cleanlabMode: DemoMode
}

const ChatMessage = ({
  message,
  scrollRef,
  isAutoScrollEnabled,
  cleanlabMode
}: {
  message: StoreMessage
  scrollRef: RefObject<HTMLElement | null>
  isAutoScrollEnabled: boolean
  showRetryButton?: boolean
  cleanlabMode: DemoMode
}) => {
  const messageRef = useRef<HTMLDivElement>(null)
  useAutoScrollMessage(scrollRef, messageRef, isAutoScrollEnabled)
  const rateLimitedMessage = useRateLimitedValue(
    message.content,
    RATE_LIMIT_WAIT_MS
  )

  useEffect(() => {
    if (message.role === 'assistant' && !message.isPending) {
      console.info('Message:\n', message)
    }
  }, [message.role, message.isPending])

  const detectionMetadata = { ...message.metadata, is_expert_answer: false }

  const disableScores = cleanlabMode === 'no-cleanlab'

  const display = (() => {
    switch (message.role) {
      case 'user':
        return <MessageUser data-id={message.id} content={message.content} />
      case 'assistant':
        const status =
          message.isContentPending && message.isPending
            ? MessageAssistantStatus.ContentPending
            : message.isPending
              ? MessageAssistantStatus.MetadataPending
              : MessageAssistantStatus.Done
        const content =
          status === MessageAssistantStatus.Done
            ? message.content
            : rateLimitedMessage
        return (
          <div className={cn('rounded-4 border border-border-2 px-6 py-7')}>
            <MessageAssistant
              data-id={message.id}
              content={
                cleanlabMode !== 'cleanlab-enforce'
                  ? (message?.metadata?.original_llm_response ?? content)
                  : content
              }
              error={message.error}
              status={
                // Set content pending if rate limited content is still coming in to prevent trustworthiness score chip from showing up prematurely
                content !== message.content
                  ? MessageAssistantStatus.ContentPending
                  : status
              }
              messageMetadata={
                cleanlabMode === 'cleanlab-detection'
                  ? detectionMetadata
                  : (message.metadata ?? null)
              }
              showAccordion={cleanlabMode === 'cleanlab-detection'}
              disableScores={!!disableScores}
              icon={
                <LogoImg
                  className="size-7"
                  src={{ light: logoLightMode.src, dark: logoDarkMode.src }}
                  {...logoMetadata[128].logo}
                />
              }
            />
          </div>
        )
      case 'tool':
        // Display tool call messages
        return (
          <div
            className={cn(
              'rounded-4 border border-border-2 bg-surface-1 px-6 py-7'
            )}
          >
            <div className="flex items-start gap-4">
              <div className="bg-primary-1 text-primary-11 flex h-7 w-7 items-center justify-center rounded-full">
                <span className="text-xs font-medium">🔧</span>
              </div>
              <div className="flex-1">
                <div className="text-sm mb-2 font-medium text-foreground">
                  Tool Call
                </div>
                <div className="text-sm text-foreground-2">
                  {typeof message.content === 'object'
                    ? JSON.stringify(message.content, null, 2)
                    : message.content}
                </div>
              </div>
            </div>
          </div>
        )
      default:
        return null
    }
  })()

  return (
    <div data-chat-message={true} ref={messageRef}>
      {display}
    </div>
  )
}

export function ChatList({ threadId, scrollRef, cleanlabMode }: ChatListProps) {
  const allMessages = useMessagesStore(state => state.currentThread?.messages)
  const error = useMessagesStore(state => state.currentThread?.error)

  const filteredMessages = allMessages?.filter(message => {
    if (message?.content || message.isContentPending || message.isPending) {
      return true
    }
    if (message.role === 'assistant') {
      const md = message.metadata as any
      return !!(
        md &&
        (md.guardrailed ||
          md.original_llm_response ||
          md.escalated_to_sme ||
          md.is_expert_answer)
      )
    }
    if (message.role === 'tool') {
      return true // Always show tool call messages
    }
    return false
  })

  if (!filteredMessages?.length) {
    return null
  }

  return (
    <div
      className="mx-auto flex w-full max-w-2xl grow flex-col gap-9"
      data-chat-list={true}
      data-chat-id={threadId}
    >
      {filteredMessages.map((message, index) => {
        const showRetryButton =
          !!error?.canRetry &&
          message?.role === 'user' &&
          index === filteredMessages.length - 1
        return (
          <div key={message.localId || message.id}>
            <ChatMessage
              isAutoScrollEnabled={index === filteredMessages.length - 1}
              scrollRef={scrollRef}
              message={message}
              cleanlabMode={cleanlabMode}
            />
            {showRetryButton && <RetryButton />}
          </div>
        )
      })}
      <MessageError data-at-status={error?.atStatus} error={error?.message} />
    </div>
  )
}
