import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient({
  log: ['query', 'info', 'warn', 'error'],
})

async function testConnection() {
  try {
    console.log('🔍 Testing database connection...')
    console.log('📡 DATABASE_URL:', process.env.DATABASE_URL?.replace(/:[^:@]+@/, ':****@'))
    
    // Try a simple query
    const result = await prisma.$queryRaw`SELECT NOW() as current_time, version() as pg_version`
    
    console.log('✅ Connection successful!')
    console.log('🎉 Database info:', result)
    
    // Try listing tables
    const tables = await prisma.$queryRaw`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `
    
    console.log('\n📋 Existing tables:')
    console.log(tables)
    
  } catch (error: any) {
    console.error('❌ Connection failed!')
    console.error('Error:', error.message)
    
    if (error.message.includes("Can't reach database server")) {
      console.log('\n💡 Troubleshooting tips:')
      console.log('1. Check if your DATABASE_URL is correct')
      console.log('2. Make sure your Supabase project is running')
      console.log('3. Check if your IP is allowed in Supabase')
      console.log('4. Try using the connection pooler URL (port 6543)')
      console.log('\n📝 Expected URL format:')
      console.log('postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres')
    }
  } finally {
    await prisma.$disconnect()
  }
}

testConnection()

