'use client'

import { useTheme } from 'next-themes'
import { IconMoon, IconSun } from './icons'
import { IconFrameButton } from './design-system-components/IconFrameButton'

export const ThemeToggle = () => {
  const { resolvedTheme, setTheme } = useTheme()
  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
  }

  return (
    <IconFrameButton
      icon={resolvedTheme === 'dark' ? <IconSun /> : <IconMoon />}
      aria-label="Toggle theme"
      variant="level1"
      size="small"
      onClick={toggleTheme}
    />
  )
}
