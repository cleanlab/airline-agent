'use client'

import { InputMessage } from '@cleanlab/design-system/chat'
import { type FormEvent,useEffect, useRef } from 'react'

import { useStreamMessage } from '@/lib/hooks/useStreamMessage'
import { useMessageIsPending } from '@/providers/messages-store-provider'

export function PromptForm({
  input,
  setInput,
  promptPlaceholder,
  threadId,
  cleanlabEnabled = true
}: {
  input: string
  setInput: (value: string) => void
  promptPlaceholder: string
  threadId?: string
  cleanlabEnabled?: boolean
}) {
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const { sendMessage } = useStreamMessage(cleanlabEnabled)
  const isPending = useMessageIsPending()
  const submitDisabled = isPending || !input

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  return (
    <form
      onSubmit={async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault()

        if (!submitDisabled) {
          // Blur focus on mobile
          if (window.innerWidth < 600) {
            const form = e.currentTarget
            const messageEl = form.elements.namedItem('message') as
              | HTMLTextAreaElement
              | HTMLInputElement
              | null
            messageEl?.blur()
          }

          const value = input.trim()
          setInput('')
          if (!value) return
          sendMessage(value, threadId)
        }
      }}
    >
      <InputMessage
        ref={inputRef}
        tabIndex={0}
        placeholder={promptPlaceholder}
        autoFocus
        name="message"
        value={input}
        onChange={e => {
          setInput(e.currentTarget.value)
        }}
        submitDisabled={submitDisabled}
      />
    </form>
  )
}
