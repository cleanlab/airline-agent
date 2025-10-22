import { produce } from 'immer'
import type { StateCreator } from 'zustand'

export type ResponseRating = boolean | undefined

export type ResponseRatingsSlice = {
  responseRatings: Record<string, ResponseRating>
  setResponseRating: (args: {
    messageId: string
    rating: ResponseRating
  }) => void
}

export const createRatingsSlice: StateCreator<ResponseRatingsSlice> = (
  set,
  get
) => ({
  responseRatings: {},
  setResponseRating: ({ messageId, rating }) => {
    const ratings = get().responseRatings ?? {}
    set({
      responseRatings: produce(ratings, draft => {
        draft[messageId] = rating
      })
    })
  }
})
