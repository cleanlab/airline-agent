import type { ComponentProps } from 'react'

import { IconAirplane } from './icons'

export const LogoLockup = async ({
  ...props
}: ComponentProps<'img'> & {
  logoText?: string | null
}) => {
  return (
    <div className="flex items-center gap-3">
      <IconAirplane size={22} />
      <p className="type-body-200 text-[18px] lg:type-body-300 lg:text-[22px]">
        <span className="inline md:hidden lg:inline">Support </span> Agent
      </p>
    </div>
  )
}
