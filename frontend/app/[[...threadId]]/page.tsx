import { Chat } from '@/components/chat'
import { Header } from '@/components/header'
import { HeaderChatWrapper } from '@/components/header-chat-wrapper'
import { getMissingKeys } from '@/app/actions'
import { SidebarDesktop } from '@/components/sidebar-desktop'
type PageProps = {
  params: Promise<{
    threadId?: string[]
  }>
}
type MessageListMessagesRouteResponse = any

export type ChatPageParams = {
  threadId?: string[]
}

export default async function ChatPage({ params }: PageProps) {
  const missingKeys = await getMissingKeys()
  const threadId = ((await params) as ChatPageParams).threadId?.[0]

  let messages: MessageListMessagesRouteResponse | undefined

  return (
    <div className="flex min-h-0 flex-1 flex-col md:flex-row">
      <SidebarDesktop />
      <HeaderChatWrapper>
        <Header />
        <Chat
          threadId={threadId}
          initialMessages={messages}
          missingKeys={missingKeys}
          promptPlaceholder="Ask a question..."
        />
      </HeaderChatWrapper>
    </div>
  )
}
