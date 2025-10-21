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
              showAccordion={true}
              disableScores={false}
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
        const toolCallData = (() => {
          try {
            return JSON.parse(message.content)
          } catch {
            return null
          }
        })()

        // Helper function to parse and pretty-print JSON strings
        const parseAndPrettyPrint = (jsonString: string) => {
          try {
            // First try to parse as JSON
            let parsed = JSON.parse(jsonString)

            // If the result is still a string, it might be double-encoded JSON
            if (typeof parsed === 'string') {
              try {
                parsed = JSON.parse(parsed)
              } catch {
                // If second parse fails, use the first parsed result
              }
            }

            // Pretty print the final result
            return JSON.stringify(parsed, null, 2)
          } catch {
            // If all parsing fails, return the original string
            return jsonString
          }
        }

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
              <div className="flex-1 space-y-3">
                <div className="text-sm font-medium text-foreground">
                  Tool Call: {toolCallData?.tool_name || 'Unknown'}
                </div>

                {toolCallData?.arguments && (
                  <div>
                    <div className="type-body-100 mb-1 font-medium">
                      Arguments:
                    </div>
                    <div className="type-caption-medium whitespace-pre-wrap break-all rounded-2 bg-surface-2 px-5 py-4">
                      {parseAndPrettyPrint(toolCallData.arguments)}
                    </div>
                  </div>
                )}

                {toolCallData?.result && (
                  <div>
                    <div className="text-foreground-2 type-body-100 mb-1 font-medium">
                      Result:
                    </div>
                    <div className="rounded max-h-32 type-caption-medium overflow-y-auto whitespace-pre-wrap rounded-2 bg-surface-2 px-5 py-4">
                      {parseAndPrettyPrint(toolCallData.result)}
                    </div>
                  </div>
                )}

                {!toolCallData && (
                  <div className="text-xs text-foreground-2 rounded break-all bg-surface-2 p-2 font-mono">
                    {message.content}
                  </div>
                )}
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
  const isPending = useMessagesStore(state => state.currentThread?.isPending)

  // Separate actual messages from loading messages
  const actualMessages =
    allMessages?.filter(message => {
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

  // Find any pending assistant message for the loading state
  const pendingAssistantMessage = allMessages?.find(
    message =>
      message.role === 'assistant' && message.isPending && !message.content
  )

  if (!actualMessages.length && !pendingAssistantMessage) {
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
              cleanlabMode={cleanlabMode}
            />
            {showRetryButton && <RetryButton />}
          </div>
        )
      })}

      {/* Show loading message at the bottom if there's a pending assistant message */}
      {pendingAssistantMessage && (
        <div key="loading-message">
          <ChatMessage
            isAutoScrollEnabled={true}
            scrollRef={scrollRef}
            message={pendingAssistantMessage}
            cleanlabMode={cleanlabMode}
          />
        </div>
      )}

      <MessageError data-at-status={error?.atStatus} error={error?.message} />
    </div>
  )
}
