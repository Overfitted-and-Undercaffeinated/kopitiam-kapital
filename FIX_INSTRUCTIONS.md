# 🔧 Quick Fix for "Unexpected token" Error

## The Problem
The error "Unexpected token '<', "<!DOCTYPE "... is not valid JSON" means the API route couldn't load the environment variables.

## The Solution

### Step 1: Stop Your Dev Server
Press `Ctrl+C` in the terminal where the server is running

### Step 2: Restart the Dev Server
```bash
cd apps/web
npm run dev
```

### Step 3: Try Again
1. Visit: http://localhost:3002/onboarding
2. Fill out all 4 steps
3. Submit

## What I Fixed

✅ Created `apps/web/.env.local` with Supabase credentials  
✅ This file makes the environment variables available to Next.js API routes  
✅ The server needs to restart to pick up the new file  

## If It Still Doesn't Work

Check the terminal where `npm run dev` is running. You should see:
```
○ Compiling /api/onboarding/route ...
✓ Compiled /api/onboarding/route
```

If you see errors about "Missing Supabase environment variables", the .env.local file didn't load properly.

## Alternative: Copy Environment Variables

If the automated fix didn't work, manually create this file:

**File: `apps/web/.env.local`**
```
# Supabase Configuration for Next.js
NEXT_PUBLIC_SUPABASE_URL=https://gpwzlcqbcvqhzsgekitt.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdwd3psY3FiY3ZxaHpzZ2VraXR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA3NTgxMjQsImV4cCI6MjA3NjMzNDEyNH0.SifzxSgNWLI4LldpOsPM5mIXHM5gPA1kn80bxQ-27qw

# Server-side Supabase (for API routes)
SUPABASE_URL=https://gpwzlcqbcvqhzsgekitt.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdwd3psY3FiY3ZxaHpzZ2VraXR0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDc1ODEyNCwiZXhwIjoyMDc2MzM0MTI0fQ.Abfp6xfhRto2cyBtguNBijRue5B6ZLtjzFE-19XifWk
```

Then restart: `npm run dev`

---

**That's it! The onboarding should work now.** 🎉

