import { NextResponse } from 'next/server'
import { createServerSupabaseClient } from '@/lib/supabase-server'

/**
 * POST /api/auth/logout - Sign out the current user
 */
export async function POST(request: Request) {
  try {
    const supabase = await createServerSupabaseClient()
    
    const { error } = await supabase.auth.signOut()

    if (error) {
      throw error
    }

    return NextResponse.json({
      success: true,
      message: 'Logged out successfully',
    })

  } catch (error: any) {
    console.error('❌ Error logging out:', error)
    return NextResponse.json(
      { error: 'Failed to logout', message: error.message },
      { status: 500 }
    )
  }
}

