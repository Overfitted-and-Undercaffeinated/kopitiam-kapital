#!/usr/bin/env node

/**
 * Quick script to check database connectivity
 * Run: node scripts/check-db-connection.js
 */

const { PrismaClient } = require('@prisma/client')

const prisma = new PrismaClient()

async function checkConnection() {
  console.log('🔌 Checking database connection...\n')

  try {
    // Test basic connection
    await prisma.$connect()
    console.log('✅ Database connected successfully!')

    // Try a simple query
    const userCount = await prisma.user.count()
    console.log(`✅ User count query successful: ${userCount} users found`)

    // Check tables exist
    const instrumentCount = await prisma.instrument.count()
    console.log(`✅ Instrument count query successful: ${instrumentCount} instruments found`)

    console.log('\n🎉 All checks passed! Your database is ready.')
    console.log('\nYou can now:')
    console.log('  1. Start the dev server: cd apps/web && npm run dev')
    console.log('  2. Visit: http://localhost:3000/onboarding')
    console.log('  3. Fill out the form and submit')
    console.log('  4. Check your Supabase dashboard to see the new user!\n')

  } catch (error) {
    console.error('❌ Database connection failed!\n')
    console.error('Error:', error.message)
    
    if (error.code === 'P1001') {
      console.error('\n📝 Troubleshooting tips:')
      console.error('  1. Check if DATABASE_URL is correct in .env')
      console.error('  2. Verify your Supabase project is active (not paused)')
      console.error('  3. Check if your IP is whitelisted in Supabase dashboard')
      console.error('  4. Try: npx prisma db pull')
      console.error('\n  Your DATABASE_URL should look like:')
      console.error('  postgresql://postgres:password@db.xxx.supabase.co:5432/postgres\n')
    }
    
    process.exit(1)
  } finally {
    await prisma.$disconnect()
  }
}

checkConnection()

