'use client'

import type {
  ForwardedRef,
  HTMLAttributes,
  ReactElement,
  ReactNode
} from 'react'
import { cloneElement, forwardRef, memo } from 'react'

import {
  IconCaution,
  IconCheckCircleFilled,
  IconInfo,
  IconWarning
} from '../icons'
import { cn, tv } from '@/lib/utils/tailwindUtils'

type MessageInfoStatus = 'default' | 'info' | 'success' | 'warning' | 'caution'

type MessageInfoProps = {
  heading?: ReactNode
  description?: ReactNode
  status: MessageInfoStatus
  actions?: ReactNode
  icon?: ReactElement<{ size?: number }> | null | undefined
} & HTMLAttributes<HTMLDivElement>

const variants = tv(
  {
    slots: {
      base: 'flex min-h-[42px] w-max min-w-0 max-w-full flex-row flex-wrap items-center justify-between gap-6 rounded-3 bg-surface-1 px-6 py-4 align-middle outline outline-1 -outline-offset-1 outline-border-1',
      heading: 'type-body-200-medium text-text-primary',
      description: 'type-body-100 text-text-faint',
      icon: 'shrink-0 pt-[3px]'
    },
    variants: {
      status: {
        default: {
          base: 'outline-border-1',
          heading: 'text-text-strong',
          icon: 'text-text-strong'
        },
        info: {
          base: 'outline-blue-600',
          heading: 'text-blue-600',
          icon: 'text-blue-600'
        },
        success: {
          base: 'outline-green-700',
          heading: 'text-green-700',
          icon: 'text-green-700'
        },
        caution: {
          base: 'outline-yellow-800',
          heading: 'text-yellow-800',
          icon: 'text-yellow-800'
        },
        warning: {
          base: 'outline-red-600',
          heading: 'text-red-600',
          icon: 'text-red-600'
        }
      }
    }
  },
  { responsiveVariants: ['md'] }
)

const statusToIcon = {
  default: <IconWarning />,
  info: <IconInfo />,
  success: <IconCheckCircleFilled />,
  caution: <IconCaution />,
  warning: <IconWarning />
} as const satisfies Record<MessageInfoStatus, ReactNode>

const MessageInfoBase = (
  {
    heading,
    description,
    actions,
    status,
    icon: iconProp,
    className,
    ...props
  }: MessageInfoProps,
  ref: ForwardedRef<HTMLDivElement>
) => {
  const {
    base: baseClass,
    heading: headingClass,
    description: descriptionClass,
    icon: iconClass
  } = variants({ status })
  let icon = iconProp
  if (status !== 'default') {
    icon = statusToIcon[status] || undefined
  }
  icon = icon && cloneElement(icon, { size: 16 })

  return (
    <div ref={ref} className={cn(baseClass(), className)} {...props}>
      <div
        className={cn(
          'flex w-full flex-row gap-x-4',
          description ? 'items-start' : 'items-center'
        )}
      >
        <div className="flex items-start gap-x-4">
          {icon && <div className={iconClass()}>{icon}</div>}
          <div className="flex flex-wrap items-start gap-4">
            <div className="flex min-w-min max-w-max shrink grow basis-[220px] flex-col gap-1 pt-1">
              {heading && <h2 className={headingClass()}>{heading}</h2>}
              {description && (
                <p className={descriptionClass()}>{description}</p>
              )}
            </div>
            {actions && (
              <div className="flex flex-wrap items-center gap-2 self-center">
                {actions}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const MessageInfo = memo(forwardRef(MessageInfoBase))

export type { MessageInfoStatus }
export { MessageInfo }
