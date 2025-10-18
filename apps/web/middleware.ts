/**
 * IMPORTANT: After modifying this file, restart the dev server:
 * 1. Stop the dev server (Ctrl+C)
 * 2. Run: npm run dev
 * 
 * Middleware changes do not hot-reload!
 */

import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  console.log('🚨 MIDDLEWARE RUNNING - Path:', request.nextUrl.pathname)
  let response = NextResponse.next({
    request: {
      headers: request.headers,
    },
  })

  // Define protected routes first
  const protectedRoutes = ['/dashboard', '/assistant', '/portfolio', '/backtest', '/analysis', '/alerts', '/sentiment']
  const isProtectedRoute = protectedRoutes.some(route => 
    request.nextUrl.pathname.startsWith(route)
  )

  try {
    // Check environment variables
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL || !process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY) {
      console.error('🚨 Middleware - Missing Supabase environment variables')
      if (isProtectedRoute) {
        return NextResponse.redirect(new URL('/login', request.url))
      }
      return response
    }

    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
      {
        cookies: {
          get(name: string) {
            return request.cookies.get(name)?.value
          },
          set(name: string, value: string, options: CookieOptions) {
            request.cookies.set({
              name,
              value,
              ...options,
            })
            response = NextResponse.next({
              request: {
                headers: request.headers,
              },
            })
            response.cookies.set({
              name,
              value,
              ...options,
            })
          },
          remove(name: string, options: CookieOptions) {
            request.cookies.set({
              name,
              value: '',
              ...options,
            })
            response = NextResponse.next({
              request: {
                headers: request.headers,
              },
            })
            response.cookies.set({
              name,
              value: '',
              ...options,
            })
          },
        },
      }
    )

    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error) {
      console.error('🚨 Middleware - Supabase auth error:', error)
    }

    // Debug logging
    console.log('🔍 Middleware - User:', user ? { id: user.id, email: user.email } : 'None')
    console.log('🔍 Middleware - Is protected route:', isProtectedRoute)

    // Redirect to login if accessing protected route without authentication
    if (isProtectedRoute && !user) {
      console.log('🔍 Middleware - Redirecting to login for path:', request.nextUrl.pathname)
      const redirectUrl = new URL('/login', request.url)
      redirectUrl.searchParams.set('redirectTo', request.nextUrl.pathname)
      return NextResponse.redirect(redirectUrl)
    }

    // Redirect to dashboard if already logged in and trying to access login/onboarding
    if (user && (request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/onboarding')) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    return response

  } catch (error) {
    console.error('🚨 Middleware - Failed to create Supabase client:', error)
    // Redirect to login on error for protected routes
    if (isProtectedRoute) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
    return response
  }
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/assistant/:path*',
    '/portfolio/:path*',
    '/backtest/:path*',
    '/analysis/:path*',
    '/alerts/:path*',
    '/sentiment/:path*',
    '/login',
    '/onboarding',
    '/',
  ],
}

