import plugin from 'tailwindcss/plugin'

const DEFAULT_PREFIX = 'cl-shadows'
type Options = {
  prefix?: string
}

const createCssVarName = (prefix: string, key: string) => {
  return `--${prefix}-${key}`
}

const generateCssVars = (shadows: Record<string, string>, { prefix }: Options) => {
  prefix = prefix || DEFAULT_PREFIX
  return Object.fromEntries(
    Object.entries(shadows).map(([key, value]) => {
      return [createCssVarName(prefix, key), value]
    })
  )
}

/**
 * Add shadow classes to the tailwind config
 */
const twShadowsPlugin = (
  { light, dark }: { light: Record<string, string>; dark: Record<string, string> },
  options: Options
) => {
  return plugin(({ addBase }) => {
    const lightVars = generateCssVars(light, options)
    const darkVars = generateCssVars(dark, options)
    const base = {
      '[data-theme="light"]': {
        ...lightVars,
      },
      '[data-theme="dark"]': {
        ...darkVars,
      },
    }
    addBase(base)
  })
}

export const createShadows = <T extends string>(
  shadows: { light: Record<T, string>; dark: Record<T, string> },
  options: { prefix?: string } = {}
) => {
  const prefix = options.prefix || 'cl-shadows'
  return {
    plugin: twShadowsPlugin(shadows, { prefix }),
    boxShadow: Object.fromEntries(
      Object.entries(shadows.light).map(([key]) => [key, `var(${createCssVarName(prefix, key)})`])
    ),
  }
}
