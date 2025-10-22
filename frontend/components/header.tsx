import { getChatPath } from '@/lib/consts'
import Link from 'next/link'
import { HeaderButtons } from './header-buttons'
import { LogoLockup } from './logo-lockup'
import { NewChatButton } from './new-chat-button'
import { ThemeToggle } from './theme-toggle'

async function HeaderRagApp() {
  return (
    <div className="flex flex-col items-center justify-between gap-x-7 gap-y-4 border-b border-border-0 px-8 py-6 xl:flex-row">
      <div />
      <HeaderButtons
        variant="horizontal"
        className="shrink-0 xl:w-full xl:max-w-fit"
      />
    </div>
  )
}

export async function HeaderDesktop() {
  return (
    <header className="items-between hidden w-full shrink-0 flex-col justify-start bg-surface-1 backdrop-blur-xl md:flex">
      <HeaderRagApp />
    </header>
  )
}

export async function Header() {
  return (
    <header className="flex w-full shrink-0 items-center justify-between overflow-hidden bg-surface-0 px-8 py-5 backdrop-blur-xl">
      <div className="flex" />
      <Link
        className="flex md:hidden"
        href="https://cleanlab.ai/"
        target="_blank"
      >
        <h1 className="type-body-300 flex items-center justify-center gap-4 text-text-strong">
          <LogoLockup className="h-[26px] w-auto" />
        </h1>
      </Link>
      <div className="flex items-center gap-4">
        <ThemeToggle />
        <NewChatButton className="flex md:hidden" asChild>
          <Link href={getChatPath()} />
        </NewChatButton>
      </div>
    </header>
  )
}
