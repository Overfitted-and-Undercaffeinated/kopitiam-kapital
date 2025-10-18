/**
 * Test script to verify onboarding flow and database connection
 * Run with: npx ts-node --project tsconfig.json scripts/test-onboarding.ts
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient({
  log: ['query', 'info', 'warn', 'error'],
})

async function testOnboarding() {
  console.log('🧪 Testing Onboarding Flow...\n')

  try {
    // Test 1: Database connection
    console.log('1️⃣ Testing database connection...')
    await prisma.$connect()
    console.log('✅ Database connected successfully\n')

    // Test 2: Create a test user
    console.log('2️⃣ Creating test user...')
    const testEmail = `test-${Date.now()}@example.com`
    
    const user = await prisma.user.create({
      data: {
        email: testEmail,
        name: 'Test User',
        riskProfile: 'MODERATE',
        experienceLevel: 'INTERMEDIATE',
        tradingCapitalRange: 'TEN_TO_50K',
        primaryMarkets: ['SGX', 'US'],
        briefTime: '08:00',
        preferredVoice: 'default',
      },
    })
    console.log('✅ User created:', user.id)
    console.log('   Email:', user.email)
    console.log('   Name:', user.name)
    console.log('   Risk Profile:', user.riskProfile)
    console.log('')

    // Test 3: Create instruments and watchlist
    console.log('3️⃣ Adding watchlist items...')
    const watchlistSymbols = ['AAPL', 'DBS', 'TSLA']
    
    for (const symbol of watchlistSymbols) {
      const instrument = await prisma.instrument.upsert({
        where: { symbol },
        update: {},
        create: {
          symbol,
          name: symbol,
        },
      })

      await prisma.userWatchlist.create({
        data: {
          userId: user.id,
          instrumentId: instrument.id,
        },
      })
      console.log(`   ✅ Added ${symbol} to watchlist`)
    }
    console.log('')

    // Test 4: Retrieve user with watchlist
    console.log('4️⃣ Retrieving user with watchlist...')
    const userWithWatchlist = await prisma.user.findUnique({
      where: { id: user.id },
      include: {
        watchlist: {
          include: {
            instrument: true,
          },
        },
      },
    })

    console.log('✅ User retrieved:')
    console.log('   Watchlist count:', userWithWatchlist?.watchlist.length)
    userWithWatchlist?.watchlist.forEach((item) => {
      console.log(`   - ${item.instrument.symbol}`)
    })
    console.log('')

    // Test 5: Clean up test data
    console.log('5️⃣ Cleaning up test data...')
    await prisma.userWatchlist.deleteMany({
      where: { userId: user.id },
    })
    await prisma.user.delete({
      where: { id: user.id },
    })
    console.log('✅ Test data cleaned up\n')

    console.log('🎉 All tests passed!')

  } catch (error: any) {
    console.error('❌ Test failed:', error.message)
    if (error.code) {
      console.error('   Error code:', error.code)
    }
    process.exit(1)
  } finally {
    await prisma.$disconnect()
  }
}

testOnboarding()

