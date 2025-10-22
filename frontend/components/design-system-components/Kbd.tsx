import type { ForwardedRef, HTMLAttributes, ReactNode } from 'react'
import { forwardRef, memo } from 'react'

import { cn, tv } from '@/lib/utils/tailwindUtils'

type KbdProps = {
  children: ReactNode
  className?: string
  variant?:
    | 'outline'
    | 'primary'
    | 'highContrast'
    | 'subtle'
    | 'buttonPrimary'
    | 'buttonHighContrast'
  disabled?: boolean
  size?: 'xSmall' | 'small' | 'medium'
} & HTMLAttributes<HTMLDivElement>
const variants = tv({
  base: 'flex items-center rounded-1 text-center text-text-faint outline outline-1 outline-border-2 transition-colors',
  variants: {
    variant: {
      outline: '',
      buttonPrimary: 'bg-button-primary-bg text-white/90 outline-white/30',
      buttonHighContrast:
        'bg-surface-high-contrast text-neutral-300 outline-neutral-700',
      primary: 'bg-surface-2',
      highContrast:
        'bg-surface-high-contrast text-text-high-contrast outline-border-0',
      subtle: 'bg-surface-1 text-text-primary outline-border-1'
    },
    size: {
      xSmall: 'type-kbd-xs min-h-[14px] px-[3px]',
      small: 'type-kbd-sm min-h-6 px-2',
      medium: 'type-kbd min-h-7 px-3'
    }
  }
})

const KbdBase = (
  {
    className,
    variant = 'primary',
    size = 'medium',
    disabled,
    ...props
  }: KbdProps,
  ref: ForwardedRef<HTMLDivElement>
) => {
  return (
    <kbd
      ref={ref}
      className={cn(
        variants({ variant, size }),
        disabled && 'text-text-disabled',
        className
      )}
      {...props}
    ></kbd>
  )
}

/**
 * Kbd component
 */
const Kbd = memo(forwardRef(KbdBase))
Kbd.displayName = 'Kbd'

export { Kbd }
