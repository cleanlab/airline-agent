'use client'

/**
 * Checks if a given platform or user agent string indicates an Apple operating system.
 * @param platformOrUserAgent - The platform or user agent string to check
 * @returns {boolean} True if the platform or user agent indicates an Apple OS (macOS, iOS, iPadOS), false otherwise
 * @example
 * ```ts
 * getPlatformOrUserAgentIsAppleOS('MacIntel') // returns true
 * getPlatformOrUserAgentIsAppleOS('iPhone')   // returns true
 * getPlatformOrUserAgentIsAppleOS('Windows')  // returns false
 * ```
 */
export const getPlatformIsAppleOS = (
  platformOrUserAgent: string | null | undefined
) => {
  return /(mac|iphone|ipod|ipad|ios)/i.test(
    (platformOrUserAgent ?? '').toLowerCase()
  )
}

/**
 * Determines if the current operating system is an Apple OS (macOS, iOS, iPadOS).
 * This function checks both the platform and user agent strings to ensure accurate detection.
 *
 * @returns {boolean} True if the current OS is an Apple OS, false otherwise
 * @example
 * ```ts
 * if (getIsAppleOS()) {
 *   // Use Apple-specific features
 * }
 * ```
 */
export const getIsAppleOS = () => {
  // If navigator is not defined, we're not running in a browser environment, so we can't detect the OS.
  if (typeof navigator === 'undefined') {
    return false
  }
  return getPlatformIsAppleOS(
    navigator.userAgentData?.platform || navigator.platform
  )
}
