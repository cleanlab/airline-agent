'use client'

import { useMergeRefs } from '@floating-ui/react'
import { Dialog as DialogPrimitive } from 'radix-ui'
import type { ComponentProps, ForwardedRef, HTMLAttributes } from 'react'
import { createContext, forwardRef, useContext, useEffect, useRef } from 'react'

import {
  createKeyboardShortcutHandler,
  getKeyboardShortcutString
} from '@/lib/utils/keyboardShortcuts'
import { cn } from '@/lib/utils/tailwindUtils'
import type { ButtonProps } from './Button'
import { Button } from './Button'

import { Kbd } from './Kbd'
import { modalVariants } from './modalVariants'
import { ButtonClose } from './ButtonClose'

const MODAL_VARIANTS = ['default', 'extended'] as const
type ModalVariant = (typeof MODAL_VARIANTS)[number]

const MODAL_SIZES = ['small', 'medium', 'large', 'xLarge'] as const
type ModalSize = (typeof MODAL_SIZES)[number]

type ModalContextValue = {
  variant: ModalVariant
  size: ModalSize
  showCloseButton?: boolean
}

const ModalContext = createContext<ModalContextValue>({
  variant: 'default',
  size: 'medium',
  showCloseButton: false
})
const useModalContext = () => {
  return useContext(ModalContext)
}
const ModalContextProvider = ModalContext.Provider

/**
 * Close button for the dialog. Used in the <ModalDialogHeader /> component.
 * Automatically closes the dialog when clicked, unless `preventDefault` is
 * called in the `onClick` handler. Should be provided as a child of the
 * <ModalDialogFooter /> component.
 */
const ModalDialogClose = forwardRef(
  ({ children, ...props }: ComponentProps<'div'>, ref: ForwardedRef<any>) => {
    return (
      <div className={modalVariants.close()} {...props}>
        <Kbd variant="subtle">esc</Kbd>
        <DialogPrimitive.Close ref={ref} asChild>
          <ButtonClose size="xSmall" aria-label="Close dialog" />
        </DialogPrimitive.Close>
      </div>
    )
  }
)
ModalDialogClose.displayName = 'ModalDialogClose'

/**
 * The header of the dialog. Will render a border at the bottom if the variant is
 * `extended`. Used as the container for the `<ModalDialogTitle />` and
 * `<ModalDialogDescription />` components. Should not contain
 * `<ModalDialogDescription />` for the `extended variant`.
 */
const ModalHeader = ({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) => {
  const { variant, showCloseButton } = useModalContext()
  const { base, inner } = modalVariants.header({ variant })
  return (
    <div className={base()} {...props}>
      <div className={cn(inner(), className)}>{children}</div>
      {showCloseButton && <ModalDialogClose />}
    </div>
  )
}
ModalHeader.displayName = 'ModalHeader'

const ButtonModalAction = forwardRef(
  (
    props: ButtonProps & { isPrimaryAction?: boolean },
    refProp: ForwardedRef<any>
  ) => {
    const { children, asChild, isPrimaryAction, ...rest } = props
    const internalRef = useRef<HTMLButtonElement>(null)
    const finalRef = useMergeRefs([refProp, internalRef])

    // Handle Cmd/Ctrl enter
    useEffect(() => {
      if (!props.isPrimaryAction) return
      const handleKeyDown = createKeyboardShortcutHandler(
        { key: 'Enter', modifiers: ['mod'] },
        e => {
          e.preventDefault()
          internalRef.current?.click?.()
        }
      )
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }, [props.isPrimaryAction])

    return (
      <Button
        ref={finalRef}
        variant="highContrast"
        size="small"
        {...(isPrimaryAction
          ? {
              shortcutKey: getKeyboardShortcutString({
                key: 'Enter',
                modifiers: ['mod']
              })
            }
          : {})}
        {...rest}
      >
        {children}
      </Button>
    )
  }
)
ButtonModalAction.displayName = 'ModalActionButton'

const ButtonModalCancel = forwardRef(
  (props: ButtonProps, ref: ForwardedRef<any>) => {
    const { children, asChild, ...rest } = props
    return (
      <Button ref={ref} variant="secondary" size="small" {...rest}>
        {children || 'Cancel'}
      </Button>
    )
  }
)
ButtonModalCancel.displayName = 'ModalCancelButton'

const ModalConsts = {
  SIZES: MODAL_SIZES,
  VARIANTS: MODAL_VARIANTS
}

export {
  ButtonModalAction,
  ButtonModalCancel,
  ModalConsts,
  ModalContext,
  ModalContextProvider,
  ModalHeader,
  useModalContext
}
export type { ModalContextValue, ModalSize, ModalVariant }
