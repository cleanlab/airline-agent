// Must not use @ import path aliases so tailwind can import this
// Minimal local definition to satisfy "satisfies" checks without external import
// Accept any value shape to accommodate nested component tokens
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type WidenStringVals<T> = { [K in keyof T]: any } & Record<string, unknown>
import { lightModeColors } from './colorsLight'
import { type components as lightModeComponents } from './colorsLight.js'

const neutral = {
  '0': '#0D1016',
  '50': '#181C25',
  '80': '#1E222D',
  '100': '#232834',
  '200': '#343C4B',
  '300': '#444D5F',
  '400': '#586174',
  '500': '#6E788C',
  '600': '#959DAC',
  '700': '#AEBBC6',
  '800': '#D8DEE3',
  '900': '#FCFCFD'
} as const satisfies WidenStringVals<typeof lightModeColors.neutral>

const blue = {
  '50': '#013775',
  '100': '#004B9A',
  '200': '#0264C5',
  '300': '#0678E0',
  '400': '#0E87EB',
  '500': '#3FA6F6',
  '600': '#65BFFB',
  '700': '#9CD7FC',
  '800': '#D6EFFE',
  '900': '#F0F9FF'
} as const satisfies WidenStringVals<typeof lightModeColors.blue>

const red = {
  '50': '#691617',
  '100': '#991B1B',
  '200': '#B91C1B',
  '300': '#DC2625',
  '400': '#EF4444',
  '500': '#F87171',
  '600': '#FDA5A5',
  '700': '#FECACA',
  '800': '#FEE2E1',
  '900': '#FEF2F2'
} as const satisfies WidenStringVals<typeof lightModeColors.red>

const orange = {
  '50': '#6F3810',
  '100': '#9A4B12',
  '200': '#C2580D',
  '300': '#EA6A0E',
  '400': '#F97517',
  '500': '#FB8C3C',
  '600': '#FDAE74',
  '700': '#FECEAB',
  '800': '#FFE7D5',
  '900': '#FFF5ED'
} as const satisfies WidenStringVals<typeof lightModeColors.orange>

const yellow = {
  '50': '#703E0B',
  '100': '#985407',
  '200': '#BB6D03',
  '300': '#E29900',
  '400': '#FFC502',
  '500': '#FFE419',
  '600': '#FFF247',
  '700': '#FFFB85',
  '800': '#FEFCC5',
  '900': '#FFFFEA'
} as const satisfies WidenStringVals<typeof lightModeColors.yellow>

const green = {
  '50': '#183A2A',
  '100': '#22543D',
  '200': '#276749',
  '300': '#25855A',
  '400': '#38A169',
  '500': '#48BB78',
  '600': '#68D391',
  '700': '#9AE6B4',
  '800': '#C6F6D5',
  '900': '#F0FFF4'
} as const satisfies WidenStringVals<typeof lightModeColors.green>

const teal = {
  '50': '#0D4040',
  '100': '#0E5F60',
  '200': '#0C7978',
  '300': '#0B9796',
  '400': '#0FBCB6',
  '500': '#27D8CF',
  '600': '#59EEE0',
  '700': '#97F8EC',
  '800': '#CBFCF6',
  '900': '#EFFDFB'
} as const satisfies WidenStringVals<typeof lightModeColors.teal>

const cyan = {
  '50': '#07445F',
  '100': '#03628A',
  '200': '#0275A7',
  '300': '#0092CE',
  '400': '#06B6F0',
  '500': '#28CAFF',
  '600': '#78DDFF',
  '700': '#B7EBFF',
  '800': '#DFF4FF',
  '900': '#EFFAFF'
} as const satisfies WidenStringVals<typeof lightModeColors.cyan>

const purple = {
  '50': '#311C64',
  '100': '#4A2999',
  '200': '#6137C9',
  '300': '#754EDF',
  '400': '#8369E9',
  '500': '#A295F1',
  '600': '#C2BBF6',
  '700': '#DBD9FB',
  '800': '#ECEBFC',
  '900': '#F5F4FE'
} as const satisfies WidenStringVals<typeof lightModeColors.purple>

const violet = {
  '50': '#520266',
  '100': '#6F028A',
  '200': '#8B03AD',
  '300': '#AC03D6',
  '400': '#CA04FB',
  '500': '#DD53FF',
  '600': '#E990FF',
  '700': '#F2BDFF',
  '800': '#F8DDFF',
  '900': '#FCF3FB'
} as const satisfies WidenStringVals<typeof lightModeColors.violet>

const pink = {
  '50': '#641644',
  '100': '#971D65',
  '200': '#B6207B',
  '300': '#D6409F',
  '400': '#E44FB5',
  '500': '#EE78CC',
  '600': '#F5ACE2',
  '700': '#FAD0F0',
  '800': '#FBE8F7',
  '900': '#FCF3FB'
} as const satisfies WidenStringVals<typeof lightModeColors.pink>

const lime = {
  '50': '#304710',
  '100': '#436411',
  '200': '#527E0D',
  '300': '#6DA70A',
  '400': '#9CE612',
  '500': '#ACEA32',
  '600': '#C5F561',
  '700': '#DFFB9B',
  '800': '#EEFDCA',
  '900': '#F8FEE7'
} as const satisfies WidenStringVals<typeof lightModeColors.lime>

const white = lightModeColors.white
const black = lightModeColors.black
const focus = blue[500]

const text = {
  strong: neutral[900],
  primary: neutral[800],
  faint: neutral[700],
  disabled: neutral[500],
  'high-contrast': neutral[0],
  'high-contrast-dark': neutral[0],
  'high-contrast-light': lightModeColors.text['high-contrast']
} as const satisfies WidenStringVals<typeof lightModeColors.text>

const surface = {
  base: '#000000',
  '0': neutral[0],
  '0-hover': neutral[50],
  '0-active': neutral[100],
  '1': neutral[50],
  '1-hover': neutral[100],
  '1-active': neutral[200],
  '2': neutral[100],
  '2-hover': neutral[200],
  '2-active': neutral[300],
  disabled: neutral[200],
  'high-contrast': neutral[900]
} as const satisfies WidenStringVals<typeof lightModeColors.surface>

const border = {
  '0': neutral[100],
  '1': neutral[200],
  '2': neutral[300]
} as const satisfies WidenStringVals<typeof lightModeColors.border>

const brand = {
  ...lightModeColors.brand,
  neutral: neutral[900]
} as const satisfies WidenStringVals<typeof lightModeColors.brand>

const product = {
  agility: brand.violet,
  tlm: brand.lime,
  studio: brand.cyan,
  cleanlab: brand.neutral
} as const satisfies Record<string, (typeof brand)[keyof typeof brand]>

const components = {
  'button-primary': {
    bg: blue[200],
    border: blue[300],
    text: blue[900],
    'bg-hover': blue[300],
    'border-hover': blue[300],
    'bg-active': blue[400],
    'border-active': blue[300],
    'bg-focus': blue[300],
    'border-focus': blue[900]
  },
  'radio-card': {
    bg: surface['1'],
    'radio-bg': surface['2']
  },
  modal: {
    bg: surface['1']
  },
  tooltip: {
    bg: neutral[400],
    border: neutral[500],
    text: text.strong
  },
  popover: {
    bg: surface['1']
  },
  switch: {
    'bg-unchecked': neutral[400],
    'bg-unchecked-hover': neutral[300],
    'bg-checked': blue[300],
    'bg-checked-hover': blue[200],
    'thumb-bg': neutral[800],
    'thumb-bg-disabled': neutral[200],
    'bg-disabled': neutral[100]
  },
  'tlmchip-green': {
    bg: green[500],
    border: green[500],
    text: text['high-contrast-dark'],
    'bg-hover': green[600],
    'border-hover': green[600],
    'bg-active': green[700],
    'border-active': green[700]
  },
  'tlmchip-yellow': {
    bg: yellow[500],
    border: yellow[500],
    text: text['high-contrast-dark'],
    'bg-hover': yellow[600],
    'border-hover': yellow[600],
    'bg-active': yellow[700],
    'border-active': yellow[700]
  },
  'tlmchip-red': {
    bg: red[500],
    border: red[500],
    text: text['high-contrast-dark'],
    'bg-hover': red[600],
    'border-hover': red[600],
    'bg-active': red[700],
    'border-active': red[700]
  }
} as const satisfies WidenStringVals<typeof lightModeComponents>

export const darkModeColors = {
  neutral,
  white,
  black,
  blue,
  red,
  orange,
  yellow,
  green,
  teal,
  cyan,
  purple,
  violet,
  pink,
  lime,
  text,
  surface,
  border,
  focus,
  product,
  brand,
  ...components
} as const satisfies WidenStringVals<typeof lightModeColors>
