// @ts-nocheck
'use client'

import { createContext, type FC, type ReactNode, useContext } from 'react'
import rehypeRaw from 'rehype-raw'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'

import { CodeInline } from './CodeInline'
import { cn, tw } from '@/lib/utils/tailwindUtils'
import { ChatCodeBlock } from './ChatCodeBlock'
import { MemoizedReactMarkdown } from './MemoizedReactMarkdown'

type MarkdownTextSize = '200' | '100' | '50'
const DEFAULT_TEXT_SIZE: MarkdownTextSize = '200'

const MarkdownContext = createContext<MarkdownTextSize>('200')

const useMarkdownContext = () => useContext(MarkdownContext)

const HEADING_TYPE_MAP = {
  '50': {
    1: 'type-caption-bold',
    2: 'type-caption-semibold',
    3: 'type-caption-medium',
    4: 'type-caption-medium',
    5: 'type-caption-medium',
    6: 'type-caption-medium'
  },
  '100': {
    1: 'type-body-100-bold',
    2: 'type-body-100-semibold',
    3: 'type-body-100-medium',
    4: 'type-body-100-medium',
    5: 'type-body-100-medium',
    6: 'type-body-100-medium'
  },
  '200': {
    1: 'type-body-200-bold',
    2: 'type-body-200-semibold',
    3: 'type-body-200-medium',
    4: 'type-body-200-medium',
    5: 'type-body-200-medium',
    6: 'type-body-200-medium'
  }
}

const getHeadingTypeClass = (
  level: number,
  textSize: MarkdownTextSize = DEFAULT_TEXT_SIZE
) => {
  const typeMap =
    HEADING_TYPE_MAP[textSize] ?? HEADING_TYPE_MAP[DEFAULT_TEXT_SIZE]
  return typeMap[level as keyof typeof typeMap] ?? typeMap[6]
}

const Heading: FC<{
  level: 1 | 2 | 3 | 4 | 5 | 6
  children: ReactNode
}> = ({ level, children }) => {
  const textSize = useMarkdownContext()
  const Component = `h${level}` as const
  return (
    <Component
      className={cn(
        'mb-2 mt-5 text-text-primary first:mt-0 last:mb-0',
        getHeadingTypeClass(level, textSize)
      )}
    >
      {children}
    </Component>
  )
}

const tableCellClassName = tw(
  'type-body-100 border-solid border-r-border-0 px-4 py-2 text-text-primary group-[&:not(:last-child)]/tr:border-b [&:not(:last-child)]:border-r'
)

// This class must be defined outside of JSX, otherwise Typescript will escape
// the bullet character and the tailwind compiler won't recognize it properly.
const ulLiClassName =
  "type-body-200 relative mb-3 pl-[var(--left-pad)] text-text-primary [--left-pad:theme(spacing.5)] before:absolute before:left-0 before:top-0 before:w-[var(--left-pad)] before:truncate before:text-[1.5em] before:text-text-strong before:content-['•'] last:mb-0"

// Narrowly suppress react-markdown components typing mismatch
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const markdownComponents: any = {
  a({ children, ...props }) {
    return (
      <a
        className="text-text-strong underline transition-colors duration-200 hover:text-text-primary"
        {...props}
      >
        {children}
      </a>
    )
  },
  h1: ({ children }) => <Heading level={1}>{children}</Heading>,
  h2: ({ children }) => <Heading level={2}>{children}</Heading>,
  h3: ({ children }) => <Heading level={3}>{children}</Heading>,
  h4: ({ children }) => <Heading level={4}>{children}</Heading>,
  h5: ({ children }) => <Heading level={5}>{children}</Heading>,
  h6: ({ children }) => <Heading level={6}>{children}</Heading>,
  p: function P({ children }) {
    const textSize = useMarkdownContext()
    return (
      <p
        className={cn(
          'type-body-200 mb-4 text-text-primary last:mb-0',
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption'
        )}
      >
        {children}
      </p>
    )
  },
  hr: function Hr() {
    return <hr className="my-4 h-0 border-0 border-t border-t-border-1" />
  },
  // Usually unnecesary, but `role="list"` 100% guarantees list will be accessible
  // See: https://gerardkcohen.me/writing/2017/voiceover-list-style-type.htm
  ol: function Ol({ children, start }) {
    const textSize = useMarkdownContext()
    const startIndex = typeof start === 'number' ? start : undefined
    return (
      <ol
        role="list"
        className={cn(
          'group type-body-200 mb-5 list-decimal pl-6',
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption'
        )}
        start={startIndex}
      >
        {children}
      </ol>
    )
  },
  // Usually unnecesary, but `role="list"` 100% guarantees list will be accessible
  // See: https://gerardkcohen.me/writing/2017/voiceover-list-style-type.htm
  ul: function Ul({ children }) {
    const textSize = useMarkdownContext()
    return (
      <ul
        role="list"
        className={cn(
          'reset-list group type-body-200 mb-5',
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption'
        )}
      >
        {children}
      </ul>
    )
  },
  li: function Li({ children, ordered }) {
    const textSize = useMarkdownContext()
    if (ordered) {
      return (
        <li
          className={cn(
            'type-body-200 mb-3 text-text-primary',
            textSize === '100' && 'type-body-100',
            textSize === '50' && 'type-caption'
          )}
        >
          {children}
        </li>
      )
    }
    return (
      <li
        className={cn(
          ulLiClassName,
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption'
        )}
      >
        {children}
      </li>
    )
  },
  pre({ children }) {
    return <div className="mb-4 mt-2 first:mt-0 last:mb-0">{children}</div>
  },
  code: function Code({ children, className, inline, ...props }) {
    const textSize = useMarkdownContext()
    if (children.length) {
      if (children[0] == '▍') {
        return <span className="mt-1 animate-pulse cursor-default">▍</span>
      }

      children[0] = (children[0] as string).replace('`▍`', '▍')
    }

    const match = /language-(\w+)/.exec(className || '')

    if (inline) {
      return <CodeInline>{children}</CodeInline>
    }

    return (
      <ChatCodeBlock
        key={Math.random()}
        language={match?.[1] || ''}
        code={String(children).replace(/\n$/, '')}
        className={className}
        // Map '200' to '100' for larger text size and all other values to '50' for smaller text size.
        textSize={textSize === '200' ? '100' : '50'}
        {...props}
      />
    )
  },
  table({ children }) {
    return (
      <div className="mb-4 mt-2 w-fit max-w-full overflow-hidden rounded-2 border border-solid border-border-1 bg-surface-0 first:mt-0 last:mb-0">
        <div className="w-fit max-w-full overflow-x-auto [scrollbar-width:thin]">
          <table className="border-spacing-0">{children}</table>
        </div>
      </div>
    )
  },
  thead({ children }) {
    return (
      <thead className="border-0 border-b border-solid border-border-1 bg-surface-2">
        {children}
      </thead>
    )
  },
  th: function Th({ children }) {
    const textSize = useMarkdownContext()
    return (
      <th
        className={cn(
          tableCellClassName,
          'type-body-100-semibold border-r-border-1 text-text-strong',
          textSize === '100' && 'type-caption-semibold',
          textSize === '50' && 'type-caption-semibold'
        )}
      >
        {children}
      </th>
    )
  },
  tr({ children }) {
    return <tr className="group/tr">{children}</tr>
  },
  td: function Td({ children }) {
    const textSize = useMarkdownContext()
    return (
      <td
        className={cn(
          tableCellClassName,
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption'
        )}
      >
        {children}
      </td>
    )
  },
  blockquote: function Blockquote({ children }) {
    const textSize = useMarkdownContext()
    return (
      <blockquote
        className={cn(
          'border-l-solid type-body-200 mb-4 mt-2 border-l-[3px] border-text-strong border-l-border-2 pl-5 text-text-strong first:mt-0 last:mb-0',
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption'
        )}
      >
        {children}
      </blockquote>
    )
  }
} as const

// Normalize ordered list markers so that lines starting with "1) " are
// converted to the CommonMark style "1. ". This helps react-markdown parse
// them as ordered lists. We avoid transforming content inside fenced code blocks.
const normalizeOrderedListMarkers = (markdown: string) => {
  let inCodeFence = false
  const fenceRegex = /^\s*```/
  return markdown
    .split('\n')
    .map(line => {
      if (fenceRegex.test(line)) {
        inCodeFence = !inCodeFence
        return line
      }
      if (inCodeFence) return line
      return line.replace(/^(\s*)(\d+)\)\s+/, '$1$2. ')
    })
    .join('\n')
}

const MessageMarkdown = ({
  children,
  className,
  allowHtml,
  textSize = '200'
}: {
  children: string
  className?: string
  allowHtml?: boolean
  textSize?: MarkdownTextSize
}) => {
  const normalized = normalizeOrderedListMarkers(children)
  return (
    <MarkdownContext.Provider value={textSize}>
      <MemoizedReactMarkdown
        className={cn(
          'type-body-200 break-words',
          textSize === '100' && 'type-body-100',
          textSize === '50' && 'type-caption',
          className
        )}
        remarkPlugins={[remarkGfm, remarkMath]}
        // @ts-expect-error
        rehypePlugins={
          allowHtml ? [[rehypeRaw, { tagfilter: true }]] : undefined
        }
        components={markdownComponents}
      >
        {normalized}
      </MemoizedReactMarkdown>
    </MarkdownContext.Provider>
  )
}

export { MessageMarkdown }
