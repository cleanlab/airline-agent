/**
 * Creates a custom string sorting function based on a specified order.
 *
 * @param order - An array of strings that defines the custom sorting order.
 * @returns A comparison function that can be used with Array.sort().
 *
 * @example
 * const customSort = createCustomStringSort(['apple', 'banana', 'cherry']);
 * const fruits = ['cherry', 'apple', 'date', 'banana'];
 * fruits.sort(customSort);
 * // Result: ['apple', 'banana', 'cherry', 'date']
 */
export const createCustomStringSort =
  (order: string[]) =>
  /**
   * Compares two strings based on the custom order.
   *
   * @param a - The first string to compare.
   * @param b - The second string to compare.
   * @returns A number indicating the sort order:
   *          - Negative if 'a' should come before 'b'
   *          - Positive if 'b' should come before 'a'
   *          - Zero if the order doesn't matter
   */
  (a: string, b: string): number => {
    const indexA = order.indexOf(a)
    const indexB = order.indexOf(b)

    if (indexA !== -1 && indexB !== -1) {
      // Both elements are in the order array
      return indexA - indexB
    } else if (indexA !== -1) {
      // Only 'a' is in the order array
      return -1
    } else if (indexB !== -1) {
      // Only 'b' is in the order array
      return 1
    } else {
      // Neither element is in the order array, sort alphabetically
      return a.localeCompare(b)
    }
  }
