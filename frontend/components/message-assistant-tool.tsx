import { ChatCodeBlock } from '@cleanlab/design-system/chat'
import { IconChevronDown } from '@cleanlab/design-system/icons'
import { Collapsible } from 'radix-ui'

import type { StoreMessage } from '@/stores/messages-store'

export function MessageAssistantTool({ message }: { message: StoreMessage }) {
  // Display tool call messages
  const toolCallData = (() => {
    // If content is already an object, use it directly
    if (typeof message.content === 'object' && message.content !== null) {
      return message.content
    }

    // If content is a string, try to parse it as JSON
    if (typeof message.content === 'string') {
      try {
        return JSON.parse(message.content)
      } catch {
        return null
      }
    }

    return null
  })()

  // Helper function to parse and pretty-print JSON strings or objects
  const parseAndPrettyPrint = (data: unknown) => {
    // If it's already an object, just stringify it
    if (typeof data === 'object' && data !== null) {
      return JSON.stringify(data, null, 2)
    }

    // If it's not a string, return as-is
    if (typeof data !== 'string') {
      return String(data)
    }

    // Check if the string looks like JSON or double-encoded JSON
    const trimmed = data.trim()
    const looksLikeJson =
      (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
      (trimmed.startsWith('[') && trimmed.endsWith(']')) ||
      (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
      // Check for double-encoded JSON (starts with " and contains escaped quotes)
      (trimmed.startsWith('"') && trimmed.includes('\\"'))

    if (!looksLikeJson) {
      return data
    }

    try {
      // First try to parse as JSON
      let parsed = JSON.parse(data)

      // If the result is still a string, it might be double-encoded JSON
      if (typeof parsed === 'string') {
        try {
          parsed = JSON.parse(parsed)
        } catch {
          // If second parse fails, use the first parsed result
        }
      }

      // Pretty print the final result with better formatting
      return JSON.stringify(parsed, null, 2)
    } catch (error) {
      // If all parsing fails, return the original string
      console.error(error)
      return data
    }
  }

  return (
    <div className="rounded-4 border border-border-2 bg-surface-1">
      <div className="flex min-w-0 items-start gap-4">
        <Collapsible.Root className="group/collapsible group min-w-0 flex-1">
          <Collapsible.Trigger className="type-body-200-semibold flex w-full items-center justify-between gap-5 rounded-4 px-6 py-7 hover:bg-surface-1-hover">
            <div className="type-body-200-semibold flex items-center gap-4">
              <span>🔧</span> Tool Call: {toolCallData?.tool_name || 'Unknown'}
            </div>
            <IconChevronDown
              size={16}
              className="text-text-disabled transition-transform group-data-[state=open]/collapsible:-scale-y-100"
            />
          </Collapsible.Trigger>
          <Collapsible.Content className="min-w-0 max-w-full overflow-x-auto overflow-y-hidden data-[state=closed]:animate-collapsible-close data-[state=open]:animate-collapsible-open">
            {toolCallData?.arguments && (
              <div className="px-6 pt-4">
                <div className="type-body-100 mb-2 font-medium">Arguments:</div>
                <div className="min-w-0 max-w-full overflow-x-auto rounded-2">
                  <ChatCodeBlock
                    language="json"
                    code={(() => {
                      // Handle arguments - they might be a string that needs parsing
                      let argumentsData = toolCallData.arguments
                      if (typeof argumentsData === 'string') {
                        try {
                          argumentsData = JSON.parse(argumentsData)
                        } catch {
                          // If parsing fails, use the string as-is
                        }
                      }
                      return parseAndPrettyPrint(argumentsData)
                    })()}
                    showLineNumbers={false}
                    textSize="50"
                    className="inline-block"
                  />
                </div>
              </div>
            )}

            {toolCallData?.result && (
              <div className="p-6">
                <div className="type-body-100 mb-1 font-medium">Result:</div>
                {(() => {
                  const resultContent = parseAndPrettyPrint(toolCallData.result)

                  // Check if the result is valid JSON
                  const isJson = (() => {
                    try {
                      const parsed = JSON.parse(resultContent)
                      return typeof parsed === 'object' && parsed !== null
                    } catch {
                      return false
                    }
                  })()

                  if (isJson) {
                    // Use ChatCodeBlock for JSON results
                    return (
                      <div className="min-w-0 max-w-full overflow-x-auto rounded-2">
                        <ChatCodeBlock
                          language="json"
                          code={resultContent}
                          showLineNumbers={false}
                          textSize="50"
                          className="inline-block"
                        />
                      </div>
                    )
                  } else {
                    // Use plain text for non-JSON results
                    return (
                      <div className="max-h-32 max-w-full overflow-auto rounded-2 bg-surface-2 px-5 py-4">
                        <pre className="type-caption whitespace-pre-wrap break-all font-mono">
                          {resultContent}
                        </pre>
                      </div>
                    )
                  }
                })()}
              </div>
            )}

            {!toolCallData && (
              <div className="px-6 pb-6">
                <div className="type-caption max-w-full overflow-x-auto whitespace-pre break-words rounded-2 bg-surface-2 px-5 py-4">
                  {String(message.content)}
                </div>
              </div>
            )}
          </Collapsible.Content>
        </Collapsible.Root>
      </div>
    </div>
  )
}
