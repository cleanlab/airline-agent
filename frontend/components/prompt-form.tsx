'use client'

import * as React from 'react'
import { useEffect } from 'react'
import { useMessageIsPending } from '@/providers/messages-store-provider'
import { useStreamMessage } from '../lib/hooks/useStreamMessage'
import { InputMessage } from './design-system-components/InputMessage'

export function PromptForm({
  input,
  setInput,
  promptPlaceholder
}: {
  input: string
  setInput: (value: string) => void
  promptPlaceholder: string
}) {
  const inputRef = React.useRef<HTMLTextAreaElement>(null)
  const { sendMessage: sendMessage } = useStreamMessage()
  const isPending = useMessageIsPending()
  const submitDisabled = isPending || !input

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  return (
    <form
      onSubmit={async (e: any) => {
        e.preventDefault()

        if (!submitDisabled) {
          // Blur focus on mobile
          if (window.innerWidth < 600) {
            e.target['message']?.blur()
          }

          const value = input.trim()
          setInput('')
          if (!value) return
          sendMessage(value)
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
