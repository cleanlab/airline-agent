'use client'

import { Slot as SlotPrimitive } from 'radix-ui'
import type { ButtonHTMLAttributes, ForwardedRef, ReactElement } from 'react'
import { cloneElement, forwardRef, memo, useMemo } from 'react'
import type { UnionToIntersection } from 'type-fest'

import type { AsChildProps } from '@/lib/utils/AsChildProps'
import { cn, tv } from '@/lib/utils/tailwindUtils'
import { Kbd } from './Kbd'
import { SlotChild } from './SlotChild'

const Slot = SlotPrimitive.Root

type ButtonVariant =
  | 'primary'
  | 'primaryFaint'
  | 'secondary'
  | 'secondaryStrong'
  | 'secondaryFaint'
  | 'highContrast'
  | 'critical'

type ButtonSize = 'xSmall' | 'small' | 'medium' | 'large'

type ButtonPropsCommon = AsChildProps<
  ButtonHTMLAttributes<HTMLButtonElement>
> & {
  contentClassName?: string
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: ButtonHTMLAttributes<HTMLButtonElement>['disabled']
  isTruncatable?: boolean
}

type ButtonProps = ButtonPropsUnion & ButtonPropsCommon
type ButtonPropsUnion =
  /* Weird bug in prettier or eslint ¯\_(ツ)_/¯ that's fixed by adding a comment */
  /* Gets stuck in a loop of switching to/from single/multi-line */
  | {
      iconStart?: ReactElement<{ size?: number }>
    }
  | { iconEnd?: ReactElement<{ size?: number }> }
  | { shortcutKey?: string }

// For internal use only
type ButtonPropsAll = ButtonPropsCommon & UnionToIntersection<ButtonPropsUnion>

const variants = tv({
  base: 'group/button relative flex shrink-0 items-center rounded-2 outline outline-1 -outline-offset-1 transition-colors focus-visible:outline-1 focus-visible:ring-2 focus-visible:ring-focus disabled:cursor-not-allowed disabled:bg-surface-disabled disabled:text-text-disabled disabled:outline-border-2',
  variants: {
    // Main variant
    variant: {
      primary:
        'bg-button-primary-bg text-button-primary-text outline-button-primary-border hover:bg-button-primary-bg-hover hover:outline-button-primary-border-hover focus-visible:outline-button-primary-border-focus active:bg-button-primary-bg-active group-hover/button:bg-button-primary-bg-hover group-hover/button:outline-button-primary-border-hover',
      primaryFaint:
        'bg-surface-0 text-blue-600 outline-blue-200 hover:bg-blue-50 focus-visible:outline-blue-700 active:bg-blue-200 group-hover/button:bg-blue-50',
      secondary:
        'bg-surface-1 text-text-primary outline-border-1 hover:bg-surface-1-hover focus-visible:outline-blue-700 active:bg-surface-1-active group-hover/button:bg-surface-1-hover',
      secondaryStrong:
        'bg-surface-2 text-text-strong outline-border-2 hover:bg-surface-2-hover focus-visible:outline-blue-700 active:bg-surface-2-active group-hover/button:bg-surface-2-hover',
      secondaryFaint:
        'bg-surface-0 text-text-primary outline-border-1 hover:bg-surface-0-hover focus-visible:outline-blue-700 active:bg-surface-0-active group-hover/button:bg-surface-0-hover',
      highContrast:
        'bg-surface-high-contrast text-text-high-contrast outline-surface-high-contrast hover:bg-neutral-800 focus-visible:outline-blue-50 active:bg-neutral-700 group-hover/button:hover:bg-neutral-800',
      critical:
        'bg-red-50 text-red-700 outline-red-600 hover:bg-red-600 hover:text-red-50 hover:outline-red-700 focus-visible:outline-red-700 active:bg-red-600 active:text-red-50 group-hover/button:bg-red-600 group-hover/button:text-red-50 group-hover/button:outline-red-700'
    },
    // Additional options
    size: {
      xSmall: 'type-button-xs min-h-8 px-4',
      small: 'type-button-sm min-h-9 px-5 py-3',
      medium: 'type-button-md min-h-[36px] px-6 py-4',
      large: 'type-button-lg min-h-10 px-7 py-4',
      none: ''
    }
  },
  compoundVariants: [
    { variant: ['primary', 'primaryFaint'], class: '' },
    { variant: ['secondary', 'secondaryFaint', 'secondaryStrong'], class: '' }
  ]
})

const iconSizes = {
  xSmall: 12,
  small: 16,
  medium: 16,
  large: 16
} as const satisfies Record<ButtonSize, number>

const getKbdVariant = (
  buttonVariant: ButtonVariant,
  disabled: boolean | undefined
) => {
  if (disabled) return 'outline'
  switch (buttonVariant) {
    case 'highContrast':
      return 'buttonHighContrast'
    case 'primary':
      return 'buttonPrimary'
    default:
      return 'outline'
  }
}

const getKbdSize = (buttonSize: ButtonSize) => {
  switch (buttonSize) {
    case 'large':
      return 'medium'
    case 'xSmall':
      return 'xSmall'
    default:
      return 'small'
  }
}

const ButtonBase = (
  allProps: ButtonProps,
  ref: ForwardedRef<HTMLButtonElement>
) => {
  const {
    className,
    contentClassName,
    children,
    variant = 'primary',
    size = 'medium',
    iconEnd,
    iconStart,
    shortcutKey,
    disabled,
    isTruncatable = false,
    asChild = false,
    ...props
  } = allProps as ButtonPropsAll

  const Comp = asChild ? Slot : 'button'
  let iconStartClone: ReturnType<typeof cloneElement> | undefined
  let iconEndClone: ReturnType<typeof cloneElement> | undefined
  if (iconStart) {
    iconStartClone = cloneElement(iconStart, {
      size: iconSizes[size]
    })
  } else if (iconEnd) {
    iconEndClone = cloneElement(iconEnd, {
      size: iconSizes[size]
    })
  }
  const classN = useMemo(
    () => cn(variants({ variant, size }), className),
    [className, size, variant]
  )
  const ret = (
    <Comp
      ref={ref}
      className={classN}
      disabled={disabled}
      type={allProps.asChild ? undefined : (allProps.type ?? 'button')}
      {...props}
    >
      <SlotChild asChild={!!asChild} child={children}>
        {child => (
          <>
            {iconStartClone && (
              <span
                className={cn('relative -ms-1 block pe-2', {
                  'pe-3': size === 'medium' || size === 'large'
                })}
              >
                {iconStartClone}
              </span>
            )}
            <span
              className={cn(
                'relative block',
                isTruncatable && 'truncate',
                contentClassName
              )}
            >
              {child}
            </span>
            {iconEndClone && (
              <span
                className={cn('p relative -me-1 block ps-2', {
                  'ps-3': size === 'medium' || size === 'large'
                })}
              >
                {iconEndClone}
              </span>
            )}
            {shortcutKey && !iconEnd && (
              <span
                className={cn(
                  'relative block ps-3',
                  (size === 'large' || size === 'medium') && 'ps-4'
                )}
              >
                <Kbd
                  size={getKbdSize(size)}
                  className={cn(
                    'relative',
                    variant === 'critical' && 'group-hover/button:text-red-50'
                  )}
                  variant={getKbdVariant(variant, disabled)}
                  disabled={disabled}
                >
                  {shortcutKey}
                </Kbd>
              </span>
            )}
          </>
        )}
      </SlotChild>
    </Comp>
  )
  return ret
}

/**
 * Button component
 */
const Button = memo(forwardRef(ButtonBase))
Button.displayName = 'Button'

export type { ButtonProps, ButtonPropsAll, ButtonPropsCommon, ButtonPropsUnion }
export { Button, variants as buttonVariants }
