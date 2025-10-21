import { prefixKeys } from '../../utils/transformKeys'
import type { TypographyStack, TypographyStyle } from './consts'
import { BODY_FONT_FAMILY, FONT_WEIGHTS, MARKETING_PREFIX } from './consts'

const diagramBlockBase = {
  fontFamily: BODY_FONT_FAMILY,
  letterSpacing: '0px',
  textTransform: 'none',
  fontSize: '12px',
  lineHeight: '16px',
} as const satisfies Partial<TypographyStyle>

const diagramChartBase = {
  fontFamily: BODY_FONT_FAMILY,
  letterSpacing: '0px',
  textTransform: 'none',
  fontSize: '12px',
  lineHeight: '16px',
} as const satisfies Partial<TypographyStyle>

const listBase = {
  fontFamily: BODY_FONT_FAMILY,
  letterSpacing: '0px',
  textTransform: 'none',
  fontWeight: FONT_WEIGHTS.normal,
} as const satisfies Partial<TypographyStyle>

const utils = {
  'diagram-block': {
    ...diagramBlockBase,
    fontWeight: FONT_WEIGHTS.normal,
  },
  'diagram-block-medium': {
    ...diagramBlockBase,
    fontWeight: FONT_WEIGHTS.medium,
  },
  'diagram-chart': {
    ...diagramChartBase,
    fontWeight: FONT_WEIGHTS.normal,
    fontSize: '11px',
    lineHeight: '14px',
  },
  'diagram-chart-medium': {
    ...diagramBlockBase,
    fontWeight: FONT_WEIGHTS.medium,
    fontSize: '11px',
    lineHeight: '14px',
  },
  'list-100': {
    ...listBase,
    fontSize: '14px',
    lineHeight: '21px',
  },
  'list-200': {
    ...listBase,
    fontSize: '16px',
    lineHeight: '24px',
  },
  'list-300': {
    ...listBase,
    fontSize: '18px',
    lineHeight: '28px',
  },
} as const satisfies TypographyStack

export const marketingUtilities = prefixKeys(utils, `${MARKETING_PREFIX}-`)
