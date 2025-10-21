import type { TypographyStack, TypographyStyle } from './consts'
import { DISPLAY_FONT_FAMILY, FONT_WEIGHTS } from './consts'

const displayBaseStyle = {
  fontFamily: DISPLAY_FONT_FAMILY,
  letterSpacing: '0px',
  fontWeight: FONT_WEIGHTS.semibold,
  textTransform: 'none',
} as const satisfies Partial<TypographyStyle>

export const display = {
  '500': {
    ...displayBaseStyle,
    fontSize: '88px',
    lineHeight: '104px',
  },
  '400': {
    ...displayBaseStyle,
    fontSize: '64px',
    lineHeight: '84px',
  },
  '300': {
    ...displayBaseStyle,
    fontSize: '48px',
    lineHeight: '56px',
  },
  '250': {
    ...displayBaseStyle,
    fontSize: '40px',
    lineHeight: '48px',
  },
  '200': {
    ...displayBaseStyle,
    fontSize: '32px',
    lineHeight: '40px',
  },
  '100': {
    ...displayBaseStyle,
    fontSize: '24px',
    lineHeight: '32px',
  },
  '50': {
    ...displayBaseStyle,
    fontSize: '20px',
    lineHeight: '24px',
  },
} as const satisfies TypographyStack
