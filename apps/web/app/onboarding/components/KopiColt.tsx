'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import dynamic from 'next/dynamic'

// Dynamically import entire component to avoid SSR issues
const CowboyScene = dynamic(
  () => import('./CowboyScene'),
  {
    ssr: false,
    loading: () => <div style={{ width: '100%', height: '100%' }} />
  }
) as React.ComponentType<{ expression: string; cursorPosition: { x: number; y: number } }>

interface KopiColtProps {
  expression: 'neutral' | 'concerned' | 'impressed' | 'happy'
  cursorPosition: { x: number; y: number }
  step: number
  isIntro: boolean
}

export default function KopiColt({ expression, cursorPosition, step, isIntro }: KopiColtProps) {
  const [voiceText, setVoiceText] = useState('')
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ bottom: -400, right: 80 })

  useEffect(() => {
    if (isIntro) {
      // Intro animation
      setTimeout(() => setIsVisible(true), 500)
      setTimeout(() => {
        setVoiceText("Howdy, partner!")
        playVoice("Howdy, partner! Welcome to Kopitiam Capital!")
      }, 1500)
      setTimeout(() => {
        setPosition({ bottom: 120, right: 80 })
      }, 3000)
    } else {
      setIsVisible(true)
    }
  }, [isIntro])

  // Update position based on step
  useEffect(() => {
    if (step === 1 && !isIntro) {
      setPosition({ bottom: 120, right: 80 })
    } else if (step > 1) {
      // Move to corner after intro
      setPosition({ bottom: 40, right: 40 })
    }
  }, [step, isIntro])

  // Voice lines for different steps
  useEffect(() => {
    if (step === 2 && expression === 'concerned') {
      setVoiceText("Aggressive, eh? Bold choice!")
      playVoice("Aggressive, eh? That's a bold choice, partner!")
    } else if (step === 2 && expression === 'impressed') {
      setVoiceText("Big capital, big opportunity!")
      playVoice("That's some serious capital you're working with, partner!")
    } else if (step === 4 && expression === 'happy') {
      setVoiceText("You're all set, partner!")
      playVoice("You're all set, partner! Let's ride!")
    }
  }, [step, expression])

  const playVoice = async (text: string) => {
    try {
      const response = await fetch('/api/voice/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, voice: 'cowboy' })
      })

      if (!response.ok) {
        console.warn('Voice generation failed, showing text only')
        return
      }

      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      
      await audio.play()
      
      // Clear voice text after audio finishes
      audio.onended = () => {
        setTimeout(() => setVoiceText(''), 1000)
      }
    } catch (error) {
      console.error('Voice error:', error)
      // Fallback: just show text without audio
      setTimeout(() => setVoiceText(''), 4000)
    }
  }

  // Mobile responsive position
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 768
      if (isMobile) {
        if (step === 1) {
          setPosition({ bottom: 60, right: 20 })
        } else {
          setPosition({ bottom: 20, right: 20 })
        }
      }
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [step])

  if (!isVisible) return null

  return (
    <>
      {/* 3D Canvas */}
      <motion.div
        initial={{ bottom: -400 }}
        animate={position}
        transition={{ type: 'spring', damping: 20, stiffness: 100 }}
        className="fixed z-40 pointer-events-none"
        style={{
          width: step === 1 ? '400px' : '250px',
          height: step === 1 ? '400px' : '250px',
        }}
      >
        <CowboyScene expression={expression} cursorPosition={cursorPosition} />
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
            bottom: position.bottom + (step === 1 ? 420 : 270),
            right: position.right + (step === 1 ? 50 : 20),
          }}
        >
          <div className="relative bg-white border-4 border-[#8B4513] rounded-2xl px-6 py-4 shadow-xl max-w-xs">
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
