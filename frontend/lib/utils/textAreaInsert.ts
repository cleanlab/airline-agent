'use client'

const nativeTextAreaValueSetter =
  (typeof window !== 'undefined' &&
    window?.HTMLTextAreaElement?.prototype &&
    Object?.getOwnPropertyDescriptor?.(window.HTMLTextAreaElement.prototype, 'value')?.set) ||
  undefined

/**
 * Inserts text at the current cursor position in a textarea element.
 * If the browser supports execCommand, it will use that method.
 * Otherwise, it falls back to manual text insertion.
 *
 * @param tArea - The textarea element to insert text into
 * @param text - The text to insert at the current cursor position
 *
 * @example
 * ```typescript
 * const textarea = document.querySelector('textarea');
 * textAreaInsert(textarea, 'Hello world');
 * ```
 */
export function textAreaInsert(tArea: HTMLTextAreaElement | null | undefined, text: string) {
  if (!tArea || !text) {
    return
  }
  tArea.focus()
  let curVal = tArea.value

  if (typeof document.execCommand === 'function') {
    document.execCommand('insertText', false, text)
  } else {
    const startPos = tArea.selectionStart
    const endPos = tArea.selectionEnd

    curVal = `${tArea.value.substring(0, startPos)}${text}${curVal.substring(endPos, curVal.length)}`

    if (nativeTextAreaValueSetter) {
      nativeTextAreaValueSetter?.call?.(tArea, curVal)
    } else {
      tArea.value = curVal
    }
    tArea.selectionStart = startPos + 1
    tArea.selectionEnd = tArea.selectionStart

    tArea.dispatchEvent(new Event('change', { bubbles: true }))
    tArea.dispatchEvent(new Event('input', { bubbles: true }))
  }
  tArea.blur()
  tArea.focus()
}
