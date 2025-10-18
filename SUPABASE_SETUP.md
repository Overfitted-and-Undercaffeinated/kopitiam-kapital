# Supabase Setup Guide

## Quick Fix for Your Issue

The database connection works, but the tables haven't been created yet. Let's fix that!

## Option 1: Run Migrations via Supabase Dashboard (EASIEST)

1. **Go to your Supabase Dashboard**:
   - Visit: https://supabase.com/dashboard/project/gpwzlcqbcvqhzsgekitt

2. **Open SQL Editor**:
   - Click on "SQL Editor" in the left sidebar

3. **Run the migration SQL**:
   - Copy the content from `supabase/migrations/20240101000000_create_schema.sql`
   - Paste it into the SQL editor
   - Click "Run"

4. **Run additional migrations**:
   - Do the same for `20240101000001_add_vector_search.sql`
   - And `20250101000000_add_onboarding_fields.sql`

## Option 2: Use Supabase CLI (Recommended for Development)

### Install Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# Or using npm
npm install -g supabase
```

### Link to Your Project

```bash
cd supabase
supabase link --project-ref gpwzlcqbcvqhzsgekitt
```

When prompted, enter your database password: `Repmonkeys123$`

### Push Migrations

```bash
# From the project root
npm run db:migrate

# Or directly
cd supabase
supabase db push
```

## Option 3: Quick Manual Setup (If migrations don't work)

Run this SQL directly in your Supabase SQL Editor:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  risk_profile TEXT CHECK (risk_profile IN ('Conservative', 'Moderate', 'Aggressive')),
  explanation_level TEXT CHECK (explanation_level IN ('beginner', 'intermediate', 'expert')) DEFAULT 'intermediate',
  trading_capital_range TEXT CHECK (trading_capital_range IN ('<10K', '10K-50K', '50K-100K', '100K+')),
  primary_markets TEXT[] DEFAULT '{}',
  brief_time TEXT DEFAULT '08:00',
  preferred_voice TEXT DEFAULT 'default',
  timezone TEXT DEFAULT 'Asia/Singapore',
  language TEXT DEFAULT 'en',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create instruments table
CREATE TABLE IF NOT EXISTS instruments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  symbol TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  mic TEXT,
  asset_class TEXT,
  tick_size DECIMAL,
  lot_size INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  instrument_id UUID REFERENCES instruments(id) ON DELETE CASCADE NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, instrument_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON user_watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_instrument ON user_watchlist(instrument_id);

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;

-- Create policies to allow service role full access
CREATE POLICY "Service role has full access to users" ON users
  FOR ALL USING (true);

CREATE POLICY "Service role has full access to instruments" ON instruments
  FOR ALL USING (true);

CREATE POLICY "Service role has full access to user_watchlist" ON user_watchlist
  FOR ALL USING (true);
```

## Verify Setup

After running migrations, test the connection:

```bash
npm run supabase:test
```

You should see:
```
✅ Found X users
✅ Found X instruments
✅ User created successfully!
✅ Test data cleaned up
🎉 All tests passed!
```

## Test Your Onboarding

1. **Start the dev server**:
   ```bash
   cd apps/web
   npm run dev
   ```

2. **Visit the onboarding page**:
   ```
   http://localhost:3002/onboarding
   ```

3. **Fill out the form and submit**

4. **Check Supabase Dashboard**:
   - Go to Table Editor
   - Look for your new user in the `users` table
   - Check `user_watchlist` for watchlist items

## Troubleshooting

### "Could not find the table"
- Tables haven't been created yet
- Run the SQL from Option 3 above

### "relation does not exist"
- Same as above - tables missing
- Use Supabase dashboard SQL editor

### "permission denied"
- RLS policies might be blocking
- Add the policies from Option 3
- Or disable RLS for testing: `ALTER TABLE users DISABLE ROW LEVEL SECURITY;`

### "connection refused" 
- Project might be paused (free tier)
- Go to dashboard and wake it up

## What Changed from Prisma

**Before (Prisma)**:
- Used Prisma Client → PostgreSQL
- Required Prisma generate
- Connection through connection pool

**Now (Supabase Client)**:
- Direct Supabase JavaScript client
- No code generation needed
- HTTP API connection (more reliable)
- Uses service role key for admin operations

## Next Steps

Once tables are created and test passes:

1. ✅ Test onboarding flow
2. ✅ Verify data in Supabase dashboard  
3. ✅ Build your dashboard using user data
4. ✅ Add more features as needed

---

**Quick Command Reference:**

```bash
# Test connection
npm run supabase:test

# Run migrations (if using Supabase CLI)
npm run db:migrate

# Start dev server
npm run web:dev
```

