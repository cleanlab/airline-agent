import type { TypographyStack, TypographyStyle } from './consts'
import { BODY_FONT_FAMILY, CODE_FONT_FAMILY } from './consts'
import { FONT_WEIGHTS } from './consts'

const badgeBaseStyle = {
  fontFamily: BODY_FONT_FAMILY,
  letterSpacing: '0px',
  fontWeight: FONT_WEIGHTS.medium,
  textTransform: 'none',
} as const satisfies Partial<TypographyStyle>

const badgeCodeBaseStyle = {
  ...badgeBaseStyle,
  fontFamily: CODE_FONT_FAMILY,
} as const satisfies Partial<TypographyStyle>

export const badge = {
  sm: {
    ...badgeBaseStyle,
    fontSize: '11px',
    lineHeight: '20px',
  },
  md: {
    ...badgeBaseStyle,
    fontSize: '12px',
    lineHeight: '24px',
  },
  lg: {
    ...badgeBaseStyle,
    fontSize: '14px',
    lineHeight: '28px',
  },
  'code-sm': {
    ...badgeCodeBaseStyle,
    fontSize: '11px',
    lineHeight: '20px',
  },
  'code-md': {
    ...badgeCodeBaseStyle,
    fontSize: '12px',
    lineHeight: '24px',
  },
  'code-lg': {
    ...badgeCodeBaseStyle,
    fontSize: '14px',
    lineHeight: '28px',
  },
} as const satisfies TypographyStack
