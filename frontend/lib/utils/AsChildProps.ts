import { type ReactElement } from 'react'

export type AsChildProps<DefaultElementProps = Record<string, never>> =
  | ({
      /**
       * If true, the component will be rendered as its child instead of its
       * default element. Properties intended to be passed as html attributes on
       * the child (except for `className`) and most event handlers should be
       * set on the child instead of the parent.
       */
      asChild?: false | undefined | null
    } & DefaultElementProps)
  | {
      /**
       * If true, the component will be rendered as its child instead of its
       * default element. Properties intended to be passed as html attributes on
       * the child (except for `className`) and most event handlers should be
       * set on the child instead of the parent.
       */
      asChild: true
      className?: string
      children: ReactElement
    }
