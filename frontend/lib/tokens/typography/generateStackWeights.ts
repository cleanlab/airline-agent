import { FONT_WEIGHTS, type FontWeight, type TypographyStack } from './consts'

export const generateStackWeights = (styles: TypographyStack, weights: (FontWeight | 'link')[]) => {
  return Object.fromEntries(
    Object.entries(styles).flatMap(([size, style]) => {
      return Object.entries(FONT_WEIGHTS)
        .filter(([weightName]) => weights.includes(weightName as FontWeight))
        .map(([weightName, weightValue]) => {
          return [
            `${size}${weightName === 'normal' ? '' : `-${weightName}`}`,
            {
              ...style,
              fontWeight: weightValue,
            },
          ]
        })
    })
  )
}
