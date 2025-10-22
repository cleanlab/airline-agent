import { mapKeys } from 'lodash'
import plugin from 'tailwindcss/plugin'
import type { CSSRuleObject } from 'tailwindcss/types/config'

import { badge } from './typography/badge'
import { body } from './typography/body'
import { button } from './typography/button'
import { code } from './typography/code'
import { TYPOGRAPHY_PREFIX } from './typography/consts'
import { display } from './typography/display'
import { marketingDisplay } from './typography/marketingDisplay'
import { marketingUtilities } from './typography/marketingUtilities'
import { utilities } from './typography/utilities'

const typography = {
  display: display,
  'mkt-display': marketingDisplay,
  body: body,
  button: button,
  badge: badge,
  code: code,
} as const

const createTypeClass = (key: string, stackKey?: string) => {
  return `${TYPOGRAPHY_PREFIX}${stackKey ? `-${stackKey}` : ''}-${key}`
}

/**
 * Add typography classes to the tailwind config
 */
const twTypographyPlugin = plugin(({ addComponents }) => {
  addComponents({
    ...Object.entries(typography).reduce((components, [stackKey, styles]) => {
      const stackStyles = mapKeys(styles, (_, key) => `.${createTypeClass(key, stackKey)}`)
      return { ...components, ...stackStyles }
    }, {} as CSSRuleObject),
    ...mapKeys({ ...utilities, ...marketingUtilities }, (_, key) => `.${createTypeClass(key)}`),
  })
})

/**
 * Get all typography keys to configure tailwind-merge
 */
const typographyKeys = Object.entries(typography).reduce((components, [stackKey, styles]) => {
  const styleKeys: string[] = Object.keys(styles).map((key) => `${stackKey}-${key}`)
  return [...components, ...styleKeys]
}, [] as string[])

const typographyStyles = {
  ...typography,
  utilities,
  'mkt-utilities': marketingUtilities,
} as const

export { createTypeClass, twTypographyPlugin, typography, typographyKeys, typographyStyles }
