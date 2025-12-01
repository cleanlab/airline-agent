'use client'

import type { StoreMessage } from '@/stores/messages-store'
import { ChatList } from '@/components/chat-list'
import { EmptyScreen } from '@/components/empty-screen'
import { getChatPath } from '@/lib/consts'
import {
  scrollElementToBottom,
  useScrollToBottom
} from '@/lib/hooks/use-scroll-to-bottom'
import { useMessagesStore } from '@/providers/messages-store-provider'
import { cn } from '@cleanlab/design-system/utils'
import { useEffect, useLayoutEffect, useMemo, useState } from 'react'
import { toast } from 'sonner'
import { CurrentThreadStatus } from '../lib/hooks/useStreamMessage'
import { getThreadBufferSnapshot } from '../lib/hooks/useStreamMessage'
import type { CurrentThread } from '../stores/messages-store'
import { PromptForm } from './prompt-form'
import { ChatInputPanel } from '@cleanlab/design-system/chat'
import { Tooltip } from '@cleanlab/design-system/components'
import { useAssistantHistory } from '@/providers/rag-app-store-provider'
import { useAppSettings } from '@/lib/hooks/use-app-settings'
import { ToggleGroup, ToggleGroupItem } from '@radix-ui/react-toggle-group'
export interface ChatProps {
  threadId?: string
  className?: string
  missingKeys?: string[]
  currentThread?: CurrentThread
  initialMessages?: StoreMessage[]
  promptPlaceholder: string
}

export const useChatAppContext = () => undefined

const toggleGroupItemClasses =
  'first:border-r last:border-l border-border-1 py-3 px-4 type-caption-medium flex items-center justify-center bg-surface-1 leading-4 hover:bg-surface-1-hover focus:z-10 focus:outline-none data-[state=on]:bg-surface-1-active data-[state=on]:text-text-strong'

export function Chat({
  threadId,
  initialMessages,
  className,
  missingKeys,
  promptPlaceholder
}: ChatProps) {
  const [input, setInput] = useState('')
  const setCurrentThread = useMessagesStore(state => state.setCurrentThread)
  const currentThread = useMessagesStore(state => state.currentThread)
  const [appSettings] = useAppSettings()
  const assistantId = appSettings.assistantId ?? ''
  const history = useAssistantHistory(assistantId || undefined)
  const [cleanlabEnabled, setCleanlabEnabled] = useState<boolean>(() => {
    try {
      if (threadId) {
        // Prefer reading from saved history thread
        const historyItem = history?.find(
          h => h.thread?.id === threadId || h.localThreadId === threadId
        )
        if (typeof historyItem?.cleanlabEnabled === 'boolean') {
          return historyItem.cleanlabEnabled
        }
        // Fallback to legacy localStorage key for backward compatibility
        const key = `cleanlabEnabled:thread:${threadId}`
        const v = localStorage.getItem(key)
        if (v !== null) {
          const parsed = JSON.parse(v)
          return parsed
        }
      }
      return true
    } catch {
      return true
    }
  })

  // Debug toggle state - defaults to true, globally persistent
  const [viewToolsEnabled, setViewToolsEnabled] = useState<boolean>(() => {
    try {
      const key = 'debugEnabled'
      const v = localStorage.getItem(key)
      if (v !== null) {
        return JSON.parse(v)
      }
      // Default to true (show tools by default)
      return true
    } catch {
      return true
    }
  })

  const historySnapshot = useMemo(() => {
    if (!threadId) return undefined
    const item = history?.find(
      h => h.thread?.id === threadId || h.localThreadId === threadId
    )
    return item?.snapshot
  }, [history, threadId])

  // Hydrate per-thread cleanlabEnabled on thread change
  useEffect(() => {
    if (!threadId) return
    try {
      const historyItem = history?.find(
        h => h.thread?.id === threadId || h.localThreadId === threadId
      )
      if (typeof historyItem?.cleanlabEnabled === 'boolean') {
        setCleanlabEnabled(historyItem.cleanlabEnabled)
        return
      }
      // Fallback: legacy localStorage
      const key = `cleanlabEnabled:thread:${threadId}`
      const v = localStorage.getItem(key)
      if (v !== null) setCleanlabEnabled(JSON.parse(v))
    } catch {}
  }, [threadId, history])

  // Persist debug toggle to localStorage when it changes (globally)
  useEffect(() => {
    try {
      const key = 'debugEnabled'
      localStorage.setItem(key, JSON.stringify(viewToolsEnabled))
    } catch {}
  }, [viewToolsEnabled])

  useEffect(() => {
    if (!threadId) {
      setCurrentThread(undefined)
      return
    }
    // Prefer initialMessages if provided
    if (initialMessages && initialMessages.length) {
      setCurrentThread({
        threadId: threadId,
        messages: initialMessages,
        status: CurrentThreadStatus.complete
      })
      return
    }
    // If a stream is in progress for this thread, prefer hydrating from
    // the live buffer BEFORE falling back to snapshot. Snapshot at creation
    // time contains an empty assistant and would hide loading state.
    const inProgressBufferSnapshot = getThreadBufferSnapshot(threadId)
    if (inProgressBufferSnapshot && inProgressBufferSnapshot.length > 0) {
      setCurrentThread({
        threadId: threadId,
        messages: inProgressBufferSnapshot,
        isPending: true,
        status: CurrentThreadStatus.responsePending
      })
      return
    }
    if (historySnapshot) {
      // Check if we have complete message history saved
      const historyItem = history?.find(
        h => h.localThreadId === threadId || h.thread?.id === threadId
      )
      if (historyItem?.messages && historyItem.messages.length > 0) {
        // Use the complete message history including tool calls
        const hydrated: StoreMessage[] = historyItem.messages.map(msg => ({
          localId: msg.localId,
          id: msg.id,
          role: msg.role,
          content: msg.content,
          metadata: msg.metadata || {},
          isPending: false, // Always mark as complete when loading from history
          isContentPending: false, // Always mark as complete when loading from history
          error: msg.error
        }))
        setCurrentThread({
          threadId: threadId,
          messages: hydrated,
          status: CurrentThreadStatus.complete
        })
        return
      } else {
        // Fallback to snapshot for backward compatibility
        const hydrated: StoreMessage[] = [
          {
            localId: 'user',
            role: 'user',
            content: historySnapshot.user?.content ?? '',
            metadata: historySnapshot.user?.metadata ?? {}
          },
          {
            localId: 'assistant',
            role: 'assistant',
            content: historySnapshot.assistant?.content ?? '',
            metadata: historySnapshot.assistant?.metadata ?? {}
          }
        ]
        setCurrentThread({
          threadId: threadId,
          messages: hydrated,
          status: CurrentThreadStatus.complete
        })
        return
      }
    }
    setCurrentThread(undefined)
  }, [historySnapshot, initialMessages, setCurrentThread, threadId])

  const messages = currentThread?.messages
  const { scrollRef, isAtBottom, scrollToBottom } = useScrollToBottom()

  useEffect(() => {
    if (messages?.length === 1) {
      window.history.replaceState({}, '', getChatPath(currentThread?.threadId))
    }
  }, [currentThread?.threadId, messages?.length])

  const messageIsLoading = false

  useLayoutEffect(() => {
    if (scrollRef.current) {
      if (scrollRef.current.scrollTop === 0) {
        scrollElementToBottom(scrollRef.current, 'instant')
      }
    }
  }, [scrollRef, threadId])

  useEffect(() => {
    missingKeys?.forEach(key => {
      toast.error(`Missing ${key} environment variable!`)
    })
  }, [missingKeys])

  const disableToggleGroup =
    (messages?.length ?? 0) > 0 || currentThread?.isPending

  const toggleGroupControl = (
    <ToggleGroup
      disabled={disableToggleGroup}
      type="single"
      value={cleanlabEnabled ? 'cleanlab-enabled' : 'cleanlab-disabled'}
      onValueChange={value => {
        if (!value) return
        const next = value === 'cleanlab-enabled'
        setCleanlabEnabled(next)
      }}
      className="absolute top-0 z-50 mx-4 inline-flex w-fit justify-center self-center overflow-hidden rounded-2 border border-border-1 bg-surface-1 shadow-elev-2"
    >
      <ToggleGroupItem
        value="cleanlab-disabled"
        className={cn(
          toggleGroupItemClasses,
          disableToggleGroup &&
            'cursor-not-allowed bg-surface-disabled text-text-disabled hover:bg-surface-disabled'
        )}
      >
        Cleanlab Disabled
      </ToggleGroupItem>
      <ToggleGroupItem
        value="cleanlab-enabled"
        className={cn(
          toggleGroupItemClasses,
          disableToggleGroup &&
            'cursor-not-allowed bg-surface-disabled text-text-disabled hover:bg-surface-disabled'
        )}
      >
        Cleanlab Enabled
      </ToggleGroupItem>
    </ToggleGroup>
  )

  // Debug toggle - subtle, positioned at bottom right
  const viewToolsToggle = (
    <ToggleGroup
      type="single"
      value={viewToolsEnabled ? 'debug-on' : 'debug-off'}
      onValueChange={value => {
        const next = value === 'debug-on'
        setViewToolsEnabled(next)
      }}
      className="fixed bottom-4 right-4 z-40 inline-flex w-fit justify-center overflow-hidden rounded-2 border border-border-1 bg-surface-1 shadow-elev-1"
    >
      <ToggleGroupItem
        value="debug-off"
        className="first:border-r last:border-l border-border-1 py-1.5 px-3 text-xs flex items-center justify-center bg-surface-1 leading-3 hover:bg-surface-1-hover focus:z-10 focus:outline-none data-[state=on]:bg-surface-1-active data-[state=on]:text-text-strong"
      >
        Debug: Off
      </ToggleGroupItem>
      <ToggleGroupItem
        value="debug-on"
        className="first:border-r last:border-l border-border-1 py-1.5 px-3 text-xs flex items-center justify-center bg-surface-1 leading-3 hover:bg-surface-1-hover focus:z-10 focus:outline-none data-[state=on]:bg-surface-1-active data-[state=on]:text-text-strong"
      >
        Debug: On
      </ToggleGroupItem>
    </ToggleGroup>
  )

  const content = (
    <div
      className={cn(
        'group relative flex min-h-0 grow flex-col overflow-hidden bg-surface-0 pl-0 duration-300 ease-in-out'
      )}
    >
      <div
        ref={scrollRef}
        className={cn(
          'flex min-h-0 flex-1 flex-col overflow-auto md:pt-12',
          className
        )}
      >
        <div className="flex min-h-full flex-col">
          <div
            className={cn(
              'sm:rounded-t-xl mx-auto flex w-full max-w-[680px] grow flex-col px-8 md:px-9'
            )}
          >
            {disableToggleGroup ? (
              <Tooltip content="This setting can only be changed in an empty conversation thread">
                {toggleGroupControl}
              </Tooltip>
            ) : (
              toggleGroupControl
            )}
            {viewToolsToggle}
            {messages?.length ? (
              <ChatList
                threadId={currentThread?.threadId}
                scrollRef={scrollRef}
                cleanlabEnabled={cleanlabEnabled}
                viewToolsEnabled={viewToolsEnabled}
              />
            ) : (
              <EmptyScreen />
            )}
            <div className="sticky bottom-0 flex shrink-0 flex-col justify-end">
              <ChatInputPanel
                isAtBottom={isAtBottom}
                onScrollToBottom={scrollToBottom}
              >
                <PromptForm
                  input={input}
                  setInput={setInput}
                  promptPlaceholder={promptPlaceholder}
                  threadId={threadId}
                  cleanlabEnabled={cleanlabEnabled}
                />
              </ChatInputPanel>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  return content
}
