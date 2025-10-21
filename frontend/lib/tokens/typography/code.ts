import type {} from 'csstype'

import type { TypographyStack, TypographyStyle } from './consts'
import { CODE_FONT_FAMILY, FONT_WEIGHTS } from './consts'
import { generateStackWeights } from './generateStackWeights'

const codeBaseStyle = {
  fontFamily: CODE_FONT_FAMILY,
  letterSpacing: '0px',
  fontWeight: FONT_WEIGHTS.normal,
  textTransform: 'none',
} as const satisfies Partial<TypographyStyle>

const codeBase = {
  '300': {
    ...codeBaseStyle,
    fontSize: '18px',
    lineHeight: '28px',
  },
  '200': {
    ...codeBaseStyle,
    fontSize: '16px',
    lineHeight: '24px',
  },
  '100': {
    ...codeBaseStyle,
    fontSize: '14px',
    lineHeight: '20px',
  },
  '50': {
    ...codeBaseStyle,
    fontSize: '11px',
    lineHeight: '15px',
  },
} as const satisfies TypographyStack

export const code = generateStackWeights(codeBase, ['normal', 'bold'])
