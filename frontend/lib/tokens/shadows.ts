// Must not use @ import path aliases so tailwind can import this
// Minimal local definition
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type WidenStringVals<T> = { [K in keyof T]: any }

const SHADOW_COLORS = {
  light: {
    1: 'var(--twc-neutral-600)',
    inner: 'var(--twc-neutral-600)'
  },
  dark: {
    1: '195 20% 96%',
    2: '0 0% 0%',
    inner: '223 12% 40%'
  }
} as const satisfies Record<
  'dark' | 'light',
  Partial<Record<'1' | '2' | 'inner', string>>
>

const shadowsLight = {
  'elev-0': `0px 1px 1px 0px hsl(${SHADOW_COLORS.light['1']} / 0.05), 0px 2px 2px 0px hsl(${SHADOW_COLORS.light['1']} / 0.05)`,
  'elev-1': `0px 2px 3px 0px hsl(${SHADOW_COLORS.light['1']} / 0.1), 0px 4px 1px -4px hsl(${SHADOW_COLORS.light['1']} / 0.05)`,
  'elev-2': `0px 2px 3px 0px hsl(${SHADOW_COLORS.light['1']} / 0.1), 0px 8px 16px -10px hsl(${SHADOW_COLORS.light['1']} / 0.2)`,
  'elev-3': `0px 2px 3px 0px hsl(${SHADOW_COLORS.light['1']} / 0.15), 0px 16px 16px -10px hsl(${SHADOW_COLORS.light['1']} / 0.2)`,
  'elev-4': `0px 2px 3px 0px hsl(${SHADOW_COLORS.light['1']} / 0.1), 0px 12px 28px 0px hsl(${SHADOW_COLORS.light['1']} / 0.25)`,
  inner: `0px 1px 2px 1px hsl(${SHADOW_COLORS.light.inner} / 0.1) inset`
} as const

const shadowsDark = {
  'elev-0': `0px 1px 2px -1px hsl(${SHADOW_COLORS.dark['1']} / 0.16), 0px 2px 4px 0px rgba(0, 0, 0, 0.4)`,
  'elev-1': `0px 1px 2px -1px hsl(${SHADOW_COLORS.dark['1']} / 0.16), 0px 2px 8px 0px rgba(0, 0, 0, 0.4)`,
  'elev-2': `0px 4px 8px 0px hsl(${SHADOW_COLORS.dark['2']} / 0.32)`,
  'elev-3': `0px 8px 16px 0px hsl(${SHADOW_COLORS.dark['2']} / 0.42)`,
  'elev-4': `0px 16px 32px 0px hsl(${SHADOW_COLORS.dark['2']} / 0.32), 0px 2px 24px 9px rgba(0, 0, 0, 0.32)`,
  inner: `0px 2px 4px 0px hsl(${SHADOW_COLORS.dark.inner} / 0.05) inset`
} as const satisfies WidenStringVals<typeof shadowsLight>

export const shadows = {
  light: shadowsLight,
  dark: shadowsDark
}
