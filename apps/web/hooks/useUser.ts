import { useState, useEffect } from 'react'

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
}

/**
 * Custom hook to fetch and manage current user data
 * 
 * Usage:
 * ```tsx
 * const { user, loading, error, refetch } = useUser()
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

  const fetchUser = async () => {
    try {
      setLoading(true)
      setError(null)

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

  useEffect(() => {
    fetchUser()
  }, [])

  return {
    user,
    loading,
    error,
    refetch: fetchUser,
    updateUser,
  }
}

