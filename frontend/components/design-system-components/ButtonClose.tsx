'use client'
import type { ForwardedRef } from 'react'
import { forwardRef, memo } from 'react'
import { type Except } from 'type-fest'

import { IconX } from '@/components/icons'
import { IconFrameButton } from './IconFrameButton'
import type { IconButtonProps, IconFrameRootSize } from './IconFrameRoot'
import { IconFrameRoot } from './IconFrameRoot'

type ButtonCloseSize = Extract<
  IconFrameRootSize,
  'xxSmall' | 'xSmall' | 'small' | 'medium' | 'large'
>

const ButtonCloseBase = (
  {
    className,
    size = 'medium',
    ...props
  }: Except<IconButtonProps, 'variant' | 'icon' | 'size'> & {
    size?: ButtonCloseSize
  },
  ref: ForwardedRef<HTMLButtonElement>
) => {
  return (
    <IconFrameRoot
      ref={ref}
      className={className}
      variant="closeButton"
      size={size}
      icon={<IconX />}
      clickable={true}
      {...props}
    />
  )
}

/**
 * ButtonClose component
 */
const ButtonClose = memo(forwardRef(ButtonCloseBase))
IconFrameButton.displayName = 'ButtonClose'

export { ButtonClose }
