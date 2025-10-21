'use client'

import type { HTMLAttributes, ReactNode } from 'react'

import { cn } from '@/lib/utils/tailwindUtils'
import { TextWithLineBreaks } from './TextWithLineBreaks'

export function MessageUser({
  content,
  className,
  ...props
}: {
  content: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('relative flex w-full justify-end', className)}
      {...props}
    >
      <div
        className="type-body-200 rounded-s-4 rounded-br-none rounded-tr-4 bg-surface-2 px-6 py-5 text-text-primary"
        {...props}
      >
        <TextWithLineBreaks content={content} />
      </div>
    </div>
  )
}
