'use client'

import { IconFrameButton } from '@cleanlab/design-system/components'
import { IconMoon, IconSun } from '@cleanlab/design-system/icons'
import { useTheme } from 'next-themes'

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
