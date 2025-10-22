import { useRef, useState } from 'react'
import { screens } from '@/tailwind/screens'
import useResizeObserver from './use-resize-observer'

const sortedScreensDesc = Object.entries(screens)
  .map(
    ([key, val]) =>
      [key, Number(removeNonDigits(val))] as [keyof typeof screens, number]
  )
  .sort((a, b) => {
    return b[1] - a[1]
  })

const getScreenFromWidth = (width: number): keyof typeof screens => {
  return (
    sortedScreensDesc.find(([, size]) => size <= width)?.[0] ??
    sortedScreensDesc[sortedScreensDesc.length - 1][0]
  )
}

export const useScreen = () => {
  const docRef = useRef(document.documentElement)
  const [screen, setScreen] = useState<keyof typeof screens | null>(() =>
    getScreenFromWidth(docRef.current.clientWidth)
  )
  useResizeObserver(docRef, () => {
    const newScreen = getScreenFromWidth(docRef.current.clientWidth)

    if (newScreen !== screen) {
      setScreen(newScreen)
    }
  })
  const isLessThan = (breakpoint: keyof typeof screens) => {
    return (
      sortedScreensDesc.findIndex(s => s[0] === breakpoint) >=
      sortedScreensDesc.findIndex(s => s[0] === screen)
    )
  }
  const isEqualOrGreaterThan = (breakpoint: keyof typeof screens) => {
    return (
      sortedScreensDesc.findIndex(s => s[0] === breakpoint) <
      sortedScreensDesc.findIndex(s => s[0] === screen)
    )
  }
  return { breakpoint: screen, isLessThan, isEqualOrGreaterThan }
}

function removeNonDigits(str: string): string {
  return str.replace(/\D/g, '')
}
