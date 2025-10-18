'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'

const KopiColt2D = dynamic(
  () => import('../app/onboarding/components/KopiColt2D'),
  { 
    ssr: false,
    loading: () => <div className="w-80 h-80 flex items-center justify-center text-[#8B4513]">Loading...</div>
  }
)

interface WelcomeSequenceProps {
  userName: string | null
  isDataLoaded: boolean
  onComplete: () => void
  onSkip?: () => void
  show?: boolean
}

type SequenceStage = 'welcome' | 'but-first' | 'kopi-appears' | 'kopi-speaks' | 'continue-button' | 'waiting' | 'animating-out'

export default function WelcomeSequence({ userName, isDataLoaded, onComplete, onSkip, show = true }: WelcomeSequenceProps) {
  const [stage, setStage] = useState<SequenceStage>('welcome')
  const [showKopi, setShowKopi] = useState(false)
  const [kopiExpression, setKopiExpression] = useState<'neutral' | 'happy' | 'impressed'>('happy')
  const [showContinueButton, setShowContinueButton] = useState(false)
  const [isWaitingForData, setIsWaitingForData] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)

  // Stage 1: Welcome Back message
  useEffect(() => {
    if (stage === 'welcome') {
      const timer = setTimeout(() => {
        setStage('but-first')
      }, 4000) // Show for 4 seconds
      return () => clearTimeout(timer)
    }
  }, [stage])

  // Stage 2: But First message
  useEffect(() => {
    if (stage === 'but-first') {
      const timer = setTimeout(() => {
        setStage('kopi-appears')
      }, 4000) // Show for 4 seconds
      return () => clearTimeout(timer)
    }
  }, [stage])

  // Stage 3: Kopi appears
  useEffect(() => {
    if (stage === 'kopi-appears') {
      setShowKopi(true)
      setKopiExpression('happy')
      // Wait a bit for animation, then speak
      const timer = setTimeout(() => {
        setStage('kopi-speaks')
      }, 1000) // Let Kopi pop in first
      return () => clearTimeout(timer)
    }
  }, [stage])

  // Stage 4: Kopi speaks with voiceover
  useEffect(() => {
    if (stage === 'kopi-speaks') {
      // The KopiColt2D component will handle its own voice when isIntro={true}
      // Show continue button after a delay
      const timer = setTimeout(() => {
        setStage('continue-button')
        setShowContinueButton(true)
      }, 5000) // Show continue after 5 seconds
      return () => clearTimeout(timer)
    }
  }, [stage])

  const playVoice = async (text: string) => {
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
        // Timeout (408) or other errors - skip voice and continue
        if (response.status === 408) {
          console.warn('Voice generation timed out, continuing without audio')
        } else {
          console.warn('Voice generation failed, continuing without audio')
        }
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
    // Stop audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setIsPlayingAudio(false)

    if (isDataLoaded) {
      // Data is ready, animate Kopi out and complete
      setStage('animating-out')
      setTimeout(() => {
        onComplete()
      }, 1200) // Wait for animation
    } else {
      // Data not ready, show waiting message
      setStage('waiting')
      setIsWaitingForData(true)
      setShowContinueButton(false)
      // The KopiColt2D component will handle its own voice
    }
  }

  const handleSkip = () => {
    // Stop audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setIsPlayingAudio(false)
    
    // Call onSkip callback if provided
    if (onSkip) {
      onSkip()
    }
    
    // Skip directly to completion without waiting for data
    setStage('animating-out')
    setTimeout(() => {
      onComplete()
    }, 1200)
  }

  // Poll for data when waiting
  useEffect(() => {
    if (isWaitingForData && isDataLoaded) {
      // Data just became ready!
      setStage('animating-out')
      setTimeout(() => {
        onComplete()
      }, 1200)
    }
  }, [isDataLoaded, isWaitingForData, onComplete])

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  if (!show) {
    return null
  }

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[100] bg-white">
        {/* Stage 1: Welcome Back */}
        <AnimatePresence>
          {stage === 'welcome' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <h1 
                className="bbh-sans-bogle-bold text-[#8B4513] px-8 text-center"
                style={{ 
                  fontSize: 'clamp(2.5rem, 8vw, 6rem)',
                  lineHeight: 1.2,
                  textTransform: 'uppercase'
                }}
              >
                Welcome Back, {userName || 'Partner'}
              </h1>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stage 2: But First */}
        <AnimatePresence>
          {stage === 'but-first' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <h1 
                className="bbh-sans-bogle-bold text-[#8B4513] px-8 text-center"
                style={{ 
                  fontSize: 'clamp(2.5rem, 8vw, 6rem)',
                  lineHeight: 1.2,
                  textTransform: 'uppercase'
                }}
              >
                But First, Here's your morning report
              </h1>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stage 3+: Kopi Colt */}
        <AnimatePresence>
          {(stage === 'kopi-appears' || stage === 'kopi-speaks' || stage === 'continue-button' || stage === 'waiting') && (
            <div className="absolute inset-0">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.6 }}
              >
                <KopiColt2D
                  key={`kopi-${stage}`}
                  expression={kopiExpression}
                  step={0}
                  isIntro={true}
                  customVoiceText={stage === 'kopi-speaks' ? "Howdy partner, the market's cookin' today! Here's your morning 5 mins" : stage === 'waiting' ? "Hold on while we get your mornin' report ready, partner" : undefined}
                  onIntroComplete={() => {
                    // Don't let the component move to corner automatically
                  }}
                />
              </motion.div>


              {/* Continue and Skip buttons */}
              {showContinueButton && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute bottom-20 left-1/2 transform -translate-x-1/2"
                >
                  <div className="flex gap-4 items-center">
                    <motion.button
                      onClick={handleContinue}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="px-12 py-4 rounded-xl text-xl font-bold text-white bg-[#8B4513] hover:bg-[#6F4E37] transition-all shadow-lg"
                    >
                      Continue →
                    </motion.button>
                    <motion.button
                      onClick={handleSkip}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="px-8 py-4 rounded-xl text-lg font-medium text-[#8B4513] bg-white hover:bg-gray-50 transition-all shadow-lg border-2 border-[#8B4513]"
                    >
                      Skip
                    </motion.button>
                  </div>
                </motion.div>
              )}

              {/* Waiting indicator */}
              {isWaitingForData && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute bottom-20 left-1/2 transform -translate-x-1/2"
                >
                  <div className="flex items-center gap-3 text-[#8B4513]">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
                      className="text-4xl"
                    >
                      ⏳
                    </motion.div>
                    <p className="text-xl font-semibold">Loading your brief...</p>
                  </div>
                </motion.div>
              )}
            </div>
          )}
        </AnimatePresence>
      </div>
    </AnimatePresence>
  )
}

