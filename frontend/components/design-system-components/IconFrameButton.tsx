'use client'

import type { ForwardedRef } from 'react'
import { forwardRef, memo } from 'react'

import type { IconButtonProps } from './IconFrameRoot'
import { IconFrameRoot } from './IconFrameRoot'

const IconButtonBase = (props: IconButtonProps, ref: ForwardedRef<HTMLButtonElement>) => {
  return <IconFrameRoot ref={ref} {...props} clickable={true} />
}

/**
 * IconFrameButton component
 */
const IconFrameButton = memo(forwardRef(IconButtonBase))
IconFrameButton.displayName = 'IconFrameButton'

export type { IconButtonProps as IconFrameButtonProps }
export { IconFrameButton }
