export const RATE_LIMIT_WAIT_MS =
  Number(process.env.NEXT_PUBLIC_RATE_LIMIT_WAIT_MS) || 40

export const getChatPath = (threadId?: string) => {
  // With a single assistant, URLs are of the form "/" or "/:threadId"
  if (!threadId) return '/'
  return `/${threadId}`
}
