import type { Alignment, FloatingContext, Side } from '@floating-ui/react'
import type {
  ComponentPropsWithoutRef,
  ComponentPropsWithRef,
  ForwardedRef
} from 'react'
import { forwardRef, memo, type JSX } from 'react'

const TOOLTIP_ARROW_HEIGHT = 3
const TOOLTIP_ARROW_WIDTH = 12
const TOOLTIP_ARROW_BOX_HEIGHT = 12

const getSideAlignment = (placement: string) => {
  const [side, alignment] = placement.split('-') as [Side, Alignment]
  return { side, alignment }
}

const TooltipArrowSvg = memo((props: ComponentPropsWithoutRef<'svg'>) => {
  return (
    <svg viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg" {...props}>
      <path
        d="m1.17157 4v1l4.82843 4 4.82843-4v-.997864z"
        className="fill-inherit transition-[fill] duration-100"
      />
      <path
        d="m6 9.580078c-.562012 0-.961426-.334473-1.212891-.585938l-2.34668-2.34668c-.573242-.583984-.76416-.647461-1.27002-.647461-.276367 0-.5-.223633-.5-.5s.223633-.5.5-.5c.817871 0 1.261719.211914 1.980469.943848l2.343262 2.343262c.13623.13623.317383.292969.505859.292969s.369629-.156738.505859-.292969l2.34668-2.34668c.714844-.728516 1.15918-.94043 1.977539-.94043.276367 0 .5.223633.5.5s-.223633.5-.5.5c-.506836 0-.697266.063477-1.267578.644043l-2.349609 2.350098c-.251465.251465-.650879.585938-1.212891.585938z"
        className="fill-tooltip-border transition-[fill] duration-100"
      />
    </svg>
  )
})

type TooltipArrowProps = ComponentPropsWithRef<'div'> & {
  // Omit the original `refs` property from the context to avoid issues with
  // generics: https://github.com/floating-ui/floating-ui/issues/2483
  /**
   * The floating context.
   */
  context: Omit<FloatingContext, 'refs'> & { refs: any }
}

/**
 * Renders a pointing arrow triangle.
 */
const TooltipArrow = forwardRef(function FloatingArrow(
  props: TooltipArrowProps,
  ref: ForwardedRef<HTMLDivElement>
): JSX.Element | null {
  const {
    context: {
      placement,
      elements: { floating },
      middlewareData: { arrow }
    },
    style: { transform, ...restStyle } = {},
    ...rest
  } = props

  if (!floating) {
    return null
  }

  const { side } = getSideAlignment(placement)

  const rotation = {
    top: '',
    left: 'rotate(-90deg)',
    bottom: 'rotate(180deg)',
    right: 'rotate(90deg)'
  }[side]

  return (
    <div
      {...rest}
      aria-hidden
      ref={ref}
      style={{
        width: TOOLTIP_ARROW_BOX_HEIGHT,
        height: TOOLTIP_ARROW_BOX_HEIGHT,
        transformOrigin: '',
        position: 'absolute',
        pointerEvents: 'none',
        left: arrow?.x != null ? arrow.x : '',
        top: arrow?.y != null ? arrow.y : '',
        [side]: '100%',
        transform: `${rotation} ${transform ?? ''}`,
        ...restStyle
      }}
    >
      <TooltipArrowSvg
        style={{ position: 'absolute', transform: 'translateY(-50%)' }}
      />
    </div>
  )
})

export {
  getSideAlignment,
  TOOLTIP_ARROW_BOX_HEIGHT,
  TOOLTIP_ARROW_HEIGHT,
  TOOLTIP_ARROW_WIDTH,
  TooltipArrow
}
export type { TooltipArrowProps }
