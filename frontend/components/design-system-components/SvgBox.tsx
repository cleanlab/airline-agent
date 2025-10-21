'use client'

import type { ComponentPropsWithoutRef, ForwardedRef } from 'react'
import { forwardRef } from 'react'

import { DEFAULT_ICON_SIZE, DEFAULT_ICON_VIEWBOX_SIZE } from '../icons/iconConsts'

type SvgBoxProps = {
  className?: string
  size?: number
  viewBoxSize?: number
} & ComponentPropsWithoutRef<'svg'>

export const SvgBox = forwardRef(
  (
    { size = DEFAULT_ICON_SIZE, viewBoxSize = DEFAULT_ICON_VIEWBOX_SIZE, ...props }: SvgBoxProps,
    ref: ForwardedRef<SVGSVGElement>
  ) => {
    return (
      <svg
        ref={ref}
        fill="none"
        stroke="currentColor"
        viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
        height={size}
        width={size}
        xmlns="http://www.w3.org/2000/svg"
        {...props}
      />
    )
  }
)
