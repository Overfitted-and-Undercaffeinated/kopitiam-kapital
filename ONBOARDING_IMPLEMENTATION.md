# Onboarding Implementation Guide

## Overview

Your onboarding system is connected to Supabase PostgreSQL via Prisma ORM. This document explains how everything works together.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Frontend Form  │─────▶│  API Route       │─────▶│  Supabase DB    │
│  (Next.js)      │      │  /api/onboarding │      │  (PostgreSQL)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Prisma Client   │
                         │  (ORM)           │
                         └──────────────────┘
```

## Key Components

### 1. Database Schema (`prisma/schema.prisma`)

The schema defines your data structure:

```prisma
model User {
  id                  String          @id @default(uuid())
  email               String          @unique
  name                String?
  riskProfile         RiskProfile     @default(MODERATE)
  experienceLevel     ExperienceLevel @default(INTERMEDIATE)
  tradingCapitalRange TradingCapital?
  primaryMarkets      String[]
  briefTime           String?
  preferredVoice      String          @default("default")
  watchlist           UserWatchlist[]
  // ... other relations
}

model UserWatchlist {
  id           String      @id @default(uuid())
  userId       String
  instrumentId String
  user         User        @relation(...)
  instrument   Instrument  @relation(...)
}
```

### 2. Validation Layer (`apps/web/lib/validations/onboarding.ts`)

Uses Zod for runtime validation:

```typescript
export const onboardingSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  riskProfile: z.enum(['conservative', 'moderate', 'aggressive']),
  // ... other fields
})
```

### 3. API Route (`apps/web/app/api/onboarding/route.ts`)

Handles the onboarding request:

#### POST `/api/onboarding`
- **Purpose**: Create a new user with their onboarding data
- **Input**: User form data (validated with Zod)
- **Output**: `{ success: true, userId: string, message: string }`
- **Features**:
  - Transaction-based (atomic operations)
  - Enum mapping (frontend → database)
  - Watchlist creation with instrument upsert
  - Session cookie creation
  - Comprehensive error handling

#### GET `/api/onboarding?email=user@example.com`
- **Purpose**: Check if a user already exists
- **Output**: `{ exists: boolean, user?: {...} }`

### 4. Frontend Form (`apps/web/app/onboarding/page.tsx`)

4-step wizard that collects:
1. Name, email, risk profile
2. Experience level, trading capital
3. Primary markets, brief time
4. Initial watchlist

## Data Flow

### When User Submits Onboarding:

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Prisma
    participant Supabase

    User->>Frontend: Fill form & submit
    Frontend->>API: POST /api/onboarding
    API->>API: Validate with Zod
    API->>Prisma: Begin transaction
    Prisma->>Supabase: CREATE user
    Supabase-->>Prisma: User created
    loop For each watchlist item
        Prisma->>Supabase: UPSERT instrument
        Prisma->>Supabase: CREATE user_watchlist
    end
    Prisma->>API: Commit transaction
    API->>Frontend: Success + userId + cookie
    Frontend->>User: Redirect to dashboard
```

## Key Features

### ✅ Transaction Safety
Uses Prisma transactions to ensure all-or-nothing operations:
```typescript
await prisma.$transaction(async (tx) => {
  const user = await tx.user.create({...})
  // Watchlist operations
  return user
})
```

### ✅ Enum Mapping
Converts frontend values to database enums:
- `"conservative"` → `CONSERVATIVE`
- `"<10K"` → `UNDER_10K`
- `"beginner"` → `BEGINNER`

### ✅ Instrument Upsert
Creates instruments only if they don't exist:
```typescript
const instrument = await tx.instrument.upsert({
  where: { symbol },
  update: {},
  create: { symbol, name: symbol },
})
```

### ✅ Error Handling
Comprehensive error messages:
- `P2002`: Duplicate email
- `P2003`: Foreign key constraint
- Validation errors
- Generic fallback

### ✅ Session Management
Sets httpOnly cookie with user ID for 30 days

## Environment Variables

Required in `.env`:
```env
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
NODE_ENV=development
```

## Testing

### Manual Test
1. Start dev server: `cd apps/web && npm run dev`
2. Visit: `http://localhost:3000/onboarding`
3. Fill form and submit
4. Check Supabase dashboard for new user

### Automated Test
Run the test script:
```bash
cd apps/web
npx ts-node --project tsconfig.json scripts/test-onboarding.ts
```

This will:
1. ✅ Test database connection
2. ✅ Create a test user
3. ✅ Add watchlist items
4. ✅ Retrieve user with relations
5. ✅ Clean up test data

## Common Issues & Solutions

### Issue: `@prisma/client` not found
**Solution**: 
```bash
cd /path/to/root
npm install @prisma/client
npx prisma generate
```

### Issue: Database connection fails
**Solution**: 
1. Check `DATABASE_URL` in `.env`
2. Ensure Supabase instance is running
3. Test connection: `npx prisma db pull`

### Issue: Enum type errors
**Solution**: 
- Use the mapping functions in `lib/validations/onboarding.ts`
- Ensure frontend values match validation schema

### Issue: Migration needed
**Solution**:
```bash
npx prisma migrate dev --name add_new_field
```

## Database Schema Updates

When you need to add fields to the User model:

1. Update `prisma/schema.prisma`
2. Create migration: `npx prisma migrate dev --name describe_changes`
3. Update frontend form to collect new data
4. Update validation schema
5. Regenerate Prisma client: `npx prisma generate`

## Best Practices

1. **Always use transactions** for multi-step operations
2. **Validate at both layers** (frontend + backend)
3. **Map enums properly** to avoid type errors
4. **Use upsert** for idempotent operations
5. **Set proper cookie flags** (httpOnly, secure, sameSite)
6. **Handle all error cases** explicitly
7. **Log for debugging** (console.log statements included)

## Next Steps

### Recommended Enhancements:

1. **Real Authentication**: Replace simple cookie with NextAuth.js or Clerk
2. **Email Verification**: Send verification email on signup
3. **Instrument API**: Fetch real instrument data (name, market, etc.)
4. **Progress Persistence**: Save partial form data to localStorage
5. **Analytics**: Track onboarding completion rates
6. **A/B Testing**: Test different onboarding flows
7. **Welcome Email**: Send personalized welcome email
8. **Profile Pictures**: Allow users to upload avatars

### API Enhancements:

```typescript
// apps/web/app/api/onboarding/route.ts

// Add endpoint to update preferences
export async function PATCH(request: Request) { ... }

// Add endpoint to resend verification email
export async function POST /api/onboarding/resend-verification { ... }
```

## Quick Reference

### Check if user exists:
```typescript
const response = await fetch('/api/onboarding?email=user@example.com')
const { exists, user } = await response.json()
```

### Get user data:
```typescript
const user = await prisma.user.findUnique({
  where: { id: userId },
  include: {
    watchlist: { include: { instrument: true } },
    positions: true,
    recommendations: true,
  },
})
```

### Update user preferences:
```typescript
await prisma.user.update({
  where: { id: userId },
  data: {
    riskProfile: 'AGGRESSIVE',
    briefTime: '09:00',
  },
})
```

## Support

- **Prisma Docs**: https://www.prisma.io/docs
- **Supabase Docs**: https://supabase.com/docs
- **Next.js API Routes**: https://nextjs.org/docs/api-routes/introduction
- **Zod Validation**: https://zod.dev/

---

**Status**: ✅ Fully Implemented and Ready to Use
**Last Updated**: October 18, 2025

