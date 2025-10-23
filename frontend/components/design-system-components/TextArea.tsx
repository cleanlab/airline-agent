'use client'

import { useMergeRefs } from '@floating-ui/react'
import { useMutationObserver } from '@react-hooks-library/core'
import type { ComponentProps } from 'react'
import { forwardRef, useCallback, useRef } from 'react'
import TextareaAutosize from 'react-textarea-autosize'

import { useResizeObserver } from '@/lib/hooks/useResizeObserver'
import { submitForm } from '@/lib/utils/submitForm'
import { cn, tv } from '@/lib/utils/tailwindUtils'

import { useFormField } from './FormFieldContext'
import { textAreaInsert } from '@/lib/utils/textAreaInsert'

/**
 * Size of the text areas.
 */
type TextAreaSize = 'xSmall' | 'small' | 'medium' | 'large'
/**
 * Variant of the text area.
 */
type TextAreaVariant = 'default' | 'monospace'
type TextAreaProps = Omit<
  ComponentProps<typeof TextareaAutosize>,
  'className'
> & {
  /**
   * Size of the text area.
   */
  size: TextAreaSize
  /**
   * The variant of the text area.
   */
  variant: TextAreaVariant
  /**
   * Surface level of the text area.
   */
  surfaceLevel: '0' | '1' | '2'
  /**
   * Indicates if the text area has an error.
   */
  error?: boolean | string
  /**
   * The resize direction of the text area. Shortcut for setting `resize` CSS property on the inner `<textarea>`. Default is `vertical`.
   */
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
  /**
   * Minimum number of rows to show
   */
  minRows?: ComponentProps<typeof TextareaAutosize>['minRows']
  /**
   *  Maximum number of rows up to which the textarea can grow
   */
  maxRows?: ComponentProps<typeof TextareaAutosize>['maxRows']
  /**
   * Function invoked on textarea height change, with height as first argument. The second function argument is an object containing additional information that might be useful for custom behaviors. Current options include { rowHeight: number }.
   */
  onHeightChange?: ComponentProps<typeof TextareaAutosize>['onHeightChange']
  /**
   * Reuse previously computed measurements when computing height of textarea. Default: `false`
   */
  cacheMeasurements?: boolean
  /**
   * If true, the text area will submit the form when the Enter key is pressed. If a the Shift, Alt/Opt or Ctrl key is pressed, then the form will not be submitted, and a new line will be added instead.
   */
  submitOnEnter?: boolean
  /**
   * If provided a string:
   *  - `className` applies only to the outer wrapper `<div>`
   *
   * If provided an object:
   *  - `wrapper` property applies className to the outer wrapper `<div>`
   *  - `textArea` property applies className to the inner `<textarea>`
   */
  className?:
    | string
    | {
        wrapper?: string
        textArea?: string
      }
}

type TextAreaUnstyledProps = Omit<
  TextAreaProps,
  'size' | 'variant' | 'surfaceLevel' | 'error'
>

const inputUnstyledVariants = tv({
  slots: {
    base: 'w-full overflow-hidden p-0 [container-type:inline-size]',
    textArea:
      'pointer-events-auto block w-[100cqw] rounded-2 bg-transparent ring-0 [scrollbar-width:thin] focus:outline-none'
  },
  variants: {
    resize: {
      none: { textArea: 'resize-none' },
      vertical: { textArea: 'resize-y' },
      horizontal: { textArea: 'resize-x' },
      both: { textArea: 'resize' },
      block: { textArea: '[resize:block]' },
      inline: { textArea: '[resize:inline]' }
    },
    disabled: {
      true: {
        base: 'cursor-not-allowed text-text-disabled',
        textArea: 'cursor-not-allowed text-text-disabled'
      }
    }
  }
})

const inputVariants = tv({
  extend: inputUnstyledVariants,
  slots: {
    base: 'type-body-100 rounded-2 text-text-strong shadow-inner outline outline-1 -outline-offset-1 outline-border-1 focus-within:outline-blue-700 focus-within:ring-2 focus-within:ring-focus',
    textArea: 'rounded-2'
  },
  variants: {
    surfaceLevel: {
      '0': {
        base: 'bg-surface-0 outline-border-1 hover:bg-surface-0-hover'
      },
      '1': {
        base: 'bg-surface-1 outline-border-1 hover:bg-surface-1-hover'
      },
      '2': {
        base: 'bg-surface-2 outline-border-2 hover:bg-surface-2-hover'
      }
    },
    variant: {
      default: {
        base: 'type-body-100'
      },
      monospace: {
        base: 'type-code-100'
      }
    },
    size: {
      xSmall: { base: 'type-caption', textArea: 'min-h-8 px-3 py-2' },
      small: { textArea: 'min-h-9 px-4 py-3' },
      medium: { textArea: 'min-h-[36px] px-5 py-4' },
      large: { textArea: 'min-h-10 px-5 py-[10px]' }
    },
    error: {
      true: {
        base: '[&:not(:focus-within)]:outline-red-700 [&:not(:focus-within)]:ring-2 [&:not(:focus-within)]:ring-red-500'
      }
    },
    disabled: {
      true: {
        base: 'cursor-not-allowed bg-surface-disabled text-text-disabled shadow-none outline-none hover:bg-surface-disabled'
      }
    }
  },
  compoundVariants: [
    {
      variant: 'monospace',
      size: 'xSmall',
      class: {
        base: 'font-mono'
      }
    }
  ]
})

const USE_MUTATION_OPTS: MutationObserverInit = {
  attributeFilter: ['style']
}

/**
 * A flexible textarea component that automatically resizes based on content.
 *
 * @component
 * @param {TextAreaProps} props - The component props
 * @param {string} props.surfaceLevel - Background color level ('0', '1', or '2')
 * @param {boolean | string} [props.error] - Error state that changes the border color
 * @param {string} [props.resize='none'] - Controls how the textarea can be resized
 * @param {number} [props.minRows] - Minimum number of rows to display
 * @param {number} [props.maxRows] - Maximum number of rows before scrolling
 * @param {boolean} [props.submitOnEnter] - Whether pressing Enter submits the form
 * @param {string | {wrapper?: string, textArea?: string}} [props.className] - Custom CSS classes
 */
const TextAreaUnstyled = forwardRef<HTMLTextAreaElement, TextAreaUnstyledProps>(
  (
    {
      id: idProp,
      required: requiredProp,
      disabled: disabledProp,
      submitOnEnter,
      onKeyDown,
      resize = 'none',
      className,
      children,
      ...props
    },
    refProp
  ) => {
    const textAreaRefInternal = useRef<HTMLTextAreaElement>(null)
    const textAreaRef = useMergeRefs([textAreaRefInternal, refProp])
    const wrapperRef = useRef<HTMLDivElement>(null)
    const updateWrapperSize = useCallback(() => {
      if (!wrapperRef.current) return
      if (textAreaRefInternal.current?.style.width) {
        wrapperRef.current.style.width =
          textAreaRefInternal.current?.style.width
      } else {
        wrapperRef.current.style.removeProperty('width')
      }
      if (textAreaRefInternal.current?.style.height) {
        wrapperRef.current.style.height =
          textAreaRefInternal.current?.style.height
      } else {
        wrapperRef.current.style.removeProperty('height')
      }
    }, [wrapperRef])
    // Make sure to update the wrapper size when the textarea size changes
    useResizeObserver(
      textAreaRefInternal as unknown as React.RefObject<HTMLElement>,
      updateWrapperSize
    )
    // Make sure to update the wrapper size when the textarea style changes
    useMutationObserver(
      textAreaRefInternal as unknown as React.RefObject<HTMLElement>,
      updateWrapperSize,
      USE_MUTATION_OPTS
    )

    const formFieldContext = useFormField()
    const id = idProp || formFieldContext?.htmlFor || undefined
    const required =
      requiredProp !== null && requiredProp !== undefined
        ? !!requiredProp
        : !!formFieldContext?.required
    const disabled =
      disabledProp !== null && disabledProp !== undefined
        ? !!disabledProp
        : !!formFieldContext?.disabled

    const slots = inputUnstyledVariants({
      resize: resize,
      disabled: disabled
    })

    return (
      <div
        ref={wrapperRef}
        className={cn(
          slots.base(),
          typeof className === 'string' ? className : className?.wrapper
        )}
      >
        <TextareaAutosize
          ref={textAreaRef}
          id={id}
          required={required}
          disabled={disabled}
          onKeyDown={e => {
            if (e.key === 'Enter') {
              const modKeyPressed = e.shiftKey || e.altKey || e.ctrlKey
              if (modKeyPressed) {
                // Mimic behavior of Slack message input, where pressing enter with Shift, Alt, or Ctrl keys adds a new line and doesn't submit the form
                e.preventDefault()
                textAreaInsert(textAreaRefInternal.current, '\n')
              } else if (submitOnEnter) {
                e.preventDefault()
                submitForm(e.currentTarget.form)
              }
            }
            onKeyDown?.(e)
          }}
          className={cn(
            slots.textArea(),
            typeof className === 'string' ? '' : className?.textArea
          )}
          {...props}
        />
        {children}
      </div>
    )
  }
)

/**
 * A flexible textarea component that automatically resizes based on content.
 *
 * @component
 * @param {TextAreaProps} props - The component props
 * @param {TextAreaSize} props.size - Controls the padding and minimum height of the textarea
 * @param {TextAreaVariant} props.variant - Determines the font styling ('default' or 'monospace')
 * @param {string} props.surfaceLevel - Background color level ('0', '1', or '2')
 * @param {boolean | string} [props.error] - Error state that changes the border color
 * @param {string} [props.resize='none'] - Controls how the textarea can be resized
 * @param {number} [props.minRows] - Minimum number of rows to display
 * @param {number} [props.maxRows] - Maximum number of rows before scrolling
 * @param {boolean} [props.submitOnEnter] - Whether pressing Enter submits the form
 * @param {string | {wrapper?: string, textArea?: string}} [props.className] - Custom CSS classes
 */
const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ className, size, variant, error, surfaceLevel, ...props }, refProp) => {
    const slots = inputVariants({
      size: size,
      variant: variant,
      error: !!error,
      surfaceLevel,
      disabled: props.disabled,
      resize: props.resize
    })
    return (
      <TextAreaUnstyled
        ref={refProp}
        className={{
          wrapper: cn(
            slots.base(),
            typeof className === 'string' ? className : className?.wrapper
          ),
          textArea: cn(
            slots.textArea(),
            typeof className === 'string' ? '' : className?.textArea
          )
        }}
        {...props}
      />
    )
  }
)

export { TextArea, TextAreaUnstyled }
