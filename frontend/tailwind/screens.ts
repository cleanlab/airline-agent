import type { ScreensConfig } from 'tailwindcss/types/config'

export const screens = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1400px'
} as const satisfies ScreensConfig
