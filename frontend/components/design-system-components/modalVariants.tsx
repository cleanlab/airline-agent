'use client'

import { tv } from '@/lib/utils/tailwindUtils'
import type { ModalSize } from './Modal.common'

export const modalVariants = {
  /**
   * For ModalAlertOverlay and ModalDialogOverlay
   **/
  overlay: tv({
    base: 'fixed inset-0 z-50 bg-[var(--cl-overlay-bg)] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0'
  }),
  /**
   * For ModalAlertContent and ModalDialogContent
   **/
  content: tv({
    slots: {
      base:
        'fixed left-[50%] top-[50%] z-50 flex w-full translate-x-[-50%] translate-y-[-50%] flex-col overflow-hidden rounded-2 border border-border-1 bg-modal-bg' +
        ' ' +
        // Give 24px minimum vertical margin to modal Except when modal would be
        // shorter than 320px Then give 8px minimum vertical margin But allow
        // shrinking below 320px height if it would exceed 100vh - (8px*2)
        'max-h-[min(100vh-(2*theme(spacing.4)),max(320px,calc(100vh-(2*theme(spacing.8)))))]' +
        ' ' +
        // Transition animation classes
        ' transition-opacity transition-transform duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%]',
      inner: 'flex w-full flex-col gap-6 overflow-auto'
    },
    variants: {
      // Main variants
      variant: {
        default: {},
        extended: {
          inner: 'gap-0 overflow-hidden'
        }
      },
      // Additional options
      size: {
        small: {
          base: 'w-[420px] max-w-[min(420px,calc(100vw-(theme(spacing.8))*2))]'
        },
        medium: {
          base: 'w-[520px] max-w-[min(520px,calc(100vw-(theme(spacing.8))*2))]'
        },
        large: {
          base: 'w-[640px] max-w-[min(640px,calc(100vw-(theme(spacing.8))*2))]'
        },
        xLarge: {
          base: 'w-[820px] max-w-[min(820px,calc(100vw-(theme(spacing.8))*2))]'
        }
      } satisfies Record<ModalSize, { base: string }>
    }
  }),
  /**
   * For ModalAlertHeader and ModalDialogHeader
   **/
  header: tv({
    slots: {
      base: 'flex w-full shrink-0 items-start gap-4 overflow-hidden px-8 pt-6 text-start',
      inner: 'flex shrink grow flex-col overflow-hidden'
    },
    variants: {
      variant: {
        default: {
          base: '',
          inner: ''
        },
        extended: {
          base: 'border-b border-b-border-1 pb-6',
          inner: ''
        }
      }
    }
  }),
  close: tv({ base: 'mt-1 flex shrink-0 items-center gap-4' }),
  /**
   * For ModalAlertTitle and ModalDialogTitle
   **/
  title: tv({
    base: 'type-body-300-medium break-words text-text-strong'
  }),
  /**
   * For ModalAlertDescription and ModalDialogDescription
   **/
  description: tv({
    base: 'type-body-200 m-0 mt-1 text-text-faint [&>p+p]:mt-2'
  }),
  /**
   * For ModalDialogBody
   **/
  body: tv({
    base: 'shrink overflow-auto p-8'
  }),
  /**
   * For ModalAlertFooter and ModalDialogFooter
   **/
  footer: tv({
    base: 'flex flex-row-reverse gap-5 px-8 pb-6',
    variants: {
      variant: {
        default: '',
        extended: 'border-t border-t-border-1 pt-6'
      }
    }
  })
}
