export function assertExhaustive(
  value: never,
  message: string = 'Reached unexpected case in exhaustive switch'
): never {
  throw new Error(
    message ?? `Reached unexpected case in exhaustive switch: ${value}`
  )
}
