import type { Config } from 'tailwindcss'
import plugin from 'tailwindcss/plugin'
import twAnimate from 'tailwindcss-animate'
import { createThemes } from 'tw-colors'

import { borderRadius } from './borderRadius'
import { colors } from './colors'
import { createShadows } from './createShadows'
import { shadows } from './shadows'
import { spacing } from './spacing'
import { twTypographyPlugin } from './typography'
import { FONT_FAMILIES, FONT_WEIGHTS } from './typography/consts'

const addMisc = plugin(({ addBase }) => {
  addBase({
    ':root': {
      // Font family vars
      '--cl-font-family-fallbacks':
        'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"',
      '--cl-font-family-body':
        '"Geist Variable", Geist, -apple-system-body, var(--cl-font-family-fallbacks)',
      '--cl-font-family-display':
        '"Geist Variable", Geist, var(--cl-font-family-fallbacks)',
      '--cl-font-family-code':
        '"Geist Mono Variable", "Geist Mono", ui-monospace, "Courier new", "Courier", monospace, var(--cl-font-family-fallbacks)',

      // Global gradient vars
      '--cl-gradient-magic':
        '#0fbcb6, #48bb78, #9ce612, #ffe419, #fd9774, #ee78cc, #8369e9',
      '--cl-overlay-bg': 'hsla(var(--twc-black) / 0.5)'
    },
    '[data-theme="dark"]': {
      '--cl-overlay-bg': 'hsla(var(--twc-black) / 0.6)'
    },
    '*': {
      scrollbarColor: 'hsl(var(--twc-neutral-300)) hsl(var(--twc-surface-base))'
    }
  })
})

const textBalancePrettyPlugin = plugin(({ addUtilities }) => {
  addUtilities({
    '.text-balance-pretty': {
      'text-wrap': 'balance',
      '@supports (text-wrap: pretty)': {
        'text-wrap': 'pretty'
      }
    }
  })
})

const { plugin: shadowsPlugin, boxShadow } = createShadows(shadows, {
  prefix: 'cl-shadow'
})

export const twPresetCleanlab = {
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      keyframes: {
        'disable-pointer-events': {
          '0%, 99%': { pointerEvents: 'none' }
        },
        'cleanlab-collapsible-open': {
          from: { height: '0' },
          to: { height: 'var(--radix-collapsible-content-height)' }
        },
        'cleanlab-collapsible-close': {
          from: { height: 'var(--radix-collapsible-content-height)' },
          to: { height: '0' }
        },
        'cleanlab-accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' }
        },
        'cleanlab-accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' }
        },
        'cleanlab-dot-bounce': {
          '0%, 100%': {
            transform: 'translateY(-50%)',
            'animation-timing-function': 'cubic-bezier(0.8,0,1,1)'
          },
          '50%': {
            transform: 'translateY(25%)',
            'animation-timing-function': 'cubic-bezier(0,0,0.2,1)'
          }
        }
      },
      animation: {
        'collapsible-open': 'cleanlab-collapsible-open 0.2s ease-in-out',
        'collapsible-close': 'cleanlab-collapsible-close 0.2s ease-out',
        'accordion-down':
          'cleanlab-accordion-down 0.2s cubic-bezier(0.87, 0, 0.13, 1)',
        'accordion-up':
          'cleanlab-accordion-up 0.2s cubic-bezier(0.87, 0, 0.13, 1)'
      },
      transitionDuration: {
        '400': '400ms'
      },
      transitionTimingFunction: {
        'scale-out-bounce': 'cubic-bezier(.41,1.97,.55,1)'
      }
    },
    spacing,
    borderRadius,
    fontWeight: FONT_WEIGHTS,
    fontFamily: FONT_FAMILIES,
    ringWidth: { DEFAULT: '2px', 0: '0', 1: '1px', 2: '2px' },
    boxShadow: {
      none: 'none',
      ...boxShadow
    },
    // Remove tailwind default font classes
    // Use our custom `type-` classes from `twTypographyPlugin` instead
    fontSize: {},
    letterSpacing: {
      normal: '0'
    },
    lineHeight: {}
  },
  plugins: [
    createThemes(colors),
    twAnimate,
    twTypographyPlugin,
    shadowsPlugin,
    addMisc,
    textBalancePrettyPlugin
  ]
} satisfies Partial<Config>
