'use client'

import type { ReactNode } from 'react'

import { cn } from '@/lib/utils/tailwindUtils'
import { ButtonScrollToBottom } from './ButtonScrollToBottom'

type ChatInputPanelProps = {
  isAtBottom: boolean
  onScrollToBottom: () => void
  className?: string
  children?: ReactNode
}

function ChatInputPanel({
  isAtBottom,
  children,
  onScrollToBottom,
  className
}: ChatInputPanelProps) {
  return (
    <div
      className={cn(
        'inset-x-0 bottom-0 flex w-full flex-col items-center duration-300 ease-in-out animate-in',
        className
      )}
    >
      {/* Div used for the gradient to be a consistent height and to provide the top padding for the chat input. */}
      <div className="h-8 w-full bg-gradient-to-b from-surface-0/0 from-0% to-surface-0 to-100% pt-8 md:h-9"></div>

      <div className="relative w-full bg-surface-0 pb-8 md:pb-9">
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 -translate-y-full">
          <ButtonScrollToBottom
            onClick={onScrollToBottom}
            hidden={!!isAtBottom}
          />
        </div>
        {children}
      </div>
    </div>
  )
}

export type { ChatInputPanelProps }
export { ChatInputPanel }
