'use client'

import type { ButtonHTMLAttributes } from 'react'

import { Tooltip } from './Tooltip'
import { IconArrowCornerDownLeft } from '../icons'
import { cn } from '@/lib/utils/tailwindUtils'

const SUBMIT_BUTTON_LABEL = 'Send message'

const ButtonSubmitMessage = ({
  disabled,
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) => {
  return (
    <Tooltip
      disabled={disabled}
      content={props['aria-label'] || SUBMIT_BUTTON_LABEL}
    >
      <button
        className={cn(
          'absolute right-4 top-1/2 z-10 flex size-9 -translate-y-1/2 items-center justify-center rounded-2 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-focus disabled:opacity-50 [&:not(:disabled)]:hover:bg-surface-2',
          disabled && 'cursor-not-allowed',
          className
        )}
        type="submit"
        disabled={disabled}
        aria-label={SUBMIT_BUTTON_LABEL}
        {...props}
      >
        <IconArrowCornerDownLeft size={24} />
      </button>
    </Tooltip>
  )
}
export { ButtonSubmitMessage }
