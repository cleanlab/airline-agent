export type EventProperties = {
  [key: string]: string | number | boolean | null | undefined
}

export const analytics = {
  init: () => {},
  track: (_eventName: string, _properties?: EventProperties) => {},
  identify: (_userId: string | undefined, _properties?: EventProperties) => {},
  reset: () => {},
  getAnalyticsInstance: () => null
}
