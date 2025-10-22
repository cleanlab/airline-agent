import type { ReactNode } from 'react'
import { cn } from '@/lib/utils/tailwindUtils'

export const AssistantMetadataSection = ({
  heading,
  className,
  children
}: {
  heading: ReactNode
  className?: string
  children: ReactNode
}) => (
  <div className={cn('overflow-hidden', className)}>
    <h6 className="type-body-100 whitespace-nowrap text-text-disabled">
      {heading}
    </h6>
    <div className="type-body-100 text-text-primary">{children}</div>
  </div>
)
