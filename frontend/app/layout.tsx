import '@/app/globals.css'
import { Providers } from '@/components/providers'
import { TailwindIndicator } from '@/components/tailwind-indicator'
import { Toaster } from '@/components/ui/sonner'
import { GeistMono } from 'geist/font/mono'
import { GeistSans } from 'geist/font/sans'
import type { Metadata } from 'next'
import { ScrollRestoration } from '../components/next-scroll-restoration'
import { cn } from '@/lib/utils/tailwindUtils'

export async function generateMetadata(): Promise<Metadata> {
  const title = 'RAG app'
  const description =
    'A trustworthy AI agent enhanced with your own data, built by Cleanlab.'

  return {
    metadataBase: process.env.VERCEL_URL
      ? new URL(`https://${process.env.VERCEL_URL}`)
      : undefined,
    title: {
      default: title,
      template: `%s - ${title}`
    },
    description,
    openGraph: {},
    twitter: {}
  }
}

export const viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' }
  ]
}

interface RootLayoutProps {
  children: React.ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          'min-h-screen min-w-[250px] font-sans antialiased',
          GeistSans.variable,
          GeistMono.variable
        )}
      >
        <ScrollRestoration />
        <Toaster position="top-center" />
        <Providers
          themes={['light', 'dark']}
          attribute="data-theme"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex h-dvh min-h-0 flex-col">
            <main className="flex min-h-0 flex-1 flex-col bg-muted/50">
              {children}
            </main>
          </div>
          <TailwindIndicator />
        </Providers>
      </body>
    </html>
  )
}
