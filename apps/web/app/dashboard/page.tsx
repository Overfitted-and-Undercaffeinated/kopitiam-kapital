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

  // Track cursor position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Fetch briefs on mount - ALWAYS USE DUMMY DATA FOR DEMO
  useEffect(() => {
    // Always load dummy data immediately for demo
    setTimeout(() => {
      setDummyData()
      setIsLoading(false)
    }, 800)
  }, [])

  const setDummyData = () => {
    const today = new Date().toISOString().split('T')[0]
    
    const dummyMorning: Brief = {
      id: '1',
      type: 'morning',
      date: today,
      content: {
        summary: "Well howdy there, partner! Kopi Colt here with your morning round-up. Saddle up 'cause today's lookin' mighty profitable! The markets are ridin' high like a tumbleweed in a dust storm, and I've wrangled up some golden opportunities for ya. Banks are gallopin' ahead, and there's treasure to be found if you know where to dig!",
        market_overview: "Rise and shine, buckaroo! The STI's opened up 0.3% higher at 3,245 points - that's what I call a strong start to the day! Wall Street gave us a mighty fine boost overnight, and our banking cowboys are leading the charge with DBS up 1.2% in pre-market. Hong Kong's takin' it easy today, but Japan's ridin' up 0.5%. It's a mixed bag across the frontier, but opportunity's knockin'!",
        key_points: [
          "Hot diggity! DBS just announced earnings that knocked it clean outta the park - beat expectations by 8%! That's what I call shootin' straight!",
          "Singapore's GDP got revised upward to 3.2% - economy's stronger than a bull at a rodeo, partner!",
          "Tech sector's takin' some heat from them US chip restrictions - might see some good entry points for the brave!",
          "REITs are catchin' wind with stable interest rates - steady as a trusty steed!",
          "Keep your eyes peeled for the Fed Chair speech at 10PM SGT - could shake things up come tomorrow!"
        ],
        recommendations: [
          "DBS Group Holdings (D05) - This stallion's ready to run! Strong buy on that earnings beat. Hop on at $35.20, ridin' to $37.50!",
          "CapitaLand Investment (9CI) - Time to accumulate, partner. REIT strength lookin' solid. Entry: $3.15, Target: $3.45",
          "Venture Corp (V03) - Keep this one in your sights. Oversold bounce comin'. Entry: $15.80, Stop-loss: $15.20 - don't let it buck ya off!"
        ]
      }
    }

    const dummyEOD: Brief = {
      id: '2',
      type: 'eod',
      date: today,
      content: {
        summary: "Well partner, we can hang up our spurs for today - and what a ride it was! Kopi Colt here reportin' from the end of the trail. Your portfolio rode like a champion today, with solid gains across the board. The banks delivered just like I told ya this mornin', and we dodged them tech tumbleweeds real nice!",
        market_overview: "The dust has settled and the STI closed up 0.45% at 3,259 points - not bad for a day's work! Banking stocks were the real heroes, leadin' the stampede. We saw some mighty fine volume at 1.2B shares traded - that's a busy waterin' hole! Hong Kong dipped 0.3% but Japan finished strong at +0.8%. Mixed results across the frontier, but we came out on top!",
        key_points: [
          "Hot damn! Your DBS position galloped up 1.5% today - that's $450 straight into your saddlebag!",
          "Tech stocks got a little dusty as expected, but we held our ground at them support levels - no stampede here!",
          "Banking sector's still got momentum - looks like tomorrow's gonna be another good day for a ride!",
          "Keep your eyes open for some profit-takin' in early trading tomorrow - some cowboys might cash in their chips",
          "Your risk exposure is lookin' mighty conservative - just the way I like it, partner!"
        ],
        portfolio_summary: {
          total_value: "$52,450",
          daily_pnl: "+$685 (+1.3%)",
          positions: 5
        }
      }
    }

    const historical: Brief[] = [
      {
        id: '3',
        type: 'morning',
        date: new Date(Date.now() - 86400000).toISOString().split('T')[0],
        content: {
          summary: "Yesterday's morning brief...",
          market_overview: "Markets opened cautiously...",
          key_points: ["Point 1", "Point 2"],
          recommendations: ["Rec 1"]
        }
      },
      {
        id: '4',
        type: 'eod',
        date: new Date(Date.now() - 86400000).toISOString().split('T')[0],
        content: {
          summary: "Yesterday's EOD report...",
          market_overview: "Markets closed mixed...",
          key_points: ["Point 1", "Point 2"],
          portfolio_summary: {
            total_value: "$51,765",
            daily_pnl: "-$235 (-0.45%)",
            positions: 5
          }
        }
      }
    ]

    setTodayMorningBrief(dummyMorning)
    setTodayEODBrief(dummyEOD)
    setHistoricalBriefs(historical)
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

      {/* Brief Overlays - ALWAYS RENDER FOR DEMO */}
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
        />
      )}
    </div>
  )
}
