import { ceil, floor, round } from 'lodash'

/**
 * Rounds a number to a specified precision in a given direction.
 *
 * @param num - The number to round.
 * @param precision - The number of decimal places to round to.
 * @param direction - The direction to round:
 *   - 'up': Round up (ceiling)
 *   - 'down': Round down (floor)
 *   - 'nearest': Round to the nearest value (default)
 * @returns The rounded number.
 *
 * @example
 * roundNum(3.14159, 2, 'up') // Returns 3.15
 * roundNum(3.14159, 2, 'down') // Returns 3.14
 * roundNum(3.14159, 2, 'nearest') // Returns 3.14
 */
export const roundNum = (
  num: number,
  precision: number,
  direction: 'up' | 'down' | 'nearest' = 'nearest'
) => {
  switch (direction) {
    case 'up':
      return ceil(num, precision)
    case 'down':
      return floor(num, precision)
    case 'nearest':
    default:
      return round(num, precision)
  }
}
