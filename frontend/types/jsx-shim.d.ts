// Global JSX namespace shim to satisfy libraries that reference JSX.IntrinsicElements
// without importing React types. Keeps app running while preserving most types.
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any
  }
}
