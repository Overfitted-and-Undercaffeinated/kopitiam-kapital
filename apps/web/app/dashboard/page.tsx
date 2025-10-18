'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'
import BriefOverlay from '@/components/BriefOverlay'

// Dynamically import the cowboy scene
const CowboyScene = dynamic(
  () => import('../onboarding/components/CowboyScene').then((mod) => mod.default),
  { ssr: false }
)

interface Brief {
  id: string
  type: 'morning' | 'eod'
  date: string
  content: {
    summary: string
    market_overview: string
    key_points: string[]
    recommendations?: string[]
    portfolio_summary?: {
      total_value: string
      daily_pnl: string
      positions: number
    }
  }
}

export default function DashboardPage() {
  const [showMorningBrief, setShowMorningBrief] = useState(true) // ALWAYS SHOW ON LOAD
  const [showEODBrief, setShowEODBrief] = useState(false)
  const [activeTab, setActiveTab] = useState<'dashboard' | 'history'>('dashboard')
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 })
  const [todayMorningBrief, setTodayMorningBrief] = useState<Brief | null>(null)
  const [todayEODBrief, setTodayEODBrief] = useState<Brief | null>(null)
  const [historicalBriefs, setHistoricalBriefs] = useState<Brief[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [rawMorningData, setRawMorningData] = useState<any>(null)
  const [rawEODData, setRawEODData] = useState<any>(null)

  // Track cursor position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Fetch briefs on mount
  useEffect(() => {
    const userId = localStorage.getItem('userId') || 'demo_user'
    
    // Try to fetch real briefs from AI backend
    fetchRealBriefs(userId)
  }, [])
  
  const fetchRealBriefs = async (userId: string) => {
    setIsLoading(true)
    
    try {
      const AI_API_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000'
      const watchlist = ['NVDA', 'AAPL', 'DBS'] // Default watchlist
      
      console.log('=== FETCHING MORNING BRIEF FROM PYTHON API ===')
      console.log('API URL:', AI_API_URL)
      console.log('Request payload:', { watchlist, market: 'US', user_id: userId, include_voice: false })
      
      // Fetch raw morning brief directly from Python backend
      const morningResponse = await fetch(`${AI_API_URL}/briefs/morning`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          watchlist,
          market: 'US',
          user_id: userId,
          include_voice: true
        }),
        signal: AbortSignal.timeout(60000) // 60 second timeout
      })
      
      console.log('Morning brief response status:', morningResponse.status)
      
      if (morningResponse.ok) {
        const morningData = await morningResponse.json()
        console.log('✅ MORNING BRIEF RECEIVED FROM PYTHON API:')
        console.log('Full response:', morningData)
        setRawMorningData(morningData)
        
        // Create a simple brief object for fallback
        setTodayMorningBrief({
          id: '1',
          type: 'morning',
          date: new Date().toISOString(),
          content: {
            summary: morningData.text || 'No summary available',
            market_overview: morningData.text || 'No overview available',
            key_points: []
          }
        })
      } else {
        const errorText = await morningResponse.text()
        console.error('❌ Failed to fetch morning brief from backend')
        console.error('Status:', morningResponse.status)
        console.error('Error response:', errorText)
      }
      
      console.log('=== FETCHING EOD BRIEF FROM PYTHON API ===')
      
      // Fetch raw EOD brief directly from Python backend
      const eodResponse = await fetch(`${AI_API_URL}/briefs/eod`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          watchlist,
          market: 'US',
          user_id: userId,
          include_voice: true
        }),
        signal: AbortSignal.timeout(60000) // 60 second timeout
      })
      
      console.log('EOD brief response status:', eodResponse.status)
      
      if (eodResponse.ok) {
        const eodData = await eodResponse.json()
        console.log('✅ EOD BRIEF RECEIVED FROM PYTHON API:')
        console.log('Full response:', eodData)
        setRawEODData(eodData)
        
        // Create a simple brief object for fallback
        setTodayEODBrief({
          id: '2',
          type: 'eod',
          date: new Date().toISOString(),
          content: {
            summary: eodData.text || 'No summary available',
            market_overview: eodData.text || 'No overview available',
            key_points: []
          }
        })
      } else {
        const errorText = await eodResponse.text()
        console.error('❌ Failed to fetch EOD brief from backend')
        console.error('Status:', eodResponse.status)
        console.error('Error response:', errorText)
      }
      
      // If both failed, log it clearly but don't use dummy data
      if (!morningResponse.ok && !eodResponse.ok) {
        console.error('❌ BOTH BRIEFS FAILED - NO DATA AVAILABLE')
        console.error('Check that Python backend is running at:', AI_API_URL)
      }
      
    } catch (error) {
      console.error('❌ EXCEPTION WHILE FETCHING BRIEFS:', error)
      console.error('Error details:', {
        name: error instanceof Error ? error.name : 'Unknown',
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined
      })
    } finally {
      setIsLoading(false)
      console.log('=== BRIEF FETCHING COMPLETE ===')
    }
  }


  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-4 border-[#8B7355] border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9] relative" style={{ fontFamily: 'var(--font-body)' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#2F1810]">
                Kopitiam Capital
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                Your AI-powered trading companion
              </p>
            </div>
            <div className="flex gap-3">
              <motion.button
                onClick={() => setShowMorningBrief(true)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-4 py-2 bg-[#8B7355] text-white rounded-lg text-sm font-medium hover:bg-[#6F5D47] transition-colors"
              >
                Morning Brief
              </motion.button>
              <motion.button
                onClick={() => setShowEODBrief(true)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-4 py-2 bg-white text-[#2F1810] rounded-lg text-sm font-medium hover:bg-[#F5F5F4] transition-colors border border-[#E5E5E5]"
              >
                EOD Report
              </motion.button>
              <motion.a
                href="/assistant"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="px-4 py-2 bg-gradient-to-r from-[#CD853F] to-[#D2691E] text-white rounded-lg text-sm font-medium hover:from-[#D2691E] hover:to-[#8B4513] transition-all shadow-md"
              >
                🤠 Ask Kopi
              </motion.a>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="sticky top-[73px] z-30 bg-white border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6">
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-4 py-3 text-sm font-medium transition-all relative ${
                activeTab === 'dashboard'
                  ? 'text-[#2F1810]'
                  : 'text-[#9CA3AF] hover:text-[#6B5D52]'
              }`}
            >
              Dashboard
              {activeTab === 'dashboard' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B7355]"
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              )}
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-4 py-3 text-sm font-medium transition-all relative ${
                activeTab === 'history'
                  ? 'text-[#2F1810]'
                  : 'text-[#9CA3AF] hover:text-[#6B5D52]'
              }`}
            >
              History
              {activeTab === 'history' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B7355]"
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' ? (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {/* Portfolio Overview */}
              <section className="bg-white rounded-lg p-6 border border-[#E5E5E5]">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-[#2F1810]">
                    Portfolio
                  </h2>
                  <button className="text-sm text-[#6B5D52] hover:text-[#2F1810] transition-colors font-medium">
                    View Details
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-[#FAFAF9] rounded-lg border border-[#E5E5E5]">
                    <div className="text-sm text-[#6B5D52] mb-1">Portfolio Value</div>
                    <div className="text-3xl font-bold text-[#2F1810]">$52,450</div>
                    <div className="text-sm text-green-600 mt-1">+8.5% all time</div>
                  </div>
                  <div className="p-4 bg-[#FAFAF9] rounded-lg border border-[#E5E5E5]">
                    <div className="text-sm text-[#6B5D52] mb-1">Today's P&L</div>
                    <div className="text-3xl font-bold text-green-600">+$685</div>
                    <div className="text-sm text-green-600 mt-1">+1.3%</div>
                  </div>
                  <div className="p-4 bg-[#FAFAF9] rounded-lg border border-[#E5E5E5]">
                    <div className="text-sm text-[#6B5D52] mb-1">Open Positions</div>
                    <div className="text-3xl font-bold text-[#2F1810]">5</div>
                    <div className="text-sm text-[#6B5D52] mt-1">All in profit</div>
                  </div>
                </div>
              </section>

              {/* Positions */}
              <section className="bg-white rounded-lg border border-[#E5E5E5]">
                <div className="p-6 border-b border-[#E5E5E5]">
                  <h2 className="text-xl font-bold text-[#2F1810]">
                    Active Positions
                  </h2>
                </div>
                <div className="divide-y divide-[#E5E5E5]">
                  {[
                    { symbol: 'DBS', name: 'DBS Group Holdings', qty: 100, entry: 35.2, current: 35.73, pnl: 53 },
                    { symbol: '9CI', name: 'CapitaLand Investment', qty: 500, entry: 3.15, current: 3.21, pnl: 30 },
                    { symbol: 'O39', name: 'OCBC Bank', qty: 150, entry: 13.5, current: 13.68, pnl: 27 },
                    { symbol: 'U11', name: 'UOB', qty: 80, entry: 30.8, current: 31.15, pnl: 28 },
                    { symbol: 'C52', name: 'ComfortDelGro', qty: 1000, entry: 1.35, current: 1.38, pnl: 30 },
                  ].map((position, idx) => (
                    <motion.div
                      key={position.symbol}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-4 hover:bg-[#FAFAF9] transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-10 h-10 bg-[#8B7355] rounded-full flex items-center justify-center text-white font-bold text-sm">
                            {position.symbol.charAt(0)}
                          </div>
                          <div>
                            <div className="font-semibold text-[#2F1810]">{position.symbol}</div>
                            <div className="text-sm text-[#6B5D52]">{position.name}</div>
                          </div>
                        </div>
                        <div className="text-right mr-8">
                          <div className="text-sm text-[#6B5D52]">
                            {position.qty} @ ${position.entry.toFixed(2)}
                          </div>
                          <div className="text-[#2F1810] font-medium">
                            ${position.current.toFixed(2)}
                          </div>
                        </div>
                        <div className="text-right min-w-[100px]">
                          <div className="font-semibold text-green-600">+${position.pnl}</div>
                          <div className="text-sm text-green-600">
                            +{((position.pnl / (position.qty * position.entry)) * 100).toFixed(2)}%
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </section>

              {/* Trading Ideas */}
              <section className="bg-white rounded-lg p-6 border border-[#E5E5E5]">
                <h2 className="text-xl font-bold text-[#2F1810] mb-6">
                  Today's Opportunities
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    {
                      symbol: 'V03',
                      name: 'Venture Corp',
                      action: 'BUY',
                      entry: 15.8,
                      target: 16.5,
                      reason: 'Oversold bounce opportunity on strong support',
                    },
                    {
                      symbol: 'S68',
                      name: 'SGX',
                      action: 'WATCH',
                      entry: 9.2,
                      target: 9.6,
                      reason: 'Breaking above resistance, volume confirming',
                    },
                  ].map((idea, idx) => (
                    <motion.div
                      key={idea.symbol}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: idx * 0.1 }}
                      className="p-5 bg-[#FAFAF9] rounded-lg border border-[#E5E5E5] hover:border-[#8B7355] transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <div className="text-lg font-bold text-[#2F1810]">{idea.symbol}</div>
                          <div className="text-sm text-[#6B5D52]">{idea.name}</div>
                        </div>
                        <div
                          className={`px-3 py-1 rounded-md text-xs font-semibold ${
                            idea.action === 'BUY'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}
                        >
                          {idea.action}
                        </div>
                      </div>
                      <p className="text-[#4A3F35] text-sm mb-4">{idea.reason}</p>
                      <div className="flex items-center justify-between text-sm">
                        <div>
                          <div className="text-[#6B5D52]">Entry</div>
                          <div className="font-semibold text-[#2F1810]">${idea.entry}</div>
                        </div>
                        <div className="text-[#9CA3AF]">→</div>
                        <div>
                          <div className="text-[#6B5D52]">Target</div>
                          <div className="font-semibold text-[#2F1810]">${idea.target}</div>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </section>
            </motion.div>
          ) : (
            <motion.div
              key="history"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              <section className="bg-white rounded-lg border border-[#E5E5E5]">
                <div className="p-6 border-b border-[#E5E5E5]">
                  <h2 className="text-xl font-bold text-[#2F1810]">
                    Brief History
                  </h2>
                </div>
                <div className="divide-y divide-[#E5E5E5]">
                  {historicalBriefs.map((brief, idx) => (
                    <motion.div
                      key={brief.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      onClick={() => {
                        if (brief.type === 'morning') {
                          setTodayMorningBrief(brief)
                          setShowMorningBrief(true)
                        } else {
                          setTodayEODBrief(brief)
                          setShowEODBrief(true)
                        }
                      }}
                      className="p-5 hover:bg-[#FAFAF9] transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-semibold text-sm ${
                            brief.type === 'morning' 
                              ? 'bg-amber-100 text-amber-700' 
                              : 'bg-indigo-100 text-indigo-700'
                          }`}>
                            {brief.type === 'morning' ? 'AM' : 'PM'}
                          </div>
                          <div>
                            <div className="font-semibold text-[#2F1810]">
                              {brief.type === 'morning' ? 'Morning Brief' : 'EOD Report'}
                            </div>
                            <div className="text-sm text-[#6B5D52]">
                              {new Date(brief.date).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                              })}
                            </div>
                          </div>
                        </div>
                        <svg className="w-5 h-5 text-[#9CA3AF]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                      <p className="mt-3 text-[#6B5D52] text-sm line-clamp-2">
                        {brief.content.summary}
                      </p>
                    </motion.div>
                  ))}
                </div>
              </section>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Brief Overlays - SHOW RAW BACKEND DATA */}
      <BriefOverlay
        isOpen={showMorningBrief && !isLoading}
        onClose={() => setShowMorningBrief(false)}
        type="morning"
        brief={{
          date: todayMorningBrief?.date || new Date().toISOString().split('T')[0],
          summary: todayMorningBrief?.content.summary || "Loading your morning brief...",
          market_overview: todayMorningBrief?.content.market_overview || "Markets are opening...",
          key_points: todayMorningBrief?.content.key_points || ["Loading..."],
          recommendations: todayMorningBrief?.content.recommendations || []
        }}
        rawBackendData={rawMorningData}
      />
      {todayEODBrief && (
        <BriefOverlay
          isOpen={showEODBrief}
          onClose={() => setShowEODBrief(false)}
          type="eod"
          brief={{
            date: todayEODBrief.date,
            ...todayEODBrief.content,
          }}
          rawBackendData={rawEODData}
        />
      )}
    </div>
  )
}
