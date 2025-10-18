import { NextResponse } from 'next/server'
import { supabaseAdmin, isSupabaseConfigured } from '@/lib/supabase-server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    const {
      name,
      email,
      password,
      riskProfile,
      experienceLevel,
      tradingCapital,
      primaryMarkets,
      briefTime,
      voicePreference,
      watchlist,
    } = body

    console.log('📝 Creating user with Supabase:', { name, email, riskProfile })

    // Check if Supabase is configured
    if (!isSupabaseConfigured()) {
      console.error('❌ Supabase not configured - missing SUPABASE_SERVICE_KEY')
      return NextResponse.json(
        { 
          error: 'Service unavailable', 
          message: 'Database service is not configured. Please contact support.' 
        },
        { status: 503 }
      )
    }

    // Validate required fields
    if (!name || !email || !password || !riskProfile) {
      return NextResponse.json(
        { error: 'Missing required fields', message: 'Name, email, password, and risk profile are required' },
        { status: 400 }
      )
    }

    // Validate password strength
    if (password.length < 6) {
      return NextResponse.json(
        { error: 'Weak password', message: 'Password must be at least 6 characters long' },
        { status: 400 }
      )
    }

    // Create Supabase Auth user first
    const { data: authData, error: authError } = await supabaseAdmin.auth.admin.createUser({
      email,
      password,
      email_confirm: true, // Auto-confirm email for demo purposes
    })

    if (authError) {
      console.error('❌ Error creating auth user:', authError)
      return NextResponse.json(
        { error: 'Failed to create account', message: authError.message },
        { status: 400 }
      )
    }

    console.log('✅ Auth user created:', authData.user.id)

    // Create user profile in database
    // Map values to match database constraints
    const formatRiskProfile = (profile: string) => {
      return profile.charAt(0).toUpperCase() + profile.slice(1).toLowerCase()
    }

    const { data: user, error: userError } = await supabaseAdmin
      .from('users')
      .insert({
        id: authData.user.id, // Use the auth user ID
        email,
        name,
        risk_profile: formatRiskProfile(riskProfile), // 'moderate' -> 'Moderate'
        explanation_level: experienceLevel?.toLowerCase() || 'intermediate',
        trading_capital_range: tradingCapital,
        primary_markets: primaryMarkets || [],
        brief_time: briefTime || '08:00',
        preferred_voice: voicePreference || 'default',
      })
      .select()
      .single()

    if (userError) {
      console.error('❌ Error creating user profile:', userError)
      // Cleanup: delete the auth user if profile creation fails
      await supabaseAdmin.auth.admin.deleteUser(authData.user.id)
      return NextResponse.json(
        { error: 'Failed to create user profile', message: userError.message },
        { status: 500 }
      )
    }

    console.log('✅ User profile created:', user.id)

    // Add watchlist items if provided
    if (watchlist && watchlist.length > 0) {
      console.log('📋 Adding watchlist items:', watchlist)

      for (const symbol of watchlist) {
        // Check if instrument exists
        let { data: instrument } = await supabaseAdmin
          .from('instruments')
          .select('id')
          .eq('symbol', symbol)
          .single()

        // If not, create it
        if (!instrument) {
          const { data: newInstrument, error: instrumentError } = await supabaseAdmin
            .from('instruments')
            .insert({
              symbol,
              name: symbol,
            })
            .select()
            .single()

          if (instrumentError) {
            console.error('⚠️ Error creating instrument:', instrumentError)
            continue
          }
          instrument = newInstrument
        }

        // Add to watchlist
        const { error: watchlistError } = await supabaseAdmin
          .from('user_watchlist')
          .insert({
            user_id: user.id,
            instrument_id: instrument.id,
          })

        if (watchlistError) {
          console.error('⚠️ Error adding to watchlist:', watchlistError)
        }
      }

      console.log('✅ Watchlist items added')
    }

    console.log('✅ Onboarding completed successfully for user:', user.id)

    const response = NextResponse.json({ 
      success: true, 
      userId: user.id,
      message: 'Onboarding completed successfully!' 
    })

    return response

  } catch (error: any) {
    console.error('❌ Onboarding error:', error)
    return NextResponse.json(
      { 
        error: 'Failed to complete onboarding', 
        message: error.message || 'An unexpected error occurred' 
      },
      { status: 500 }
    )
  }
}

// GET endpoint to check if user exists
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const email = searchParams.get('email')

    if (!email) {
      return NextResponse.json(
        { error: 'Email parameter is required' },
        { status: 400 }
      )
    }

    const { data: user, error } = await supabaseAdmin
      .from('users')
      .select('id, email, name, created_at')
      .eq('email', email)
      .single()

    if (error || !user) {
      return NextResponse.json({ exists: false })
    }

    return NextResponse.json({
      exists: true,
      user,
    })

  } catch (error: any) {
    console.error('❌ Error checking user:', error)
    return NextResponse.json(
      { error: 'Failed to check user status' },
      { status: 500 }
    )
  }
}

