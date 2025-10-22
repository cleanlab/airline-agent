import type { ComponentPropsWithoutRef, ReactNode } from 'react'
import { cn } from '@/lib/utils/tailwindUtils'
import type { AnimationPlaybackControls } from 'motion/react'
import { useAnimate } from 'motion/react'
import { useEffect, useState } from 'react'

const SuggestedQuestion = ({
  isInputDisabled,
  className,
  children,
  ...props
}: {
  className?: string
  isInputDisabled?: boolean
  children: ReactNode
} & ComponentPropsWithoutRef<'button'>) => {
  return (
    <button
      type="button"
      className={cn(
        'type-body-100 flex min-w-fit items-center rounded-2 border border-border-0 bg-surface-1 px-5 py-3 text-start text-text-primary md:type-body-200 hover:bg-surface-1-hover active:bg-surface-1-active',
        isInputDisabled ? 'cursor-not-allowed' : 'cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}

const QuestionGrid = ({
  children,
  width,
  animationDuration = 45
}: {
  children: ReactNode
  width: number
  animationDuration?: number
}) => {
  const [scope, animate] = useAnimate()
  const [controls, setControls] = useState<AnimationPlaybackControls | null>(
    null
  )
  const [contentWidth, setContentWidth] = useState(0)

  useEffect(() => {
    if (scope.current) {
      const fullWidth = scope.current.scrollWidth / 2
      const computedGap = parseInt(getComputedStyle(scope.current).gap) / 2

      // it's fine: won't cause infinite loop
      // eslint-disable-next-line @eslint-react/hooks-extra/no-direct-set-state-in-use-effect
      setContentWidth(fullWidth + computedGap)
    }
  }, [scope])

  useEffect(() => {
    if (!contentWidth) return

    const isReduced = window.matchMedia(
      `(prefers-reduced-motion: reduce)`
    ).matches

    animate(scope.current, { opacity: [0, 1] }, { duration: 2, ease: 'easeIn' })

    const scrollerControls = animate(
      scope.current,
      {
        transform: [`translateX(0px)`, `translateX(-${contentWidth}px)`]
      },
      {
        duration: isReduced ? animationDuration * 2 : animationDuration,
        ease: 'linear',
        repeat: Infinity
      }
    )

    // it's fine: won't cause infinite loop
    // eslint-disable-next-line @eslint-react/hooks-extra/no-direct-set-state-in-use-effect
    setControls(scrollerControls)

    return () => {
      scrollerControls.stop()
    }
  }, [animate, animationDuration, scope, contentWidth])

  return (
    <div className="overflow-hidden" style={{ width }}>
      {/* Screen reader accessible static version */}
      <div className="sr-only">{children}</div>

      {/* Animated version - hidden from screen readers */}
      <div
        className="relative overflow-hidden"
        aria-hidden="true"
        onMouseEnter={() => controls?.pause()}
        onMouseLeave={() => controls?.play()}
      >
        <div ref={scope} className="flex gap-6 whitespace-nowrap sm:gap-8">
          {children}
          {children}
        </div>
      </div>
    </div>
  )
}

export function EmptyScreen() {
  const isDefaultAssistant = true

  if (isDefaultAssistant) {
    return (
      <div className="flex h-full grow flex-col items-center justify-center gap-8" />
    )
  }
  return null
}
