'use client'

import { Highlight } from 'prism-react-renderer'
import type { FC } from 'react'
import { memo } from 'react'

import { IconFrameButton } from './IconFrameButton'
import { useTheme } from './ThemeProvider'
import { Tooltip } from './Tooltip'
import { useClipboard } from '@/lib/hooks/useClipboard'
import { IconCheck, IconCopy } from '../icons'
import { cn } from '@/lib/utils/tailwindUtils'
import { prismThemeDark } from './prismThemeDark'
import { prismThemeLight } from './prismThemeLight'

// Inspired by Chatbot-UI and modified to fit the needs of this project
// @see https://github.com/mckaywrigley/chatbot-ui/blob/main/components/Markdown/CodeBlock.tsx

/**
 * Props for the ChatCodeBlock component
 */
interface Props {
  /** The programming language for syntax highlighting (e.g., 'javascript', 'python', 'typescript') */
  language: string
  /** The source code content to display and highlight */
  code: string
  /** Additional CSS classes to apply to the code block container */
  className?: string
  /** Additional CSS classes to apply to the code section container */
  codeSectionClassName?: string
  /** Whether to display line numbers alongside the code. Defaults to true */
  showLineNumbers?: boolean
  /** The text size variant for the code block. '100' is normal size, '50' is smaller */
  textSize?: '100' | '50'
}

/**
 * A syntax-highlighted code block component with copy functionality and customizable display options.
 *
 * Features:
 * - Syntax highlighting using Prism.js via prism-react-renderer
 * - Copy to clipboard functionality with visual feedback
 * - Support for light and dark themes
 * - Optional line numbers
 * - Configurable text size
 * - Language label display
 *
 * @example
 * ```tsx
 * <ChatCodeBlock
 *   language="javascript"
 *   code="const message = 'Hello, world!';"
 * />
 * ```
 *
 * @example
 * ```tsx
 * <ChatCodeBlock
 *   language="bash"
 *   code="npm install zustand"
 *   showLineNumbers={false}
 *   textSize="50"
 * />
 * ```
 *
 * @example
 * ```tsx
 * <ChatCodeBlock
 *   language="python"
 *   code="print('Hello, world!')"
 * />
 * ```
 *
 * @example
 * ```tsx
 * <ChatCodeBlock
 *   language="typescript"
 *   code="const result = await fetch('/api/data');"
 *   codeSectionClassName="max-h-64 custom-scrollbar"
 * />
 * ```
 */
const CodeBlock: FC<Props> = memo(props => {
  const {
    language,
    code,
    className,
    codeSectionClassName,
    showLineNumbers = true,
    textSize = '100'
  } = props
  const { hasCopied, copyToClipboard } = useClipboard(2000)
  const isDark = useTheme().theme === 'dark'

  const onCopy = () => {
    if (hasCopied) return
    copyToClipboard(code)
  }

  return (
    <div
      className={cn(
        'type-code-100 relative w-full overflow-hidden rounded-2 border border-border-1 bg-surface-0-hover',
        textSize === '50' && 'type-code-50',
        className
      )}
    >
      <div
        className={cn(
          'flex w-full items-center justify-between border-b border-border-1 bg-surface-2 px-6 py-2',
          textSize === '50' && 'px-5 py-1'
        )}
      >
        <span
          className={cn(
            'type-body-100 text-text-faint',
            textSize === '50' && 'type-caption'
          )}
        >
          {language}
        </span>
        <div className="flex items-center space-x-1">
          <Tooltip content={hasCopied ? 'Copied' : 'Copy code'}>
            <IconFrameButton
              aria-label="Copy code"
              variant="outline"
              size="xSmall"
              onClick={onCopy}
              icon={
                hasCopied ? (
                  <IconCheck size={16} className="text-text-primary" />
                ) : (
                  <IconCopy size={16} className="text-text-primary" />
                )
              }
            />
          </Tooltip>
        </div>
      </div>
      <Highlight
        language={language}
        theme={isDark ? prismThemeDark : prismThemeLight}
        code={code}
      >
        {({
          className: classNameFromPrism,
          style,
          tokens,
          getLineProps,
          getTokenProps
        }) => (
          <div
            style={style}
            className={cn(
              'type-code-100 m-0 flex flex-nowrap overflow-auto p-0 py-8 pr-6 [scrollbar-width:thin]',
              textSize === '50' && 'type-code-50 p-5',
              classNameFromPrism,
              codeSectionClassName
            )}
          >
            {showLineNumbers && (
              <div
                aria-hidden
                className="sticky left-0 block h-full select-none bg-surface-1 px-6 text-right text-text-faint"
              >
                {tokens.map((_, i) => [<div key={i}>{i}</div>])}
              </div>
            )}
            <div>
              {tokens.map((line, i) => (
                <pre key={i} {...getLineProps({ line })}>
                  {line.map((token, key) => (
                    <span key={key} {...getTokenProps({ token })} />
                  ))}
                </pre>
              ))}
            </div>
          </div>
        )}
      </Highlight>
    </div>
  )
})
CodeBlock.displayName = 'ChatCodeBlock'

export { CodeBlock as ChatCodeBlock }
