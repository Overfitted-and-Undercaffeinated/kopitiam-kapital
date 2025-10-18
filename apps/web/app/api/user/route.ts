import { NextResponse } from 'next/server'
import { createServerSupabaseClient, supabaseAdmin } from '@/lib/supabase-server'

/**
 * GET /api/user - Get current user information
 * Retrieves user data based on Supabase authentication
 */
export async function GET(request: Request) {
  try {
    console.log('🔍 /api/user called')
    const supabase = await createServerSupabaseClient()
    
    // Get the authenticated user
    const { data: { user: authUser }, error: authError } = await supabase.auth.getUser()
    console.log('🔐 Auth user:', authUser ? { id: authUser.id, email: authUser.email } : 'None')
    console.log('❌ Auth error:', authError)

    if (authError || !authUser) {
      console.log('❌ Not authenticated, returning 401')
      return NextResponse.json(
        { error: 'Not authenticated', message: 'No user session found' },
        { status: 401 }
      )
    }

    // Get user profile from database with their watchlist and positions
    console.log('🔍 Fetching user profile for ID:', authUser.id)
    const { data: user, error: userError } = await supabaseAdmin
      .from('users')
      .select(`
        *,
        watchlist:user_watchlist(
          id,
          added_at,
          instrument:instruments(
            id,
            symbol,
            name,
            asset_class
          )
        ),
        positions(
          id,
          instrument_id,
          qty,
          avg_price,
          opened_at,
          instrument:instruments(
            symbol,
            name
          )
        )
      `)
      .eq('id', authUser.id)
      .is('positions.closed_at', null)
      .single()

    console.log('📦 User profile query result:', { user, userError })
    if (user) {
      console.log('✅ User profile found:', { id: user.id, name: user.name, email: user.email })
    }

    if (userError || !user) {
      console.log('❌ User profile not found, returning 404')
      return NextResponse.json(
        { error: 'User not found', message: 'User profile not found' },
        { status: 404 }
      )
    }

    console.log('✅ Returning user data successfully')
    return NextResponse.json({
      success: true,
      user: user,
    })

  } catch (error: any) {
    console.error('❌ Error fetching user:', error)
    return NextResponse.json(
      { error: 'Failed to fetch user data', message: error.message },
      { status: 500 }
    )
  }
}

/**
 * PATCH /api/user - Update user preferences
 */
export async function PATCH(request: Request) {
  try {
    const supabase = await createServerSupabaseClient()
    
    // Get the authenticated user
    const { data: { user: authUser }, error: authError } = await supabase.auth.getUser()

    if (authError || !authUser) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    // Only allow updating specific fields (convert camelCase to snake_case)
    const fieldMapping: Record<string, string> = {
      'name': 'name',
      'riskProfile': 'risk_profile',
      'experienceLevel': 'explanation_level',
      'tradingCapitalRange': 'trading_capital_range',
      'primaryMarkets': 'primary_markets',
      'briefTime': 'brief_time',
      'preferredVoice': 'preferred_voice',
      'timezone': 'timezone',
      'language': 'language',
    }

    const updateData: any = {}
    
    for (const [camelKey, snakeKey] of Object.entries(fieldMapping)) {
      if (body[camelKey] !== undefined) {
        updateData[snakeKey] = body[camelKey]
      }
    }

    const { data: updatedUser, error: updateError } = await supabaseAdmin
      .from('users')
      .update(updateData)
      .eq('id', authUser.id)
      .select()
      .single()

    if (updateError) {
      throw updateError
    }

    return NextResponse.json({
      success: true,
      user: updatedUser,
      message: 'User preferences updated successfully',
    })

  } catch (error: any) {
    console.error('❌ Error updating user:', error)
    return NextResponse.json(
      { error: 'Failed to update user', message: error.message },
      { status: 500 }
    )
  }
}

