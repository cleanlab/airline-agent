import { upperFirst } from 'lodash'
import type React from 'react'
import type { ReadonlyDeep } from 'type-fest'

import { createCustomStringSort } from './createCustomStringSort'
import { getIsAppleOS } from './getIsAppleOS'

type KeyboardShortcut = {
  key: string
  modifiers: KeyboardShortcutModifierKey[]
}

const KEYBOARD_SHORTCUT_MODIFIERS = ['shift', 'alt', 'mod'] as const
/**
 * Represents a modifier key that can be used in keyboard shortcuts.
 * - 'shift': The Shift key
 * - 'alt': The Alt/Option key
 * - 'mod': The Command key on Apple platforms or Control key on all other platforms
 */
type KeyboardShortcutModifierKey = (typeof KEYBOARD_SHORTCUT_MODIFIERS)[number]

/**
 * Converts a keyboard shortcut modifier key to its platform-specific symbol or text representation.
 * @param modifier - The modifier key to convert ('shift', 'alt', or 'mod')
 * @param isAppleOS - Whether the current platform is Apple OS (macOS/iOS)
 * @returns The platform-specific representation of the modifier key:
 * - For Apple OS: '⌘' for mod, '⇧' for shift, '⎇' for alt
 * - For other platforms: 'Ctrl' for mod, '⇧' for shift, 'Alt' for alt
 * @example
 * getModifierKey('mod', true) // returns '⌘'
 * getModifierKey('mod', false) // returns 'Ctrl'
 */
const getModifierKey = (modifier: KeyboardShortcutModifierKey, isAppleOS: boolean) => {
  switch (modifier) {
    case 'mod':
      return isAppleOS ? '⌘' : 'Ctrl'
    case 'shift':
      return isAppleOS ? '⇧' : 'Shift'
    case 'alt':
      return isAppleOS ? '⎇' : 'Alt'
    default:
      return modifier
  }
}

const keyToShortcutString = (key: string, isAppleOS: boolean) =>
  ({
    backspace: isAppleOS ? '⌫' : 'Bksp',
    delete: isAppleOS ? '⌦' : 'Del',
    escape: 'Esc',
    arrowleft: '←',
    arrowright: '→',
    arrowup: '↑',
    arrowdown: '↓',
    ' ': 'Space',
  })[key.toLowerCase() as string] ?? upperFirst(key)

const modifierSort = {
  apple: createCustomStringSort([
    'shift',
    'alt', // option (⎇)
    'mod', // command (⌘)
  ] as const satisfies KeyboardShortcutModifierKey[]),
  other: createCustomStringSort([
    'mod', // control
    'alt',
    'shift',
  ] as const satisfies KeyboardShortcutModifierKey[]),
} as const satisfies Record<string, (a: string, b: string) => number>

const getKeyboardShortcutString = ({ key, modifiers }: ReadonlyDeep<KeyboardShortcut>) => {
  const isAppleOS = getIsAppleOS()
  if (typeof modifiers === 'string') {
    modifiers = [modifiers]
  }
  const modifierKeyStrings = modifiers
    .map((m) => getModifierKey(m, isAppleOS))
    .sort(modifierSort[isAppleOS ? 'apple' : 'other'])
  const shortcut = [...modifierKeyStrings, keyToShortcutString(key, isAppleOS)].join(
    isAppleOS ? '\u2009' /* <thin space> */ : '\u200a+\u200a' /* <hair space> + <hair space> */
  )

  return shortcut
}

/**
 * Converts a platform-agnostic modifier key to its corresponding event property name.
 * @param key - The modifier key to convert
 * @returns The corresponding event property name (e.g., 'shiftKey', 'metaKey', 'ctrlKey')
 */
const convertPlatformModifierKey = (key: KeyboardShortcutModifierKey) => {
  switch (key) {
    case 'shift':
      return 'shiftKey'
    case 'alt':
      return 'altKey'
    case 'mod':
      return getIsAppleOS() ? 'metaKey' : 'ctrlKey'
  }
}

/**
 * Creates a keyboard shortcut handler for a given element.
 * @param shortcut - The keyboard shortcut configuration
 * @param shortcut.key - The key to listen for
 * @param shortcut.modifiers - The modifiers to listen for
 * @param handler - The handler function to call when the keyboard shortcut is pressed
 * @returns A keyboard event handler that can be attached to an element
 * @example
 * ```tsx
 * const handleSave = createKeyboardShortcutHandler(
 *   { key: 's', modifiers: ['mod'] },
 *   (e) => {
 *     e.preventDefault();
 *     saveDocument();
 *   }
 * );
 * ```
 */
const createKeyboardShortcutHandler =
  (
    { key, modifiers }: KeyboardShortcut,
    handler: (e: React.KeyboardEvent | KeyboardEvent) => void
  ) =>
  (e: React.KeyboardEvent<HTMLElement> | KeyboardEvent) => {
    if (e.key.toLowerCase() !== key.toLowerCase()) return
    for (const modifier of modifiers) {
      const modifierKey = convertPlatformModifierKey(modifier)
      if (!e[modifierKey]) return
    }
    return handler(e)
  }

export { createKeyboardShortcutHandler, getKeyboardShortcutString, KEYBOARD_SHORTCUT_MODIFIERS }
export type { KeyboardShortcut, KeyboardShortcutModifierKey }
