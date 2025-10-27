'use client'

import { RATE_LIMIT_WAIT_MS } from '@/lib/consts'
import { useRateLimitedValue } from '@/lib/hooks/useRateLimitedValue'
import { useMessagesStore } from '@/providers/messages-store-provider'
import type { StoreMessage } from '@/stores/messages-store'

import type { RefObject } from 'react'
import { useEffect, useRef } from 'react'
import { useAutoScrollMessage } from '../lib/hooks/use-auto-scroll-message'
import { RetryButton } from './message'
import { MessageUser } from './design-system-components/MessageUser'
import {
  MessageAssistant,
  MessageAssistantStatus
} from './design-system-components/MessageAssistant'
import { MessageError } from './design-system-components/MessageError'
import { ChatCodeBlock } from './design-system-components/ChatCodeBlock'
import { Collapsible } from 'radix-ui'
import { IconAirplane, IconChevronDown } from './icons'

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
        // Display tool call messages
        const toolCallData = (() => {
          // If content is already an object, use it directly
          if (typeof message.content === 'object' && message.content !== null) {
            return message.content
          }

          // If content is a string, try to parse it as JSON
          if (typeof message.content === 'string') {
            try {
              return JSON.parse(message.content)
            } catch {
              return null
            }
          }

          return null
        })()

        // Helper function to parse and pretty-print JSON strings or objects
        const parseAndPrettyPrint = (data: any) => {
          // If it's already an object, just stringify it
          if (typeof data === 'object' && data !== null) {
            return JSON.stringify(data, null, 2)
          }

          // If it's not a string, return as-is
          if (typeof data !== 'string') {
            return String(data)
          }

          // Check if the string looks like JSON or double-encoded JSON
          const trimmed = data.trim()
          const looksLikeJson =
            (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
            (trimmed.startsWith('[') && trimmed.endsWith(']')) ||
            (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
            // Check for double-encoded JSON (starts with " and contains escaped quotes)
            (trimmed.startsWith('"') && trimmed.includes('\\"'))

          if (!looksLikeJson) {
            return data
          }

          try {
            // First try to parse as JSON
            let parsed = JSON.parse(data)

            // If the result is still a string, it might be double-encoded JSON
            if (typeof parsed === 'string') {
              try {
                parsed = JSON.parse(parsed)
              } catch {
                // If second parse fails, use the first parsed result
              }
            }

            // Pretty print the final result with better formatting
            return JSON.stringify(parsed, null, 2)
          } catch (error) {
            // If all parsing fails, return the original string
            return data
          }
        }

        return (
          <div className="rounded-4 border border-border-2 bg-surface-1">
            <div className="flex items-start gap-4">
              <Collapsible.Root className="group/collapsible group flex-1">
                <Collapsible.Trigger className="type-body-200-semibold flex w-full items-center justify-between gap-5 rounded-4 px-6 py-7 hover:bg-surface-1-hover">
                  <div className="type-body-200-semibold flex items-center gap-4">
                    <span>🔧</span> Tool Call:{' '}
                    {toolCallData?.tool_name || 'Unknown'}
                  </div>
                  <IconChevronDown
                    size={16}
                    className="text-text-disabled transition-transform group-data-[state=open]/collapsible:-scale-y-100"
                  />
                </Collapsible.Trigger>
                <Collapsible.Content className="overflow-hidden data-[state=closed]:animate-collapsible-close data-[state=open]:animate-collapsible-open">
                  {toolCallData?.arguments && (
                    <div className="px-6 pt-4">
                      <div className="type-body-100 mb-2 font-medium">
                        Arguments:
                      </div>
                      <div className="w-full max-w-full overflow-hidden">
                        <ChatCodeBlock
                          language="json"
                          code={(() => {
                            // Handle arguments - they might be a string that needs parsing
                            let argumentsData = toolCallData.arguments
                            if (typeof argumentsData === 'string') {
                              try {
                                argumentsData = JSON.parse(argumentsData)
                              } catch {
                                // If parsing fails, use the string as-is
                              }
                            }
                            return parseAndPrettyPrint(argumentsData)
                          })()}
                          showLineNumbers={false}
                          textSize="50"
                          className="w-full max-w-full"
                        />
                      </div>
                    </div>
                  )}

                  {toolCallData?.result && (
                    <div className="px-6 py-6">
                      <div className="type-body-100 mb-1 font-medium">
                        Result:
                      </div>
                      {(() => {
                        const resultContent = parseAndPrettyPrint(
                          toolCallData.result
                        )

                        // Check if the result is valid JSON
                        const isJson = (() => {
                          try {
                            const parsed = JSON.parse(resultContent)
                            return typeof parsed === 'object' && parsed !== null
                          } catch {
                            return false
                          }
                        })()

                        if (isJson) {
                          // Use ChatCodeBlock for JSON results
                          return (
                            <div className="w-full max-w-full overflow-hidden">
                              <ChatCodeBlock
                                language="json"
                                code={resultContent}
                                showLineNumbers={false}
                                textSize="50"
                                className="w-full max-w-full"
                              />
                            </div>
                          )
                        } else {
                          // Use plain text for non-JSON results
                          return (
                            <div className="max-h-32 max-w-full overflow-x-auto overflow-y-auto rounded-2 bg-surface-2 px-5 py-4">
                              <pre className="type-caption whitespace-pre-wrap break-words break-all font-mono">
                                {resultContent}
                              </pre>
                            </div>
                          )
                        }
                      })()}
                    </div>
                  )}

                  {!toolCallData && (
                    <div className="type-caption max-w-full overflow-x-auto whitespace-pre-wrap break-all rounded-2 bg-surface-2 px-5 py-4">
                      {message.content}
                    </div>
                  )}
                </Collapsible.Content>
              </Collapsible.Root>
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
