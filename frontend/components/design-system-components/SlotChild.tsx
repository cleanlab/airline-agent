'use client'

import { useMergeRefs } from '@floating-ui/react'
// Solves issue with using Slots with nested children
// https://github.com/radix-ui/primitives/issues/1825#issuecomment-1865423970
import { Slot as SlotPrimitive } from 'radix-ui'
import type { ForwardedRef, ReactNode } from 'react'
import { cloneElement, forwardRef, isValidElement } from 'react'

import { mergeProps } from '@/lib/utils/mergeProps'

const Slot = SlotPrimitive.Root
type SlotChildProps = {
  asChild?: boolean
  child: ReactNode
  children: ReactNode | ((child: ReactNode) => ReactNode)
}

function getContent({ children }: SlotChildProps, arg: ReactNode) {
  return typeof children === 'function' ? children(arg) : <>{children}</>
}

const SlotChild = forwardRef(
  (props: SlotChildProps, forwardedRef: ForwardedRef<any>) => {
    const { asChild, child, children, ...attrs } = props
    const mergedRef = useMergeRefs([(child as any).ref, forwardedRef])

    if (!isValidElement(child)) {
      return asChild ? null : <>{getContent(props, child)}</>
    }

    const slot = (child as any).type === Slot
    const childSlot = !!(child as any).props?.asChild

    return (
      <>
        {cloneElement(
          child,
          {
            ...mergeProps((child as any).props, attrs),
            // @ts-expect-error
            ref: mergedRef
          },
          slot || childSlot ? (
            <SlotChild
              asChild={asChild}
              child={(child as any).props.children}
              children={children}
            />
          ) : (
            getContent(props, (child as any).props.children)
          )
        )}
      </>
    )
  }
)

export type { SlotChildProps }
export { SlotChild }
