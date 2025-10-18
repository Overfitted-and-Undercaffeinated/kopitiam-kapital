#!/usr/bin/env node

/**
 * Test Supabase connection using the JavaScript client
 * Run: node scripts/test-supabase-connection.js
 */

require('dotenv').config()
const { createClient } = require('@supabase/supabase-js')

const supabaseUrl = process.env.SUPABASE_URL
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('❌ Missing environment variables!')
  console.error('Please ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set in .env')
  process.exit(1)
}

const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
  },
})

async function testConnection() {
  console.log('🔌 Testing Supabase connection...\n')
  console.log('URL:', supabaseUrl)
  console.log('')

  try {
    // Test 1: Check users table
    console.log('1️⃣ Querying users table...')
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('id, email, name')
      .limit(5)

    if (usersError) {
      console.error('❌ Error querying users:', usersError.message)
      throw usersError
    }

    console.log(`✅ Found ${users.length} users`)
    if (users.length > 0) {
      console.log('   Sample:', users[0].email)
    }
    console.log('')

    // Test 2: Check instruments table
    console.log('2️⃣ Querying instruments table...')
    const { data: instruments, error: instrumentsError } = await supabase
      .from('instruments')
      .select('id, symbol, name')
      .limit(5)

    if (instrumentsError) {
      console.error('❌ Error querying instruments:', instrumentsError.message)
      throw instrumentsError
    }

    console.log(`✅ Found ${instruments.length} instruments`)
    if (instruments.length > 0) {
      console.log('   Sample:', instruments[0].symbol)
    }
    console.log('')

    // Test 3: Try creating a test user
    console.log('3️⃣ Testing user creation...')
    const testEmail = `test-${Date.now()}@example.com`
    
    const { data: newUser, error: createError } = await supabase
      .from('users')
      .insert({
        email: testEmail,
        name: 'Test User',
        risk_profile: 'Moderate',
        explanation_level: 'intermediate',
      })
      .select()
      .single()

    if (createError) {
      console.error('❌ Error creating user:', createError.message)
      throw createError
    }

    console.log('✅ User created successfully!')
    console.log('   ID:', newUser.id)
    console.log('   Email:', newUser.email)
    console.log('')

    // Test 4: Clean up
    console.log('4️⃣ Cleaning up test data...')
    const { error: deleteError } = await supabase
      .from('users')
      .delete()
      .eq('id', newUser.id)

    if (deleteError) {
      console.error('❌ Error deleting user:', deleteError.message)
    } else {
      console.log('✅ Test data cleaned up')
    }
    console.log('')

    console.log('🎉 All tests passed! Your Supabase connection is working.')
    console.log('\nYou can now:')
    console.log('  1. Start the dev server: cd apps/web && npm run dev')
    console.log('  2. Visit: http://localhost:3002/onboarding')
    console.log('  3. Fill out the form and submit')
    console.log('  4. Check your Supabase dashboard to see the new user!\n')

  } catch (error) {
    console.error('\n❌ Connection test failed!')
    console.error('Error:', error.message)
    console.error('\n📝 Troubleshooting tips:')
    console.error('  1. Check if SUPABASE_URL and SUPABASE_SERVICE_KEY are correct in .env')
    console.error('  2. Verify your Supabase project is active in the dashboard')
    console.error('  3. Ensure the tables exist (users, instruments, user_watchlist)')
    console.error('  4. Try running migrations: npm run db:migrate\n')
    process.exit(1)
  }
}

testConnection()

