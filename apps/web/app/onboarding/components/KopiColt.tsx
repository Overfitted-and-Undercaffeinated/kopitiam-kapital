'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'

// Dynamically import entire component to avoid SSR issues
const CowboyScene = dynamic(
  () => import('./CowboyScene'),
  {
    ssr: false,
    loading: () => <div style={{ width: '100%', height: '100%' }} />
  }
) as React.ComponentType<{ 
  expression: string
  cursorPosition: { x: number; y: number }
  onSceneReady?: () => void
}>

interface KopiColtProps {
  expression: 'neutral' | 'concerned' | 'impressed' | 'happy'
  cursorPosition: { x: number; y: number }
  step: number
  isIntro: boolean
  onIntroComplete?: () => void
}

export default function KopiColt({ expression, cursorPosition, step, isIntro, onIntroComplete }: KopiColtProps) {
  const [voiceText, setVoiceText] = useState('')
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ bottom: -400, right: 80 })
  const [size, setSize] = useState({ width: 600, height: 600 })
  const [isCentered, setIsCentered] = useState(true)
  const [hasPlayedIntro, setHasPlayedIntro] = useState(false)
  const [sceneReady, setSceneReady] = useState(false)
  const [loadingDots, setLoadingDots] = useState('.')
  const [lastExpression, setLastExpression] = useState('')
  const [audioEnabled, setAudioEnabled] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const pendingVoiceRef = useRef<string | null>(null)

  // Enable audio immediately when component mounts (user has already interacted with start screen)
  useEffect(() => {
    console.log('🎤 Enabling audio on component mount')
    setAudioEnabled(true)
  }, [])

  // Animate loading dots
  useEffect(() => {
    if (!sceneReady) {
      const interval = setInterval(() => {
        setLoadingDots(prev => {
          if (prev === '.') return '..'
          if (prev === '..') return '...'
          return '.'
        })
      }, 500)
      
      return () => clearInterval(interval)
    }
  }, [sceneReady])

  useEffect(() => {
    if (isIntro && !hasPlayedIntro && audioEnabled) {
      console.log('🎬 Starting intro sequence, audioEnabled:', audioEnabled)
      
      // Step 1: Appear in center (300ms)
      setTimeout(() => {
        setIsVisible(true)
        // Calculate center position
        const centerX = window.innerWidth / 2 - 300 // 300 = half of 600px width
        const centerY = window.innerHeight / 2 - 300 // 300 = half of 600px height
        setPosition({ bottom: centerY, right: window.innerWidth - centerX - 600 })
      }, 300)
      
    } else if (!isIntro) {
      setIsVisible(true)
      setIsCentered(false)
      setSceneReady(true)
    }
  }, [isIntro, hasPlayedIntro, audioEnabled])
  
  // Wait for scene to be ready before showing greeting
  useEffect(() => {
    if (isIntro && sceneReady && !hasPlayedIntro && audioEnabled) {
      console.log('✅ Scene is ready, showing greeting')
      
      // Show greeting immediately after scene is ready
      setTimeout(() => {
        setVoiceText("Howdy, partner!")
        const introText = "Howdy, partner! Welcome to Kopitiam Capital!"
        console.log('📢 About to play intro voice')
        playVoice(introText)
      }, 500)
      
      // Move to corner and shrink after 3 seconds
      setTimeout(() => {
        setIsCentered(false)
        setSize({ width: 320, height: 320 })
        setPosition({ bottom: 80, right: 80 })
        setVoiceText('') // Clear voice text during transition
      }, 3500)
      
      // Mark intro as complete
      setTimeout(() => {
        setHasPlayedIntro(true)
      }, 4500)
    }
  }, [isIntro, sceneReady, hasPlayedIntro, audioEnabled])

  // Keep position consistent across all steps after intro
  useEffect(() => {
    if (!isIntro && !isCentered) {
      setPosition({ bottom: 80, right: 80 })
      setSize({ width: 320, height: 320 })
    }
  }, [isIntro, isCentered])

  // Voice lines for different steps based on form data changes
  useEffect(() => {
    const expressionKey = `${step}-${expression}`
    
    // Only play if this is a new expression change
    if (expressionKey === lastExpression) return
    
    // Step 1: Risk Profile
    if (step === 1 && expression === 'concerned') {
      setLastExpression(expressionKey)
      setVoiceText("Aggressive, eh? Bold choice!")
      playVoice("Aggressive, eh? That's a bold choice, partner!")
    } else if (step === 1 && expression === 'impressed') {
      setLastExpression(expressionKey)
      setVoiceText("Moderate - Smart move!")
      playVoice("Moderate risk - that's a smart move, partner!")
    }
    // Step 2: Experience and Capital
    else if (step === 2 && expression === 'impressed') {
      setLastExpression(expressionKey)
      setVoiceText("Big capital, big opportunity!")
      playVoice("That's some serious capital you're working with, partner!")
    } else if (step === 2 && expression === 'happy') {
      setLastExpression(expressionKey)
      setVoiceText("Everyone starts somewhere!")
      playVoice("Everyone starts somewhere, partner! I'll help you learn!")
    }
    // Step 4: Final step
    else if (step === 4 && expression === 'happy') {
      setLastExpression(expressionKey)
      setVoiceText("You're all set, partner!")
      playVoice("You're all set, partner! Let's ride!")
    }
  }, [step, expression, lastExpression])

  const enableAudio = () => {
    setAudioEnabled(true)
    // Play pending voice if any
    if (pendingVoiceRef.current) {
      playVoice(pendingVoiceRef.current)
      pendingVoiceRef.current = null
    }
  }

  const playVoice = async (text: string) => {
    console.log('🎵 playVoice called with audioEnabled:', audioEnabled)
    if (!audioEnabled) {
      console.log('⏸️ Audio not enabled yet, waiting for user interaction')
      pendingVoiceRef.current = text
      return
    }
    
    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      
      console.log('🔊 Attempting to generate voice for:', text)
      
      const response = await fetch('/api/voice/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'cowboy' })
      })

      console.log('📡 Voice API response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        // Timeout (408) or other errors - skip voice and continue
        if (response.status === 408) {
          console.warn('⏱️ Voice generation timed out, continuing without audio')
        } else {
          console.warn('❌ Voice generation failed:', errorData)
        }
        return
      }

      const audioBlob = await response.blob()
      console.log('🎵 Audio blob received, size:', audioBlob.size, 'bytes')
      
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      audioRef.current = audio
      
      // Add volume
      audio.volume = 1.0
      
      console.log('▶️ Attempting to play audio...')
      
      try {
        await audio.play()
        console.log('✅ Audio playing successfully!')
      } catch (playError: any) {
        console.error('🚫 Autoplay blocked or play failed:', playError.message)
        console.log('💡 User needs to interact with page first for audio to play')
      }
      
      // Clear voice text after audio finishes
      audio.onended = () => {
        console.log('🏁 Audio finished playing')
        setTimeout(() => {
          setVoiceText('')
          // If this is the intro voice, trigger form to appear
          if (text.includes("Howdy, partner!") && onIntroComplete) {
            onIntroComplete()
          }
        }, 1000)
        audioRef.current = null
      }
    } catch (error: any) {
      console.error('❌ Voice error:', error.message || error)
      // Fallback: just show text without audio
      setTimeout(() => {
        setVoiceText('')
        // If this is the intro voice, trigger form to appear even if audio fails
        if (text.includes("Howdy, partner!") && onIntroComplete) {
          onIntroComplete()
        }
      }, 2000) // Show form after 2 seconds if voice fails
    }
  }

  // Mobile responsive position
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 768
      if (isMobile && !isIntro && !isCentered) {
        setPosition({ bottom: 40, right: 20 })
        setSize({ width: 280, height: 280 })
      } else if (!isMobile && !isIntro && !isCentered) {
        setPosition({ bottom: 80, right: 80 })
        setSize({ width: 320, height: 320 })
      }
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [isIntro, isCentered])

  if (!isVisible) return null

  return (
    <>
      {/* Loading Animation */}
      {isVisible && !sceneReady && (
        <div
          className="fixed z-50 pointer-events-none"
          style={{
            bottom: position.bottom + size.height / 2 - 20,
            left: '50%',
            transform: 'translateX(-50%)',
          }}
        >
          <p className="text-center text-[#8B4513] font-bold text-xl whitespace-nowrap">
            Loading{loadingDots}
          </p>
        </div>
      )}
      
      {/* 3D Canvas */}
      <motion.div
        initial={{ bottom: -400, scale: 0.8, opacity: 0 }}
        animate={{ 
          bottom: position.bottom, 
          right: position.right,
          scale: 1,
          opacity: sceneReady ? 1 : 0
        }}
        transition={{ 
          type: 'spring', 
          damping: 20, 
          stiffness: 100,
          opacity: { duration: 0.3 }
        }}
        className="fixed z-40 pointer-events-none"
        style={{
          width: `${size.width}px`,
          height: `${size.height}px`,
        }}
      >
        <CowboyScene 
          expression={expression} 
          cursorPosition={cursorPosition}
          onSceneReady={() => setSceneReady(true)}
        />
      </motion.div>

      {/* Speech Bubble */}
      {voiceText && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.3 }}
          className="fixed z-50 pointer-events-none"
          style={{
            bottom: position.bottom + (isCentered ? size.height + 20 : 340),
            right: position.right + (isCentered ? size.width / 2 - 100 : 30),
          }}
        >
          <div className="relative bg-white border-4 border-[#8B4513] rounded-2xl px-6 py-4 max-w-xs">
            <p className="text-lg font-bold text-[#2F1810] text-center">
              {voiceText}
            </p>
            {/* Speech bubble tail */}
            <div 
              className="absolute bottom-[-12px] right-12 w-0 h-0"
              style={{
                borderLeft: '12px solid transparent',
                borderRight: '12px solid transparent',
                borderTop: '12px solid #8B4513',
              }}
            />
          </div>
        </motion.div>
      )}
    </>
  )
}
