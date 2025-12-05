'use client'

import { SidebarItems } from '@/components/sidebar-items'
import { useAssistantHistory } from '@/providers/rag-app-store-provider'

export function SidebarList() {
  const history = useAssistantHistory()

  return (
    <div className="-ml-4 flex flex-1 flex-col">
      <div className="flex-1">
        {history?.length ? (
          <div className="space-y-4">
            <SidebarItems historyThreads={history} />
          </div>
        ) : (
          <p className="type-body-100 ml-4 text-text-faint">No chat history</p>
        )}
      </div>
    </div>
  )
}
