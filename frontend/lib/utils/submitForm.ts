'use client'

/**
 * Programmatically submits an HTML form using the most appropriate available method.
 * First attempts to use the `requestSubmit()` method, falling back to dispatching
 * a submit event if `requestSubmit` is not supported.
 *
 * @param form - The HTML form element to submit. Can be null or undefined.
 * @remarks
 * - If the form is null/undefined, the function will silently return
 * - Uses `requestSubmit()` when available as it more closely simulates a real form submission
 * - Falls back to dispatching a cancelable 'submit' event for broader browser compatibility
 */
export function submitForm(form: HTMLFormElement | null | undefined) {
  if (form) {
    if (typeof form.requestSubmit === 'function') {
      form.requestSubmit()
    } else {
      form.dispatchEvent(new Event('submit', { cancelable: true }))
    }
  }
}
