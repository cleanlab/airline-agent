'use client'

import type { ComponentProps, ReactNode } from 'react'
import {
  ModalAlert,
  ModalAlertContent,
  ModalAlertDescription,
  ModalAlertFooter,
  ModalAlertHeader,
  ModalAlertTitle,
  ModalAlertTrigger
} from './ModalAlert'

/**
 * Shorthand component for creating basic `<ModalAlerts />`. Prefer this when
 * possible, but if you need more control over the component, feel free to use
 * this as a template for creating your own custom `<ModalAlert />` using the parts
 */
export const ModalAlertBasic = ({
  title,
  description,
  bodyContent,
  footerContent,
  onOpenAutoFocus,
  onCloseAutoFocus,
  onEscapeKeyDown,
  trigger,
  ...props
}: {
  title?: ReactNode
  description?: ReactNode
  bodyContent?: ReactNode
  footerContent?: ReactNode
  trigger?: ReactNode
} & Omit<ComponentProps<typeof ModalAlert>, 'children'> &
  Pick<
    ComponentProps<typeof ModalAlertContent>,
    'onOpenAutoFocus' | 'onCloseAutoFocus' | 'onEscapeKeyDown'
  >) => {
  return (
    <ModalAlert {...props}>
      {trigger && <ModalAlertTrigger asChild>{trigger}</ModalAlertTrigger>}
      <ModalAlertContent
        {...{ onOpenAutoFocus, onCloseAutoFocus, onEscapeKeyDown }}
      >
        {(title || description) && (
          <ModalAlertHeader>
            {title && <ModalAlertTitle>{title}</ModalAlertTitle>}
            {description && (
              <ModalAlertDescription>{description}</ModalAlertDescription>
            )}
          </ModalAlertHeader>
        )}
        <ModalAlertFooter>{footerContent}</ModalAlertFooter>
      </ModalAlertContent>
    </ModalAlert>
  )
}
