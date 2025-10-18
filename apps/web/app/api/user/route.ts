import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { cookies } from 'next/headers'

/**
 * GET /api/user - Get current user information
 * Retrieves user data based on the user_id cookie
 */
export async function GET(request: Request) {
  try {
    const cookieStore = cookies()
    const userId = cookieStore.get('user_id')?.value

    if (!userId) {
      return NextResponse.json(
        { error: 'Not authenticated', message: 'No user session found' },
        { status: 401 }
      )
    }

    // Get user with their watchlist and positions
    const user = await prisma.user.findUnique({
      where: { id: userId },
      include: {
        watchlist: {
          include: {
            instrument: {
              select: {
                id: true,
                symbol: true,
                name: true,
                assetClass: true,
              },
            },
          },
          orderBy: {
            addedAt: 'desc',
          },
        },
        positions: {
          where: {
            closedAt: null, // Only get open positions
          },
          include: {
            instrument: {
              select: {
                symbol: true,
                name: true,
              },
            },
          },
        },
      },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found', message: 'User session is invalid' },
        { status: 404 }
      )
    }

    // Don't send sensitive data to frontend
    const { ...userData } = user

    return NextResponse.json({
      success: true,
      user: userData,
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
    const cookieStore = cookies()
    const userId = cookieStore.get('user_id')?.value

    if (!userId) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      )
    }

    const body = await request.json()
    
    // Only allow updating specific fields
    const allowedFields = [
      'name',
      'riskProfile',
      'experienceLevel',
      'tradingCapitalRange',
      'primaryMarkets',
      'briefTime',
      'preferredVoice',
      'timezone',
      'language',
    ]

    const updateData: any = {}
    
    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        updateData[field] = body[field]
      }
    }

    const updatedUser = await prisma.user.update({
      where: { id: userId },
      data: updateData,
    })

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

