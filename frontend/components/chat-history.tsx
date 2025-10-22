'use client'

import { Tooltip } from './design-system-components/Tooltip'
import Link from 'next/link'
import type { ReactNode } from 'react'
import * as React from 'react'
import { NewChatButton } from './new-chat-button'
import { cn } from '@/lib/utils/tailwindUtils'
import { SidebarList } from './sidebar-list'

interface ChatHistoryProps {
  mobile?: boolean
  logoLockup: ReactNode
}

export const isExternalUrl = (url?: string) => {
  if (!url) {
    return false
  }
  return url.startsWith('http') || url.startsWith('//')
}

export function UrlsList({ urls }: { urls?: string[] }) {
  if (!urls?.length) return null
  return (
    <>
      {urls.map(url => (
        <Tooltip key={url} content={url}>
          {isExternalUrl(url) ? (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="block max-w-full truncate hover:underline"
            >
              {url}
            </a>
          ) : (
            <div>{url}</div>
          )}
        </Tooltip>
      ))}
    </>
  )
}

export function ChatHistory({ mobile, logoLockup }: ChatHistoryProps) {
  return (
    <div
      data-scroll-restoration-id="chat-history"
      className="flex h-full flex-col overflow-auto"
    >
      <div className="sticky top-0 z-10 flex items-center justify-between bg-surface-0 px-8 pb-5 pt-7">
        <Link href="/">
          <h1
            className={cn(
              'flex grow items-center gap-4 text-text-strong',
              mobile && 'justify-center'
            )}
          >
            {logoLockup}
          </h1>
        </Link>
        <NewChatButton asChild>
          <Link href="/" />
        </NewChatButton>
      </div>
      <div className="shrink grow px-8">
        <div>
          <h4 className="type-caption-medium pb-2 pl-0 pr-4 pt-4 text-text-strong">
            History
          </h4>
          <React.Suspense
            fallback={
              <div className="flex flex-1 flex-col space-y-4">
                {Array.from({ length: 10 }).map((_, i) => (
                  <div
                    // eslint-disable-next-line @eslint-react/no-array-index-key
                    key={i}
                    className="h-6 w-full shrink-0 animate-pulse rounded-2 bg-zinc-200 dark:bg-zinc-800"
                  />
                ))}
              </div>
            }
          >
            <SidebarList />
          </React.Suspense>
        </div>
      </div>
    </div>
  )
}
