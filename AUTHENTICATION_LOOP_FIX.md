# Authentication Loop Fix

## Problem Diagnosis

The authentication loop was caused by several issues in the middleware:

### 1. **Cookie Handling Issue**
The middleware was recreating the `response` object every time cookies were set/removed (lines 50-59 in old code). This could cause cookie synchronization issues between the request and response.

**Old Code:**
```typescript
set(name: string, value: string, options: CookieOptions) {
  request.cookies.set({ name, value, ...options })
  response = NextResponse.next({  // ❌ Recreating response object
    request: { headers: request.headers }
  })
  response.cookies.set({ name, value, ...options })
}
```

**Fixed:**
```typescript
set(name: string, value: string, options: CookieOptions) {
  // Update both request and response cookies without recreating response
  request.cookies.set({ name, value, ...options })
  response.cookies.set({ name, value, ...options })
}
```

### 2. **Aggressive Redirect on Auth Routes**
The middleware was unconditionally redirecting authenticated users away from `/login` and `/onboarding`, which interfered with the login flow when users had a `redirectTo` parameter.

**Old Code:**
```typescript
if (user && (request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/onboarding')) {
  return NextResponse.redirect(new URL('/dashboard', request.url))  // ❌ Always redirects
}
```

**Fixed:**
```typescript
if (user && isAuthRoute) {
  const redirectTo = request.nextUrl.searchParams.get('redirectTo')
  // Only redirect if there's no redirectTo parameter
  if (!redirectTo) {
    console.log('🔍 Middleware - User already authenticated, redirecting to dashboard')
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }
}
```

### 3. **Response Object Initialization Timing**
The response object was being initialized before checking environment variables, which could cause issues if the environment check failed.

**Fixed:** Response object is now created after environment validation.

## Changes Made

### File: `apps/web/middleware.ts`

1. **Moved response initialization** to after environment checks
2. **Fixed cookie handlers** to not recreate the response object
3. **Added auth route detection** to distinguish between public auth pages and protected routes
4. **Improved redirect logic** to respect `redirectTo` query parameters during authentication flow
5. **Enhanced logging** to show auth route status for better debugging

## Key Improvements

✅ **No more redirect loops** - Middleware now respects the authentication flow  
✅ **Better cookie handling** - Cookies are properly synchronized without object recreation  
✅ **Smarter redirects** - Only redirects when appropriate, respects query parameters  
✅ **Enhanced debugging** - More detailed console logs for troubleshooting  

## Testing Instructions

1. **Test Login Flow:**
   ```bash
   # Navigate to protected route without authentication
   # Should redirect to /login with redirectTo parameter
   http://localhost:3000/dashboard
   # After login, should redirect back to /dashboard
   ```

2. **Test Direct Dashboard Access:**
   ```bash
   # If already logged in, should access dashboard directly
   http://localhost:3000/dashboard
   ```

3. **Test Login Page with Auth:**
   ```bash
   # If already logged in and no redirectTo parameter
   # Should redirect to /dashboard
   http://localhost:3000/login
   
   # If already logged in WITH redirectTo parameter
   # Should NOT redirect (let login page handle it)
   http://localhost:3000/login?redirectTo=/dashboard
   ```

4. **Test Logout Flow:**
   ```bash
   # Logout, then try to access protected route
   # Should redirect to login
   ```

## Important Notes

⚠️ **Middleware changes require server restart**  
After modifying middleware.ts, you MUST restart the Next.js dev server:
```bash
# Stop server (Ctrl+C)
# Then restart
npm run dev
```

⚠️ **Clear browser cookies if issues persist**  
If you still experience loops after the fix, clear your browser cookies for localhost:3000

## Related Files

- `apps/web/middleware.ts` - Main fix applied here
- `apps/web/app/login/page.tsx` - Handles redirectTo parameter
- `apps/web/app/dashboard/page.tsx` - Protected route
- `apps/web/hooks/useUser.ts` - Client-side auth state

## Root Cause Summary

The authentication loop occurred because:
1. Middleware was aggressively redirecting from /login → /dashboard
2. Dashboard was checking auth and redirecting to /login
3. Cookie handling was unreliable due to response object recreation
4. This created an infinite loop: `/dashboard` → `/login` → `/dashboard` → ...

The fix breaks this loop by:
- Allowing the login page to handle its own redirects when a `redirectTo` parameter exists
- Properly maintaining cookie state throughout the authentication flow
- Only redirecting when necessary and appropriate

