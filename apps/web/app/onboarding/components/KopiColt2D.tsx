'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

interface KopiColt2DProps {
  expression: 'neutral' | 'concerned' | 'impressed' | 'happy'
  step: number
  isIntro: boolean
  onIntroComplete?: () => void
  customVoiceText?: string
  formData?: {
    riskProfile: string
    experienceLevel: string
    tradingCapital: string
    primaryMarkets: string[]
  }
}

export default function KopiColt2D({ expression, step, isIntro, onIntroComplete, customVoiceText, formData = { riskProfile: '', experienceLevel: '', tradingCapital: '', primaryMarkets: [] } }: KopiColt2DProps) {
  const [voiceText, setVoiceText] = useState('')
  const [isVisible, setIsVisible] = useState(false)
  const [position, setPosition] = useState({ bottom: -400, right: 80 })
  const [size, setSize] = useState({ width: 400, height: 400 })
  const [isCentered, setIsCentered] = useState(true)
  const [hasPlayedIntro, setHasPlayedIntro] = useState(false)
  const [lastExpression, setLastExpression] = useState('')
  const [audioEnabled, setAudioEnabled] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const pendingVoiceRef = useRef<string | null>(null)
  const [isBlinking, setIsBlinking] = useState(false)
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 })
  const containerRef = useRef<HTMLDivElement>(null)
  const [isPlayingAudio, setIsPlayingAudio] = useState(false)
  const [hasPlayedDefaultIntro, setHasPlayedDefaultIntro] = useState(false)

  // Enable audio immediately when component mounts
  useEffect(() => {
    setAudioEnabled(true)
  }, [])

  // Blinking animation
  useEffect(() => {
    // Random blinking
    const blinkInterval = setInterval(() => {
      setIsBlinking(true)
      setTimeout(() => setIsBlinking(false), 150)
    }, 3000 + Math.random() * 2000)

    return () => clearInterval(blinkInterval)
  }, [])

  // Track cursor position for eye movement
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  useEffect(() => {
    if (isIntro && !hasPlayedIntro && audioEnabled) {
      // Step 1: Appear in center (300ms)
      setTimeout(() => {
        setIsVisible(true)
        const centerX = window.innerWidth / 2 - 200 // 200 = half of 400px width
        const centerY = window.innerHeight / 2 - 200
        setPosition({ bottom: centerY, right: window.innerWidth - centerX - 400 })
      }, 300)
      
      // Show greeting (only if no custom voice text is provided and we haven't played default intro yet)
      if (!customVoiceText && !hasPlayedDefaultIntro) {
        console.log('Playing default intro voice')
        setHasPlayedDefaultIntro(true)
        setTimeout(() => {
          setVoiceText("Howdy, partner!")
          const introText = "Howdy, partner! Welcome to Kopitiam Capital!"
          playVoice(introText)
        }, 800)
      } else if (customVoiceText) {
        console.log('Custom voice text provided, skipping default intro:', customVoiceText)
      }
      
      // Move to corner and shrink after 3 seconds (only if not custom voice)
      if (!customVoiceText) {
        setTimeout(() => {
          setIsCentered(false)
          setSize({ width: 280, height: 280 })
          setPosition({ bottom: 80, right: 80 })
          setVoiceText('')
        }, 3500)
        
        // Mark intro as complete
        setTimeout(() => {
          setHasPlayedIntro(true)
        }, 4500)
      } else {
        // If custom voice text, stay centered and don't auto-move
        setTimeout(() => {
          setHasPlayedIntro(true)
        }, 1000)
      }
    } else if (!isIntro) {
      setIsVisible(true)
      setIsCentered(false)
    }
  }, [isIntro, hasPlayedIntro, audioEnabled, customVoiceText])

  // Handle custom voice text changes
  useEffect(() => {
    console.log('Custom voice effect triggered:', { customVoiceText, isVisible, audioEnabled })
    if (customVoiceText && isVisible && audioEnabled) {
      console.log('Playing custom voice:', customVoiceText)
      setVoiceText(customVoiceText)
      playVoice(customVoiceText)
    }
  }, [customVoiceText, isVisible, audioEnabled])

  // Keep position consistent across all steps after intro
  useEffect(() => {
    if (!isIntro && !isCentered) {
      setPosition({ bottom: 80, right: 80 })
      setSize({ width: 280, height: 280 })
    }
  }, [isIntro, isCentered])

  // Voice lines for different steps - with proper tracking
  useEffect(() => {
    const expressionKey = `${step}-${formData.riskProfile}-${formData.experienceLevel}-${formData.tradingCapital}-${formData.primaryMarkets.join(',')}`
    
    if (expressionKey === lastExpression || isPlayingAudio) return
    
    // Step 1: Risk Profile
    if (step === 1 && formData.riskProfile === 'aggressive') {
      setLastExpression(expressionKey)
      setVoiceText("Whoa there, cowboy!")
      playVoice("Whoa there, cowboy! That's a wild ride you're choosin'!")
    } else if (step === 1 && formData.riskProfile === 'moderate') {
      setLastExpression(expressionKey)
      setVoiceText("Steady as she goes!")
      playVoice("Steady as she goes! A balanced trail is a wise trail, partner!")
    } else if (step === 1 && formData.riskProfile === 'conservative') {
      setLastExpression(expressionKey)
      setVoiceText("Playing it safe, eh?")
      playVoice("Playing it safe, eh? Can't fault a cautious cowboy!")
    }
    
    // Step 2: Experience Level
    else if (step === 2 && formData.experienceLevel === 'beginner' && !formData.tradingCapital) {
      setLastExpression(expressionKey)
      setVoiceText("Everyone's gotta start somewhere!")
      playVoice("Everyone's gotta start somewhere, partner! I'll show you the ropes!")
    } else if (step === 2 && formData.experienceLevel === 'intermediate' && !formData.tradingCapital) {
      setLastExpression(expressionKey)
      setVoiceText("You know your way around!")
      playVoice("You know your way around the trading post, I reckon!")
    } else if (step === 2 && formData.experienceLevel === 'expert' && !formData.tradingCapital) {
      setLastExpression(expressionKey)
      setVoiceText("A seasoned trader, I see!")
      playVoice("Well well, a seasoned trader! I like your style, partner!")
    }
    
    // Step 2: Trading Capital
    else if (step === 2 && formData.tradingCapital === '<10K') {
      setLastExpression(expressionKey)
      setVoiceText("Small stakes, big dreams!")
      playVoice("Small stakes, big dreams! Every fortune starts somewhere, partner!")
    } else if (step === 2 && formData.tradingCapital === '10K-50K') {
      setLastExpression(expressionKey)
      setVoiceText("Now we're talking!")
      playVoice("Now we're talking! That's a solid stake you got there, partner!")
    } else if (step === 2 && formData.tradingCapital === '50K-100K') {
      setLastExpression(expressionKey)
      setVoiceText("Big capital, big opportunities!")
      playVoice("Big capital, big opportunities! Let's make that money work for ya!")
    } else if (step === 2 && formData.tradingCapital === '100K+') {
      setLastExpression(expressionKey)
      setVoiceText("Hot dang, that's serious gold!")
      playVoice("Hot dang! That's some serious gold you're packin', partner!")
    }
    
    // Step 3: Markets
    else if (step === 3 && formData.primaryMarkets.length > 0) {
      setLastExpression(expressionKey)
      if (formData.primaryMarkets.includes('CRYPTO')) {
        setVoiceText("Crypto frontier, eh?")
        playVoice("The crypto frontier! That's the wild west of trading, partner!")
      } else if (formData.primaryMarkets.includes('SGX')) {
        setVoiceText("Home turf advantage!")
        playVoice("Home turf advantage! Singapore markets, good choice partner!")
      } else {
        setVoiceText("International markets!")
        playVoice("International markets! A global cowboy, I like it!")
      }
    }
    
    // Step 4: Final
    else if (step === 4) {
      setLastExpression(expressionKey)
      setVoiceText("You're all set, partner!")
      playVoice("You're all set, partner! Let's ride into the sunset!")
    }
  }, [step, expression, lastExpression, formData.riskProfile, formData.experienceLevel, formData.tradingCapital, formData.primaryMarkets, isPlayingAudio])

  const playVoice = async (text: string) => {
    // Don't play if audio is already playing
    if (!audioEnabled || isPlayingAudio) {
      pendingVoiceRef.current = text
      return
    }
    
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
        const errorData = await response.json()
        
        // Handle timeout (408) - skip voice and continue
        if (response.status === 408) {
          console.warn('⏱️ Voice generation timed out, continuing without audio')
          setIsPlayingAudio(false)
          setTimeout(() => {
            setVoiceText('')
            if (text.includes("Howdy, partner!") && onIntroComplete) {
              onIntroComplete()
            }
          }, 2000)
          return
        }
        
        // If quota exceeded, just skip voice playback silently
        if (errorData.error === 'quota_exceeded') {
          console.warn('⚠️ Voice API quota exceeded, skipping voice playback')
          setIsPlayingAudio(false)
          // Simulate voice completion after a short delay
          setTimeout(() => {
            setVoiceText('')
            if (text.includes("Howdy, partner!") && onIntroComplete) {
              onIntroComplete()
            }
          }, 2000) // Keep speech bubble for 2 seconds
          return
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
        setTimeout(() => {
          setVoiceText('')
          if (text.includes("Howdy, partner!") && onIntroComplete) {
            onIntroComplete()
          }
        }, 1000)
        audioRef.current = null
      }
      
      // Fallback in case onended doesn't fire
      audio.onerror = () => {
        setIsPlayingAudio(false)
        audioRef.current = null
      }
    } catch (error) {
      console.error('Voice playback error:', error)
      setIsPlayingAudio(false)
      // Continue without voice
      setTimeout(() => {
        setVoiceText('')
        if (text.includes("Howdy, partner!") && onIntroComplete) {
          onIntroComplete()
        }
      }, 2000)
    }
  }

  // Mobile responsive position
  useEffect(() => {
    const handleResize = () => {
      const isMobile = window.innerWidth < 768
      if (isMobile && !isIntro && !isCentered) {
        setPosition({ bottom: 40, right: 20 })
        setSize({ width: 220, height: 220 })
      } else if (!isMobile && !isIntro && !isCentered) {
        setPosition({ bottom: 80, right: 80 })
        setSize({ width: 280, height: 280 })
      }
    }
    
    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [isIntro, isCentered])

  // Eye expressions based on mood
  const getEyeExpression = () => {
    switch (expression) {
      case 'happy':
        return { eyebrowRotate: -12, mouthCurve: 25 }
      case 'concerned':
        return { eyebrowRotate: 8, mouthCurve: -15 } // Frown, not distressed
      case 'impressed':
        return { eyebrowRotate: -10, mouthCurve: 18 }
      default:
        return { eyebrowRotate: -8, mouthCurve: 15 } // Default smile
    }
  }

  const eyeExpr = getEyeExpression()

  // Calculate pupil offset based on cursor position
  const getPupilOffset = () => {
    if (!containerRef.current) return { x: 0, y: 0 }
    
    const rect = containerRef.current.getBoundingClientRect()
    const eyeCenterX = rect.left + rect.width / 2
    const eyeCenterY = rect.top + rect.height / 2.5 // Eyes are higher up
    
    const deltaX = cursorPosition.x - eyeCenterX
    const deltaY = cursorPosition.y - eyeCenterY
    
    const angle = Math.atan2(deltaY, deltaX)
    const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY) / 200, 1)
    
    const maxOffset = 3
    return {
      x: Math.cos(angle) * distance * maxOffset,
      y: Math.sin(angle) * distance * maxOffset
    }
  }

  const pupilOffset = getPupilOffset()

  if (!isVisible) return null

  return (
    <>
      {/* Character */}
      <motion.div
        ref={containerRef}
        initial={{ bottom: -400, scale: 0.8, opacity: 0 }}
        animate={{ 
          bottom: position.bottom, 
          right: position.right,
          scale: 1,
          opacity: 1,
          y: [0, -8, 0] // Idle breathing/bobbing animation
        }}
        transition={{ 
          type: 'spring', 
          damping: 20, 
          stiffness: 100,
          y: {
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }
        }}
        className="fixed z-40 pointer-events-none"
        style={{
          width: `${size.width}px`,
          height: `${size.height}px`,
        }}
      >
        {/* Kopi Colt - Duolingo x Brawl Stars Style */}
        <svg viewBox="0 0 200 240" className="w-full h-full drop-shadow-2xl">
          <defs>
            {/* Shadow gradient */}
            <linearGradient id="shadowGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#000000" stopOpacity="0.1" />
              <stop offset="100%" stopColor="#000000" stopOpacity="0" />
            </linearGradient>
          </defs>
          
          {/* Body - rounded rectangle like Duolingo */}
          <rect x="55" y="150" width="90" height="65" rx="20" fill="#5C4033" stroke="#3D2B22" strokeWidth="3" />
          
          {/* Left Arm - angular with rounded edges - animated waving */}
          <motion.path 
            d="M 60 160 L 40 175 L 35 190 L 42 192 L 50 180 L 65 170 Z" 
            fill="#FFB38A" 
            stroke="#E8A07C" 
            strokeWidth="2.5"
            animate={{ 
              rotate: [0, -5, 0]
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{ transformOrigin: '60px 160px' }}
          />
          
          {/* Right Arm - animated waving */}
          <motion.path 
            d="M 140 160 L 160 175 L 165 190 L 158 192 L 150 180 L 135 170 Z" 
            fill="#FFB38A" 
            stroke="#E8A07C" 
            strokeWidth="2.5"
            animate={{ 
              rotate: [0, 5, 0]
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: 0.3
            }}
            style={{ transformOrigin: '140px 160px' }}
          />
          
          {/* Vest - layered rectangle */}
          <path 
            d="M 70 155 L 75 175 L 85 205 L 115 205 L 125 175 L 130 155 L 100 160 Z" 
            fill="#8B6F47" 
            stroke="#6B5437" 
            strokeWidth="2.5"
          />
          
          {/* Vest buttons */}
          <circle cx="100" cy="170" r="3" fill="#FFD700" />
          <circle cx="100" cy="185" r="3" fill="#FFD700" />
          
          {/* Bandana - geometric triangle */}
          <path 
            d="M 85 138 L 100 148 L 115 138 L 110 150 L 90 150 Z" 
            fill="#DC143C" 
            stroke="#B01030" 
            strokeWidth="2.5"
          />
          
          {/* Neck */}
          <rect x="85" y="130" width="30" height="18" rx="5" fill="#FFB38A" />
          
          {/* Head - rounded square like Duolingo characters with slight tilt */}
          <motion.rect 
            x="60" 
            y="55" 
            width="80" 
            height="85" 
            rx="25" 
            fill="#FFB38A" 
            stroke="#E8A07C" 
            strokeWidth="3"
            animate={{ 
              rotate: [-2, 2, -2]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{ transformOrigin: '100px 97.5px' }}
          />
          
          {/* Ears - small rounded rectangles */}
          <rect x="50" y="85" width="12" height="20" rx="6" fill="#FFB38A" stroke="#E8A07C" strokeWidth="2" />
          <rect x="138" y="85" width="12" height="20" rx="6" fill="#FFB38A" stroke="#E8A07C" strokeWidth="2" />
          
          {/* Hat */}
          {/* Hat brim - flatter, more stylized */}
          <ellipse cx="100" cy="58" rx="68" ry="10" fill="#8B7355" stroke="#6B5937" strokeWidth="3" />
          {/* Hat crown - rounded trapezoid */}
          <path 
            d="M 65 55 L 62 25 Q 62 15 72 15 L 128 15 Q 138 15 138 25 L 135 55 Z" 
            fill="#A0826D" 
            stroke="#80694D" 
            strokeWidth="3"
          />
          {/* Hat top crease */}
          <path 
            d="M 75 25 Q 100 20 125 25" 
            stroke="#80694D" 
            strokeWidth="2" 
            fill="none"
          />
          {/* Hat band */}
          <rect x="64" y="50" width="72" height="8" rx="2" fill="#654321" stroke="#452F18" strokeWidth="2" />
          
          {/* Hair peeks - angular chunks */}
          <path d="M 62 62 L 55 70 L 60 75 L 68 68 Z" fill="#4A3728" stroke="#3A2718" strokeWidth="2" />
          <path d="M 138 62 L 145 70 L 140 75 L 132 68 Z" fill="#4A3728" stroke="#3A2718" strokeWidth="2" />
          
          {/* Eyes - Duolingo style: semi-circle on top + rectangle below */}
          {!isBlinking ? (
            <>
              {/* Left eye - semi-circle + rectangle shape */}
              <g>
                {/* Eye white - rounded top, flat bottom */}
                <path
                  d="M 68 98 L 68 103 L 88 103 L 88 98 Q 88 90 78 90 Q 68 90 68 98 Z"
                  fill="white"
                  stroke="#2C1810"
                  strokeWidth="2.5"
                />
                {/* Pupil */}
                <ellipse 
                  cx={78 + pupilOffset.x} 
                  cy={98 + pupilOffset.y} 
                  rx="5" 
                  ry="6" 
                  fill="#2C1810"
                />
                {/* Highlight */}
                <ellipse 
                  cx={79 + pupilOffset.x} 
                  cy={96 + pupilOffset.y} 
                  rx="2" 
                  ry="2.5" 
                  fill="white" 
                />
              </g>
              
              {/* Right eye - semi-circle + rectangle shape */}
              <g>
                {/* Eye white - rounded top, flat bottom */}
                <path
                  d="M 112 98 L 112 103 L 132 103 L 132 98 Q 132 90 122 90 Q 112 90 112 98 Z"
                  fill="white"
                  stroke="#2C1810"
                  strokeWidth="2.5"
                />
                {/* Pupil */}
                <ellipse 
                  cx={122 + pupilOffset.x} 
                  cy={98 + pupilOffset.y} 
                  rx="5" 
                  ry="6" 
                  fill="#2C1810"
                />
                {/* Highlight */}
                <ellipse 
                  cx={123 + pupilOffset.x} 
                  cy={96 + pupilOffset.y} 
                  rx="2" 
                  ry="2.5" 
                  fill="white" 
                />
              </g>
            </>
          ) : (
            <>
              {/* Blinking - happy closed eyes */}
              <path d="M 68 98 Q 78 103 88 98" stroke="#2C1810" strokeWidth="3" fill="none" strokeLinecap="round" />
              <path d="M 112 98 Q 122 103 132 98" stroke="#2C1810" strokeWidth="3" fill="none" strokeLinecap="round" />
            </>
          )}
          
          {/* Eyebrows - bold rectangles with animation - COVERS the top of eyes */}
          <motion.rect 
            x="68" 
            y="88" 
            width="22" 
            height="6" 
            rx="3" 
            fill="#654321"
            animate={{ rotate: eyeExpr.eyebrowRotate }}
            style={{ transformOrigin: '79px 91px' }}
          />
          <motion.rect 
            x="110" 
            y="88" 
            width="22" 
            height="6" 
            rx="3" 
            fill="#654321"
            animate={{ rotate: -eyeExpr.eyebrowRotate }}
            style={{ transformOrigin: '121px 91px' }}
          />
          
          {/* Nose - simple triangle */}
          <path d="M 100 108 L 95 118 L 105 118 Z" fill="#E8A07C" />
          
          {/* Mouth - changes with expression - happier default */}
          {expression === 'happy' && (
            <path d="M 80 120 Q 100 135 120 120" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
          )}
          {expression === 'concerned' && (
            // Frown - inverted smile
            <path d="M 80 130 Q 100 120 120 130" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
          )}
          {expression === 'impressed' && (
            <path d="M 83 122 Q 100 132 117 122" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
          )}
          {expression === 'neutral' && (
            <path d="M 85 122 Q 100 130 115 122" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
          )}
        </svg>
      </motion.div>

      {/* Speech Bubble */}
      {console.log('Rendering speech bubble:', voiceText)}
      {voiceText && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.3 }}
          className="fixed z-50 pointer-events-none"
          style={{
            bottom: position.bottom + (isCentered ? size.height + 20 : size.height + 10),
            right: position.right + (isCentered ? size.width / 2 - 100 : 10),
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

