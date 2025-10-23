// Must not use @ import path aliases so tailwind can import this

const borderRadiusBase = {
  none: '0',
  '1': '4px',
  '2': '8px',
  '3': '12px',
  '4': '16px',
  full: '9999px',
} as const

export const borderRadius = {
  default: borderRadiusBase['3'],
  ...borderRadiusBase,
} as const
