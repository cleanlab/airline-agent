import { cn } from '@/lib/utils/tailwindUtils'
import type { HTMLAttributes } from 'react'

/**
 * Props for the LogoImg component.
 * @interface LogoProps
 * @extends {Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'width' | 'height'>}
 */
type LogoProps = {
  /**
   * Source URLs for the logo in light and dark modes.
   */
  src: { light: string; dark: string }
  /**
   * Width of the logo in pixels.
   */
  width: number
  /**
   * Height of the logo in pixels.
   */
  height: number
  /**
   * Alternative text for the logo for accessibility.
   */
  alt: string
  /**
   * Optional CSS class name for additional styling.
   */
  className?: string
} & Omit<HTMLAttributes<HTMLImageElement>, 'src' | 'alt' | 'width' | 'height'>

/**
 * A responsive logo component that displays different images based on light/dark mode.
 *
 * @component
 * @example
 * ```tsx
 * // Using the logoMetadata object
 * <LogoImg
 *   src={{ light: 'logos/128/logo-black.png', dark: 'logos/128/logo-white.png' }}
 *   {...logoMetadata['128']['logo']}
 * />
 *
 * // Using the src and width, height, and alt props
 * <LogoImg
 *   src={{ light: 'logos/128/logo-black.png', dark: 'logos/128/logo-white.png' }}
 *   width={200}
 *   height={50}
 *   alt="Cleanlab Logo"
 * />
 * ```
 *
 * @param props - The component props
 * @param props.src - Object containing URLs for light and dark mode versions of the logo
 * @param props.width - Width of the logo in pixels
 * @param props.height - Height of the logo in pixels
 * @param props.alt - Alternative text for the logo
 * @param props.className - Optional CSS class name for additional styling
 * @returns A responsive logo that changes based on the current theme
 */
export const LogoImg = ({
  className,
  src,
  width,
  height,
  alt,
  ...props
}: LogoProps) => {
  return (
    <>
      <img
        className={cn('dark:hidden', className)}
        src={src.light}
        alt={alt}
        width={width}
        height={height}
        {...props}
      />
      <img
        className={cn('hidden dark:block', className)}
        src={src.dark}
        alt={alt}
        width={width}
        height={height}
        {...props}
      />
    </>
  )
}
