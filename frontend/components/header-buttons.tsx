import { cn } from '@/lib/utils/tailwindUtils'
import { ThemeToggle } from './theme-toggle'
import { NewChatButton } from './new-chat-button'
import { getChatPath } from '@/lib/consts'
import Link from 'next/link'

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
