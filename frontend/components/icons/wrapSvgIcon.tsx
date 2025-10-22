import type {
  ComponentPropsWithoutRef,
  ComponentPropsWithRef,
  ForwardedRef,
  ReactNode
} from 'react'
import { forwardRef, memo } from 'react'

import { SvgBox } from '../design-system-components/SvgBox'

export const wrapSvgIcon = (
  node: ReactNode,
  defaultProps: Omit<ComponentPropsWithoutRef<typeof SvgBox>, 'children'> = {},
  displayName: string
) => {
  const Icon = memo(
    forwardRef(
      (
        props: Omit<
          ComponentPropsWithRef<typeof SvgBox>,
          'children' | 'viewBoxSize'
        >,
        ref: ForwardedRef<SVGSVGElement>
      ) => {
        return (
          <SvgBox ref={ref} {...defaultProps} {...props}>
            {node}
          </SvgBox>
        )
      }
    )
  )
  if (displayName) {
    Icon.displayName = displayName
  }
  return Icon
}
