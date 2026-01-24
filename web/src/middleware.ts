import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

// Block aggressive bots
const BLOCKED_BOTS = [
  'AhrefsBot',
  'SemrushBot',
  'MJ12bot',
  'DotBot',
  'BLEXBot',
  'PetalBot',
  'Bytespider',
  'GPTBot',
  'ClaudeBot',
  'anthropic-ai',
  'CCBot',
  'DataForSeoBot',
  'Amazonbot',
  'magpie-crawler',
  'Yandex',
  'bingbot',  // Optional: block Bing
]

export async function middleware(request: NextRequest) {
  // Block aggressive bots
  const userAgent = request.headers.get('user-agent') || ''
  const isBot = BLOCKED_BOTS.some(bot => userAgent.toLowerCase().includes(bot.toLowerCase()))

  if (isBot) {
    return new NextResponse('Blocked', { status: 403 })
  }

  // Skip auth callback route - it needs to process the code/token first
  if (request.nextUrl.pathname.startsWith('/auth/callback')) {
    return NextResponse.next()
  }

  let supabaseResponse = NextResponse.next({
    request,
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({
            request,
          })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          )
        },
      },
    }
  )

  // Refresh session if expired
  const {
    data: { user },
  } = await supabase.auth.getUser()

  // Protect admin routes
  if (request.nextUrl.pathname.startsWith('/admin')) {
    // Check admin status if user is logged in
    let isAdmin = false
    if (user) {
      const { data } = await supabase.rpc('check_is_admin', { check_user_id: user.id })
      isAdmin = data === true
    }

    // Login page logic
    if (request.nextUrl.pathname === '/admin/login') {
      // If logged in AND is admin, redirect to dashboard
      if (user && isAdmin) {
        return NextResponse.redirect(new URL('/admin', request.url))
      }
      // Otherwise, allow access to login page (even if logged in but not admin)
      return supabaseResponse
    }

    // For all other admin pages, require authentication AND admin role
    if (!user) {
      return NextResponse.redirect(new URL('/admin/login', request.url))
    }

    if (!isAdmin) {
      // Logged in but not admin - redirect to login with error
      return NextResponse.redirect(new URL('/admin/login?error=not_admin', request.url))
    }
  }

  return supabaseResponse
}

export const config = {
  matcher: [
    // Match all paths except static files
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
