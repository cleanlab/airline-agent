import type { MetadataRoute } from 'next'

export default async function manifest(): Promise<MetadataRoute.Manifest> {
  const name = 'Support Agent'
  const short_name = 'Agent'
  return {
    name,
    short_name,
    icons: [{ src: '/favicon.ico', sizes: 'any', type: 'image/x-icon' }]
  }
}
