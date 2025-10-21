'use client'

import Link from 'next/link'
import { useMessagesStore } from '@/providers/messages-store-provider'
import { motion } from 'motion/react'
import { getChatPath } from '@/lib/consts'
import { useLocalStorage } from '@/lib/hooks/use-local-storage'
import { truncateString } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'
import type { HistoryThread } from '../stores/history-thread-store'
import { Tooltip } from './design-system-components/Tooltip'
import { cn } from '@/lib/utils/tailwindUtils'

interface SidebarItemProps {
  index: number
  thread: HistoryThread
  children: React.ReactNode
}

export function SidebarItem({ index, thread, children }: SidebarItemProps) {
  const currentThread = useMessagesStore(state => state.currentThread)

  const isActive =
    (thread.localThreadId &&
      currentThread?.localThreadId &&
      thread.localThreadId === currentThread?.localThreadId) ||
    thread.thread?.id === currentThread?.threadId
  const [newThreadId, setNewThreadId] = useLocalStorage('newThreadId', null)
  const shouldAnimate = index === 0 && isActive && newThreadId

  const threadPath = getChatPath(thread.thread?.id)

  if (!threadPath) return null

  return (
    <motion.div
      className="group relative h-9"
      variants={{
        initial: {
          height: 0,
          opacity: 0
        },
        animate: {
          height: 'auto',
          opacity: 1
        }
      }}
      initial={shouldAnimate ? 'initial' : undefined}
      animate={shouldAnimate ? 'animate' : undefined}
      transition={{
        duration: 0.25,
        ease: 'easeIn'
      }}
    >
      <Tooltip content={truncateString(thread.title, 75)}>
        <Link
          href={threadPath}
          className={cn(
            buttonVariants({ variant: 'ghost' }),
            'group type-body-100 flex h-9 w-full items-center justify-start bg-transparent px-4 text-text-primary transition-colors group-hover:bg-surface-0-hover group-hover:pr-[38px]',
            isActive && 'bg-surface-0-active group-hover:bg-surface-0-active'
          )}
          data-id={thread.thread?.id}
          data-local-id={thread.localThreadId}
        >
          <div className="relative max-h-9 flex-1 select-none overflow-hidden text-ellipsis break-all">
            <span>
              {shouldAnimate ? (
                thread.title.split('').map((character, index) => (
                  <motion.span
                    key={thread.localThreadId || thread.thread?.id}
                    variants={{
                      initial: {
                        opacity: 0,
                        x: -100
                      },
                      animate: {
                        opacity: 1,
                        x: 0
                      }
                    }}
                    initial={shouldAnimate ? 'initial' : undefined}
                    animate={shouldAnimate ? 'animate' : undefined}
                    transition={{
                      duration: 0.25,
                      ease: 'easeIn',
                      delay: index * 0.05,
                      staggerChildren: 0.05
                    }}
                    onAnimationComplete={() => {
                      if (index === thread.title.length - 1) {
                        setNewThreadId(null)
                      }
                    }}
                  >
                    {character}
                  </motion.span>
                ))
              ) : (
                <span>{thread.title}</span>
              )}
            </span>
          </div>
        </Link>
      </Tooltip>
      <div
        className={cn(
          'absolute right-3 top-1/2 hidden h-[20px] -translate-y-1/2 group-hover:block'
        )}
      >
        {children}
      </div>
    </motion.div>
  )
}
