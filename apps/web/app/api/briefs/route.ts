import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const userId = searchParams.get('userId')

    if (!userId) {
      return NextResponse.json({ error: 'User ID is required' }, { status: 400 })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)
    const today = new Date().toISOString().split('T')[0]

    // Fetch today's morning brief
    const { data: morningData, error: morningError } = await supabase
      .from('briefs')
      .select('*')
      .eq('user_id', userId)
      .eq('type', 'morning')
      .eq('date', today)
      .single()

    // Fetch today's EOD brief
    const { data: eodData, error: eodError } = await supabase
      .from('briefs')
      .select('*')
      .eq('user_id', userId)
      .eq('type', 'eod')
      .eq('date', today)
      .single()

    // Fetch historical briefs (last 30 days, excluding today)
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

    const { data: historicalData, error: historicalError } = await supabase
      .from('briefs')
      .select('*')
      .eq('user_id', userId)
      .lt('date', today)
      .gte('date', thirtyDaysAgo.toISOString().split('T')[0])
      .order('date', { ascending: false })
      .order('type', { ascending: false }) // 'morning' comes before 'eod'
      .limit(20)

    return NextResponse.json({
      morningBrief: morningData || null,
      eodBrief: eodData || null,
      historical: historicalData || [],
      errors: {
        morning: morningError?.message,
        eod: eodError?.message,
        historical: historicalError?.message,
      },
    })
  } catch (error: any) {
    console.error('Error fetching briefs:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { userId, type, date, content } = body

    if (!userId || !type || !date || !content) {
      return NextResponse.json(
        { error: 'userId, type, date, and content are required' },
        { status: 400 }
      )
    }

    if (!['morning', 'eod'].includes(type)) {
      return NextResponse.json({ error: 'Type must be "morning" or "eod"' }, { status: 400 })
    }

    const supabase = createClient(supabaseUrl, supabaseKey)

    // Insert or update brief
    const { data, error } = await supabase
      .from('briefs')
      .upsert(
        {
          user_id: userId,
          type,
          date,
          content,
        },
        {
          onConflict: 'user_id,type,date',
        }
      )
      .select()
      .single()

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json({ error: error.message }, { status: 500 })
    }

    return NextResponse.json({ success: true, brief: data }, { status: 200 })
  } catch (error: any) {
    console.error('Error creating brief:', error)
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

