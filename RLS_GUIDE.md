# Row Level Security (RLS) Implementation Guide

## Overview

Row Level Security (RLS) is a critical security feature that ensures users can only access their own data. This guide shows you how to check and implement RLS in your Supabase database.

## Current Status

Based on your migrations, here's what we found:

### ✅ Tables with Some RLS (from `99999_quick_setup.sql`)
- `users` - Partial policies
- `instruments` - Partial policies  
- `user_watchlist` - Partial policies

### ❌ Tables Missing RLS
- `positions` - **CRITICAL** (user financial data)
- `recommendations` - **CRITICAL** (personalized AI recommendations)
- `pnl_snapshots` - **CRITICAL** (user P&L data)
- `notes` - User notes/annotations
- `events` - Market events
- `briefs` - **CRITICAL** (personalized morning/EOD briefs)

## How to Check Current RLS Status

### Option 1: Using Supabase CLI (Local)

```bash
# Start Supabase locally if not running
supabase start

# Check RLS status
supabase db remote execute "
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
"
```

### Option 2: Using Supabase Studio

1. Open Supabase Studio: `http://localhost:54323` (if running locally)
2. Go to **Database** → **Tables**
3. Click on each table and check the **RLS** toggle
4. Click **View policies** to see existing policies

### Option 3: Direct SQL Query

Connect to your database and run:

```sql
-- Check which tables have RLS enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Check existing policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd as operation
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### Option 4: Using the Helper Script

We've created a helper script for you:

```bash
chmod +x scripts/check-rls.sh
DATABASE_URL="your-database-url" ./scripts/check-rls.sh
```

## How to Apply the New RLS Migration

### Method 1: Using Supabase CLI (Recommended)

```bash
# Apply all pending migrations
supabase db reset

# Or push to remote
supabase db push
```

### Method 2: Manual SQL Execution

1. Copy the contents of `supabase/migrations/20250119000000_enable_rls_all_tables.sql`
2. Open Supabase Studio → SQL Editor
3. Paste and run the SQL
4. Verify with the check queries above

### Method 3: Using psql

```bash
psql $DATABASE_URL -f supabase/migrations/20250119000000_enable_rls_all_tables.sql
```

## What the New RLS Policies Do

### 🔒 Security Model

The new migration implements a two-tier security model:

#### 1. **Service Role** (Backend API)
- Full access to all tables
- Used by your AI agents and backend services
- Bypasses RLS (trusted backend)

#### 2. **Authenticated Users** (Frontend)
- Can only access their own data
- Policies enforce `auth.uid() = user_id`
- Cannot see other users' positions, P&L, recommendations, etc.

### 📋 Table-by-Table Breakdown

| Table | Service Role | Authenticated Users |
|-------|-------------|---------------------|
| **users** | Full access | Can view/update own profile |
| **instruments** | Full access | Read-only (public market data) |
| **positions** | Full access | CRUD own positions only |
| **events** | Full access | Read-only (public market events) |
| **recommendations** | Full access | View/update own recommendations |
| **pnl_snapshots** | Full access | View own P&L only |
| **notes** | Full access | CRUD own notes |
| **user_watchlist** | Full access | CRUD own watchlist |
| **briefs** | Full access | View own briefs only |

### 🎯 Key Features

1. **User Isolation**: Users can only see their own financial data
2. **Public Data Access**: Market instruments and events are readable by all
3. **Backend Control**: AI agents can write recommendations, briefs, etc.
4. **User Control**: Users can manage their own positions and watchlist

## Testing RLS

### Test 1: Verify RLS is Enabled

```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

All tables should show `rowsecurity = true`.

### Test 2: Test User Isolation

Create two test users and try to access each other's data:

```sql
-- As user 1
SELECT * FROM positions WHERE user_id = 'user-1-uuid';  -- ✅ Should work

-- Try to access user 2's data
SELECT * FROM positions WHERE user_id = 'user-2-uuid';  -- ❌ Should return empty
```

### Test 3: Test Service Role Access

Using your backend API (service role):

```typescript
// Should work - service role bypasses RLS
const { data } = await supabase
  .from('positions')
  .select('*')
  .eq('user_id', 'any-user-uuid');
```

### Test 4: Test Frontend Access

Using authenticated user token:

```typescript
// Should only return current user's positions
const { data } = await supabase
  .from('positions')
  .select('*');
```

## Common Issues and Solutions

### Issue 1: "permission denied for table X"

**Cause**: Missing GRANT statements

**Solution**: Run this:

```sql
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;
```

### Issue 2: "new row violates row-level security policy"

**Cause**: User trying to insert data for another user

**Solution**: Ensure frontend always uses `auth.uid()` for user_id:

```typescript
const { data: { user } } = await supabase.auth.getUser();
await supabase.from('positions').insert({
  user_id: user.id,  // Always use authenticated user's ID
  // ... other fields
});
```

### Issue 3: RLS policies not applying

**Cause**: Using service role key in frontend

**Solution**: Use anon/authenticated key in frontend:

```typescript
// ❌ DON'T use service role in frontend
const supabase = createClient(url, SERVICE_ROLE_KEY);

// ✅ DO use anon key
const supabase = createClient(url, ANON_KEY);
```

## Verification Checklist

- [ ] All tables have RLS enabled
- [ ] Service role policies exist for all tables
- [ ] User-specific policies exist for user data tables
- [ ] Tested with two different users
- [ ] Frontend uses anon/authenticated key (not service role)
- [ ] Backend uses service role key
- [ ] No permission errors in application logs

## Quick Commands Reference

```bash
# Check local Supabase status
supabase status

# Start local Supabase
supabase start

# Apply migrations
supabase db reset

# Generate TypeScript types (after migration)
supabase gen types typescript --local > apps/web/types/database.types.ts

# Open Supabase Studio
open http://localhost:54323
```

## Next Steps

1. **Apply the migration** using one of the methods above
2. **Verify RLS is enabled** on all tables
3. **Test user isolation** with multiple test accounts
4. **Update your frontend** to use authenticated Supabase client
5. **Update your backend** to use service role client

## Need Help?

If you encounter issues:

1. Check Supabase logs: `supabase logs`
2. Verify your Supabase keys in `.env`
3. Test policies in SQL Editor with `SET ROLE authenticated`
4. Review the migration file for any syntax errors

## Security Best Practices

✅ **DO:**
- Use service role only in backend/server-side code
- Use anon key in frontend
- Always filter by `auth.uid()` in client queries
- Test RLS with multiple users
- Enable RLS on all tables with user data

❌ **DON'T:**
- Expose service role key to frontend
- Disable RLS on production databases
- Trust client-provided user IDs
- Skip testing RLS policies
- Use `USING (true)` for user data without proper filters

