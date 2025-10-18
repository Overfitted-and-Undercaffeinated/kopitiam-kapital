import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

export interface User {
  id: string
  email: string
  name: string | null
  riskProfile: string
  experienceLevel: string
  tradingCapitalRange: string | null
  primaryMarkets: string[]
  briefTime: string | null
  preferredVoice: string
  timezone: string
  language: string
  createdAt: string
  watchlist?: Array<{
    id: string
    instrument: {
      id: string
      symbol: string
      name: string
      assetClass: string | null
    }
    addedAt: string
  }>
  positions?: Array<{
    id: string
    qty: number
    avgPrice: number
    stop: number | null
    target: number | null
    instrument: {
      symbol: string
      name: string
    }
  }>
}

interface UseUserReturn {
  user: User | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  updateUser: (data: Partial<User>) => Promise<void>
  logout: () => Promise<void>
}

/**
 * Custom hook to fetch and manage current user data with Supabase authentication
 * 
 * Usage:
 * ```tsx
 * const { user, loading, error, refetch, logout } = useUser()
 * 
 * if (loading) return <div>Loading...</div>
 * if (error) return <div>Error: {error}</div>
 * if (!user) return <div>Not logged in</div>
 * 
 * return <div>Welcome, {user.name}!</div>
 * ```
 */
export function useUser(): UseUserReturn {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()
  const supabase = createClient()

  const fetchUser = async () => {
    try {
      setLoading(true)
      setError(null)

      // Check auth state
      const { data: { user: authUser } } = await supabase.auth.getUser()
      
      if (!authUser) {
        setUser(null)
        setLoading(false)
        return
      }

      // Fetch user profile
      const response = await fetch('/api/user')
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || data.error || 'Failed to fetch user')
      }

      setUser(data.user)
    } catch (err: any) {
      console.error('Error fetching user:', err)
      setError(err.message)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const updateUser = async (updateData: Partial<User>) => {
    try {
      const response = await fetch('/api/user', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || data.error || 'Failed to update user')
      }

      setUser(data.user)
    } catch (err: any) {
      console.error('Error updating user:', err)
      throw err
    }
  }

  const logout = async () => {
    try {
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        throw error
      }

      setUser(null)
      router.push('/login')
      router.refresh()
    } catch (err: any) {
      console.error('Error logging out:', err)
      throw err
    }
  }

  useEffect(() => {
    fetchUser()

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_IN') {
        fetchUser()
      } else if (event === 'SIGNED_OUT') {
        setUser(null)
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  return {
    user,
    loading,
    error,
    refetch: fetchUser,
    updateUser,
    logout,
  }
}

