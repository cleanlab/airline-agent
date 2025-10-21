import type { TypographyStack, TypographyStyle } from './consts'
import { BODY_FONT_FAMILY, FONT_WEIGHTS } from './consts'
import { generateStackWeights } from './generateStackWeights'

const bodyBaseStyle = {
  fontFamily: BODY_FONT_FAMILY,
  letterSpacing: '0px',
  fontWeight: FONT_WEIGHTS.normal,
  textTransform: 'none',
} as const satisfies Partial<TypographyStyle>

const bodyBase = {
  '300': {
    ...bodyBaseStyle,
    fontSize: '18px',
    lineHeight: '28px',
  },
  '200': {
    ...bodyBaseStyle,
    fontSize: '16px',
    lineHeight: '24px',
  },
  '100': {
    ...bodyBaseStyle,
    fontSize: '14px',
    lineHeight: '20px',
  },
} as const satisfies TypographyStack
export const body = generateStackWeights(bodyBase, [
  'light',
  'normal',
  'medium',
  'semibold',
  'bold',
  'link',
])
