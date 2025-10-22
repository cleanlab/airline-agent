import type { TypographyStack, TypographyStyle } from './consts'
import { BODY_FONT_FAMILY, FONT_WEIGHTS } from './consts'

const buttonBaseStyle = {
  fontFamily: BODY_FONT_FAMILY,
  letterSpacing: '0px',
  fontWeight: FONT_WEIGHTS.medium,
  textTransform: 'none',
} as const satisfies Partial<TypographyStyle>

export const button = {
  lg: {
    ...buttonBaseStyle,
    fontSize: '16px',
    lineHeight: '24px',
  },
  md: {
    ...buttonBaseStyle,
    fontSize: '14px',
    lineHeight: '20px',
  },
  sm: {
    ...buttonBaseStyle,
    fontSize: '14px',
    lineHeight: '20px',
  },
  xs: {
    ...buttonBaseStyle,
    fontSize: '12px',
    lineHeight: '18px',
  },
} as const satisfies TypographyStack
