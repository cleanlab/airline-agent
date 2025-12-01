import { twPresetCleanlab } from '@cleanlab/design-system/tokens'
import type { Config } from 'tailwindcss'
import { screens } from './tailwind/screens'

const config: Config = {
  presets: [twPresetCleanlab],
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './providers/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
    './stores/**/*.{js,ts,jsx,tsx,mdx}',
    './client/**/*.{js,ts,jsx,tsx,mdx}',
    './public/**/*.html',
    './node_modules/@cleanlab/design-system/dist/**/*.{js,jsx}'
  ],
  prefix: '',
  theme: {
    container: {
      center: true,
      padding: '2rem'
    },
    screens: {
      ...screens,
      mdlg: '840px'
    },
    letterSpacing: {
      normal: '0'
    },
    extend: {
      fontFamily: {
        sans: ['var(--font-geist-sans)'],
        mono: ['var(--font-geist-mono)']
      },
      animation: {},
      keyframes: {}
    }
  }
}

export default config
