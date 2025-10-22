'use client'

import { Slot as SlotPrimitive } from 'radix-ui'
import type { ComponentProps } from 'react'

import type { AsChildProps } from '@/lib/utils/AsChildProps'
import { cn } from '@/lib/utils/tailwindUtils'

const Slot = SlotPrimitive.Root

const CodeInline = ({
  asChild,
  className,
  ...props
}: AsChildProps<ComponentProps<'code'>>) => {
  const Elt = asChild ? Slot : 'code'
  return (
    <Elt
      className={cn(
        'text-transform-[inherit] type-code-100 -z-10 mx-[0.15em] inline rounded-1 border border-border-1 bg-surface-1 px-[0.43em] py-[0.15em] text-[0.86em] leading-[inherit] text-text-primary',
        className
      )}
      {...props}
    />
  )
}

export { CodeInline }
