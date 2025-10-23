'use client'

import type { ButtonHTMLAttributes, ComponentProps } from 'react'
import type Link from 'next/link'
import { cn } from '@/lib/utils/tailwindUtils'
import { useMessagesStore } from '@/providers/messages-store-provider'
import { Slot } from '@radix-ui/react-slot'
import { analytics } from '@/services/analytics'
import { AsChildProps } from '@/lib/utils/AsChildProps'
import { Tooltip } from './design-system-components/Tooltip'
import { SlotChild } from './design-system-components/SlotChild'

const IconEdit = () => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className="translate-x-[5%] translate-y-[-2%]"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M11.6465 0.979821C11.8417 0.784558 12.1583 0.784558 12.3536 0.979821L15.0203 3.64649C15.2155 3.84175 15.2155 4.15833 15.0203 4.35359L8.35359 11.0203C8.25983 11.114 8.13265 11.1667 8.00004 11.1667H5.33337C5.05723 11.1667 4.83337 10.9428 4.83337 10.6667V8.00004C4.83337 7.86743 4.88605 7.74026 4.97982 7.64649L11.6465 0.979821ZM5.83337 8.20715V10.1667H7.79293L13.9596 4.00004L12 2.04048L5.83337 8.20715ZM2.66671 3.16671C2.44569 3.16671 2.23373 3.2545 2.07745 3.41079C1.92117 3.56707 1.83337 3.77903 1.83337 4.00004V13.3334C1.83337 13.5544 1.92117 13.7663 2.07745 13.9226C2.23373 14.0789 2.44569 14.1667 2.66671 14.1667H12C12.2211 14.1667 12.433 14.0789 12.5893 13.9226C12.7456 13.7663 12.8334 13.5544 12.8334 13.3334V9.77337C12.8334 9.49723 13.0572 9.27337 13.3334 9.27337C13.6095 9.27337 13.8334 9.49723 13.8334 9.77337V13.3334C13.8334 13.8196 13.6402 14.2859 13.2964 14.6297C12.9526 14.9736 12.4863 15.1667 12 15.1667H2.66671C2.18048 15.1667 1.71416 14.9736 1.37034 14.6297C1.02653 14.2859 0.833374 13.8196 0.833374 13.3334V4.00004C0.833374 3.51381 1.02653 3.04749 1.37034 2.70368C1.71416 2.35986 2.18048 2.16671 2.66671 2.16671H6.22671C6.50285 2.16671 6.72671 2.39057 6.72671 2.66671C6.72671 2.94285 6.50285 3.16671 6.22671 3.16671H2.66671Z"
        fill="currentColor"
      />
    </svg>
  )
}

export function NewChatButton({
  className,
  asChild,
  children,
  ...props
}: AsChildProps<
  {
    className?: string
    linkProps?: ComponentProps<typeof Link>
  } & ButtonHTMLAttributes<HTMLButtonElement>
>) {
  const Comp = asChild ? Slot : 'button'
  const setCurrentThread = useMessagesStore(state => state.setCurrentThread)

  return (
    <Tooltip content="New chat">
      <Comp
        className={cn(
          'flex size-[32px] shrink-0 items-center justify-center rounded-[8px] bg-neutral-800 text-text-high-contrast hover:bg-neutral-900',
          className
        )}
        onClick={() => {
          analytics.track('new_chat_button_clicked')
          setCurrentThread(undefined)
        }}
        {...props}
      >
        <SlotChild asChild={!!asChild} child={children}>
          {() => (
            <>
              <IconEdit />
              <span className="sr-only">New chat</span>
            </>
          )}
        </SlotChild>
      </Comp>
    </Tooltip>
  )
}
