'use client'

import { Slot as SlotPrimitive } from 'radix-ui'
import type {
  ButtonHTMLAttributes,
  ForwardedRef,
  HTMLAttributes,
  ReactElement,
  ReactNode
} from 'react'
import { cloneElement, forwardRef, useMemo } from 'react'
import type { SetRequired } from 'type-fest'

import type { AsChildProps } from '@/lib/utils/AsChildProps'
import { cn, tv } from '@/lib/utils/tailwindUtils'
import { Tooltip } from './Tooltip'

const Slot = SlotPrimitive.Root
const Slottable = SlotPrimitive.Slottable

type IconFrameRootVariant =
  | 'level0'
  | 'level1'
  | 'level2'
  | 'outline'
  | 'iconOnly'
  | 'closeButton'
type IconFrameVariant = Exclude<IconFrameRootVariant, 'closeButton'>
type IconFrameRootSize =
  | 'xxSmall'
  | 'xSmall'
  | 'small'
  | 'medium'
  | 'large'
  | 'xLarge'
type IconFrameSize = Exclude<IconFrameRootSize, 'xxSmall'>

type IconFrameRootProps = {
  className?: string
  icon: ReactElement<{ size?: number }>
  text?: string
  variant: IconFrameRootVariant
  size: IconFrameRootSize
  asChild?: boolean
  clickable?: boolean
  children?: ReactNode
  disabled?: boolean
  tooltipContent?: ReactNode
}
type LimitedProps = Omit<
  IconFrameRootProps,
  'clickable' | 'children' | 'variant'
> & {
  variant: IconFrameVariant
}
type IconFrameProps = LimitedProps &
  AsChildProps<HTMLAttributes<HTMLDivElement>>
type IconButtonProps = LimitedProps &
  AsChildProps<
    SetRequired<ButtonHTMLAttributes<HTMLButtonElement>, 'aria-label'>
  >

const iconVariants = tv({
  base: 'flex items-center justify-center',
  variants: {
    size: {
      xxSmall: 'size-7',
      xSmall: 'size-8',
      small: 'size-9',
      medium: 'size-[36px]',
      large: 'size-10',
      xLarge: 'size-11'
    }
  }
})

const textVariants = tv({
  base: 'w-max text-text-primary',
  variants: {
    size: {
      xxSmall: 'type-badge-sm pl-3 text-[10px]',
      xSmall: 'type-badge-sm pl-4 pr-1',
      small: 'type-badge-md pl-[10px] pr-1',
      medium: 'type-badge-lg pl-5 pr-1',
      large: 'type-badge-lg pl-5 pr-1',
      xLarge: 'type-badge-lg pl-5 pr-1 text-[16px]'
    }
  }
})

const frameVariants = tv({
  base: 'relative flex shrink-0 items-center justify-center outline outline-1 -outline-offset-1 focus-visible:outline-1',
  variants: {
    // Main variant
    variant: {
      level0: 'bg-surface-0 text-text-faint outline-border-0',
      level1: 'bg-surface-1 text-text-faint outline-border-1',
      level2: 'bg-surface-2 text-text-faint outline-border-2',
      outline: 'bg-surface-0 text-text-primary outline-border-1',
      iconOnly: 'bg-transparent text-text-primary outline-none',
      closeButton: 'bg-transparent text-text-primary outline-none',
      sidebar: 'bg-surface-0 text-text-primary outline-border-1',
      sidebarGlobal: 'bg-transparent text-text-primary outline-none'
    },
    // Additional options
    clickable: {
      true: 'cursor-pointer focus-visible:outline-blue-700 focus-visible:ring-2 focus-visible:ring-focus'
    },
    size: {
      xxSmall: 'rounded-1',
      xSmall: 'rounded-1',
      small: 'rounded-2',
      medium: 'rounded-2',
      large: 'rounded-2',
      xLarge: 'rounded-2'
    },
    disabled: {
      true: 'cursor-not-allowed',
      false: ''
    }
  },
  compoundVariants: [
    {
      size: ['xxSmall', 'xSmall', 'small', 'medium', 'large', 'xLarge'],
      variant: 'closeButton',
      class: 'rounded-1'
    },
    { clickable: true, class: 'shadow-elev-0' },
    {
      clickable: true,
      variant: 'level0',
      disabled: false,
      class: 'hover:bg-surface-0-hover active:bg-surface-0-active'
    },
    {
      clickable: true,
      variant: 'level1',
      disabled: false,
      class: 'hover:bg-surface-1-hover active:bg-surface-1-active'
    },
    {
      clickable: true,
      variant: 'level2',
      disabled: false,
      class: 'hover:bg-surface-2-hover active:bg-surface-2-active'
    },
    {
      clickable: true,
      variant: 'outline',
      disabled: false,
      class: 'hover:bg-surface-0-hover active:bg-surface-0-active'
    },
    {
      clickable: true,
      variant: ['iconOnly'],
      disabled: false,
      class:
        'bg-transparent hover:bg-surface-0-hover active:bg-surface-0-active'
    },
    {
      clickable: true,
      variant: ['closeButton'],
      disabled: false,
      class:
        'bg-transparent hover:bg-surface-2-hover active:bg-surface-2-active'
    },
    {
      clickable: true,
      variant: 'sidebar',
      disabled: false,
      class: 'hover:bg-surface-0-hover active:bg-surface-0-active'
    },
    {
      clickable: true,
      variant: 'sidebarGlobal',
      disabled: false,
      class: 'hover:bg-surface-1-hover active:bg-surface-1-active'
    },
    {
      variant: ['level0', 'level1', 'level2', 'outline', 'sidebar'],
      disabled: true,
      class: 'bg-surface-disabled text-text-disabled outline-border-2'
    },
    {
      variant: ['closeButton', 'iconOnly', 'sidebarGlobal'],
      disabled: true,
      class: 'bg-transparent text-text-disabled'
    }
  ]
})

const iconSizes = {
  xxSmall: 12,
  xSmall: 12,
  small: 16,
  medium: 20,
  large: 24,
  xLarge: 32
} as const satisfies Record<IconFrameRootSize, number>

const IconFrameRootBase = (
  {
    className,
    variant,
    size,
    icon,
    text,
    asChild = false,
    clickable,
    children,
    tooltipContent,
    ...props
  }: IconFrameRootProps,
  ref: ForwardedRef<any>
) => {
  const elementType = clickable ? 'button' : 'div'
  const Comp = asChild ? Slot : elementType
  let iconClone: ReturnType<typeof cloneElement> | undefined
  if (icon) {
    iconClone = cloneElement(icon, {
      size: variant === 'closeButton' ? 16 : iconSizes[size]
    })
  }
  const classN = useMemo(
    () =>
      cn(
        frameVariants({ variant, size, clickable, disabled: !!props.disabled }),
        className
      ),
    [className, clickable, size, variant, props.disabled]
  )
  const content = (
    <Comp
      ref={ref}
      className={classN}
      {...(clickable ? { type: 'button' } : {})}
      {...props}
    >
      <Slottable>{children}</Slottable>
      {text && <span className={textVariants({ size })}>{text}</span>}
      <span className={iconVariants({ size })}>{iconClone}</span>
    </Comp>
  )

  if (tooltipContent) {
    return <Tooltip content={tooltipContent}>{content}</Tooltip>
  }
  return content
}
const IconFrameRoot = forwardRef(IconFrameRootBase)

export type {
  IconButtonProps,
  IconFrameProps,
  IconFrameRootProps,
  IconFrameRootSize,
  IconFrameSize,
  IconFrameVariant
}
export { frameVariants, IconFrameRoot }
