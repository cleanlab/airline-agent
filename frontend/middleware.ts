import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Request pathname const
  const requestPathname = request.nextUrl.pathname

  // Set a header with path so I can get that info in my server components
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('next-url', requestPathname)

  return NextResponse.next({
    request: {
      headers: requestHeaders
    }
  })
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$).*)']
}
