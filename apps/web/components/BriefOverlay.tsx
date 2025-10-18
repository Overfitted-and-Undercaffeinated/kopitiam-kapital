'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'

const KopiColt2D = dynamic(
  () => import('../app/onboarding/components/KopiColt2D'),
  { ssr: false }
)

interface BriefOverlayProps {
  isOpen: boolean
  onClose: () => void
  type: 'morning' | 'eod'
  brief: {
    date: string
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

export default function BriefOverlay({ isOpen, onClose, type, brief }: BriefOverlayProps) {
  const isMorning = type === 'morning'
  const [currentSection, setCurrentSection] = useState(0)
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Define sections with their content and narration
  const sections = [
    {
      title: 'greeting',
      narration: isMorning 
        ? "Howdy there, partner! Kopi Colt here with your morning round-up. Let's see what the market's cookin' up today!"
        : "Well partner, time to hang up our spurs! Let me walk you through how we did today.",
      content: null
    },
    {
      title: 'Summary',
      narration: brief.summary,
      content: (
        <div className="bg-[#FAFAF9] rounded-lg p-5 border border-[#E5E5E5]">
          <h3 className="text-lg font-semibold mb-3 text-[#2F1810]">Summary</h3>
          <p className="text-[#4A3F35] leading-relaxed">{brief.summary}</p>
        </div>
      )
    },
    {
      title: 'Market Overview',
      narration: brief.market_overview,
      content: (
        <div className="bg-[#FAFAF9] rounded-lg p-5 border border-[#E5E5E5]">
          <h3 className="text-lg font-semibold mb-3 text-[#2F1810]">Market Overview</h3>
          <p className="text-[#4A3F35] leading-relaxed">{brief.market_overview}</p>
        </div>
      )
    },
    {
      title: 'Key Points',
      narration: "Now let me run through the key points you need to know, partner.",
      content: (
        <div className="bg-[#FAFAF9] rounded-lg p-5 border border-[#E5E5E5]">
          <h3 className="text-lg font-semibold mb-3 text-[#2F1810]">Key Points</h3>
          <ul className="space-y-2.5">
            {brief.key_points.map((point, idx) => (
              <motion.li
                key={idx}
                className="flex items-start gap-3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <span className="text-[#8B7355] mt-1">•</span>
                <span className="text-[#4A3F35] flex-1">{point}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      )
    },
  ]

  // Add portfolio summary for EOD
  if (!isMorning && brief.portfolio_summary) {
    sections.splice(2, 0, {
      title: 'Portfolio Summary',
      narration: `Your portfolio's sittin' at ${brief.portfolio_summary.total_value}, with ${brief.portfolio_summary.daily_pnl} for the day. You got ${brief.portfolio_summary.positions} positions holdin' strong!`,
      content: (
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-[#FAFAF9] rounded-lg p-4 border border-[#E5E5E5]">
            <div className="text-sm text-[#6B5D52] mb-1">Portfolio Value</div>
            <div className="text-2xl font-bold text-[#2F1810]">{brief.portfolio_summary.total_value}</div>
          </div>
          <div className="bg-[#FAFAF9] rounded-lg p-4 border border-[#E5E5E5]">
            <div className="text-sm text-[#6B5D52] mb-1">Today's P&L</div>
            <div className="text-2xl font-bold text-green-600">{brief.portfolio_summary.daily_pnl}</div>
          </div>
          <div className="bg-[#FAFAF9] rounded-lg p-4 border border-[#E5E5E5]">
            <div className="text-sm text-[#6B5D52] mb-1">Open Positions</div>
            <div className="text-2xl font-bold text-[#2F1810]">{brief.portfolio_summary.positions}</div>
          </div>
        </div>
      )
    })
  }

  // Add recommendations for morning
  if (isMorning && brief.recommendations && brief.recommendations.length > 0) {
    sections.push({
      title: "Today's Opportunities",
      narration: "And here's the opportunities I've wrangled up for you today, partner!",
      content: (
        <div className="bg-[#FAFAF9] rounded-lg p-5 border border-[#E5E5E5]">
          <h3 className="text-lg font-semibold mb-3 text-[#2F1810]">Today's Opportunities</h3>
          <ul className="space-y-2.5">
            {brief.recommendations.map((rec, idx) => (
              <motion.li
                key={idx}
                className="flex items-start gap-3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
              >
                <span className="text-green-600 mt-1">→</span>
                <span className="text-[#4A3F35] flex-1">{rec}</span>
              </motion.li>
            ))}
          </ul>
        </div>
      )
    })
  }

  // Reset section when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setCurrentSection(0)
    } else {
      // IMMEDIATELY stop audio when closing
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
        URL.revokeObjectURL(audioRef.current.src)
        audioRef.current = null
      }
      setIsPlayingAudio(false)
    }
  }, [isOpen])

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  // Play audio for current section
  useEffect(() => {
    if (isOpen && currentSection < sections.length) {
      playVoice(sections[currentSection].narration)
    }
  }, [currentSection, isOpen])

  const playVoice = async (text: string) => {
    if (isPlayingAudio) return
    
    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      
      setIsPlayingAudio(true)
      
      const response = await fetch('/api/voice/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'cowboy' })
      })

      if (!response.ok) {
        setIsPlayingAudio(false)
        return
      }

      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      audioRef.current = audio
      audio.volume = 1.0
      
      await audio.play()
      
      audio.onended = () => {
        setIsPlayingAudio(false)
        audioRef.current = null
      }
      
      audio.onerror = () => {
        setIsPlayingAudio(false)
        audioRef.current = null
      }
    } catch (error) {
      console.error('Voice playback error:', error)
      setIsPlayingAudio(false)
    }
  }

  const handleContinue = () => {
    // Stop current audio before moving to next section
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setIsPlayingAudio(false)

    if (currentSection < sections.length - 1) {
      setCurrentSection(currentSection + 1)
    } else {
      onClose()
    }
  }

  const handleClose = () => {
    // Stop audio immediately when closing
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      audioRef.current = null
    }
    setIsPlayingAudio(false)
    onClose()
  }

  const getKopiExpression = () => {
    if (currentSection === 0) return 'happy'
    if (currentSection === sections.length - 1) return 'happy'
    if (isMorning && sections[currentSection]?.title === "Today's Opportunities") return 'impressed'
    return 'neutral'
  }

  const isLastSection = currentSection === sections.length - 1

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-[#2F1810]/60 backdrop-blur-sm z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />

          {/* Kopi Colt Character */}
          <KopiColt2D
            expression={getKopiExpression()}
            step={currentSection}
            isIntro={false}
          />

          {/* Content Card */}
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="max-w-2xl w-full max-h-[70vh] overflow-y-auto rounded-lg shadow-2xl bg-white border border-[#E5E5E5] pointer-events-auto"
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            >
              {/* Header */}
              <div className="sticky top-0 bg-white border-b border-[#E5E5E5] p-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-sm font-bold ${
                    isMorning 
                      ? 'bg-[#8B7355] text-white' 
                      : 'bg-[#6F5D47] text-white'
                  }`}>
                    {isMorning ? 'AM' : 'PM'}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-[#2F1810]">
                      {isMorning ? 'Morning Brief from Kopi Colt' : 'EOD Report from Kopi Colt'}
                    </h2>
                    <p className="text-sm text-[#6B5D52] mt-0.5">
                      {new Date(brief.date).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </p>
                  </div>
                </div>
                <motion.button
                  onClick={handleClose}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-10 h-10 rounded-lg bg-[#FAFAF9] hover:bg-[#F5F5F4] flex items-center justify-center text-[#6B5D52] hover:text-[#2F1810] transition-colors border border-[#E5E5E5]"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </motion.button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentSection}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    {currentSection === 0 ? (
                      <div className="text-center py-12">
                        <motion.div
                          initial={{ scale: 0.8, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          transition={{ delay: 0.2 }}
                        >
                          <h3 className="text-4xl font-bold text-[#2F1810] mb-4">
                            {isMorning ? '🌅 Howdy Partner!' : '🌙 End of Trail!'}
                          </h3>
                          <p className="text-xl text-[#6B5D52] mb-2">
                            Kopi Colt here with your {isMorning ? 'morning' : 'evening'} update
                          </p>
                          <div className="flex items-center justify-center gap-2 text-[#8B7355]">
                            {isPlayingAudio && (
                              <motion.div
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ repeat: Infinity, duration: 1 }}
                              >
                                🔊
                              </motion.div>
                            )}
                            <span className="text-sm">
                              {isPlayingAudio ? 'Kopi is speaking...' : 'Ready to continue'}
                            </span>
                          </div>
                        </motion.div>
                      </div>
                    ) : (
                      sections[currentSection].content
                    )}
                  </motion.div>
                </AnimatePresence>

                {/* Progress Indicator */}
                <div className="flex items-center gap-2 justify-center">
                  {sections.map((_, idx) => (
                    <div
                      key={idx}
                      className={`h-2 rounded-full transition-all ${
                        idx === currentSection
                          ? 'w-8 bg-[#8B7355]'
                          : idx < currentSection
                          ? 'w-2 bg-[#8B7355]/50'
                          : 'w-2 bg-[#E5E5E5]'
                      }`}
                    />
                  ))}
                </div>

                {/* Continue Button */}
                <motion.button
                  onClick={handleContinue}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  disabled={isPlayingAudio}
                  className={`w-full py-4 rounded-lg font-semibold text-white transition-all ${
                    isPlayingAudio
                      ? 'bg-[#8B7355]/50 cursor-wait'
                      : 'bg-[#8B7355] hover:bg-[#6F5D47]'
                  }`}
                >
                  {isPlayingAudio ? (
                    <span className="flex items-center justify-center gap-2">
                      <motion.span
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                      >
                        ⏳
                      </motion.span>
                      Kopi's talkin'...
                    </span>
                  ) : isLastSection ? (
                    "Thanks Kopi! Let's ride! 🤠"
                  ) : (
                    `Continue ${currentSection + 1}/${sections.length}`
                  )}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
