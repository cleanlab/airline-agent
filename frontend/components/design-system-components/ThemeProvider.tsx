'use client'

import type { ReactNode } from 'react'
import { createContext, memo, useCallback, useContext, useEffect, useMemo, useState } from 'react'

const Themes = { Light: 'light', Dark: 'dark' } as const
type Theme = (typeof Themes)[keyof typeof Themes]

type ThemeConfig = {
  attrName?: string
  defaultMode?: Theme
  htmlElt?: HTMLElement
}

const DEFAULT_CONFIG = {
  attrName: 'data-theme',
  defaultMode: Themes.Light,
} as const satisfies ThemeConfig

const useThemeObserver = ({
  defaultMode = DEFAULT_CONFIG.defaultMode,
  attrName = DEFAULT_CONFIG.attrName,
  htmlElt: htmlEltProp,
}: ThemeConfig) => {
  let htmlElt = htmlEltProp
  if (!htmlElt && typeof document !== 'undefined') {
    htmlElt = document.documentElement
  }
  const [thisTheme, setThisTheme] = useState(() => htmlElt?.getAttribute(attrName) || defaultMode)
  const observerCb = useCallback(() => {
    const themeAttr = htmlElt?.getAttribute(attrName) || defaultMode

    setThisTheme(themeAttr)
  }, [attrName, defaultMode, htmlElt])
  const config = useMemo(
    () => ({
      attributes: true,
      attributeFilter: [attrName],
    }),
    [attrName]
  )
  useEffect(() => {
    if (!htmlElt) return

    const observer = new MutationObserver(observerCb)
    observer.observe(htmlElt, config)
    return () => {
      observer.disconnect()
    }
  }, [attrName, config, htmlElt, observerCb])
  const setTheme = useCallback(
    (theme: Theme) => {
      htmlElt?.setAttribute(attrName, theme)
      setThisTheme(theme)
    },
    [attrName, htmlElt]
  )

  const ret = useMemo(() => {
    return { theme: thisTheme, setTheme }
  }, [thisTheme, setTheme])
  return ret
}

const ThemeContext = createContext<ReturnType<typeof useThemeObserver> | undefined>(undefined)

const ThemeProviderBase = ({ children, ...config }: ThemeConfig & { children: ReactNode }) => {
  const theme = useThemeObserver(config)

  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
}

const ThemeProvider = memo(ThemeProviderBase, (prevProps: any, nextProps: any) => {
  return prevProps.children === nextProps.children
})

const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }

  return context
}

export { ThemeProvider, Themes, useTheme }
export type { Theme }
