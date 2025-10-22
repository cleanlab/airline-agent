import type {
  ComponentProps,
  ComponentType,
  ForwardedRef,
  ReactElement
} from 'react'
import { Children, cloneElement, forwardRef, memo } from 'react'

import { DEFAULT_ICON_SIZE, ICON_SIZES } from './iconConsts'
import { cn, tw } from '@/lib/utils/tailwindUtils'

type IconSize = (typeof ICON_SIZES)[number]
// TODO: Check with design team to determine these final values
const classes = tw({
  12: '[&>svg]:stroke-[1.8px]',
  14: '[&>svg]:stroke-[1.7px]',
  16: '[&>svg]:stroke-[1.65px]',
  24: '[&>svg]:stroke-[1.5px]',
  32: '[&>svg]:stroke-[1.25px]'
} as const satisfies Record<IconSize, string>)

const findNearestSize = (num: number) => {
  for (let i = 1; i < ICON_SIZES.length; i++) {
    if (num < ICON_SIZES[i]) {
      return ICON_SIZES[i - 1]
    }
  }
  return ICON_SIZES[ICON_SIZES.length - 1]
}

type IconProps = Omit<ComponentProps<'div'>, 'children'> & { size?: number }

const WrapperBase = (
  {
    size = DEFAULT_ICON_SIZE,
    className,
    children,
    ...props
  }: IconProps & {
    children: ReactElement<{ size?: number }>
  },
  ref: any
) => {
  const child = Children.only(children)
  if (!child) {
    return null
  }
  const clone = cloneElement(child, { size })
  const nearestSize = findNearestSize(size)

  return (
    <span
      ref={ref}
      className={cn(
        'block [&>svg]:block [&>svg]:align-middle',
        classes[nearestSize],
        className
      )}
      role="img"
      {...props}
    >
      {clone}
    </span>
  )
}
const Wrapper = forwardRef(WrapperBase)

export const wrapFeatherIcon = (Icon: ComponentType, displayName: string) => {
  const baseComponent = (
    { style, ...props }: IconProps,
    ref: ForwardedRef<HTMLDivElement>
  ) => (
    <Wrapper
      ref={ref}
      style={{
        width: props?.size ?? DEFAULT_ICON_SIZE,
        height: props?.size ?? DEFAULT_ICON_SIZE,
        ...style
      }}
      {...props}
    >
      <Icon />
    </Wrapper>
  )
  const component = memo(forwardRef(baseComponent))
  component.displayName = displayName
  return component
}
