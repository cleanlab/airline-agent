// Loosen react-markdown internal types to avoid JSX namespace and generic constraints issues during build
declare module 'react-markdown/lib/complex-types' {
  export type NormalComponents = any
  export type SpecialComponents = any
}
declare module 'react-markdown/lib/ast-to-react' {
  export type Components = any
  export type ReactMarkdownProps = any
}
