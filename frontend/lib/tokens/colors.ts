// Must not use @ import path aliases so tailwind can import this
import { darkModeColors } from './colorsDark'
import { lightModeColors } from './colorsLight'

export const colors = {
  light: lightModeColors,
  dark: darkModeColors,
} as const
