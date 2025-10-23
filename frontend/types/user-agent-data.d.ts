// Minimal ambient types for navigator.userAgentData (UA-CH). Keeps TS happy without external deps.
// See: https://wicg.github.io/ua-client-hints/

interface NavigatorUADataBrandVersion {
  brand: string
  version: string
}

interface NavigatorUAData {
  brands: NavigatorUADataBrandVersion[]
  mobile: boolean
  platform: string
  getHighEntropyValues?: (hints: string[]) => Promise<Record<string, unknown>>
}

interface Navigator {
  userAgentData?: NavigatorUAData
}

declare const navigator: Navigator
