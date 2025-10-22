import type { CurrentThread } from '@/stores/messages-store'

export function isCurrentThread({
  currentThread,
  localThreadId,
  threadId
}: {
  currentThread: CurrentThread | undefined
  localThreadId: string | undefined
  threadId: string | undefined
}) {
  if (!currentThread) return false
  if (threadId && currentThread.threadId === threadId) return true
  if (localThreadId && currentThread.localThreadId === localThreadId)
    return true
  return false
}
