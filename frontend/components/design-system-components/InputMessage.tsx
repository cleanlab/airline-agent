'use client'

import { type ComponentProps } from 'react'

import { TextAreaUnstyled } from './TextArea'
import { cn } from '@/lib/utils/tailwindUtils'
import { ButtonSubmitMessage } from './ButtonSubmitMessage'

const InputMessage = ({
  submitDisabled,
  submitOnEnter = true,
  className: classNameProp,
  children,
  ...props
}: { submitDisabled?: boolean } & Partial<
  ComponentProps<typeof TextAreaUnstyled>
>) => {
  const className = {
    wrapper: cn(
      'relative flex w-full grow flex-col items-center overflow-hidden rounded-2 bg-surface-1 shadow-inner outline outline-1 -outline-offset-1 outline-border-1',
      typeof classNameProp === 'string' ? classNameProp : classNameProp?.wrapper
    ),
    textArea: cn(
      'type-body-200 w-full resize-none bg-transparent py-5 pl-6 pr-12 placeholder:type-body-200 placeholder:text-text-disabled focus-within:outline-none',
      typeof classNameProp === 'string' ? '' : classNameProp?.textArea
    )
  }

  return (
    <TextAreaUnstyled
      submitOnEnter={submitOnEnter}
      minRows={1}
      maxRows={4}
      spellCheck={false}
      autoComplete="off"
      autoCorrect="off"
      className={className}
      {...props}
    >
      {children ?? (
        <ButtonSubmitMessage disabled={submitDisabled || props.disabled} />
      )}
    </TextAreaUnstyled>
  )
}

export { ButtonSubmitMessage, InputMessage }
