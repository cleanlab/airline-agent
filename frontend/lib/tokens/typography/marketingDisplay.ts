import type { TypographyStack, TypographyStyle } from './consts'
import { DISPLAY_FONT_FAMILY, FONT_WEIGHTS } from './consts'

const marketingDisplayBaseStyle = {
  fontFamily: DISPLAY_FONT_FAMILY,
  letterSpacing: '0px',
  // figma calls for ultralight, but browser still renders it too thick. Using thin as a workaround, but seems off.
  fontWeight: FONT_WEIGHTS.thin,
  textTransform: 'none',
} as const satisfies Partial<TypographyStyle>

export const marketingDisplay = {
  '700': {
    ...marketingDisplayBaseStyle,
    fontSize: '126px',
    lineHeight: '144px',
  },
  '600': {
    ...marketingDisplayBaseStyle,
    fontSize: '96px',
    lineHeight: '112px',
  },
  '400': {
    ...marketingDisplayBaseStyle,
    fontSize: '64px',
    lineHeight: '70px',
  },
  '300': {
    ...marketingDisplayBaseStyle,
    fontSize: '42px',
    lineHeight: '49px',
  },
  '200': {
    ...marketingDisplayBaseStyle,
    fontSize: '32px',
    lineHeight: '37px',
  },
  '100': {
    ...marketingDisplayBaseStyle,
    fontSize: '24px',
    lineHeight: '30px',
  },
} as const satisfies TypographyStack
