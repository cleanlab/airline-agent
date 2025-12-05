import { cn } from '@cleanlab/design-system/utils'
import Link from 'next/link'

import { getChatPath } from '@/lib/consts'

import { NewChatButton } from './new-chat-button'
import { ThemeToggle } from './theme-toggle'

export const HeaderButtons = async ({
  variant = 'horizontal',
  className
}: {
  variant: 'horizontal' | 'vertical'
  className?: string
}) => {
  const hFlexClass = cn(
    'flex',
    variant === 'horizontal' && 'gap-5',
    variant === 'vertical' && 'gap-4 justify-center'
  )

  return (
    <div
      className={cn(
        hFlexClass,
        'flex-row-reverse items-center',
        variant === 'vertical' ? 'flex-col' : 'justify-start',
        className
      )}
    >
      <div className={hFlexClass}>
        <ThemeToggle />
        <NewChatButton asChild>
          <Link href={getChatPath()} />
        </NewChatButton>
      </div>
    </div>
  )
}
