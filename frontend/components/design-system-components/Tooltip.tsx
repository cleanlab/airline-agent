'use client'

import type { Placement } from '@floating-ui/react'
import {
  arrow,
  autoUpdate,
  flip,
  FloatingDelayGroup,
  FloatingPortal,
  offset,
  shift,
  useDelayGroup,
  useDismiss,
  useFloating,
  useFocus,
  useHover,
  useInteractions,
  useMergeRefs,
  useRole
} from '@floating-ui/react'
import { AnimatePresence, usePresence } from 'motion/react'
import type {
  ComponentPropsWithoutRef,
  ElementRef,
  ForwardedRef,
  HTMLProps,
  ReactElement,
  ReactNode
} from 'react'
import {
  cloneElement,
  createContext,
  forwardRef,
  isValidElement,
  memo,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState
} from 'react'

import {
  getSideAlignment,
  TOOLTIP_ARROW_HEIGHT,
  TooltipArrow
} from './TooltipArrow'

/**
 * Configuration options for the Tooltip component.
 */
type TooltipOptions = {
  /**
   * Whether the tooltip should be initially open.
   * @default false
   */
  initialOpen?: boolean
  /**
   * The preferred placement of the tooltip relative to its trigger.
   * @default 'top'
   */
  placement?: Placement
  /**
   * Controlled open state. When provided, the tooltip becomes controlled.
   * @default undefined
   */
  open?: boolean
  /**
   * Callback function called when the open state changes.
   * @param open - The new open state
   */
  onOpenChange?: (open: boolean) => void
  /**
   * The distance in pixels between the tooltip and its trigger.
   * @default 4
   */
  sideOffset?: number
  /**
   * The minimum distance in pixels between the tooltip and the viewport edge.
   * @default 12
   */
  collisionPadding?: number
  /**
   * The minimum distance in pixels between the arrow and the tooltip content edge.
   * @default 4
   */
  arrowPadding?: number
  /**
   * Whether the tooltip is disabled. When disabled, the tooltip will not show.
   * @default false
   */
  disabled?: boolean
  /**
   * The visual variant of the tooltip.
   * - `default`: Small tooltip with dark background
   * - `detail`: Larger tooltip with light background for detailed content
   * @default 'default'
   */
  variant?: 'default' | 'detail'
}

// Fixes build error with floating-ui:
//   The inferred type of 'useTooltip' cannot be named without a reference to '...'.
import type {} from '@floating-ui/react-dom'
import { cn, tv } from '@/lib/utils/tailwindUtils'

const ANIMATION_TIMEOUT_MS = 300

const tooltipVariants = tv({
  slots: {
    content: [
      // Base styles
      'pointer-events-none relative rounded-1 shadow-elev-0 outline outline-1 -outline-offset-1 outline-tooltip-border',
      // Animation styles
      'duration-100 animate-in fade-in-0 zoom-in-75 fill-mode-forwards data-[state=closed]:duration-100 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-75'
    ],
    arrow: ''
  },
  variants: {
    variant: {
      default: {
        content:
          'type-caption max-w-[300px] bg-tooltip-bg px-4 py-2 text-tooltip-text',
        arrow: 'fill-tooltip-bg'
      },
      detail: {
        content: 'max-w-[400px] bg-surface-2 p-4',
        arrow: 'fill-surface-2'
      }
    }
  },
  defaultVariants: {
    variant: 'default'
  }
})

/**
 * Custom hook that provides tooltip functionality using floating-ui.
 * Handles positioning, interactions, and animations.
 *
 * @param options - Configuration options for the tooltip
 * @returns Object containing tooltip state, refs, and interaction handlers
 */
function useTooltip({
  initialOpen = false,
  placement = 'top',
  open: controlledOpen,
  onOpenChange: setControlledOpen,
  sideOffset = 4,
  collisionPadding = 12,
  arrowPadding = 4,
  disabled = false,
  variant = 'default'
}: TooltipOptions = {}) {
  const [uncontrolledOpen, setUncontrolledOpen] = useState(initialOpen)
  const arrowRef = useRef<HTMLDivElement>(null)

  const open = disabled ? false : (controlledOpen ?? uncontrolledOpen)
  const setOpen = setControlledOpen ?? setUncontrolledOpen

  const data: ReturnType<typeof useFloating> = useFloating({
    placement,
    open,
    onOpenChange: setOpen,
    whileElementsMounted: autoUpdate,
    middleware: [
      offset(sideOffset + TOOLTIP_ARROW_HEIGHT),
      flip({
        crossAxis: placement.includes('-'),
        fallbackAxisSideDirection: 'start',
        padding: collisionPadding
      }),
      shift({ padding: collisionPadding }),
      arrow({ element: arrowRef, padding: arrowPadding })
    ]
  })
  const { delay } = useDelayGroup(data.context)

  const context = data.context

  const hover = useHover(context, {
    move: false,
    enabled: disabled ? false : controlledOpen == null,
    delay
  })
  const focus = useFocus(context, {
    enabled: controlledOpen == null
  })
  const dismiss = useDismiss(context)
  const role = useRole(context, { role: 'tooltip' })

  const interactions = useInteractions([hover, focus, dismiss, role])

  return useMemo(
    () => ({
      open,
      setOpen,
      ...interactions,
      ...data,
      refs: {
        ...data.refs,
        arrow: arrowRef
      },
      variant
    }),
    [open, setOpen, interactions, data, variant]
  )
}

type ContextType =
  | (ReturnType<typeof useTooltip> & { variant?: 'default' | 'detail' })
  | null

const TooltipContext = createContext<ContextType>(null)

/**
 * Hook to access the tooltip context.
 * @throws Error if used outside of a Tooltip component
 * @returns The tooltip context
 */
const useTooltipContext = () => {
  const context = useContext(TooltipContext)

  if (context == null) {
    throw new Error('Tooltip components must be wrapped in <Tooltip />')
  }

  return context
}

/**
 * The trigger element for the tooltip. This component wraps the child element
 * and adds the necessary event handlers for tooltip interactions.
 */
const TooltipTrigger = forwardRef<HTMLElement, HTMLProps<HTMLElement>>(
  function TooltipTrigger({ children, ...props }, propRef) {
    const context = useTooltipContext()
    const childrenRef = (children as any).ref
    const ref = useMergeRefs([context.refs.setReference, propRef, childrenRef])

    if (isValidElement(children)) {
      return cloneElement(
        children,
        context.getReferenceProps({
          ref,
          ...props,
          ...(children.props && typeof children.props === 'object'
            ? (children.props as Record<string, unknown>)
            : {}),
          // @ts-expect-error data attribute for state
          'data-state': context.open ? 'open' : 'closed'
        })
      )
    } else {
      throw new Error(
        'TooltipTrigger requires a valid React element as its child'
      )
    }
  }
)

/**
 * Portal wrapper for tooltip content with animation support.
 */
const TooltipContentPortal = ({
  open,
  children
}: {
  open: boolean
  children: ReactElement
}) => {
  return (
    <AnimatePresence>
      {open && <FloatingPortal key="tooltip">{children}</FloatingPortal>}
    </AnimatePresence>
  )
}

/**
 * The content container for the tooltip. Handles positioning, styling, and animations.
 */
const TooltipContent = forwardRef<
  ElementRef<'div'>,
  ComponentPropsWithoutRef<'div'>
>(({ className, children, style, ...props }, refProp) => {
  const context = useTooltipContext()
  const ref = useMergeRefs([context.refs.setFloating, refProp])
  const { side, alignment } = getSideAlignment(context.placement)
  const arrow = context.middlewareData.arrow
  const arrowXOffset = arrow && arrow?.x !== null ? `${arrow.x}px` : '50%'
  const arrowYOffset = arrow && arrow?.y !== null ? `${arrow.y}px` : '50%'
  const [isPresent, safeToRemove] = usePresence()

  useEffect(() => {
    if (!isPresent) {
      const timeout = setTimeout(safeToRemove, ANIMATION_TIMEOUT_MS)
      return () => clearTimeout(timeout)
    }
  }, [isPresent, safeToRemove])

  const transformOrigin = {
    top: `${arrowXOffset} calc(100% + ${TOOLTIP_ARROW_HEIGHT}px)`,
    left: `calc(100% + ${TOOLTIP_ARROW_HEIGHT}px) ${arrowYOffset}`,
    right: `-${TOOLTIP_ARROW_HEIGHT}px ${arrowYOffset}`,
    bottom: `${arrowXOffset} -${TOOLTIP_ARROW_HEIGHT}px`
  }[side]

  const variant = context.variant || 'default'
  const { content: contentClasses, arrow: arrowClasses } = tooltipVariants({
    variant
  })

  return (
    <div
      ref={ref}
      style={{
        zIndex: 100,
        ...context.floatingStyles,
        ...style
      }}
      {...context.getFloatingProps(props)}
    >
      <div
        data-side={side}
        data-alignment={alignment || 'center'}
        data-state={context.open ? 'open' : 'closed'}
        className={cn(contentClasses(), className)}
        {...props}
        style={{ transformOrigin: transformOrigin }}
      >
        {children}
        <TooltipArrow
          ref={context.refs.arrow as any}
          context={context.context}
          data-arrow=""
          className={arrowClasses()}
        />
      </div>
    </div>
  )
})
TooltipContent.displayName = 'TooltipContent'

/**
 * Props for the Tooltip component.
 */
type TooltipProps = {
  /**
   * The trigger element that will show the tooltip on hover/focus.
   * Must be a valid React element.
   */
  children: ReactElement
  /**
   * The content to display inside the tooltip.
   */
  content: ReactNode
  /**
   * The visual variant of the tooltip.
   * - `default`: Small tooltip with dark background
   * - `detail`: Larger tooltip with light background for detailed content
   * @default 'default'
   */
  variant?: 'default' | 'detail'
} & TooltipOptions

type TooltipRef = ForwardedRef<HTMLDivElement>

/**
 * Base implementation of the Tooltip component.
 */
const TooltipBase = (
  {
    children,
    content,
    initialOpen,
    // useTooltip() options
    /**
     * The placement of the tooltip.
     * @default 'top'
     */
    placement,
    /**
     * Controlled open state.
     * @default undefined
     */
    open,
    onOpenChange,
    sideOffset,
    /**
     * Minimum distance between the tooltip and the viewport.
     * @default 12
     */
    collisionPadding,
    /**
     * Minimum inline distance between the arrow and the tooltip content.
     * @default 4
     */
    arrowPadding,
    disabled = false,
    /**
     * The variant of the tooltip.
     * @default 'default'
     */
    variant = 'default',
    // TooltipContent props
    ...props
  }: TooltipProps,
  ref: TooltipRef
) => {
  // This can accept any props as options, e.g. `placement`,
  // or other positioning options.
  const tooltip = useTooltip({
    initialOpen,
    placement,
    open,
    onOpenChange,
    sideOffset,
    collisionPadding,
    arrowPadding,
    disabled,
    variant
  })

  return (
    <TooltipContext.Provider value={tooltip}>
      <TooltipTrigger>{children}</TooltipTrigger>
      <TooltipContentPortal open={tooltip.open}>
        <TooltipContent ref={ref} {...props}>
          {content}
        </TooltipContent>
      </TooltipContentPortal>
    </TooltipContext.Provider>
  )
}

const TooltipBaseForwardRef = forwardRef(TooltipBase)

/**
 * A flexible tooltip component that displays contextual information when hovering or focusing on an element.
 *
 * @example
 * ```
 * <Tooltip content="This is a tooltip">
 *   <button>Hover me</button>
 * </Tooltip>
 * ```
 *
 * @example
 * ```
 * // Detailed tooltip with custom placement
 * <Tooltip
 *   content="This is a detailed tooltip with more information"
 *   variant="detail"
 *   placement="bottom-start"
 * >
 *   <button>Hover me</button>
 * </Tooltip>
 * ```
 *
 * @example
 * ```
 * // Controlled tooltip
 * const [isOpen, setIsOpen] = useState(false)
 *
 * <Tooltip
 *   content="Controlled tooltip"
 *   open={isOpen}
 *   onOpenChange={setIsOpen}
 * >
 *   <button onClick={() => setIsOpen(!isOpen)}>Click me</button>
 * </Tooltip>
 * ```
 */
const Tooltip = memo(
  forwardRef((props: TooltipProps, ref: TooltipRef) => {
    if (!props.content) {
      return props.children
    }
    return <TooltipBaseForwardRef ref={ref} {...props} />
  })
)
Tooltip.displayName = 'Tooltip'

/**
 * Provider component that manages tooltip delay groups for coordinated tooltip behavior.
 * Wrap your application or tooltip-containing components with this provider to enable
 * smooth transitions when moving between multiple tooltips.
 *
 * @example
 * ```
 * <TooltipProvider>
 *   <Tooltip content="First tooltip">
 *     <button>Button 1</button>
 *   </Tooltip>
 *   <Tooltip content="Second tooltip">
 *     <button>Button 2</button>
 *   </Tooltip>
 * </TooltipProvider>
 * ```
 */
const TooltipProvider = memo(({ children }: { children: ReactNode }) => (
  <FloatingDelayGroup delay={{ open: 500, close: 0 }} timeoutMs={400}>
    {children}
  </FloatingDelayGroup>
))

// Export all components and functions at the end of the file
export { Tooltip, TooltipProvider, useTooltip }
