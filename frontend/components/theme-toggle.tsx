'use client'

import { useTheme } from 'next-themes'
import { IconMoon, IconSun } from '@cleanlab/design-system/icons'
import { IconFrameButton } from '@cleanlab/design-system/components'

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
