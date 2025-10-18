import { NextResponse } from 'next/server'
import { supabaseAdmin } from '@/lib/supabase-server'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    const {
      name,
      email,
      riskProfile,
      experienceLevel,
      tradingCapital,
      primaryMarkets,
      briefTime,
      voicePreference,
      watchlist,
    } = body

    console.log('📝 Creating user with Supabase:', { name, email, riskProfile })

    // Validate required fields
    if (!name || !email || !riskProfile) {
      return NextResponse.json(
        { error: 'Missing required fields', message: 'Name, email, and risk profile are required' },
        { status: 400 }
      )
    }

    // Check if user already exists
    const { data: existingUser } = await supabaseAdmin
      .from('users')
      .select('id')
      .eq('email', email)
      .single()

    if (existingUser) {
      return NextResponse.json(
        { 
          error: 'Email already registered', 
          message: 'This email is already associated with an account. Please use a different email.' 
        },
        { status: 400 }
      )
    }

    // Create user
    // Map values to match database constraints
    const formatRiskProfile = (profile: string) => {
      return profile.charAt(0).toUpperCase() + profile.slice(1).toLowerCase()
    }

    const { data: user, error: userError } = await supabaseAdmin
      .from('users')
      .insert({
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
      console.error('❌ Error creating user:', userError)
      return NextResponse.json(
        { error: 'Failed to create user', message: userError.message },
        { status: 500 }
      )
    }

    console.log('✅ User created:', user.id)

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

    // Set user ID in a cookie
    const response = NextResponse.json({ 
      success: true, 
      userId: user.id,
      message: 'Onboarding completed successfully!' 
    })

    response.cookies.set('user_id', user.id, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 30, // 30 days
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

