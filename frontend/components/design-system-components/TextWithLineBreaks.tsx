import type { ReactNode } from 'react'
import { Fragment } from 'react/jsx-runtime'

/**
 * A component that renders text content with preserved line breaks.
 * If the input is a string, it splits on newline characters and renders each line
 * with proper <br /> tags. If the input is not a string (e.g., JSX), it renders
 * the content as-is.
 *
 * @component
 * @param {Object} props - The component props
 * @param {ReactNode} props.content - The content to render. Can be a string or any valid React node
 * @returns {ReactNode} The rendered content with preserved line breaks
 *
 * @example
 * ```tsx
 * // String content with line breaks
 * <TextWithLineBreaks content="Line 1\nLine 2\nLine 3" />
 *
 * // JSX content
 * <TextWithLineBreaks content={<div>Some JSX</div>} />
 * ```
 */
export const TextWithLineBreaks = ({ content }: { content: ReactNode }) => {
  if (typeof content !== 'string') {
    return content
  }
  return (
    <>
      {content.split('\n').map((line, index, array) =>
        index === array.length - 1 ? (
          line
        ) : (
          <Fragment key={index}>
            {line}
            <br />
          </Fragment>
        )
      )}
    </>
  )
}
