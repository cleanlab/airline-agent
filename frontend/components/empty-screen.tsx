export function EmptyScreen() {
  const isDefaultAssistant = true

  if (isDefaultAssistant) {
    return (
      <div className="flex h-full grow flex-col items-center justify-center gap-8" />
    )
  }
  return null
}
