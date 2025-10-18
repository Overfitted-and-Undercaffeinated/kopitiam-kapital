'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface BacktestCharacterSceneProps {
  isGoodResult: boolean // true = riding bull, false = fighting bear
}

export default function BacktestCharacterScene({ isGoodResult }: BacktestCharacterSceneProps) {
  const [isAnimating, setIsAnimating] = useState(true)

  useEffect(() => {
    // Reset animation when mode changes
    setIsAnimating(false)
    const timer = setTimeout(() => setIsAnimating(true), 50)
    return () => clearTimeout(timer)
  }, [isGoodResult])

  return (
    <div className="w-full h-full flex items-center justify-center overflow-hidden relative">
      {isGoodResult ? <BullRideScene isAnimating={isAnimating} /> : <BearFightScene isAnimating={isAnimating} />}
    </div>
  )
}

// Bull Riding Scene - Duolingo style with ORIGINAL Kopikolt
function BullRideScene({ isAnimating }: { isAnimating: boolean }) {
  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {/* Background elements */}
      <div className="absolute inset-0 flex items-end justify-center pb-8">
        {/* Ground */}
        <div className="w-full h-24 bg-gradient-to-b from-[#8B7355] to-[#6B5345] rounded-t-full" />
      </div>

      {/* Confetti */}
      <div className="absolute inset-0">
        {[...Array(12)].map((_, i) => (
          <div
            key={i}
            className="absolute w-3 h-3 rounded-full animate-confetti"
            style={{
              left: `${10 + i * 7}%`,
              top: `${20 + (i % 3) * 10}%`,
              backgroundColor: ['#FFD700', '#FF6B6B', '#4ECDC4', '#95E1D3'][i % 4],
              animationDelay: `${i * 0.15}s`,
              animationDuration: `${2 + (i % 3) * 0.5}s`,
            }}
          />
        ))}
      </div>

      {/* Main scene */}
      <div className={`relative z-10 ${isAnimating ? 'animate-float' : ''}`}>
        {/* Bull */}
        <div className="relative">
          <BullSVG className="w-96 h-80" />
        </div>

        {/* Kopikolt character riding the bull - much higher position */}
        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2">
          <KopikoltSVG 
            className="w-40 h-48" 
            expression="happy"
          />
        </div>
      </div>

      {/* Success text */}
      <div className="absolute bottom-8 text-center animate-pulse-soft">
        <div className="text-4xl font-bold text-green-600 drop-shadow-lg">
          📈 Success!
        </div>
      </div>
    </div>
  )
}

// Bear Fighting Scene - Duolingo style with ORIGINAL Kopikolt
function BearFightScene({ isAnimating }: { isAnimating: boolean }) {
  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {/* Background elements */}
      <div className="absolute inset-0 flex items-end justify-center pb-8">
        {/* Ground */}
        <div className="w-full h-24 bg-gradient-to-b from-[#8B7355] to-[#6B5345] rounded-t-full" />
      </div>

      {/* Lightning effects */}
      <div className="absolute inset-0">
        {[0, 1].map((i) => (
          <div
            key={i}
            className="absolute w-1 h-16 bg-yellow-400 animate-lightning"
            style={{
              left: `${30 + i * 40}%`,
              top: `${10 + i * 20}%`,
              animationDelay: `${i * 0.8}s`,
            }}
          />
        ))}
      </div>

      {/* Main scene */}
      <div className="relative z-10 flex items-center gap-8">
        {/* Kopikolt in fighting stance */}
        <div className={`${isAnimating ? 'animate-battle-stance' : ''}`}>
          <KopikoltSVG 
            className="w-40 h-48" 
            expression="concerned"
          />
        </div>

        {/* VS symbol */}
        <div className="text-6xl font-bold text-red-600 animate-pulse-soft drop-shadow-lg">
          ⚔️
        </div>

        {/* Bear */}
        <div className={`${isAnimating ? 'animate-battle-stance-reverse' : ''}`}>
          <BearSVG className="w-48 h-48" />
        </div>
      </div>

      {/* Challenge text */}
      <div className="absolute bottom-8 text-center animate-pulse-soft">
        <div className="text-4xl font-bold text-red-600 drop-shadow-lg">
          💪 Keep Fighting!
        </div>
      </div>
    </div>
  )
}

// ORIGINAL Kopikolt SVG from KopiColt2D.tsx - Preserved authentic design
function KopikoltSVG({ className, expression }: { className?: string; expression: 'happy' | 'concerned' | 'neutral' | 'impressed' }) {
  const getEyeExpression = () => {
    switch (expression) {
      case 'happy':
        return { eyebrowRotate: -12, mouthCurve: 25 }
      case 'concerned':
        return { eyebrowRotate: 8, mouthCurve: -15 }
      case 'impressed':
        return { eyebrowRotate: -10, mouthCurve: 18 }
      default:
        return { eyebrowRotate: -8, mouthCurve: 15 }
    }
  }

  const eyeExpr = getEyeExpression()

  return (
    <svg className={className} viewBox="0 0 200 240" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Body - rounded rectangle */}
      <rect x="55" y="150" width="90" height="65" rx="20" fill="#5C4033" stroke="#3D2B22" strokeWidth="3" />
      
      {/* Left Arm - animated waving */}
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
      
      {/* Vest */}
      <path 
        d="M 70 155 L 75 175 L 85 205 L 115 205 L 125 175 L 130 155 L 100 160 Z" 
        fill="#8B6F47" 
        stroke="#6B5437" 
        strokeWidth="2.5"
      />
      
      {/* Vest buttons */}
      <circle cx="100" cy="170" r="3" fill="#FFD700" />
      <circle cx="100" cy="185" r="3" fill="#FFD700" />
      
      {/* Bandana */}
      <path 
        d="M 85 138 L 100 148 L 115 138 L 110 150 L 90 150 Z" 
        fill="#DC143C" 
        stroke="#B01030" 
        strokeWidth="2.5"
      />
      
      {/* Neck */}
      <rect x="85" y="130" width="30" height="18" rx="5" fill="#FFB38A" />
      
      {/* Head - with subtle tilt animation */}
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
      
      {/* Ears */}
      <rect x="50" y="85" width="12" height="20" rx="6" fill="#FFB38A" stroke="#E8A07C" strokeWidth="2" />
      <rect x="138" y="85" width="12" height="20" rx="6" fill="#FFB38A" stroke="#E8A07C" strokeWidth="2" />
      
      {/* Hat brim */}
      <ellipse cx="100" cy="58" rx="68" ry="10" fill="#8B7355" stroke="#6B5937" strokeWidth="3" />
      {/* Hat crown */}
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
      
      {/* Hair peeks */}
      <path d="M 62 62 L 55 70 L 60 75 L 68 68 Z" fill="#4A3728" stroke="#3A2718" strokeWidth="2" />
      <path d="M 138 62 L 145 70 L 140 75 L 132 68 Z" fill="#4A3728" stroke="#3A2718" strokeWidth="2" />
      
      {/* Eyes - Duolingo style */}
      <g>
        {/* Left eye */}
        <path
          d="M 68 98 L 68 103 L 88 103 L 88 98 Q 88 90 78 90 Q 68 90 68 98 Z"
          fill="white"
          stroke="#2C1810"
          strokeWidth="2.5"
        />
        <ellipse cx="78" cy="98" rx="5" ry="6" fill="#2C1810" />
        <ellipse cx="79" cy="96" rx="2" ry="2.5" fill="white" />
        
        {/* Right eye */}
        <path
          d="M 112 98 L 112 103 L 132 103 L 132 98 Q 132 90 122 90 Q 112 90 112 98 Z"
          fill="white"
          stroke="#2C1810"
          strokeWidth="2.5"
        />
        <ellipse cx="122" cy="98" rx="5" ry="6" fill="#2C1810" />
        <ellipse cx="123" cy="96" rx="2" ry="2.5" fill="white" />
      </g>
      
      {/* Eyebrows - animated based on expression */}
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
      
      {/* Nose */}
      <path d="M 100 108 L 95 118 L 105 118 Z" fill="#E8A07C" />
      
      {/* Mouth - changes with expression */}
      {expression === 'happy' && (
        <path d="M 80 120 Q 100 135 120 120" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
      )}
      {expression === 'concerned' && (
        <path d="M 80 130 Q 100 120 120 130" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
      )}
      {expression === 'impressed' && (
        <path d="M 83 122 Q 100 132 117 122" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
      )}
      {expression === 'neutral' && (
        <path d="M 85 122 Q 100 130 115 122" stroke="#654321" strokeWidth="4" fill="none" strokeLinecap="round" />
      )}
    </svg>
  )
}

// Bull SVG - More realistic, muscular bull
function BullSVG({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 140 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g className="animate-bounce-subtle">
        {/* Back legs */}
        <g>
          <path d="M 85 80 L 88 95 L 92 95 L 89 80 Z" fill="#654321" stroke="#4A3219" strokeWidth="2" />
          <path d="M 100 80 L 103 95 L 107 95 L 104 80 Z" fill="#654321" stroke="#4A3219" strokeWidth="2" />
          {/* Hooves */}
          <ellipse cx="90" cy="95" rx="4" ry="2" fill="#2F1810" />
          <ellipse cx="105" cy="95" rx="4" ry="2" fill="#2F1810" />
        </g>
        
        {/* Main body - muscular, realistic shape */}
        <ellipse cx="70" cy="58" rx="42" ry="30" fill="#8B6F47" />
        <ellipse cx="70" cy="58" rx="38" ry="26" fill="#A0826D" opacity="0.6" />
        
        {/* Muscular shoulder hump */}
        <path 
          d="M 40 45 Q 50 35 65 40 Q 75 43 78 50 Q 75 55 70 58 Q 60 58 50 55 Q 42 52 40 45 Z" 
          fill="#9B7653" 
          stroke="#7A5C3F" 
          strokeWidth="2"
        />
        
        {/* Chest/shoulder muscles */}
        <ellipse cx="45" cy="50" rx="12" ry="15" fill="#8B6F47" opacity="0.7" />
        
        {/* Belly/underbelly - lighter color */}
        <ellipse cx="75" cy="68" rx="28" ry="18" fill="#C4A57B" opacity="0.5" />
        
        {/* Bull neck - thick and muscular */}
        <path 
          d="M 50 52 Q 48 48 45 45 L 40 48 Q 42 54 48 56 Z" 
          fill="#9B7653" 
          stroke="#7A5C3F" 
          strokeWidth="2"
        />
        
        {/* Bull head - more angular and realistic */}
        <ellipse cx="32" cy="48" rx="15" ry="18" fill="#A0826D" />
        <path d="M 25 55 Q 28 62 35 62 Q 38 58 36 52 Z" fill="#8B6F47" />
        
        {/* Powerful horns - larger, curved upward */}
        <path 
          d="M 22 38 Q 18 28 14 30 Q 12 34 16 38 Q 20 40 22 38 Z" 
          fill="#F5F5DC" 
          stroke="#D4D4A8" 
          strokeWidth="2.5"
        />
        <path 
          d="M 38 38 Q 42 28 46 30 Q 48 34 44 38 Q 40 40 38 38 Z" 
          fill="#F5F5DC" 
          stroke="#D4D4A8" 
          strokeWidth="2.5"
        />
        
        {/* Horn tips - dark */}
        <ellipse cx="14" cy="30" rx="2" ry="3" fill="#4A3219" />
        <ellipse cx="46" cy="30" rx="2" ry="3" fill="#4A3219" />
        
        {/* Ears */}
        <ellipse cx="24" cy="42" rx="5" ry="7" fill="#8B6F47" stroke="#7A5C3F" strokeWidth="1.5" />
        <ellipse cx="40" cy="42" rx="5" ry="7" fill="#8B6F47" stroke="#7A5C3F" strokeWidth="1.5" />
        
        {/* Eyes - determined look */}
        <ellipse cx="26" cy="46" rx="4" ry="5" fill="white" stroke="#2F1810" strokeWidth="1.5" />
        <ellipse cx="38" cy="46" rx="4" ry="5" fill="white" stroke="#2F1810" strokeWidth="1.5" />
        <circle cx="26" cy="47" r="2.5" fill="#2F1810" />
        <circle cx="38" cy="47" r="2.5" fill="#2F1810" />
        <circle cx="27" cy="46" r="1" fill="white" />
        <circle cx="39" cy="46" r="1" fill="white" />
        
        {/* Nostrils - flared */}
        <ellipse cx="28" cy="58" rx="2.5" ry="3" fill="#4A3219" />
        <ellipse cx="36" cy="58" rx="2.5" ry="3" fill="#4A3219" />
        
        {/* Nose ring - gold */}
        <ellipse cx="32" cy="60" rx="5" ry="4" fill="none" stroke="#FFD700" strokeWidth="2.5" />
        <circle cx="32" cy="56" r="2" fill="#FFD700" />
        
        {/* Front legs - muscular */}
        <g>
          <path d="M 48 75 L 50 95 L 55 95 L 53 75 Z" fill="#8B6F47" stroke="#7A5C3F" strokeWidth="2" />
          <path d="M 62 75 L 64 95 L 69 95 L 67 75 Z" fill="#8B6F47" stroke="#7A5C3F" strokeWidth="2" />
          {/* Knee joints */}
          <circle cx="51" cy="85" r="4" fill="#7A5C3F" />
          <circle cx="65" cy="85" r="4" fill="#7A5C3F" />
          {/* Hooves */}
          <ellipse cx="52.5" cy="95" rx="4.5" ry="2.5" fill="#2F1810" />
          <ellipse cx="66.5" cy="95" rx="4.5" ry="2.5" fill="#2F1810" />
        </g>
        
        {/* Tail - dynamic, swishing */}
        <motion.path 
          d="M 108 55 Q 118 50 122 58 Q 124 65 120 68" 
          stroke="#654321" 
          strokeWidth="4" 
          strokeLinecap="round" 
          fill="none"
          animate={{
            d: [
              "M 108 55 Q 118 50 122 58 Q 124 65 120 68",
              "M 108 55 Q 118 48 124 54 Q 126 62 122 66",
              "M 108 55 Q 118 50 122 58 Q 124 65 120 68"
            ]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        {/* Tail tuft */}
        <circle cx="120" cy="68" r="5" fill="#4A3219" />
        <circle cx="122" cy="70" r="4" fill="#4A3219" />
        
        {/* Muscle definition lines */}
        <path d="M 65 45 Q 70 48 72 52" stroke="#7A5C3F" strokeWidth="1.5" fill="none" opacity="0.5" />
        <path d="M 78 52 Q 82 55 85 60" stroke="#7A5C3F" strokeWidth="1.5" fill="none" opacity="0.5" />
        <path d="M 52 62 Q 58 65 62 68" stroke="#7A5C3F" strokeWidth="1.5" fill="none" opacity="0.5" />
      </g>
    </svg>
  )
}

// Bear SVG - Duolingo style
function BearSVG({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g className="animate-bounce-subtle-reverse">
        {/* Bear body */}
        <ellipse cx="50" cy="65" rx="32" ry="28" fill="#8B4513" />
        
        {/* Bear head */}
        <circle cx="50" cy="45" r="24" fill="#A0522D" />
        
        {/* Ears */}
        <circle cx="35" cy="30" r="10" fill="#8B4513" />
        <circle cx="65" cy="30" r="10" fill="#8B4513" />
        <circle cx="35" cy="32" r="6" fill="#D2691E" />
        <circle cx="65" cy="32" r="6" fill="#D2691E" />
        
        {/* Eyes - angry */}
        <circle cx="42" cy="42" r="4" fill="#2F1810" />
        <circle cx="58" cy="42" r="4" fill="#2F1810" />
        <circle cx="43" cy="41" r="1.5" fill="white" />
        <circle cx="59" cy="41" r="1.5" fill="white" />
        
        {/* Angry eyebrows */}
        <path d="M38 38 L46 36" stroke="#2F1810" strokeWidth="2.5" strokeLinecap="round" />
        <path d="M62 38 L54 36" stroke="#2F1810" strokeWidth="2.5" strokeLinecap="round" />
        
        {/* Snout */}
        <ellipse cx="50" cy="52" rx="10" ry="8" fill="#D2691E" />
        <ellipse cx="50" cy="50" rx="4" ry="3" fill="#2F1810" />
        
        {/* Teeth */}
        <path d="M45 57 L47 60" stroke="white" strokeWidth="2" strokeLinecap="round" />
        <path d="M55 57 L53 60" stroke="white" strokeWidth="2" strokeLinecap="round" />
        
        {/* Claws */}
        <g transform="translate(20, 60)">
          <path d="M0 0 L-3 8" stroke="#2F1810" strokeWidth="2" strokeLinecap="round" />
          <path d="M4 0 L1 8" stroke="#2F1810" strokeWidth="2" strokeLinecap="round" />
          <path d="M8 0 L5 8" stroke="#2F1810" strokeWidth="2" strokeLinecap="round" />
        </g>
        
        <g transform="translate(70, 60)">
          <path d="M0 0 L3 8" stroke="#2F1810" strokeWidth="2" strokeLinecap="round" />
          <path d="M4 0 L7 8" stroke="#2F1810" strokeWidth="2" strokeLinecap="round" />
          <path d="M8 0 L11 8" stroke="#2F1810" strokeWidth="2" strokeLinecap="round" />
        </g>
        
        {/* Legs */}
        <ellipse cx="35" cy="85" rx="8" ry="10" fill="#8B4513" />
        <ellipse cx="65" cy="85" rx="8" ry="10" fill="#8B4513" />
      </g>
    </svg>
  )
}
