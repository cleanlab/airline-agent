'use client'

import { AnimatePresence, motion, usePresence } from 'motion/react'
import type { ForwardedRef } from 'react'
import { type ComponentProps, forwardRef } from 'react'

import { IconArrowDownCircle } from '../icons'
import { cn } from '@/lib/utils/tailwindUtils'

const ButtonBase = forwardRef(
  (
    {
      className,
      disabled: disabledProp = false,
      ...props
    }: ComponentProps<typeof motion.button>,
    ref: ForwardedRef<HTMLButtonElement>
  ) => {
    const [isPresent, safeToRemove] = usePresence()
    const disabled = disabledProp || !isPresent
    const hidden = !isPresent

    return (
      <motion.button
        ref={ref}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{
          opacity: 0,
          y: 0
        }}
        onAnimationComplete={() => safeToRemove?.()}
        className={cn(
          'flex size-9 items-center justify-center rounded-2 border border-border-2 bg-surface-2 p-4 hover:bg-surface-2-hover disabled:cursor-not-allowed',
          disabledProp &&
            'disabled:bg-surface-disabled disabled:text-text-disabled',
          hidden && 'pointer-events-none',
          className
        )}
        aria-hidden={hidden}
        disabled={disabled}
        {...props}
      >
        <IconArrowDownCircle size={20} />
        <span className="sr-only">Scroll to bottom</span>
      </motion.button>
    )
  }
)

export function ButtonScrollToBottom({
  className,
  hidden = false,
  ...props
}: { hidden: boolean } & ComponentProps<typeof motion.button>) {
  return (
    <AnimatePresence>{!hidden && <ButtonBase {...props} />}</AnimatePresence>
  )
}
