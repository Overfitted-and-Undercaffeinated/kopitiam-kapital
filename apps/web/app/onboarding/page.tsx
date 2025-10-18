'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'

const KopiColt = dynamic(() => import('./components/KopiColt2D'), {
  ssr: false,
})

const DesertBackground = dynamic(() => import('./components/DesertBackground'), {
  ssr: false,
})

type OnboardingStep = 1 | 2 | 3 | 4

interface FormData {
  name: string
  email: string
  riskProfile: string
  experienceLevel: string
  tradingCapital: string
  primaryMarkets: string[]
  briefTime: string
  voicePreference: string
  watchlist: string[]
}

export default function OnboardingPage() {
  const [step, setStep] = useState<OnboardingStep>(1)
  const [cursorPosition, setCursorPosition] = useState({ x: 0, y: 0 })
  const [kopiExpression, setKopiExpression] = useState<'neutral' | 'concerned' | 'impressed' | 'happy'>('neutral')
  const [showKopi, setShowKopi] = useState(false)
  const [showStartOverlay, setShowStartOverlay] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    riskProfile: '',
    experienceLevel: '',
    tradingCapital: '',
    primaryMarkets: ['SGX'],
    briefTime: '08:00',
    voicePreference: 'default',
    watchlist: [],
  })

  // Track cursor position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPosition({ x: e.clientX, y: e.clientY })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Update Kopi's expression based on form inputs
  useEffect(() => {
    if (step === 1) {
      if (formData.riskProfile === 'aggressive') {
        setKopiExpression('concerned') // Frown for aggressive
      } else if (formData.riskProfile === 'moderate' || formData.riskProfile === 'conservative') {
        setKopiExpression('happy') // Smile for normal options
      }
    } else if (step === 2) {
      if (formData.experienceLevel === 'expert' || formData.experienceLevel === 'intermediate' || formData.experienceLevel === 'beginner') {
        setKopiExpression('happy') // Smile for all experience levels
      }
      // React to capital amounts
      if (formData.tradingCapital === '100K+') {
        setKopiExpression('impressed') // Impressed by big money
      }
    } else if (step === 3) {
      setKopiExpression('happy') // Happy for market selection
    } else if (step === 4) {
      setKopiExpression('happy') // Happy for final step
    }
  }, [formData, step])

  // Reset to happy when moving to next step
  const handleNext = async () => {
    setKopiExpression('happy') // Reset to smile
    if (step < 4) {
      setStep((step + 1) as OnboardingStep)
    } else {
      // Submit onboarding data
      await handleSubmit()
    }
  }

  const handleBack = () => {
    setKopiExpression('happy') // Reset to smile
    if (step > 1) {
      setStep((step - 1) as OnboardingStep)
    }
  }

  const handleStart = () => {
    setShowStartOverlay(false)
    setShowKopi(true)
  }


  const handleSubmit = async () => {
    setIsSubmitting(true)
    
    try {
      console.log('🚀 Submitting onboarding data:', formData)
      
      const response = await fetch('/api/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        // Show detailed error message from API
        const errorMessage = data.message || data.error || 'Failed to submit onboarding'
        throw new Error(errorMessage)
      }

      console.log('✅ Onboarding successful:', data)
      
      // Show success message
      setKopiExpression('happy')
      
      // Store user ID in localStorage for easy access
      if (data.userId) {
        localStorage.setItem('userId', data.userId)
      }
      
      // Redirect to dashboard after a short delay
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 1000)
      
    } catch (error: any) {
      console.error('❌ Onboarding error:', error)
      setKopiExpression('concerned')
      alert(`❌ ${error.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.name && formData.email && formData.riskProfile
      case 2:
        return formData.experienceLevel && formData.tradingCapital
      case 3:
        return formData.primaryMarkets.length > 0
      case 4:
        return true
      default:
        return false
    }
  }

  const updateFormData = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const toggleMarket = (market: string) => {
    setFormData(prev => ({
      ...prev,
      primaryMarkets: prev.primaryMarkets.includes(market)
        ? prev.primaryMarkets.filter(m => m !== market)
        : [...prev.primaryMarkets, market]
    }))
  }

  const addToWatchlist = (symbol: string) => {
    if (symbol && !formData.watchlist.includes(symbol)) {
      setFormData(prev => ({
        ...prev,
        watchlist: [...prev.watchlist, symbol]
      }))
    }
  }

  const removeFromWatchlist = (symbol: string) => {
    setFormData(prev => ({
      ...prev,
      watchlist: prev.watchlist.filter(s => s !== symbol)
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF8DC] via-[#FFE4B5] to-[#FFDAB9] relative overflow-hidden" style={{ fontFamily: 'var(--font-body)' }}>
      {/* Desert Background */}
      <DesertBackground />
      
      {/* Start Overlay */}
      <AnimatePresence>
        {showStartOverlay && (
          <motion.div
            className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50 cursor-pointer"
            onClick={handleStart}
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
          >
            <motion.div
              className="text-center space-y-6 px-8"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-8xl font-bold text-[#FFF8DC] drop-shadow-[0_4px_12px_rgba(0,0,0,0.5)]" style={{ fontFamily: 'var(--font-heading)' }}>
                Let's get you started
              </h2>
              <p className="text-2xl text-[#FFE4B5] font-bold drop-shadow-[0_2px_8px_rgba(0,0,0,0.5)]">
                click anywhere to continue
              </p>
              <motion.div
                animate={{ y: [0, 15, 0] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="text-5xl text-[#FFF8DC] opacity-80 drop-shadow-[0_2px_8px_rgba(0,0,0,0.5)]"
              >
                ↓
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Kopi Colt - 2D Cowboy */}
      <AnimatePresence>
        {showKopi && (
          <KopiColt
            expression={kopiExpression}
            step={step}
            isIntro={step === 1 && showKopi}
            onIntroComplete={() => setShowForm(true)}
            formData={{
              riskProfile: formData.riskProfile,
              experienceLevel: formData.experienceLevel,
              tradingCapital: formData.tradingCapital,
              primaryMarkets: formData.primaryMarkets
            }}
          />
        )}
      </AnimatePresence>

      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 h-3 bg-[#D2691E]/20 z-50 backdrop-blur-sm">
        <motion.div
          className="h-full bg-gradient-to-r from-[#CD853F] via-[#D2691E] to-[#8B4513] shadow-lg"
          initial={{ width: 0 }}
          animate={{ width: `${(step / 4) * 100}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>

      {/* Main Content */}
      {showForm && (
        <div className="container mx-auto px-4 py-20 max-w-2xl relative z-10">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
                <h1 className="text-6xl font-bold text-[#2F1810] mb-6" style={{ fontFamily: 'var(--font-heading)' }}>
                  Who are you, partner?
                </h1>

                <div className="space-y-8">
                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-3">
                      Your Name
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => updateFormData('name', e.target.value)}
                      className="w-full px-6 py-5 rounded-2xl border-3 border-[#CD853F] bg-white text-[#2F1810] text-xl font-semibold focus:outline-none focus:border-[#D2691E] focus:ring-4 focus:ring-[#CD853F]/30 transition-all shadow-lg"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-3">
                      Email
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => updateFormData('email', e.target.value)}
                      className="w-full px-6 py-5 rounded-2xl border-3 border-[#CD853F] bg-white text-[#2F1810] text-xl font-semibold focus:outline-none focus:border-[#D2691E] focus:ring-4 focus:ring-[#CD853F]/30 transition-all"
                      placeholder="john@example.com"
                    />
                  </div>

                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-4">
                      Risk Profile
                    </label>
                    <div className="grid grid-cols-3 gap-4">
                      {['conservative', 'moderate', 'aggressive'].map((profile) => (
                        <motion.button
                          key={profile}
                          onClick={() => updateFormData('riskProfile', profile)}
                          whileHover={{ scale: 1.05, y: -3 }}
                          whileTap={{ scale: 0.95 }}
                          className={`px-6 py-5 rounded-2xl border-3 font-bold text-lg transition-all capitalize shadow-xl ${
                            formData.riskProfile === profile
                              ? 'bg-gradient-to-br from-[#CD853F] to-[#8B4513] text-white border-[#8B4513]'
                              : 'bg-white text-[#8B4513] border-[#CD853F] hover:border-[#D2691E] hover:shadow-2xl'
                          }`}
                        >
                          {profile}
                        </motion.button>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
                <h1 className="text-6xl font-bold text-[#2F1810] mb-6" style={{ fontFamily: 'var(--font-heading)' }}>
                  Trading Experience
                </h1>

                <div className="space-y-8">
                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-4">
                      Experience Level
                    </label>
                    <div className="grid grid-cols-3 gap-4">
                      {['beginner', 'intermediate', 'expert'].map((level) => (
                        <motion.button
                          key={level}
                          onClick={() => updateFormData('experienceLevel', level)}
                          whileHover={{ scale: 1.05, y: -3 }}
                          whileTap={{ scale: 0.95 }}
                          className={`px-6 py-5 rounded-2xl border-3 font-bold text-lg transition-all capitalize ${
                            formData.experienceLevel === level
                              ? 'bg-gradient-to-br from-[#CD853F] to-[#8B4513] text-white border-[#8B4513]'
                              : 'bg-white text-[#8B4513] border-[#CD853F] hover:border-[#CD853F] hover:shadow-2xl'
                          }`}
                        >
                          {level}
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-4">
                      Trading Capital
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      {['<10K', '10K-50K', '50K-100K', '100K+'].map((capital) => (
                        <motion.button
                          key={capital}
                          onClick={() => updateFormData('tradingCapital', capital)}
                          whileHover={{ scale: 1.05, y: -3 }}
                          whileTap={{ scale: 0.95 }}
                          className={`px-6 py-5 rounded-2xl border-3 font-bold text-lg transition-all ${
                            formData.tradingCapital === capital
                              ? 'bg-gradient-to-br from-[#CD853F] to-[#8B4513] text-white border-[#8B4513]'
                              : 'bg-white text-[#8B4513] border-[#CD853F] hover:border-[#CD853F] hover:shadow-2xl'
                          }`}
                        >
                          ${capital}
                        </motion.button>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
                <h1 className="text-6xl font-bold text-[#2F1810] mb-6" style={{ fontFamily: 'var(--font-heading)' }}>
                  Market Preferences
                </h1>

                <div className="space-y-8">
                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-4">
                      Primary Markets (select all that apply)
                    </label>
                    <div className="grid grid-cols-3 gap-4">
                      {['SGX', 'US', 'HK', 'EU', 'CRYPTO'].map((market) => (
                        <motion.button
                          key={market}
                          onClick={() => toggleMarket(market)}
                          whileHover={{ scale: 1.05, y: -3 }}
                          whileTap={{ scale: 0.95 }}
                          className={`px-6 py-5 rounded-2xl border-3 font-bold text-lg transition-all ${
                            formData.primaryMarkets.includes(market)
                              ? 'bg-gradient-to-br from-[#CD853F] to-[#8B4513] text-white border-[#8B4513]'
                              : 'bg-white text-[#8B4513] border-[#CD853F] hover:border-[#CD853F] hover:shadow-2xl'
                          }`}
                        >
                          {market}
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-3">
                      Morning Brief Time
                    </label>
                    <input
                      type="time"
                      value={formData.briefTime}
                      onChange={(e) => updateFormData('briefTime', e.target.value)}
                      className="w-full px-6 py-5 rounded-2xl border-3 border-[#CD853F] bg-white text-[#2F1810] text-xl font-semibold focus:outline-none focus:border-[#D2691E] focus:ring-4 focus:ring-[#CD853F]/30 transition-all shadow-lg time-picker-western"
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -50 }}
                transition={{ duration: 0.5 }}
                className="space-y-8"
              >
                <h1 className="text-6xl font-bold text-[#2F1810] mb-6" style={{ fontFamily: 'var(--font-heading)' }}>
                  Initial Watchlist
                </h1>

                <div className="space-y-8">
                  <div>
                    <label className="block text-xl font-bold text-[#8B4513] mb-3">
                      Add symbols to track (optional)
                    </label>
                    <div className="flex gap-3">
                      <input
                        type="text"
                        id="watchlist-input"
                        placeholder="e.g., AAPL, DBS, BTC"
                        className="flex-1 px-6 py-5 rounded-2xl border-3 border-[#CD853F] bg-white text-[#2F1810] text-xl font-semibold focus:outline-none focus:border-[#D2691E] focus:ring-4 focus:ring-[#CD853F]/30 transition-all uppercase"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            const input = e.currentTarget
                            addToWatchlist(input.value.trim().toUpperCase())
                            input.value = ''
                          }
                        }}
                      />
                      <motion.button
                        onClick={() => {
                          const input = document.getElementById('watchlist-input') as HTMLInputElement
                          addToWatchlist(input.value.trim().toUpperCase())
                          input.value = ''
                        }}
                        whileHover={{ scale: 1.05, y: -3 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-10 py-5 rounded-2xl bg-gradient-to-br from-[#D2691E] to-[#8B4513] text-white font-bold text-xl transition-all"
                      >
                        Add
                      </motion.button>
                    </div>
                  </div>

                  {formData.watchlist.length > 0 && (
                    <div className="space-y-3">
                      <label className="block text-xl font-bold text-[#8B4513]">
                        Your Watchlist
                      </label>
                      <div className="flex flex-wrap gap-3">
                        {formData.watchlist.map((symbol) => (
                          <motion.div
                            key={symbol}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                            whileHover={{ scale: 1.05 }}
                            className="px-5 py-3 bg-gradient-to-br from-[#CD853F] to-[#8B4513] text-white rounded-2xl font-bold text-lg flex items-center gap-2"
                          >
                            {symbol}
                            <button
                              onClick={() => removeFromWatchlist(symbol)}
                              className="ml-2 text-white hover:text-red-300 transition-colors font-bold text-xl"
                            >
                              ✕
                            </button>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Navigation Buttons */}
          <motion.div
            className="flex justify-between mt-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {step > 1 && (
              <motion.button
                onClick={handleBack}
                disabled={isSubmitting}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 rounded-xl border-2 border-[#CD853F] text-[#8B4513] font-bold text-lg hover:bg-[#CD853F] hover:text-white transition-colors disabled:opacity-50"
              >
                Back
              </motion.button>
            )}
            <motion.button
              onClick={handleNext}
              disabled={!canProceed() || isSubmitting}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className={`px-8 py-4 rounded-xl font-bold text-lg transition-colors ${
                step === 1 ? 'ml-auto' : ''
              } ${
                canProceed() && !isSubmitting
                  ? 'bg-[#8B4513] text-white hover:bg-[#A0522D]'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isSubmitting ? 'Saving...' : step === 4 ? "Let's Ride!" : 'Next'}
            </motion.button>
          </motion.div>
        </div>
      )}
    </div>
  )
}
