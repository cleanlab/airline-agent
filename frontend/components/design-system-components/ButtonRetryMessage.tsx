'use client'

import type { ComponentPropsWithoutRef } from 'react'

import { Button } from './Button'

import { cn } from '@/lib/utils/tailwindUtils'
import { IconRefresh } from '../icons'

export function ButtonRetryMessage({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof Button>) {
  if (props.asChild) {
    return (
      <Button
        className={cn(className)}
        iconStart={<IconRefresh />}
        size="xSmall"
        variant="secondaryFaint"
        {...props}
      />
    )
  }
  return (
    <Button
      className={cn(className)}
      iconStart={<IconRefresh />}
      size="xSmall"
      variant="secondaryFaint"
      {...props}
    >
      {props.children || 'Retry'}
    </Button>
  )
}
