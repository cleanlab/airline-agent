// Slightly modified version of
// https://github.com/javascripter/next-scroll-restoration to support the use of
// the same pathname for different chat histories within the same assistant

export type ScrollState = {
  /**
   * key: `[PAGE_KEY]:[RESTORATION_ID]`
   */
  [key: string]: {
    scrollX: number
    scrollY: number
  }
}

export type ScrollRestorationManager = {
  updateScroll: (
    scrollKey: string,
    restorationId: string,
    {
      scrollX,
      scrollY
    }: {
      scrollX: number
      scrollY: number
    }
  ) => void
  restoreScroll: (
    href: string,
    scrollKey: string,
    scroll: 'default' | 'scroll' | 'no-scroll'
  ) => void
}
