// Must not use @ import path aliases so tailwind can import this

const neutral = {
  '0': '#FFFFFF',
  '50': '#F9FAFB',
  '80': '#F3F4F7',
  '100': '#EDEFF2',
  '200': '#DEE2E8',
  '300': '#CFD5DE',
  '400': '#B9BFCB',
  '500': '#9199A6',
  '600': '#6F798A',
  '700': '#5B6371',
  '800': '#343B46',
  '900': '#080A0C',
} as const satisfies Record<string, string>

const blue = {
  '50': '#EFF8FF',
  '100': '#DBEFFE',
  '200': '#BFE0FE',
  '300': '#92C5FD',
  '400': '#60A5FA',
  '500': '#3C82F6',
  '600': '#2463EB',
  '700': '#1C4ED8',
  '800': '#1B3BA2',
  '900': '#1C357D',
} as const satisfies Record<string, string>

const red = {
  '50': '#FEF2F2',
  '100': '#FEE2E1',
  '200': '#FECACA',
  '300': '#FDA5A5',
  '400': '#F87171',
  '500': '#EF4444',
  '600': '#DC2625',
  '700': '#B91C1B',
  '800': '#991B1B',
  '900': '#691617',
} as const satisfies Record<string, string>

const orange = {
  '50': '#FFF5ED',
  '100': '#FFE7D5',
  '200': '#FECEAB',
  '300': '#FDAE74',
  '400': '#FB8C3C',
  '500': '#F97517',
  '600': '#EA6A0E',
  '700': '#C2580D',
  '800': '#9A4B12',
  '900': '#6F3810',
} as const satisfies Record<string, string>

const yellow = {
  '50': '#FFFFEA',
  '100': '#FEFCC5',
  '200': '#FFFB85',
  '300': '#FFF247',
  '400': '#FFE419',
  '500': '#FFC502',
  '600': '#E29900',
  '700': '#BB6D03',
  '800': '#985407',
  '900': '#703E0B',
} as const satisfies Record<string, string>

const green = {
  '50': '#F0FFF4',
  '100': '#C6F6D5',
  '200': '#9AE6B4',
  '300': '#68D391',
  '400': '#48BB78',
  '500': '#38A169',
  '600': '#25855A',
  '700': '#276749',
  '800': '#22543D',
  '900': '#183A2A',
} as const satisfies Record<string, string>

const teal = {
  '50': '#EFFDFB',
  '100': '#CBFCF6',
  '200': '#97F8EC',
  '300': '#59EEE0',
  '400': '#27D8CF',
  '500': '#0FBCB6',
  '600': '#0B9796',
  '700': '#0C7978',
  '800': '#0E5F60',
  '900': '#0D4040',
} as const satisfies Record<string, string>

const cyan = {
  '50': '#EFFAFF',
  '100': '#DFF4FF',
  '200': '#B7EBFF',
  '300': '#78DDFF',
  '400': '#28CAFF',
  '500': '#06B6F0',
  '600': '#0092CE',
  '700': '#0275A7',
  '800': '#03628A',
  '900': '#07445F',
} as const satisfies Record<string, string>

const purple = {
  '50': '#F5F4FE',
  '100': '#ECEBFC',
  '200': '#DBD9FB',
  '300': '#C2BBF6',
  '400': '#A295F1',
  '500': '#8369E9',
  '600': '#754EDF',
  '700': '#6137C9',
  '800': '#4A2999',
  '900': '#311C64',
} as const satisfies Record<string, string>

const violet = {
  50: '#FCF0FF',
  100: '#F8DDFF',
  200: '#F2BDFF',
  300: '#E990FF',
  400: '#DA47FF',
  500: '#CA04FB',
  600: '#AC03D6',
  700: '#8B03AD',
  800: '#6F028A',
  900: '#520266',
} as const satisfies Record<string, string>

const pink = {
  '50': '#FCF3FB',
  '100': '#FBE8F7',
  '200': '#FAD0F0',
  '300': '#F5ACE2',
  '400': '#EE78CC',
  '500': '#E44FB5',
  '600': '#D6409F',
  '700': '#B6207B',
  '800': '#971D65',
  '900': '#641644',
} as const satisfies Record<string, string>

const lime = {
  '50': '#F8FEE7',
  '100': '#EEFDCA',
  '200': '#DFFB9B',
  '300': '#C5F561',
  '400': '#ACEA32',
  '500': '#9CE612',
  '600': '#6DA70A',
  '700': '#527E0D',
  '800': '#436411',
  '900': '#304710',
} as const satisfies Record<string, string>

const white = neutral[0]
const black = neutral[900]
const focus = blue[500]

const text = {
  strong: neutral[900],
  primary: neutral[800],
  faint: neutral[700],
  disabled: neutral[500],
  'high-contrast': neutral[0],
  'high-contrast-dark': '#0D1016',
  'high-contrast-light': neutral[0],
} as const satisfies Record<string, string>

const surface = {
  base: '#ffffff',
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
  'high-contrast': neutral[900],
} as const satisfies Record<string, string>

const border = {
  '0': neutral[100],
  '1': neutral[200],
  '2': neutral[300],
} as const satisfies Record<string, string>

const brand = {
  violet: violet['500'],
  lime: lime['500'],
  cyan: cyan['500'],
  neutral: neutral[900],
} as const satisfies Record<string, string>

const product = {
  agility: brand.violet,
  tlm: brand.lime,
  studio: brand.cyan,
  cleanlab: brand.neutral,
} as const satisfies Record<string, (typeof brand)[keyof typeof brand]>

export const components = {
  'button-primary': {
    bg: blue[800],
    border: blue[900],
    text: text['high-contrast'],
    'bg-hover': blue[700],
    'border-hover': blue[800],
    'bg-active': blue[600],
    'border-active': blue[700],
    'bg-focus': blue[800],
    'border-focus': blue[50],
  },
  'radio-card': {
    bg: surface['0'],
    'radio-bg': surface['1'],
  },
  modal: {
    bg: surface['0'],
  },
  tooltip: {
    bg: neutral[300],
    border: neutral[400],
    text: text.strong,
  },
  popover: {
    bg: surface['0'],
  },
  switch: {
    'bg-unchecked': neutral[200],
    'bg-unchecked-hover': neutral[300],
    'bg-checked': blue[500],
    'bg-checked-hover': blue[600],
    'thumb-bg': neutral[0],
    'thumb-bg-disabled': neutral[200],
    'bg-disabled': neutral[100],
  },
  'tlmchip-green': {
    bg: green[50],
    border: green[300],
    text: green[700],
    'bg-hover': green[100],
    'border-hover': green[300],
    'bg-active': green[200],
    'border-active': green[300],
  },
  'tlmchip-yellow': {
    bg: yellow[50],
    border: yellow[500],
    text: yellow[700],
    'bg-hover': yellow[100],
    'border-hover': yellow[500],
    'bg-active': yellow[200],
    'border-active': yellow[500],
  },
  'tlmchip-red': {
    bg: red[50],
    border: red[300],
    text: red[700],
    'bg-hover': red[100],
    'border-hover': red[300],
    'bg-active': red[200],
    'border-active': red[300],
  },
} as const satisfies Record<string, Record<string, string>>

export const lightModeColors = {
  black,
  white,
  neutral,
  pink,
  red,
  orange,
  yellow,
  lime,
  green,
  teal,
  cyan,
  blue,
  purple,
  violet,
  text,
  surface,
  border,
  focus,
  brand,
  product,
  ...components,
} as const satisfies Record<string, string | Record<string, string>>
