'use client'

import { RATE_LIMIT_WAIT_MS } from '@/lib/consts'
import { useRateLimitedValue } from '@/lib/hooks/useRateLimitedValue'
import { useMessagesStore } from '@/providers/messages-store-provider'
import type { StoreMessage } from '@/stores/messages-store'

import type { RefObject } from 'react'
import { useEffect, useRef } from 'react'
import { useAutoScrollMessage } from '../lib/hooks/use-auto-scroll-message'
import { RetryButton } from './message'
import {
  MessageAssistant,
  MessageError,
  MessageAssistantStatus,
  MessageUser
} from '@cleanlab/design-system/chat'
import { IconAirplane } from './icons'
import { MessageAssistantTool } from './message-assistant-tool'

export interface ChatListProps {
  threadId?: string
  scrollRef: RefObject<HTMLElement | null>
  cleanlabEnabled: boolean
}

const ChatMessage = ({
  message,
  scrollRef,
  isAutoScrollEnabled
}: {
  message: StoreMessage
  scrollRef: RefObject<HTMLElement | null>
  isAutoScrollEnabled: boolean
  showRetryButton?: boolean
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
          <div className="rounded-4 border border-border-2 px-6 py-7">
            <MessageAssistant
              data-id={message.id}
              content={content}
              error={message.error}
              status={
                // Set content pending if rate limited content is still coming in to prevent trustworthiness score chip from showing up prematurely
                content !== message.content
                  ? MessageAssistantStatus.ContentPending
                  : status
              }
              messageMetadata={message.metadata ?? null}
              showAccordion={false}
              disableScores={true}
              icon={<IconAirplane size={16} />}
            />
          </div>
        )
      case 'tool':
        return <MessageAssistantTool message={message} />
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

export function ChatList({
  threadId,
  scrollRef,
  cleanlabEnabled
}: ChatListProps) {
  const allMessages = useMessagesStore(state => state.currentThread?.messages)
  const error = useMessagesStore(state => state.currentThread?.error)
  const isPending = useMessagesStore(state => state.currentThread?.isPending)

  // Separate actual messages from loading messages
  const actualMessages =
    allMessages?.filter(message => {
      // Always show user messages
      if (message.role === 'user' && message.content) {
        return true
      }
      // Show messages that have content and are not pending
      if (message?.content && !message.isPending) {
        return true
      }
      // Show tool calls that have content
      if (message.role === 'tool' && message.content) {
        return true
      }
      // Show assistant messages with metadata even if no content
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
      return false
    }) || []

  if (!actualMessages.length && !isPending) {
    return null
  }

  return (
    <div
      className="mx-auto flex w-full max-w-2xl grow flex-col gap-9"
      data-chat-list={true}
      data-chat-id={threadId}
    >
      {actualMessages.map((message, index) => {
        const showRetryButton =
          !!error?.canRetry &&
          message?.role === 'user' &&
          index === actualMessages.length - 1
        return (
          <div key={message.localId || message.id}>
            <ChatMessage
              isAutoScrollEnabled={index === actualMessages.length - 1}
              scrollRef={scrollRef}
              message={message}
            />
            {showRetryButton && (
              <RetryButton cleanlabEnabled={cleanlabEnabled} />
            )}
          </div>
        )
      })}

      {/* Show loading message at the bottom if thread is pending */}
      {isPending && (
        <div key="loading-message">
          <ChatMessage
            isAutoScrollEnabled={true}
            scrollRef={scrollRef}
            message={{
              localId: 'loading-placeholder',
              role: 'assistant',
              content: '',
              metadata: {},
              isPending: true,
              isContentPending: true
            }}
          />
        </div>
      )}

      <MessageError data-at-status={error?.atStatus} error={error?.message} />
    </div>
  )
}
