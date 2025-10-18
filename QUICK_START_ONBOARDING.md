# 🚀 Quick Start - Get Your Onboarding Working NOW!

## The Issue

Your Supabase database tables haven't been created yet, so the onboarding can't save data.

## The Solution (2 Minutes!)

Follow these simple steps:

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase Dashboard:
   ```
   https://supabase.com/dashboard/project/gpwzlcqbcvqhzsgekitt
   ```

2. Click **"SQL Editor"** in the left sidebar

3. Click **"New query"**

### Step 2: Copy & Paste SQL

1. Open the file: `SETUP_DATABASE.sql` (in this folder)

2. **Copy ALL the SQL** (Cmd+A, Cmd+C)

3. **Paste into the Supabase SQL Editor** (Cmd+V)

4. Click **"Run"** (or press Cmd+Enter)

You should see:
```
✅ Database setup complete!
📊 Tables created: users, instruments, user_watchlist...
🔒 Row Level Security enabled
🚀 Ready for onboarding!
```

### Step 3: Test It Works

Run this in your terminal:

```bash
cd "/Users/winstonyang/Desktop/Coding/Hackathons/Cursor Hackathon/kopitiam-kapital"
npm run supabase:test
```

You should see:
```
✅ Found X users
✅ Found X instruments
✅ User created successfully!
🎉 All tests passed!
```

### Step 4: Try Your Onboarding

```bash
cd apps/web
npm run dev
```

Then visit: **http://localhost:3002/onboarding**

Fill out the form, submit, and check your Supabase dashboard - you'll see the new user! 🎉

---

## What Just Happened?

The SQL script created all the tables you need:

✅ `users` - Your onboarding users  
✅ `instruments` - Stock symbols (AAPL, TSLA, etc.)  
✅ `user_watchlist` - User's watchlist items  
✅ `positions` - Trading positions  
✅ `recommendations` - AI trading recommendations  
✅ `pnl_snapshots` - P&L tracking  
✅ `notes` - RAG knowledge base  
✅ `events` - Market events  

Plus all the indexes, RLS policies, and helper functions!

---

## Troubleshooting

### "Extension vector does not exist"

No problem! The vector extension is optional (for AI embeddings later). 

Remove these lines from the SQL:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
-- And the line about vector in notes table
```

### Tables already exist?

That's fine! The script uses `CREATE TABLE IF NOT EXISTS`, so it won't error.

### Still having issues?

1. Check the SQL Editor output for specific errors
2. Make sure your project is active (not paused)
3. Try running individual CREATE TABLE statements one at a time

---

## What's Different from Prisma?

**Before (Prisma)**:
- Connection through Prisma → PostgreSQL pool → Supabase
- Needed migrations via Prisma CLI
- Connection pool issues

**Now (Supabase Client)**:
- Direct HTTP API connection
- More reliable and faster
- Easier to debug
- No connection pool limits

---

## Next Steps

Once your onboarding works:

1. ✅ Test creating multiple users
2. ✅ Check the data in Supabase dashboard
3. ✅ Build your dashboard using the `useUser()` hook
4. ✅ Add more features!

---

**Need more help?** Check the other documentation:
- `SUPABASE_SETUP.md` - Detailed Supabase guide
- `ONBOARDING_SUMMARY.md` - Complete onboarding docs
- `README_ONBOARDING.md` - Full implementation guide

