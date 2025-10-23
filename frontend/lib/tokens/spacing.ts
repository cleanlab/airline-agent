// Must not use @ import path aliases so tailwind can import this

export const spacingPx = {
  px: 1,
  '0': 0,
  '1': 2,
  '2': 4,
  '3': 6,
  '4': 8,
  '5': 12,
  '6': 16,
  '7': 20,
  '8': 24,
  '9': 32,
  '10': 40,
  '11': 48,
  '12': 64,
  '13': 80,
  '14': 96,
} as const

export const spacing = Object.fromEntries(
  Object.entries(spacingPx).map(([key, value]) => [key, `${value}px`])
) as { [K in keyof typeof spacingPx]: `${(typeof spacingPx)[K]}px` }
