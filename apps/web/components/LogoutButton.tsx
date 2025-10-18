'use client'

import { useState } from 'react'
import { createClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'

interface LogoutButtonProps {
  className?: string
  variant?: 'default' | 'danger'
}

export default function LogoutButton({ className = '', variant = 'default' }: LogoutButtonProps) {
  const [loading, setLoading] = useState(false)
  const router = useRouter()
  const supabase = createClient()

  const handleLogout = async () => {
    setLoading(true)
    
    try {
      const { error } = await supabase.auth.signOut()
      
      if (error) {
        throw error
      }

      router.push('/login')
      router.refresh()
    } catch (error: any) {
      console.error('Logout error:', error)
      alert('Failed to logout: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const baseClasses = "px-4 py-2 rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
  
  const variantClasses = {
    default: "bg-[#D2691E] hover:bg-[#CD853F] text-white",
    danger: "bg-red-600 hover:bg-red-700 text-white"
  }

  return (
    <button
      onClick={handleLogout}
      disabled={loading}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    >
      {loading ? 'Logging out...' : 'Logout'}
    </button>
  )
}

