import { roundNum } from './roundNum'

const DEFAULT_PRECISION = 3

type PercentPadding = 'start' | 'end' | 'none'

type RatioFormatterProps = {
  /** The ratio to format, must be between 0 and 1 */
  ratio: string | number
  /** The direction in which to round the number */
  roundDirection?: 'nearest' | 'up' | 'down'
  /** Whether for format as a percentage or a number between 0 and 1 */
  format?: 'decimal' | 'percent'
  /** The number of digits to display after the decimal point */
  precision?: number
  /**
   * Pads the string with empty characters to ensure consistent widths for percentages. Can pad either 'start' or 'end' of the string.
   */
  percentPadding?: PercentPadding
  /**
   * If true:
   *
   * If ratio <= 0, return the smallest number greater than zero that meets the
   * `precision` requirement
   *
   * If ratio >= 1, return the largest number less than 1 that meets the
   * `precision` requirements
   *
   * When precision is 1, the smallest number greater than zero is 0.1 and the
   * largest number less than 1 is 0.9
   * */
  probabilityMode?: boolean
}

const ratioFormatter = ({
  ratio,
  roundDirection,
  precision: precisionProp = DEFAULT_PRECISION,
  format,
  percentPadding,
  probabilityMode = false
}: RatioFormatterProps) => {
  const pNum = typeof ratio === 'string' ? parseFloat(ratio) : ratio
  if (ratio === undefined || ratio === null || isNaN(pNum)) {
    return '—'
  }

  if (precisionProp < 0) {
    precisionProp = 0
  }
  const calcPrecision = format === 'percent' ? precisionProp + 2 : precisionProp

  let ratioRounded = roundNum(pNum, calcPrecision, roundDirection)

  if (probabilityMode) {
    if (ratioRounded <= 0) {
      ratioRounded = Math.pow(10, -calcPrecision)
    } else if (ratioRounded >= 1) {
      ratioRounded = 1 - Math.pow(10, -calcPrecision)
    }
  }

  return ratioToString(ratioRounded, format, precisionProp, percentPadding)
}

function ratioToString(
  ratio: number,
  format: string | undefined,
  precision: number,
  percentPadding: PercentPadding | undefined
) {
  let stringValue = ratio.toLocaleString(undefined, {
    style: format === 'percent' ? 'percent' : 'decimal',
    minimumFractionDigits: precision,
    maximumFractionDigits: precision
  })
  if (format === 'percent') {
    stringValue = addPercentPadding(stringValue, precision, percentPadding)
  }
  return stringValue
}

function addPercentPadding(
  stringValue: string,
  precision: number,
  percentPadding: PercentPadding | undefined
) {
  const padLength = 4 + (precision > 0 ? precision + 1 : 0)
  if (percentPadding === 'start') {
    return stringValue.padStart(padLength, '\u2007')
  } else if (percentPadding === 'end') {
    return stringValue.padEnd(padLength, '\u2007')
  }
  return stringValue
}

export type { RatioFormatterProps }
export { DEFAULT_PRECISION, ratioFormatter }
