import type { StateCreator } from 'zustand'
import type { PersistOptions } from 'zustand/middleware'

/**
 * Workaround for zustand persist middleware typing
 */
export type ZustandPersist<T> = (
  config: StateCreator<T>,
  options: Omit<PersistOptions<T>, 'partialize'> & {
    partialize: (state: T) => Partial<T>
  }
) => StateCreator<T>
