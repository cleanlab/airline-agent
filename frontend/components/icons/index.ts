import { wrapFeatherIcon } from './wrapFeatherIcon'
import {
  FiAlertOctagon,
  FiAlertTriangle,
  FiArrowDownCircle,
  FiCheck,
  FiChevronDown,
  FiCopy,
  FiCornerDownLeft,
  FiInfo,
  FiMoon,
  FiRefreshCw,
  FiSun,
  FiTrash
} from 'react-icons/fi'

export const IconMoon = wrapFeatherIcon(FiMoon, 'IconMoon')
export const IconSun = wrapFeatherIcon(FiSun, 'IconSun')
export const IconArrowCornerDownLeft = wrapFeatherIcon(
  FiCornerDownLeft,
  'IconArrowCornerDownLeft'
)
export const IconRefresh = wrapFeatherIcon(FiRefreshCw, 'IconRefresh')
export const IconArrowDownCircle = wrapFeatherIcon(
  FiArrowDownCircle,
  'IconArrowDownCircle'
)
export const IconCheck = wrapFeatherIcon(FiCheck, 'IconCheck')
export const IconCopy = wrapFeatherIcon(FiCopy, 'IconCopy')
export const IconChevronDown = wrapFeatherIcon(FiChevronDown, 'IconChevronDown')
export const IconInfo = wrapFeatherIcon(FiInfo, 'IconInfo')
export const IconWarning = wrapFeatherIcon(FiAlertOctagon, 'IconWarning')
export const IconCaution = wrapFeatherIcon(FiAlertTriangle, 'IconCaution')
export const IconTrash = wrapFeatherIcon(FiTrash, 'IconTrash')
export { IconCheckCircleFilled } from './IconCheckCircleFilled'
