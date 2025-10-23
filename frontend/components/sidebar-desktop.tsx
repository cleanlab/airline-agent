import { LogoLockup } from './logo-lockup'
import { Sidebar } from './sidebar'
import { ChatHistory } from './chat-history'
export async function SidebarDesktop() {
  return (
    <Sidebar className="relative inset-y-0 z-30 hidden -translate-x-full border-r bg-muted bg-surface-0 duration-300 ease-in-out data-[state=open]:translate-x-0 md:flex md:w-[220px] lg:w-[300px]">
      <ChatHistory
        mobile={false}
        logoLockup={<LogoLockup className="h-[26px] w-auto" />}
      />
    </Sidebar>
  )
}
