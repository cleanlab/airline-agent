import { type ClassValue, clsx } from 'clsx'
// eslint-disable-next-line no-restricted-imports
import { extendTailwindMerge, mergeConfigs } from 'tailwind-merge'
import { createTV } from 'tailwind-variants'

import { typographyKeys } from '../tokens/typography'
import { TYPOGRAPHY_PREFIX } from '../tokens/typography/consts'

const twMergeConfig = {
  extend: {
    classGroups: {
      [TYPOGRAPHY_PREFIX]: [
        {
          [TYPOGRAPHY_PREFIX]: typographyKeys
        }
      ],
      'text-wrap': ['text-balance-pretty']
    }
  }
}

/**
 * Customized tailwind merge function to handle typography component classes
 */
const twMerge = extendTailwindMerge(config =>
  mergeConfigs<string>(config, twMergeConfig)
)

/**
 * Customized tailwind-variants `tv` function including customized twMerge configuration
 */
const tv = createTV({
  twMerge: true,
  twMergeConfig: twMergeConfig
})

/**
 * Use clsx to merge classnames, then use twMerge to remove
 * overridden tailwind classes
 * @param inputs
 * @returns
 */
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Identity function that wraps values for Prettier Tailwind plugin auto-sorting
 * @template T - The type of the argument
 * @param {T} arg - The value to wrap
 * @returns {T} The same value, unchanged
 */
const tw: <T>(arg: T) => T = arg => arg

export { cn, tv, tw }
