// Modified from https://github.com/FormidableLabs/prism-react-renderer/blob/master/packages/prism-react-renderer/src/themes/vsDark.ts
import type { PrismTheme } from 'prism-react-renderer'

const theme: PrismTheme = {
  plain: {
    color: 'hsl(var(--twc-text-primary))',
    backgroundColor: 'transparent',
  },
  styles: [
    {
      types: ['comment'],
      style: {
        color: 'hsl(var(--twc-neutral-500))',
      },
    },
    {
      types: ['keyword'],
      style: {
        color: 'hsl(var(--twc-cyan-400))',
      },
    },
    {
      types: ['number', 'inserted', 'attr-name', 'variable', 'constant'],
      style: {
        color: 'hsl(var(--twc-text-strong))',
      },
    },
    {
      types: ['char', 'deleted', 'string', 'attr-value', 'template-punctuation'],
      style: {
        color: 'hsl(var(--twc-green-500))',
      },
    },
    {
      types: ['selector'],
      style: {
        color: 'hsl(var(--twc-purple-500))',
      },
    },
    {
      types: ['tag'],
      style: {
        color: 'hsl(var(--twc-blue-500))',
      },
    },
    {
      types: ['punctuation', 'operator'],
      style: {
        color: 'hsl(var(--twc-yellow-700))',
      },
    },
    {
      types: ['function'],
      style: {
        color: 'hsl(var(--twc-cyan-500))',
      },
    },
    {
      types: ['class-name'],
      style: {
        color: 'hsl(var(--twc-blue-500))',
      },
    },
  ],
}
export { theme as prismThemeDark }
