import { getChatPath } from '@/lib/consts'
import { assertExhaustive } from '@/lib/ts/assertExhaustive'
import { nanoid } from '@/lib/utils'
import {
  useBareMessagesStore,
  useMessagesStore
} from '@/providers/messages-store-provider'
import { useRagAppStore } from '@/providers/rag-app-store-provider'
import type { StoreMessage, ThreadError } from '@/stores/messages-store'
import type { UserMessage } from '@/client/types.gen'
import ENV_VARS from '@/lib/envVars'
import { useCallback, useMemo, useRef } from 'react'
import { useAppSettings } from './use-app-settings'
import { AGILITY_DEFAULT_ASSISTANT_SLUG } from '../consts'
import type { SetOptional } from 'type-fest'

export const CurrentThreadStatus = {
  threadPending: 'threadPending',
  responsePending: 'responsePending',
  contentPending: 'contentPending',
  metadataPending: 'metadataPending',
  complete: 'complete',
  failed: 'failed'
} as const satisfies Record<string, string>

export type CurrentThreadStatus =
  (typeof CurrentThreadStatus)[keyof typeof CurrentThreadStatus]

const RetryLabels = { sendAgain: 'Send message again', retry: 'Retry' } as const

const getErrorFromCurrentStatus = (status: CurrentThreadStatus | undefined) => {
  const error: ThreadError | undefined = (() => {
    switch (status) {
      case undefined:
      case CurrentThreadStatus.threadPending:
        return {
          message: 'Could not create thread',
          canRetry: true
        }
      case CurrentThreadStatus.responsePending:
        return {
          message: 'Unable to send message',
          canRetry: true
        }
      case CurrentThreadStatus.contentPending:
        return {
          message: 'Response did not complete',
          canRetry: true,
          retryLabel: RetryLabels.sendAgain
        }
      case CurrentThreadStatus.metadataPending:
        return {
          message: 'Could not retrieve trustworthiness score',
          canRetry: true,
          retryLabel: RetryLabels.sendAgain
        }
      case CurrentThreadStatus.complete:
      case CurrentThreadStatus.failed:
        return undefined
      default:
        assertExhaustive(status)
    }
  })()
  if (error) {
    error.atStatus = status
  }
  return error
}

const createInitialMessages = ({
  content,
  threadId
}: {
  content: string
  threadId: string
}) => {
  const dateString = new Date().toISOString()

  return [
    {
      localId: nanoid(),
      role: 'user',
      content: content,
      metadata: {},
      isPending: true
    },
    {
      localId: nanoid(),
      role: 'assistant',
      content: '',
      metadata: {},
      isPending: true,
      isContentPending: true
    }
  ] as const satisfies StoreMessage[]
}

// Global in-memory buffers for in-progress streams keyed by threadId
const threadBuffers = new Map<string, StoreMessage[]>()

export const getThreadBufferSnapshot = (
  threadId: string
): StoreMessage[] | undefined => {
  const buf = threadBuffers.get(threadId)
  if (!buf) return undefined
  // return a shallow copy to avoid accidental mutations
  return buf.map(m => ({
    ...m,
    metadata: m.metadata ? { ...m.metadata } : m.metadata
  }))
}

// Module-scoped helpers to avoid recreating callbacks inside the hook
const getOrInitBuffer = (threadId: string) => {
  let buffer = threadBuffers.get(threadId)
  if (!buffer) {
    buffer = []
    threadBuffers.set(threadId, buffer)
  }
  return buffer
}

const bufferAppendUser = ({
  threadId,
  content
}: {
  threadId: string
  content: string
}) => {
  const buffer = getOrInitBuffer(threadId)
  buffer.push({
    localId: nanoid(),
    role: 'user',
    content,
    metadata: {}
  })
}

const bufferAppendTool = ({
  threadId,
  content,
  metadata
}: {
  threadId: string
  content: any
  metadata?: any
}) => {
  const buffer = getOrInitBuffer(threadId)
  buffer.push({
    localId: nanoid(),
    role: 'tool',
    content,
    metadata: metadata || {}
  })
}

const bufferAppendAssistantChunk = ({
  threadId,
  content,
  metadata
}: {
  threadId: string
  content: string
  metadata?: any
}) => {
  const buffer = getOrInitBuffer(threadId)
  const last = buffer[buffer.length - 1]
  if (last && last.role === 'assistant') {
    last.content = `${last.content || ''}${content || ''}`
    last.metadata = { ...(last.metadata || {}), ...(metadata || {}) }
  } else {
    buffer.push({
      localId: nanoid(),
      role: 'assistant',
      content: content || '',
      metadata: metadata || {}
    })
  }
}

const clearThreadBuffer = (threadId: string) => {
  threadBuffers.delete(threadId)
}

// Ensure a thread's buffer starts with the existing persisted messages so
// toggling threads mid-stream never drops earlier history.
const bufferSeedFromMessages = ({
  threadId,
  seedMessages
}: {
  threadId: string
  seedMessages?: StoreMessage[]
}) => {
  if (!seedMessages || seedMessages.length === 0) return
  const buffer = getOrInitBuffer(threadId)
  if (buffer.length > 0) return
  for (const msg of seedMessages) {
    buffer.push({
      localId: msg.localId || nanoid(),
      id: msg.id,
      role: msg.role,
      content: msg.content,
      metadata: msg.metadata ? { ...msg.metadata } : {}
    })
  }
}

function useStreamMessage(cleanlabEnabled: boolean = true) {
  const currentThread = useMessagesStore(state => state.currentThread)
  const setCurrentThread = useMessagesStore(state => state.setCurrentThread)
  const appendMessage = useMessagesStore(state => state.appendMessage)

  const messageIsPending = useMessagesStore(
    state => state.currentThread?.isPending
  )
  const setThreadStatus = useMessagesStore(state => state.setThreadStatus)

  const addHistoryThread = useRagAppStore(state => state.addHistoryThread)
  const updateHistoryThread = useRagAppStore(state => state.updateHistoryThread)
  const [appSettings] = useAppSettings()

  // Always use latest cleanlabEnabled in callbacks
  const cleanlabRef = useRef(cleanlabEnabled)
  cleanlabRef.current = cleanlabEnabled

  // Persist the latest buffered messages for a thread into history so that
  // switching to an inactive, in-progress thread shows up-to-date content.
  const syncHistoryFromBuffer = useCallback(
    (threadId: string) => {
      try {
        const buffered = threadBuffers.get(threadId) || []
        if (!buffered.length) return
        updateHistoryThread({
          assistantId:
            appSettings.assistantId ?? AGILITY_DEFAULT_ASSISTANT_SLUG,
          threadId,
          thread: {
            messages: buffered.map(msg => ({
              localId: msg.localId,
              id: msg.id,
              role: msg.role,
              content: msg.content,
              metadata: msg.metadata || {},
              isPending: false,
              isContentPending: false,
              error: msg.error
            }))
          }
        })
      } catch (e) {
        // best-effort; ignore persistence errors during streaming
      }
    },
    [updateHistoryThread, appSettings.assistantId]
  )

  const setDone = useCallback(
    (opts: SetOptional<Parameters<typeof setThreadStatus>[0], 'status'>) => {
      setThreadStatus({
        status: opts.error
          ? CurrentThreadStatus.failed
          : CurrentThreadStatus.complete,
        ...opts
      })
    },
    [setThreadStatus]
  )

  const bareStore = useBareMessagesStore()

  const handleStreamChunk = useCallback(
    ({ threadId, value }: { threadId: string; value: any }) => {
      // Handle different types of streaming chunks
      if (value.role === 'tool') {
        // Handle tool call messages
        const toolMessage: StoreMessage = {
          localId: nanoid(),
          role: 'tool',
          content: value.content,
          metadata: value.metadata || {}
        }
        appendMessage({ threadId, message: toolMessage })
        bufferAppendTool({
          threadId,
          content: value.content,
          metadata: value.metadata
        })
        syncHistoryFromBuffer(threadId)
      } else if (value.role === 'assistant') {
        // Handle assistant messages - appendMessage will automatically replace pending message
        const assistantMessage: StoreMessage = {
          localId: nanoid(),
          role: 'assistant',
          content: value.content,
          metadata: value.metadata || {}
        }
        appendMessage({ threadId, message: assistantMessage })
        bufferAppendAssistantChunk({
          threadId,
          content: value.content,
          metadata: value.metadata
        })
        syncHistoryFromBuffer(threadId)
        // Don't set status to complete here - wait for thread.run.completed
      }
    },
    [appendMessage, setThreadStatus, syncHistoryFromBuffer]
  )

  const postMessage = useCallback(
    async ({
      threadId,
      localThreadId,
      messageContent,
      cleanlabEnabled = true
    }: {
      threadId: string
      localThreadId?: string
      messageContent?: string
      cleanlabEnabled?: boolean
    }) => {
      if (!threadId) return
      setThreadStatus({
        threadId,
        localThreadId,
        status: CurrentThreadStatus.responsePending,
        error: undefined
      })

      let response: Response | undefined
      let finalAssistantMessage: StoreMessage | null = null

      try {
        const baseURL =
          ENV_VARS.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
        const userMessage: UserMessage = {
          role: 'user',
          content: messageContent || '',
          thread_id: threadId
        }

        response = await fetch(
          `${baseURL}/api/agent/stream?thread_id=${threadId}&cleanlab_enabled=${cleanlabEnabled}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Accept: 'text/event-stream'
            },
            body: JSON.stringify(userMessage)
          }
        )

        if (!response.ok) {
          setDone({
            threadId,
            error: {
              message: `HTTP error! status: ${response.status}`,
              canRetry: true
            },
            status: CurrentThreadStatus.failed
          })
          return
        }

        if (!response.body) {
          setDone({
            threadId,
            error: {
              message: 'This browser does not support streaming responses.',
              canRetry: false
            },
            status: CurrentThreadStatus.failed
          })
          return
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        const errHandler = (err: Error) => {
          console.error('Error in stream reader', err)
          setDone({
            threadId,
            error: getErrorFromCurrentStatus(
              bareStore.getState().currentThread?.status
            )
          })
        }

        const pump = async () => {
          try {
            const { done, value } = await reader.read()

            if (done) {
              const currentThread = bareStore.getState().currentThread
              if (currentThread?.status !== 'complete') {
                const error =
                  currentThread?.error ||
                  getErrorFromCurrentStatus(currentThread?.status)
                setDone({
                  threadId,
                  localThreadId,
                  status: CurrentThreadStatus.failed,
                  error: error
                })
              }
              clearThreadBuffer(threadId)
              return
            }

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')

            let currentEvent = ''
            let currentData = ''

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                currentEvent = line.slice(7).trim()
              } else if (line.startsWith('data: ')) {
                currentData = line.slice(6).trim()

                if (currentEvent && currentData) {
                  try {
                    const eventData = JSON.parse(currentData)

                    // Handle different event types
                    if (currentEvent === 'thread.run.in_progress') {
                      setThreadStatus({
                        threadId,
                        status: CurrentThreadStatus.responsePending
                      })
                    } else if (currentEvent === 'thread.message') {
                      const messageData = eventData.data
                      if (messageData.role === 'tool') {
                        handleStreamChunk({ threadId, value: messageData })
                      } else if (messageData.role === 'assistant') {
                        handleStreamChunk({ threadId, value: messageData })
                        finalAssistantMessage = {
                          localId: nanoid(),
                          role: 'assistant',
                          content: messageData.content,
                          metadata: messageData.metadata || {}
                        }
                      }
                    } else if (currentEvent === 'thread.run.completed') {
                      // Save history when stream completes
                      // Use per-thread buffer (avoids cross-thread clobbering)
                      const bufferedMessages = threadBuffers.get(threadId) || []

                      // Fall back to currentThread only if it matches, otherwise keep buffer
                      const possibleThread = bareStore.getState().currentThread
                      const sourceMessages =
                        possibleThread?.threadId === threadId &&
                        possibleThread?.messages?.length
                          ? possibleThread.messages
                          : bufferedMessages

                      if (sourceMessages && sourceMessages.length) {
                        const firstUserMessage = sourceMessages.find(
                          m => m.role === 'user'
                        )
                        const lastAssistantMessage = sourceMessages
                          .filter(m => m.role === 'assistant')
                          .pop()

                        if (firstUserMessage) {
                          addHistoryThread({
                            title: firstUserMessage.content || 'New thread',
                            assistantId:
                              appSettings.assistantId ??
                              AGILITY_DEFAULT_ASSISTANT_SLUG,
                            thread: { id: threadId } as any,
                            cleanlabEnabled: cleanlabRef.current,
                            snapshot: lastAssistantMessage
                              ? {
                                  user: {
                                    content: firstUserMessage.content,
                                    metadata: firstUserMessage.metadata || {}
                                  },
                                  assistant: {
                                    content: lastAssistantMessage.content,
                                    metadata:
                                      lastAssistantMessage.metadata || {}
                                  }
                                }
                              : {
                                  user: {
                                    content: firstUserMessage.content,
                                    metadata: firstUserMessage.metadata || {}
                                  },
                                  assistant: {
                                    content: '',
                                    metadata: {}
                                  }
                                },
                            messages: sourceMessages.map(msg => ({
                              localId: msg.localId,
                              id: msg.id,
                              role: msg.role,
                              content: msg.content,
                              metadata: msg.metadata,
                              isPending: false,
                              isContentPending: false,
                              error: msg.error
                            }))
                          })
                        }
                      }
                      clearThreadBuffer(threadId)
                      setDone({ threadId, localThreadId })
                      return
                    } else if (currentEvent === 'thread.run.failed') {
                      setDone({
                        threadId,
                        error: { message: 'Run failed', canRetry: true },
                        status: CurrentThreadStatus.failed
                      })
                      clearThreadBuffer(threadId)
                      return
                    }
                  } catch (e) {
                    console.warn(
                      'Failed to parse streaming data:',
                      currentData,
                      e
                    )
                  }

                  // Reset for next event
                  currentEvent = ''
                  currentData = ''
                }
              }
            }

            pump()
          } catch (err) {
            errHandler(err as Error)
          }
        }

        pump()
      } catch (e) {
        setDone({
          threadId,
          error: { message: 'Request failed', canRetry: true },
          status: CurrentThreadStatus.failed
        })
      }
    },
    [
      setThreadStatus,
      bareStore,
      handleStreamChunk,
      setDone,
      addHistoryThread,
      appSettings.assistantId
    ]
  )

  const createThreadPending = false

  const isPending = messageIsPending || createThreadPending
  const createThreadAndPostMessage = useCallback(
    async ({ messageContent }: { messageContent: string }) => {
      const localThreadId = nanoid()
      addHistoryThread({
        title: messageContent || 'New thread',
        assistantId: appSettings.assistantId ?? AGILITY_DEFAULT_ASSISTANT_SLUG,
        thread: { id: localThreadId } as any,
        cleanlabEnabled: cleanlabRef.current,
        snapshot: {
          user: { content: messageContent || '', metadata: {} },
          assistant: { content: '', metadata: {} }
        }
      })
      const initialMessages = createInitialMessages({
        threadId: localThreadId,
        content: messageContent
      })
      setCurrentThread({
        localThreadId,
        threadId: localThreadId,
        messages: initialMessages,
        isPending: true,
        status: CurrentThreadStatus.threadPending
      })
      // Track the initiating user message for this thread in the buffer
      bufferAppendUser({ threadId: localThreadId, content: messageContent })
      // Immediately post to backend and treat this as a standalone Q+A thread
      window?.history.pushState({}, '', getChatPath(localThreadId))
      postMessage({
        threadId: localThreadId,
        localThreadId,
        messageContent: messageContent,
        cleanlabEnabled: cleanlabRef.current
      })
    },
    [addHistoryThread, setCurrentThread, postMessage, bufferAppendUser]
  )

  const sendMessage = useCallback(
    (messageContent: string, urlThreadId?: string) => {
      if (isPending) {
        return
      }
      const currentThreadId = currentThread?.threadId
      const threadIdToUse = urlThreadId || currentThreadId

      if (
        threadIdToUse &&
        currentThread?.messages &&
        currentThread.messages.length > 0
      ) {
        // Seed the per-thread buffer with existing conversation history
        bufferSeedFromMessages({
          threadId: threadIdToUse,
          seedMessages: currentThread.messages
        })
        // Continue existing conversation - add user message to current thread
        const userMessage: StoreMessage = {
          localId: nanoid(),
          role: 'user',
          content: messageContent,
          metadata: {}
        }
        appendMessage({ threadId: threadIdToUse, message: userMessage })
        // Also record in the per-thread buffer for history when stream completes
        bufferAppendUser({ threadId: threadIdToUse, content: messageContent })
        // Persist new buffered state to history for inactive thread visibility
        syncHistoryFromBuffer(threadIdToUse)

        // Add optimistic assistant placeholder
        const assistantMessage: StoreMessage = {
          localId: nanoid(),
          role: 'assistant',
          content: '',
          metadata: {},
          isPending: true,
          isContentPending: true
        }
        appendMessage({ threadId: threadIdToUse, message: assistantMessage })

        // Post message to backend
        postMessage({
          threadId: threadIdToUse,
          localThreadId: currentThread?.localThreadId,
          messageContent: messageContent,
          cleanlabEnabled: cleanlabRef.current
        })
      } else {
        // Start new conversation
        createThreadAndPostMessage({ messageContent })
      }
    },
    [
      currentThread,
      appendMessage,
      postMessage,
      createThreadAndPostMessage,
      isPending,
      syncHistoryFromBuffer
    ]
  )

  const retrySendMessage = useCallback(() => {
    const lastUserMessage = currentThread?.messages?.find(
      m => m.role === 'user'
    )
    const existingThreadId = currentThread?.threadId
    if (!lastUserMessage?.content || !existingThreadId) return
    // Seed buffer with existing history if needed
    bufferSeedFromMessages({
      threadId: existingThreadId,
      seedMessages: currentThread?.messages
    })
    // Add optimistic assistant placeholder to show loading state
    appendMessage({
      threadId: existingThreadId,
      message: {
        localId: nanoid(),
        role: 'assistant',
        content: '',
        metadata: {},
        isPending: true,
        isContentPending: true
      }
    })
    // Keep history in sync for inactive thread visibility
    syncHistoryFromBuffer(existingThreadId)
    postMessage({
      threadId: existingThreadId,
      localThreadId: currentThread?.localThreadId,
      messageContent: lastUserMessage.content,
      cleanlabEnabled: cleanlabRef.current
    })
  }, [appendMessage, currentThread, postMessage, syncHistoryFromBuffer])

  return useMemo(
    () => ({
      sendMessage,
      retrySendMessage
    }),
    [retrySendMessage, sendMessage]
  )
}

export { useStreamMessage }
