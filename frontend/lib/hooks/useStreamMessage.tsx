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
import { useCallback, useMemo } from 'react'
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

function useStreamMessage() {
  const currentThread = useMessagesStore(state => state.currentThread)
  const setCurrentThread = useMessagesStore(state => state.setCurrentThread)
  const appendMessage = useMessagesStore(state => state.appendMessage)
  const updateMessageContent = useMessagesStore(
    state => state.updateMessageContent
  )
  const updateMessage = useMessagesStore(state => state.updateMessage)
  const updateMessageMetadata = useMessagesStore(
    state => state.updateMessageMetadata
  )
  const messageIsPending = useMessagesStore(
    state => state.currentThread?.isPending
  )
  const setThreadStatus = useMessagesStore(state => state.setThreadStatus)

  const addHistoryThread = useRagAppStore(state => state.addHistoryThread)
  const [appSettings] = useAppSettings()

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
          content: JSON.stringify(value.content),
          metadata: value.metadata || {}
        }
        appendMessage({ threadId, message: toolMessage })
      } else if (value.role === 'assistant') {
        // Handle assistant messages - appendMessage will automatically replace pending message
        const assistantMessage: StoreMessage = {
          localId: nanoid(),
          role: 'assistant',
          content: value.content,
          metadata: value.metadata || {}
        }
        appendMessage({ threadId, message: assistantMessage })
        // Don't set status to complete here - wait for thread.run.completed
      }
    },
    [appendMessage, setThreadStatus]
  )

  const postMessage = useCallback(
    async ({
      threadId,
      localThreadId,
      messageContent
    }: {
      threadId: string
      localThreadId?: string
      messageContent?: string
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
          `${baseURL}/api/airline-agent/stream?thread_id=${threadId}`,
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

        // Verify we're getting a streaming response
        const contentType = response.headers.get('content-type')
        if (!contentType || !contentType.includes('text/event-stream')) {
          console.warn('Expected text/event-stream, got:', contentType)
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
                  currentThread?.error ??
                  getErrorFromCurrentStatus(currentThread?.status)
                setDone({
                  threadId,
                  localThreadId,
                  status: CurrentThreadStatus.failed,
                  error: error
                })
              }
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
                      // Get all messages from the current thread to save complete conversation
                      const currentThread = bareStore.getState().currentThread
                      if (currentThread && currentThread.messages) {
                        // Find user and assistant messages for the snapshot
                        const userMessage = currentThread.messages.find(
                          m => m.role === 'user'
                        )
                        const assistantMessage = currentThread.messages.find(
                          m => m.role === 'assistant'
                        )

                        if (userMessage && assistantMessage) {
                          addHistoryThread({
                            title: messageContent || 'New thread',
                            assistantId:
                              appSettings.assistantId ??
                              AGILITY_DEFAULT_ASSISTANT_SLUG,
                            thread: { id: threadId } as any,
                            snapshot: {
                              user: {
                                content: userMessage.content,
                                metadata: userMessage.metadata || {}
                              },
                              assistant: {
                                content: assistantMessage.content,
                                metadata: assistantMessage.metadata || {}
                              }
                            },
                            messages: currentThread.messages.map(msg => ({
                              localId: msg.localId,
                              id: msg.id,
                              role: msg.role,
                              content: msg.content,
                              metadata: msg.metadata,
                              isPending: msg.isPending,
                              isContentPending: msg.isContentPending,
                              error: msg.error
                            }))
                          })
                        }
                      }
                      setDone({ threadId, localThreadId })
                      return
                    } else if (currentEvent === 'thread.run.failed') {
                      setDone({
                        threadId,
                        error: { message: 'Run failed', canRetry: true },
                        status: CurrentThreadStatus.failed
                      })
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
      // Immediately post to backend and treat this as a standalone Q+A thread
      window?.history.pushState({}, '', getChatPath(localThreadId))
      postMessage({
        threadId: localThreadId,
        localThreadId,
        messageContent: messageContent
      })
    },
    [addHistoryThread, setCurrentThread, postMessage]
  )

  const sendMessage = useCallback(
    (messageContent: string) => {
      if (isPending) {
        return
      }
      const currentThreadId = currentThread?.threadId

      // Always start a new thread for each new submission
      createThreadAndPostMessage({ messageContent })
    },
    [createThreadAndPostMessage, isPending]
  )

  const retrySendMessage = useCallback(() => {
    const lastUserMessage = currentThread?.messages?.find(
      m => m.role === 'user'
    )
    const existingThreadId = currentThread?.threadId
    if (!lastUserMessage?.content || !existingThreadId) return
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
    postMessage({
      threadId: existingThreadId,
      localThreadId: currentThread?.localThreadId,
      messageContent: lastUserMessage.content
    })
  }, [appendMessage, currentThread, postMessage])

  return useMemo(
    () => ({
      sendMessage,
      retrySendMessage
    }),
    [retrySendMessage, sendMessage]
  )
}

export { useStreamMessage }
