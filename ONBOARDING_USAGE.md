# Onboarding System - Usage Guide

## Quick Start

Your onboarding system is ready to use! Here's how to test and integrate it.

## 🚀 Testing the Onboarding Flow

### Method 1: Manual Testing (Recommended)

1. **Start the development server:**
   ```bash
   cd apps/web
   npm run dev
   ```

2. **Visit the onboarding page:**
   ```
   http://localhost:3000/onboarding
   ```

3. **Fill out the form:**
   - Step 1: Name, email, risk profile
   - Step 2: Experience level, trading capital
   - Step 3: Primary markets, brief time
   - Step 4: Watchlist symbols

4. **Submit and verify:**
   - Check browser console for logs
   - Check Supabase dashboard for new user
   - Should redirect to `/dashboard` on success

### Method 2: API Testing with curl

Test the API endpoint directly:

```bash
curl -X POST http://localhost:3000/api/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "riskProfile": "moderate",
    "experienceLevel": "intermediate",
    "tradingCapital": "10K-50K",
    "primaryMarkets": ["SGX", "US"],
    "briefTime": "08:00",
    "voicePreference": "default",
    "watchlist": ["AAPL", "DBS", "TSLA"]
  }'
```

Expected response:
```json
{
  "success": true,
  "userId": "uuid-here",
  "message": "Onboarding completed successfully!"
}
```

### Method 3: Database Test Script

Once your Supabase instance is running:

```bash
node test-onboarding-simple.js
```

## 🔧 Integration Examples

### Using in Dashboard Component

```tsx
// apps/web/app/dashboard/page.tsx
'use client'

import { useUser } from '@/hooks/useUser'

export default function DashboardPage() {
  const { user, loading, error } = useUser()

  if (loading) {
    return <div>Loading your dashboard...</div>
  }

  if (error || !user) {
    // Redirect to onboarding if not logged in
    window.location.href = '/onboarding'
    return null
  }

  return (
    <div>
      <h1>Welcome, {user.name}!</h1>
      <p>Risk Profile: {user.riskProfile}</p>
      
      <h2>Your Watchlist</h2>
      <ul>
        {user.watchlist?.map((item) => (
          <li key={item.id}>
            {item.instrument.symbol} - {item.instrument.name}
          </li>
        ))}
      </ul>
    </div>
  )
}
```

### Checking User Authentication

```tsx
// apps/web/app/layout.tsx or middleware
import { cookies } from 'next/headers'

export async function checkAuth() {
  const cookieStore = cookies()
  const userId = cookieStore.get('user_id')?.value
  
  if (!userId) {
    // User not logged in
    return null
  }
  
  return userId
}
```

### Updating User Preferences

```tsx
// In any component
import { useUser } from '@/hooks/useUser'

function SettingsComponent() {
  const { user, updateUser } = useUser()

  const handleUpdateBriefTime = async () => {
    try {
      await updateUser({ briefTime: '09:00' })
      alert('Brief time updated!')
    } catch (error) {
      alert('Failed to update')
    }
  }

  return (
    <button onClick={handleUpdateBriefTime}>
      Change Brief Time to 9:00 AM
    </button>
  )
}
```

## 📊 Database Queries

### Get User with All Relations

```typescript
import { prisma } from '@/lib/prisma'

const fullUser = await prisma.user.findUnique({
  where: { id: userId },
  include: {
    watchlist: {
      include: { instrument: true }
    },
    positions: {
      include: { instrument: true }
    },
    recommendations: {
      include: { instrument: true },
      orderBy: { ts: 'desc' },
      take: 10,
    },
    pnlSnapshots: {
      orderBy: { ts: 'desc' },
      take: 30,
    },
  },
})
```

### Add Item to Watchlist

```typescript
// Create API route: apps/web/app/api/watchlist/route.ts
import { prisma } from '@/lib/prisma'
import { cookies } from 'next/headers'

export async function POST(request: Request) {
  const userId = cookies().get('user_id')?.value
  const { symbol } = await request.json()

  // Upsert instrument
  const instrument = await prisma.instrument.upsert({
    where: { symbol },
    update: {},
    create: { symbol, name: symbol },
  })

  // Add to watchlist
  const watchlistItem = await prisma.userWatchlist.create({
    data: {
      userId: userId!,
      instrumentId: instrument.id,
    },
  })

  return Response.json({ success: true, watchlistItem })
}
```

### Get User's Open Positions

```typescript
const openPositions = await prisma.position.findMany({
  where: {
    userId: userId,
    closedAt: null,
  },
  include: {
    instrument: true,
  },
})
```

## 🐛 Troubleshooting

### Issue: "Database connection failed"

**Cause**: Supabase instance not accessible

**Solution**:
1. Check if `.env` has correct `DATABASE_URL`
2. Verify Supabase project is active in dashboard
3. Check if IP is whitelisted in Supabase settings
4. Test connection: `npx prisma db pull`

### Issue: "Email already exists"

**Cause**: Trying to register with existing email

**Solution**: This is expected behavior. Either:
- Use a different email
- Delete the existing user from Supabase dashboard
- Implement login instead of signup

### Issue: "Validation failed"

**Cause**: Form data doesn't match schema

**Solution**: Check these in the frontend:
- Email is valid format
- Risk profile is one of: conservative, moderate, aggressive
- Experience level is: beginner, intermediate, expert
- Trading capital is: <10K, 10K-50K, 50K-100K, 100K+
- Primary markets array has at least one item
- Brief time is in HH:MM format

### Issue: "Cannot reach database server"

**Cause**: Network connectivity or Supabase instance paused

**Solution**:
1. Wake up Supabase project (free tier may pause)
2. Check network connectivity
3. Verify DATABASE_URL is correct
4. Try running migrations: `npx prisma migrate deploy`

## 🔐 Security Considerations

### Current Implementation

✅ **What's included:**
- httpOnly cookies (prevents XSS)
- Input validation with Zod
- Unique email constraint
- Transaction safety
- Error handling

⚠️ **What's missing (add for production):**
- Email verification
- Password authentication
- Rate limiting
- CSRF protection
- Session expiration handling
- Proper auth middleware

### Recommended for Production

Use a proper auth solution like:
- **NextAuth.js**: https://next-auth.js.org/
- **Clerk**: https://clerk.dev/
- **Supabase Auth**: https://supabase.com/docs/guides/auth
- **Auth0**: https://auth0.com/

Example with NextAuth.js:
```typescript
// Instead of simple cookie, use:
import { getServerSession } from "next-auth/next"
import { authOptions } from "@/app/api/auth/[...nextauth]/route"

const session = await getServerSession(authOptions)
const userId = session?.user?.id
```

## 📝 API Reference

### POST `/api/onboarding`

Create a new user with onboarding data.

**Request Body:**
```typescript
{
  name: string (min 2 chars)
  email: string (valid email)
  riskProfile: 'conservative' | 'moderate' | 'aggressive'
  experienceLevel: 'beginner' | 'intermediate' | 'expert'
  tradingCapital: '<10K' | '10K-50K' | '50K-100K' | '100K+'
  primaryMarkets: string[] (min 1 item)
  briefTime: string (HH:MM format)
  voicePreference: string
  watchlist: string[] (optional)
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "userId": "uuid",
  "message": "Onboarding completed successfully!"
}
```

**Response (Error - 400):**
```json
{
  "error": "Email already registered",
  "message": "This email is already associated with an account..."
}
```

### GET `/api/onboarding?email=user@example.com`

Check if a user with given email exists.

**Response:**
```json
{
  "exists": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2025-10-18T..."
  }
}
```

### GET `/api/user`

Get current authenticated user's data.

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "riskProfile": "MODERATE",
    "watchlist": [...],
    "positions": [...]
  }
}
```

### PATCH `/api/user`

Update user preferences.

**Request Body:**
```json
{
  "briefTime": "09:00",
  "riskProfile": "AGGRESSIVE"
}
```

## 🎯 Next Steps

1. **Test the flow**: Run the onboarding page and create a user
2. **Check database**: Verify data in Supabase dashboard
3. **Integrate auth**: Add proper authentication system
4. **Add features**: Build dashboard using user data
5. **Improve UX**: Add loading states, better errors, progress saving

## 📚 Resources

- [Prisma Docs](https://www.prisma.io/docs)
- [Supabase Dashboard](https://supabase.com/dashboard)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Zod Validation](https://zod.dev/)

---

**Status**: ✅ Ready for Testing
**Database**: Connected via Prisma + Supabase PostgreSQL
**Auth**: Simple cookie-based (upgrade to NextAuth for production)

