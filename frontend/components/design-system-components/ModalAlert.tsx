'use client'

import { AlertDialog as ADPrimitive } from 'radix-ui'
import type {
  ComponentProps,
  ComponentPropsWithoutRef,
  ComponentPropsWithRef,
  ElementRef,
  ForwardedRef,
  HTMLAttributes
} from 'react'
import { forwardRef, useMemo } from 'react'

import type { ButtonProps } from './Button'

import { cn } from '@/lib/utils/tailwindUtils'
import {
  ButtonModalAction,
  ButtonModalCancel,
  ModalContextProvider,
  ModalContextValue,
  ModalHeader,
  useModalContext
} from './Modal.common'
import { modalVariants } from './modalVariants'

/**
 * A modal alert component that can be used to display a brief dialog that
 * requires an action from the user. If provided an optional `<ModalAlertTrigger
 * />` component, that component will automatically open the dialog when
 * clicked.
 *
 * @param size - The width of the alert. Defaults to `medium`.
 * @param variant - The variant of the alert. Defaults to `default`. Use
 * `extended` sparingly to display longer, arbitrary content. Consider using a
 * `ModalDialog` for more complex content or content that does not require
 * immediate action.
 */
const ModalAlert = ({
  variant = 'default',
  size = 'medium',
  ...props
}: Partial<ModalContextValue> & ComponentProps<typeof ADPrimitive.Root>) => {
  const ctx = useMemo(() => ({ variant, size }), [size, variant])
  return (
    <ModalContextProvider value={ctx}>
      <ADPrimitive.Root {...props} />
    </ModalContextProvider>
  )
}

const ModalAlertTrigger = ADPrimitive.Trigger

const ModalAlertPortal = ADPrimitive.Portal

const ModalAlertOverlay = forwardRef<
  ElementRef<typeof ADPrimitive.Overlay>,
  ComponentPropsWithoutRef<typeof ADPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <ADPrimitive.Overlay
    className={cn(modalVariants.overlay(), className)}
    {...props}
    ref={ref}
  />
))
ModalAlertOverlay.displayName = ADPrimitive.Overlay.displayName

/**
 * The primary content box of the alert. Should contain the `<ModalAlertHeader>`
 */
const ModalAlertContent = forwardRef(
  (
    {
      className,
      children,
      ...props
    }: ComponentPropsWithoutRef<typeof ADPrimitive.Content>,
    ref: ComponentPropsWithRef<typeof ADPrimitive.Content>['ref']
  ) => {
    const { size, variant } = useModalContext()
    const { base: baseClass, inner: innerClass } = modalVariants.content({
      size,
      variant
    })
    return (
      <ModalAlertPortal>
        <ModalAlertOverlay />
        <ADPrimitive.Content
          ref={ref}
          className={cn(baseClass(), className)}
          {...props}
        >
          <div className={cn(innerClass())}>{children}</div>
        </ADPrimitive.Content>
      </ModalAlertPortal>
    )
  }
)
ModalAlertContent.displayName = ADPrimitive.Content.displayName

const ModalAlertHeader = ModalHeader

/**
 * Footer of the alert. Should contain the `<ModalAlertAction />` and
 * `<ModalAlertCancel />` components. Content is displayed right-to-left by
 * default.
 * @param param0
 * @returns
 */
const ModalAlertFooter = ({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) => {
  const { variant } = useModalContext()
  return (
    <div
      className={cn(
        modalVariants.footer({ variant }),

        className
      )}
      {...props}
    />
  )
}
ModalAlertFooter.displayName = 'ModalAlertFooter'

/**
 * The title of the alert. Should be provided as a child of the
 * `<ModalAlertHeader />` component.
 */
const ModalAlertTitle = forwardRef(
  (
    { className, ...props }: ComponentPropsWithoutRef<typeof ADPrimitive.Title>,
    ref: ComponentPropsWithRef<typeof ADPrimitive.Title>['ref']
  ) => (
    <ADPrimitive.Title
      ref={ref}
      className={cn(modalVariants.title(), className)}
      {...props}
    />
  )
)
ModalAlertTitle.displayName = 'ModalAlertTitle'

/**
 * An accessible description to be announced when the dialog is opened. Should
 * be provided as a child of the `<ModalAlertHeader />` component. Children
 * should be provided as `<p>` tags.
 */
const ModalAlertDescription = forwardRef<
  ElementRef<typeof ADPrimitive.Description>,
  ComponentPropsWithoutRef<typeof ADPrimitive.Description>
>(({ className, children, ...props }, ref) => {
  return (
    <ADPrimitive.Description
      ref={ref}
      className={cn(modalVariants.description(), className)}
      asChild
      {...props}
    >
      {props.asChild ? children : <div>{children}</div>}
    </ADPrimitive.Description>
  )
})
ModalAlertDescription.displayName = 'ModalAlertDescription'

/**
 * Action button for the alert. Will render as a `<Button variant="highContrast"
 * size="small" /> component or as the child component if `asChild` is true.
 * Automatically closes the alert when clicked, unless `preventDefault` is
 * called in the `onClick` handler. Should be provided as a child of the
 * <ModalAlertFooter /> component.
 */
const ModalAlertAction = forwardRef(
  (
    props: ButtonProps & { isPrimaryAction?: boolean },
    ref: ForwardedRef<any>
  ) => {
    const { children, asChild, isPrimaryAction, ...rest } = props
    if (!asChild) {
      return (
        <ADPrimitive.Action ref={ref} asChild>
          <ButtonModalAction {...rest} isPrimaryAction={isPrimaryAction}>
            {children}
          </ButtonModalAction>
        </ADPrimitive.Action>
      )
    }
    return (
      <ADPrimitive.Action ref={ref} asChild {...rest}>
        {children}
      </ADPrimitive.Action>
    )
  }
)
ModalAlertAction.displayName = 'ModalAlertAction'

/**
 * Cancel button for the alert. Will render as a `<Button variant="secondary"
 * size="small" /> component or as the child component if `asChild` is true.
 * Automatically closes the alert when clicked, unless `preventDefault` is
 * called in the `onClick` handler. Should be provided as a child of the
 * <ModalAlertFooter /> component.
 */
const ModalAlertCancel = forwardRef(
  (props: ButtonProps, ref: ForwardedRef<any>) => {
    const { children, asChild, ...rest } = props
    if (!asChild) {
      return (
        <ADPrimitive.Cancel ref={ref} asChild>
          <ButtonModalCancel {...rest}>
            {children || 'Cancel'}
          </ButtonModalCancel>
        </ADPrimitive.Cancel>
      )
    }
    return (
      <ADPrimitive.Cancel ref={ref} asChild {...rest}>
        {children || 'Cancel'}
      </ADPrimitive.Cancel>
    )
  }
)
ModalAlertCancel.displayName = 'ModalAlertCancel'

export {
  ModalAlert,
  ModalAlertAction,
  ModalAlertCancel,
  ModalAlertContent,
  ModalAlertDescription,
  ModalAlertFooter,
  ModalAlertHeader,
  ModalAlertTitle,
  ModalAlertTrigger
}
