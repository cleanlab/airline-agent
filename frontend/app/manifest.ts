import type { MetadataRoute } from 'next'

export default async function manifest(): Promise<MetadataRoute.Manifest> {
  const name = 'RAG app'
  const short_name = 'RAG app'
  return {
    name,
    short_name,
    icons: [{ src: '/favicon.ico', sizes: 'any', type: 'image/x-icon' }]
  }
}
