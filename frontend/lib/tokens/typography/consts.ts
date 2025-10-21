import type { CSSProperties } from 'react'

export type TypographyStyle = Required<
  Pick<
    CSSProperties,
    'fontFamily' | 'fontSize' | 'lineHeight' | 'letterSpacing' | 'fontWeight' | 'textTransform'
  >
>

export type TypographyStack<Key extends string = string> = Record<
  Key,
  | TypographyStyle
  | Record<
      string | Readonly<string>,
      TypographyStyle | Record<string | Readonly<string>, TypographyStyle>
    >
>

export const TYPOGRAPHY_PREFIX = 'type'

// These css custom props must be defined in the global styles via tailwind plugin
export const BODY_FONT_FAMILY = 'var(--cl-font-family-body)' as const
export const DISPLAY_FONT_FAMILY = 'var(--cl-font-family-display)' as const
export const CODE_FONT_FAMILY = 'var(--cl-font-family-code)' as const

export const FONT_FAMILIES = {
  display: DISPLAY_FONT_FAMILY,
  sans: BODY_FONT_FAMILY,
  mono: CODE_FONT_FAMILY,
} as const

export const FONT_WEIGHTS = {
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  link: '500',
} as const
export type FontWeight = keyof typeof FONT_WEIGHTS

export const MARKETING_PREFIX = 'mkt'
