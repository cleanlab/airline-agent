import type { ComponentProps } from 'react'

import logoLight from './assets/logo-black.png'
import logoDark from './assets/logo-white.png'
import { LogoImg } from './design-system-components/LogoImg'
import { logoMetadata } from './design-system-components/logoMetadata'

export const LogoLockup = async ({
  ...props
}: ComponentProps<'img'> & {
  logoText?: string | null
}) => {
  return (
    <div className="flex gap-2">
      <LogoImg
        src={{ light: logoLight.src, dark: logoDark.src }}
        {...logoMetadata[128].chat}
        className={props.className}
      />
      <p className="type-body-300 text-[22px]">RAG app</p>
    </div>
  )
}
