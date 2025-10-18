'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'
import BriefOverlay from '@/components/BriefOverlay'
import WelcomeSequence from '@/components/WelcomeSequence'
import { useUser } from '@/hooks/useUser'

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
  const [recommendations, setRecommendations] = useState<any[]>([])
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)
  
  // Welcome sequence state
  const [showWelcomeSequence, setShowWelcomeSequence] = useState(true)
  const [welcomeComplete, setWelcomeComplete] = useState(false)
  
  // Use the useUser hook to get authenticated user data
  const { user, loading: userLoading, error: userError } = useUser()
  
  // Debug logging for user data
  useEffect(() => {
    console.log('🔍 User hook state:', { user, userLoading, userError })
    if (user) {
      console.log('✅ User data loaded:', { name: user.name, email: user.email })
    }
  }, [user, userLoading, userError])

  // Check if user is not authenticated and redirect to login
  useEffect(() => {
    if (!userLoading && !user && (userError?.includes('User profile not found') || !userError)) {
      console.log('🚨 No user found, redirecting to login...')
      window.location.href = '/login?redirectTo=/dashboard'
    }
  }, [user, userLoading, userError])

  // Fallback: If useUser hook is taking too long, try direct API call
  useEffect(() => {
    if (userLoading && !user) {
      console.log('⏰ useUser hook taking too long, trying direct API call...')
      const timeoutId = setTimeout(async () => {
        try {
          const response = await fetch('/api/user')
          const data = await response.json()
          console.log('🔍 Direct API call result:', data)
        } catch (error) {
          console.error('❌ Direct API call failed:', error)
        }
      }, 2000) // Try after 2 seconds
      
      return () => clearTimeout(timeoutId)
    }
  }, [userLoading, user])

  // Track cursor position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Start data fetching immediately on mount (user data handled by useUser hook)
  useEffect(() => {
    const userId = localStorage.getItem('userId') || 'demo_user'
    
    // Try to fetch real briefs from AI backend
    fetchRealBriefs(userId)
    
    // Fetch recommendations for watchlist
    fetchRecommendations(userId, ['NVDA', 'AAPL', 'DBS'])
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

  const fetchRecommendations = async (userId: string, symbols: string[]) => {
    setLoadingRecommendations(true)
    const AI_API_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000'
    
    try {
      console.log('=== FETCHING RECOMMENDATIONS ===')
      console.log('Symbols:', symbols)
      
      // Fetch recommendations for each symbol in parallel
      const recommendationPromises = symbols.map(async (symbol) => {
        try {
          const response = await fetch(`${AI_API_URL}/ai/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              symbol,
              user_id: userId,
              include_sentiment: true,
              include_backtest: true
            }),
            signal: AbortSignal.timeout(30000) // 30 second timeout per symbol
          })
          
          if (response.ok) {
            const data = await response.json()
            console.log(`✅ Recommendation for ${symbol}:`, data)
            return { symbol, ...data, success: true }
          } else {
            console.error(`❌ Failed to fetch recommendation for ${symbol}:`, response.status)
            return { symbol, success: false }
          }
        } catch (error) {
          console.error(`❌ Error fetching recommendation for ${symbol}:`, error)
          return { symbol, success: false }
        }
      })
      
      const results = await Promise.all(recommendationPromises)
      const successfulRecommendations = results.filter(r => r.success)
      
      console.log(`✅ Fetched ${successfulRecommendations.length}/${symbols.length} recommendations`)
      setRecommendations(successfulRecommendations)
      
    } catch (error) {
      console.error('❌ Error fetching recommendations:', error)
    } finally {
      setLoadingRecommendations(false)
      console.log('=== RECOMMENDATION FETCHING COMPLETE ===')
    }
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
            <div className="flex items-center gap-4">
              <div className="flex gap-2">
                <motion.button
                  onClick={() => setShowMorningBrief(true)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-3 py-1.5 bg-[#8B7355] text-white rounded-lg text-xs font-medium hover:bg-[#6F5D47] transition-colors"
                >
                  Morning Brief
                </motion.button>
                <motion.button
                  onClick={() => setShowEODBrief(true)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-3 py-1.5 bg-white text-[#2F1810] rounded-lg text-xs font-medium hover:bg-[#F5F5F4] transition-colors border border-[#E5E5E5]"
                >
                  EOD Report
                </motion.button>
              </div>
              <motion.a
                href="/assistant"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-[#FF6B35] via-[#F7931E] to-[#FFD23F] text-white rounded-2xl text-lg font-bold hover:from-[#F7931E] hover:via-[#FF6B35] hover:to-[#FFD23F] transition-all shadow-xl border-2 border-white/20 relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent transform -skew-x-12 -translate-x-full hover:translate-x-full transition-transform duration-1000"></div>
                <span className="relative z-10 flex items-center gap-2">
                  🤠 Ask Kopi
                  <span className="text-sm opacity-80">→</span>
                </span>
              </motion.a>
            </div>
          </div>
        </div>
      </header>

      {/* Quick Access Navigation */}
      <div className="bg-white border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto py-2">
            <a href="/sentiment" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-[#FAFAF9] hover:text-[#2F1810] transition-colors whitespace-nowrap">
              📊 Sentiment
            </a>
            <a href="/backtest" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-[#FAFAF9] hover:text-[#2F1810] transition-colors whitespace-nowrap">
              📈 Backtest
            </a>
            <a href="/alerts" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-[#FAFAF9] hover:text-[#2F1810] transition-colors whitespace-nowrap">
              🔔 Alerts
            </a>
            <a href="/analysis" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-[#FAFAF9] hover:text-[#2F1810] transition-colors whitespace-nowrap">
              📄 Analysis
            </a>
            <a href="/portfolio" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-[#FAFAF9] hover:text-[#2F1810] transition-colors whitespace-nowrap">
              💼 Portfolio
            </a>
          </div>
        </div>
      </div>

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
              {/* Market Sentiment Summary (if available from briefs) */}
              {rawMorningData?.sentiment_summary && (
                <motion.section 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-br from-[#8B7355] to-[#6F5D47] rounded-lg p-6 border border-[#6F5D47] text-white"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                      📊 Market Sentiment
                    </h2>
                    <div className="text-sm opacity-90">
                      {rawMorningData.symbols_analyzed?.length || 0} symbols analyzed
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Average Sentiment</div>
                      <div className="text-3xl font-bold">
                        {(rawMorningData.sentiment_summary.average_sentiment * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs mt-1 opacity-80">
                        {rawMorningData.sentiment_summary.average_sentiment >= 0.55 ? '🟢 Bullish' :
                         rawMorningData.sentiment_summary.average_sentiment <= 0.45 ? '🔴 Bearish' :
                         '🟡 Neutral'}
                      </div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Bullish</div>
                      <div className="text-3xl font-bold text-green-300">
                        {rawMorningData.sentiment_summary.bullish_count || 0}
                      </div>
                      <div className="text-xs mt-1 opacity-80">stocks</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Bearish</div>
                      <div className="text-3xl font-bold text-red-300">
                        {rawMorningData.sentiment_summary.bearish_count || 0}
                      </div>
                      <div className="text-xs mt-1 opacity-80">stocks</div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Trending</div>
                      <div className="text-3xl font-bold text-blue-300">
                        {rawMorningData.sentiment_summary.trending_count || 0}
                      </div>
                      <div className="text-xs mt-1 opacity-80">mentions</div>
                    </div>
                  </div>
                  <div className="mt-4 text-xs opacity-75">
                    Sources: Exa.ai News, Reddit, StockTwits • Updated: {new Date(rawMorningData.generated_at).toLocaleTimeString()}
                  </div>
                </motion.section>
              )}

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
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-[#2F1810]">
                    AI Recommendations
                  </h2>
                  {loadingRecommendations && (
                    <div className="text-sm text-[#6B5D52] flex items-center gap-2">
                      <motion.div
                        className="w-2 h-2 bg-[#8B7355] rounded-full"
                        animate={{ scale: [1, 1.5, 1] }}
                        transition={{ repeat: Infinity, duration: 1 }}
                      />
                      Analyzing...
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {recommendations.length > 0 ? (
                    recommendations.map((rec, idx) => (
                      <motion.div
                        key={rec.symbol}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="p-5 bg-[#FAFAF9] rounded-lg border border-[#E5E5E5] hover:border-[#8B7355] transition-colors"
                      >
                        {/* Header with symbol and action */}
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <div className="text-lg font-bold text-[#2F1810]">{rec.symbol}</div>
                            {rec.sentiment_score !== undefined && (
                              <div className="text-xs mt-1">
                                {rec.sentiment_score >= 0.55 ? (
                                  <span className="text-green-600">🟢 Bullish {(rec.sentiment_score * 100).toFixed(0)}%</span>
                                ) : rec.sentiment_score <= 0.45 ? (
                                  <span className="text-red-600">🔴 Bearish {(rec.sentiment_score * 100).toFixed(0)}%</span>
                                ) : (
                                  <span className="text-yellow-600">🟡 Neutral {(rec.sentiment_score * 100).toFixed(0)}%</span>
                                )}
                              </div>
                            )}
                          </div>
                          <div
                            className={`px-3 py-1 rounded-md text-xs font-semibold ${
                              rec.action === 'BUY' || rec.recommendation === 'BUY'
                                ? 'bg-green-100 text-green-700'
                                : rec.action === 'SELL' || rec.recommendation === 'SELL'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-blue-100 text-blue-700'
                            }`}
                          >
                            {rec.action || rec.recommendation || 'ANALYZE'}
                          </div>
                        </div>

                        {/* Reasoning */}
                        <p className="text-[#4A3F35] text-sm mb-3 line-clamp-2">
                          {rec.reasoning || rec.rationale || 'AI-powered analysis based on sentiment and backtesting'}
                        </p>

                        {/* Backtest metrics if available */}
                        {rec.backtest_metrics && (
                          <div className="mb-3 p-2 bg-white rounded border border-[#E5E5E5]">
                            <div className="text-xs text-[#6B5D52] mb-1">Backtest Results</div>
                            <div className="flex items-center justify-between text-xs">
                              <span>Win Rate: {(rec.backtest_metrics.win_rate * 100).toFixed(0)}%</span>
                              <span>Return: {rec.backtest_metrics.total_return?.toFixed(1)}%</span>
                            </div>
                          </div>
                        )}

                        {/* Price targets */}
                        {(rec.entry_price || rec.target_price) && (
                          <div className="flex items-center justify-between text-sm pt-3 border-t border-[#E5E5E5]">
                            {rec.entry_price && (
                              <div>
                                <div className="text-[#6B5D52] text-xs">Entry</div>
                                <div className="font-semibold text-[#2F1810]">${rec.entry_price.toFixed(2)}</div>
                              </div>
                            )}
                            <div className="text-[#9CA3AF]">→</div>
                            {rec.target_price && (
                              <div>
                                <div className="text-[#6B5D52] text-xs">Target</div>
                                <div className="font-semibold text-[#2F1810]">${rec.target_price.toFixed(2)}</div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Disclaimer */}
                        {rec.disclaimer && (
                          <div className="mt-3 pt-3 border-t border-[#E5E5E5]">
                            <p className="text-xs text-[#9CA3AF] italic">{rec.disclaimer}</p>
                          </div>
                        )}
                      </motion.div>
                    ))
                  ) : !loadingRecommendations ? (
                    <div className="col-span-full text-center py-8 text-[#6B5D52]">
                      <p className="mb-2">No recommendations available yet.</p>
                      <p className="text-sm">Make sure the AI backend is running!</p>
                    </div>
                  ) : null}
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

      {/* Welcome Sequence - Shows while loading */}
      {showWelcomeSequence && !welcomeComplete && (
        <WelcomeSequence
          userName={user?.name || 'Partner'}
          isDataLoaded={!isLoading && rawMorningData !== null}
          onComplete={() => {
            setWelcomeComplete(true)
            setShowWelcomeSequence(false)
          }}
        />
      )}
      

      {/* Brief Overlays - Only show after welcome sequence */}
      {welcomeComplete && (
        <>
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
        </>
      )}
    </div>
  )
}
