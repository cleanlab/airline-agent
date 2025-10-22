import type { TypographyStack, TypographyStyle } from './consts'
import { BODY_FONT_FAMILY } from './consts'
import { FONT_WEIGHTS } from './consts'

export const captionBase = {
  fontFamily: BODY_FONT_FAMILY,
  fontSize: '12px',
  lineHeight: '16px',
  letterSpacing: '0',
  fontWeight: FONT_WEIGHTS.normal,
  textTransform: 'none',
} as const satisfies TypographyStyle

export const overlineBase = {
  fontFamily: BODY_FONT_FAMILY,
  fontSize: '12px',
  lineHeight: '18px',
  letterSpacing: '0.5px',
  fontWeight: FONT_WEIGHTS.medium,
  textTransform: 'uppercase',
} as const satisfies TypographyStyle

export const utilities = {
  label: {
    fontFamily: BODY_FONT_FAMILY,
    fontSize: '12px',
    lineHeight: '16px',
    letterSpacing: '0.5px',
    fontWeight: FONT_WEIGHTS.semibold,
    textTransform: 'none',
  },
  overline: overlineBase,
  'overline-lg': {
    ...overlineBase,
    fontSize: '16px',
    lineHeight: '24px',
  },
  'overline-sm': {
    ...overlineBase,
    fontSize: '10px',
    lineHeight: '16px',
  },
  caption: captionBase,
  'caption-medium': {
    ...captionBase,
    fontWeight: FONT_WEIGHTS.medium,
  },
  'caption-semibold': {
    ...captionBase,
    fontWeight: FONT_WEIGHTS.semibold,
  },
  'caption-bold': {
    ...captionBase,
    fontWeight: FONT_WEIGHTS.bold,
  },
  kbd: {
    fontFamily: BODY_FONT_FAMILY,
    fontSize: '12px',
    lineHeight: '12px',
    letterSpacing: '0px',
    fontWeight: FONT_WEIGHTS.normal,
    textTransform: 'none',
  },
  'kbd-sm': {
    fontFamily: BODY_FONT_FAMILY,
    fontSize: '11px',
    lineHeight: '11px',
    letterSpacing: '0px',
    fontWeight: FONT_WEIGHTS.normal,
    textTransform: 'none',
  },
  'kbd-xs': {
    fontFamily: BODY_FONT_FAMILY,
    fontSize: '10px',
    lineHeight: '10px',
    letterSpacing: '0px',
    fontWeight: FONT_WEIGHTS.normal,
    textTransform: 'none',
  },
} as const satisfies TypographyStack
