import { type ComponentProps } from 'react'

import { cn, tw } from '@/lib/utils/tailwindUtils'
import type { BadgeHue } from './Badge'

type StatusHue = Exclude<BadgeHue, 'magic'>
const statusDotClasses = tw({
  neutral: 'bg-neutral-500',
  neutralStrong: 'bg-neutral-600',
  blue: 'bg-blue-500',
  red: 'bg-red-500',
  orange: 'bg-orange-500',
  yellow: 'bg-yellow-500',
  green: 'bg-green-500',
  teal: 'bg-teal-500',
  cyan: 'bg-cyan-500',
  purple: 'bg-purple-500',
  pink: 'bg-pink-500',
  lime: 'bg-lime-500'
} as const satisfies Record<StatusHue, string>)
/**
 * Colored dot for action badges
 * @param hue - Color of the dot
 */

export const StatusDot = ({
  className,
  hue
}: ComponentProps<'div'> & { hue: StatusHue }) => {
  return (
    <div className={cn('relative p-[3px]', className)}>
      <div
        className={cn('rounded-full p-1 outline outline-1 outline-border-1')}
      >
        <div className={cn('size-3 rounded-full', statusDotClasses[hue])} />
      </div>
    </div>
  )
}
