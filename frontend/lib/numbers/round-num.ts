import { ceil, floor, round } from 'lodash'

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
