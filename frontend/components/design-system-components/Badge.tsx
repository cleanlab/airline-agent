import { Slot as SlotPrimitive } from 'radix-ui'
import type { ForwardedRef, HTMLAttributes, ReactElement } from 'react'
import { cloneElement, forwardRef, memo } from 'react'

import type { AsChildProps } from '@/lib/utils/AsChildProps'
import { cn, tv, tw } from '@/lib/utils/tailwindUtils'
import { SlotChild } from './SlotChild'
import { StatusDot } from './StatusDot'

const Slot = SlotPrimitive.Root

type BadgeVariant = 'subtle' | 'outline' | 'filled' | 'actionSubtle'
type BadgeHue =
  | 'neutral'
  | 'neutralStrong'
  | 'blue'
  | 'red'
  | 'orange'
  | 'yellow'
  | 'green'
  | 'teal'
  | 'cyan'
  | 'purple'
  | 'pink'
  | 'lime'
  | 'magic'
type BadgeSize = 'small' | 'medium' | 'large'
type BadgeRound = 'medium' | 'small' | 'full'

type BadgeProps = AsChildProps<HTMLAttributes<HTMLDivElement>> & {
  hue?: BadgeHue
  icon?: ReactElement<{ size?: number }>
  variant?: BadgeVariant
  round?: BadgeRound
  size?: BadgeSize
}

const variants = tv({
  variants: {
    // Main variant
    variant: {
      subtle: 'text-text-faint outline -outline-offset-1 outline-border-1',
      outline: 'bg-surface-0 -outline-offset-1',
      filled: 'text-text-high-contrast',
      actionSubtle:
        'bg-surface-0 text-text-primary outline -outline-offset-1 outline-border-1'
    },
    // Additional options
    size: {
      small: 'type-badge-sm min-h-7',
      medium: 'type-badge-md min-h-8',
      large: 'type-badge-lg min-h-[28px]'
    },
    round: {
      small: 'rounded-1',
      medium: 'rounded-2',
      full: 'rounded-full'
    }
  },
  compoundVariants: [
    {
      variant: ['subtle', 'outline', 'filled'],
      size: 'small',
      class: 'gap-1 px-3'
    },
    {
      variant: ['subtle', 'outline', 'filled'],
      size: 'medium',
      class: 'gap-2 px-4'
    },
    {
      variant: ['subtle', 'outline', 'filled'],
      size: 'large',
      class: 'gap-3 px-5'
    },
    { variant: ['actionSubtle'], size: 'small', class: 'gap-1 pl-2 pr-3' },
    { variant: ['actionSubtle'], size: 'medium', class: 'gap-2 pl-3 pr-4' },
    { variant: ['actionSubtle'], size: 'large', class: 'gap-2 pl-4 pr-5' }
  ]
})

const variantHueClasses = {
  subtle: {
    neutral: 'bg-surface-1 text-text-faint outline-border-1 ',
    neutralStrong: 'bg-surface-2 text-text-primary outline-border-2',
    blue: 'bg-blue-50 text-blue-700 outline-blue-200 ',
    red: 'bg-red-50 text-red-700 outline-red-200',
    orange: 'bg-orange-50 text-orange-700 outline-orange-200',
    yellow: 'bg-yellow-50 text-yellow-800 outline-yellow-400',
    green: 'bg-green-50 text-green-700 outline-green-200',
    teal: 'bg-teal-50 text-teal-700 outline-teal-200',
    cyan: 'bg-cyan-50 text-cyan-700 outline-cyan-200',
    purple: 'bg-purple-50 text-purple-700 outline-purple-200',
    pink: 'bg-pink-50 text-pink-700 outline-pink-200',
    lime: 'bg-lime-50 text-lime-700 outline-lime-200',
    magic:
      'bg-surface-1 outline-0 [background:linear-gradient(to_right,var(--cl-gradient-magic))]'
  },
  outline: {
    neutral: 'text-text-faint outline-border-2',
    neutralStrong: 'text-text-primary outline-neutral-400',
    blue: 'text-blue-700 outline-blue-400',
    red: 'text-red-700 outline-red-400',
    orange: 'text-orange-700 outline-orange-400',
    yellow: 'text-yellow-800 outline-yellow-600',
    green: 'text-green-700 outline-green-400',
    teal: 'text-teal-700 outline-teal-400',
    cyan: 'text-cyan-700 outline-cyan-400',
    purple: 'text-purple-700 outline-purple-400',
    pink: 'text-pink-700 outline-pink-400',
    lime: 'text-lime-700 outline-lime-400',
    magic:
      'text-text-primary outline-0 [background:linear-gradient(to_right,var(--cl-gradient-magic))]'
  },
  filled: {
    neutral: 'bg-neutral-700 text-text-high-contrast',
    neutralStrong: 'bg-neutral-800 text-text-high-contrast ',
    blue: 'bg-blue-700 text-text-high-contrast',
    red: 'bg-red-700 text-text-high-contrast',
    orange: 'bg-orange-700 text-text-high-contrast',
    yellow: 'bg-yellow-700 text-text-high-contrast-dark',
    green: 'bg-green-700 text-text-high-contrast',
    teal: 'bg-teal-700 text-text-high-contrast',
    cyan: 'bg-cyan-700 text-text-high-contrast',
    purple: 'bg-purple-700 text-text-high-contrast',
    pink: 'bg-pink-700 text-text-high-contrast',
    lime: 'bg-lime-700 text-text-high-contrast',
    magic:
      'text-text-high-contrast-dark [background:linear-gradient(to_right,var(--cl-gradient-magic))]'
  },
  actionSubtle: {
    neutral: '',
    neutralStrong: '',
    blue: '',
    red: '',
    orange: '',
    yellow: '',
    green: '',
    teal: '',
    cyan: '',
    purple: '',
    pink: '',
    lime: '',
    magic: ''
  }
} as const satisfies Record<BadgeVariant, Record<BadgeHue, string>>

const iconFillClasses = tw({
  subtle: {
    neutral: 'text-neutral-600',
    neutralStrong: 'text-neutral-700',
    blue: 'text-blue-600',
    red: 'text-red-600',
    orange: 'text-orange-600',
    yellow: 'text-yellow-700',
    green: 'text-green-600',
    teal: 'text-teal-600',
    cyan: 'text-cyan-600',
    purple: 'text-purple-600',
    pink: 'text-pink-600',
    lime: 'text-lime-600',
    magic: 'text-text-faint'
  },
  outline: {
    neutral: 'text-neutral-700',
    neutralStrong: 'text-neutral-800',
    blue: 'text-blue-700',
    red: 'text-red-700',
    orange: 'text-orange-700',
    yellow: 'text-yellow-800',
    green: 'text-green-700',
    teal: 'text-teal-700',
    cyan: 'text-cyan-700',
    purple: 'text-purple-700',
    pink: 'text-pink-700',
    lime: 'text-lime-700',
    magic: 'text-text-primary'
  },
  filled: {
    neutral: 'text-text-high-contrast',
    neutralStrong: 'text-text-high-contrast',
    blue: 'text-text-high-contrast',
    red: 'text-text-high-contrast',
    orange: 'text-text-high-contrast',
    yellow: 'text-text-high-contrast-dark',
    green: 'text-text-high-contrast',
    teal: 'text-text-high-contrast',
    cyan: 'text-text-high-contrast',
    purple: 'text-text-high-contrast',
    pink: 'text-text-high-contrast',
    lime: 'text-text-high-contrast',
    magic: 'text-text-high-contrast-dark'
  }
} as const satisfies Record<
  Exclude<BadgeVariant, 'actionSubtle'>,
  Record<BadgeHue, string>
>)

const iconSizes = {
  small: 11,
  medium: 14,
  large: 16
} as const satisfies Record<BadgeSize, number>

const BadgeBase = (
  {
    className,
    children,
    variant = 'subtle',
    hue = 'neutral',
    round = 'medium',
    size = 'medium',
    icon,
    asChild = false,
    ...props
  }: BadgeProps,
  ref: ForwardedRef<HTMLDivElement>
) => {
  const Comp = asChild ? Slot : 'div'
  if (hue === 'magic' && variant === 'actionSubtle') {
    console.error('ActionSubtle badges cannot have magic hue')
  }
  let iconClone: ReturnType<typeof cloneElement> | undefined
  if (icon) {
    iconClone = cloneElement(icon, {
      size: iconSizes[size]
    })
  }
  const ret = (
    <Comp
      ref={ref}
      className={cn(
        'relative flex items-center text-black transition-colors focus-visible:ring-2 focus-visible:ring-focus',
        variant !== 'filled' && 'outline outline-1',
        variants({ variant, round, size }),
        variantHueClasses[variant][hue],
        className
      )}
      {...props}
    >
      <SlotChild asChild={!!asChild} child={children}>
        {child => (
          <>
            {hue === 'magic' &&
              (variant === 'outline' || variant === 'subtle') && (
                <span
                  className={cn(
                    'absolute inset-px block bg-surface-1',
                    round === 'full' && 'rounded-full',
                    round === 'small' &&
                      'rounded-[calc(theme(borderRadius.1)-1px)]',
                    round === 'medium' &&
                      'rounded-[calc(theme(borderRadius.2)-1px)]'
                  )}
                />
              )}
            {variant === 'actionSubtle' ? (
              <StatusDot hue={hue === 'magic' ? 'neutral' : hue} />
            ) : iconClone ? (
              <span
                className={cn('relative block', iconFillClasses[variant][hue])}
              >
                {iconClone}
              </span>
            ) : null}
            <span className="relative block">{child}</span>
          </>
        )}
      </SlotChild>
    </Comp>
  )
  return ret
}

/**
 * Badge component
 */
const Badge = memo(forwardRef(BadgeBase))
Badge.displayName = 'Badge'

export type { BadgeHue, BadgeProps }
export { Badge }
