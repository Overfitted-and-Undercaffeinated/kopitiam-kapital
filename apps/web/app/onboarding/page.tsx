'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect, useRef } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import Three.js scene to avoid SSR issues
const KopiColt = dynamic(() => import('./components/KopiColt'), {
  ssr: false,
})

type OnboardingStep = 1 | 2 | 3 | 4

interface FormData {
  name: string
  email: string
  riskProfile: 'Conservative' | 'Moderate' | 'Aggressive' | ''
  experienceLevel: 'Beginner' | 'Intermediate' | 'Expert' | ''
  tradingCapital: '<10K' | '10K-50K' | '50K-100K' | '100K+' | ''
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
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    riskProfile: '',
    experienceLevel: '',
    tradingCapital: '',
    primaryMarkets: ['SGX'],
    briefTime: '07:00',
    voicePreference: 'default',
    watchlist: []
  })
  const [watchlistInput, setWatchlistInput] = useState('')

  // Track cursor position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setCursorPosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Show Kopi with intro animation
  useEffect(() => {
    const timer = setTimeout(() => setShowKopi(true), 500)
    return () => clearTimeout(timer)
  }, [])

  const handleFieldChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))

    // Trigger expressions based on field
    if (field === 'riskProfile' && value === 'Aggressive') {
      setKopiExpression('concerned')
      setTimeout(() => setKopiExpression('neutral'), 3000)
    } else if (field === 'tradingCapital' && (value === '50K-100K' || value === '100K+')) {
      setKopiExpression('impressed')
      setTimeout(() => setKopiExpression('neutral'), 3000)
    }
  }

  const handleNext = () => {
    if (step < 4) {
      setKopiExpression('happy')
      setTimeout(() => {
        setStep((step + 1) as OnboardingStep)
        setKopiExpression('neutral')
      }, 500)
    } else {
      // Final step - redirect to dashboard
      setKopiExpression('happy')
      setTimeout(() => {
        window.location.href = '/dashboard'
      }, 2000)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep((step - 1) as OnboardingStep)
    }
  }

  const addToWatchlist = () => {
    if (watchlistInput.trim() && formData.watchlist.length < 5) {
      setFormData(prev => ({
        ...prev,
        watchlist: [...prev.watchlist, watchlistInput.trim().toUpperCase()]
      }))
      setWatchlistInput('')
    }
  }

  const removeFromWatchlist = (symbol: string) => {
    setFormData(prev => ({
      ...prev,
      watchlist: prev.watchlist.filter(s => s !== symbol)
    }))
  }

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.name && formData.email
      case 2:
        return formData.riskProfile && formData.experienceLevel && formData.tradingCapital
      case 3:
        return formData.primaryMarkets.length > 0 && formData.briefTime
      case 4:
        return formData.watchlist.length >= 3
      default:
        return false
    }
  }

  return (
    <div className="min-h-screen bg-[#FFF8DC] relative overflow-hidden" style={{ fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
      {/* Kopi Colt - 3D Cowboy */}
      <AnimatePresence>
        {showKopi && (
          <KopiColt 
            expression={kopiExpression}
            cursorPosition={cursorPosition}
            step={step}
            isIntro={step === 1 && showKopi}
          />
        )}
      </AnimatePresence>

      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 h-2 bg-[#DEB887] z-50">
        <motion.div
          className="h-full bg-[#8B4513]"
          initial={{ width: '0%' }}
          animate={{ width: `${(step / 4) * 100}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-20 max-w-2xl">
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
              <div className="text-center space-y-4 mb-12">
                <h1 className="text-5xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>
                  Welcome, Partner!
                </h1>
                <p className="text-xl text-[#8B4513]">
                  Let's get you set up with your personal AI trading analyst
                </p>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-2">
                    What should we call you?
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleFieldChange('name', e.target.value)}
                    placeholder="Your name"
                    className="w-full px-6 py-4 rounded-xl border-2 border-[#CD853F] bg-white text-[#2F1810] text-lg focus:outline-none focus:border-[#8B4513] transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleFieldChange('email', e.target.value)}
                    placeholder="your@email.com"
                    className="w-full px-6 py-4 rounded-xl border-2 border-[#CD853F] bg-white text-[#2F1810] text-lg focus:outline-none focus:border-[#8B4513] transition-colors"
                  />
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
              <div className="text-center space-y-4 mb-12">
                <h1 className="text-5xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>
                  Know Your Risk
                </h1>
                <p className="text-xl text-[#8B4513]">
                  Help us calibrate recommendations to your comfort zone
                </p>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-4">
                    Risk Profile
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    {(['Conservative', 'Moderate', 'Aggressive'] as const).map((risk) => (
                      <motion.button
                        key={risk}
                        onClick={() => handleFieldChange('riskProfile', risk)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-6 py-4 rounded-xl font-bold text-lg transition-all ${
                          formData.riskProfile === risk
                            ? 'bg-[#8B4513] text-white border-2 border-[#8B4513]'
                            : 'bg-white text-[#8B4513] border-2 border-[#CD853F] hover:border-[#8B4513]'
                        }`}
                      >
                        {risk}
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-4">
                    Experience Level
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    {(['Beginner', 'Intermediate', 'Expert'] as const).map((level) => (
                      <motion.button
                        key={level}
                        onClick={() => handleFieldChange('experienceLevel', level)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-6 py-4 rounded-xl font-bold text-lg transition-all ${
                          formData.experienceLevel === level
                            ? 'bg-[#8B4513] text-white border-2 border-[#8B4513]'
                            : 'bg-white text-[#8B4513] border-2 border-[#CD853F] hover:border-[#8B4513]'
                        }`}
                      >
                        {level}
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-4">
                    Trading Capital Range
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    {(['<10K', '10K-50K', '50K-100K', '100K+'] as const).map((capital) => (
                      <motion.button
                        key={capital}
                        onClick={() => handleFieldChange('tradingCapital', capital)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-6 py-4 rounded-xl font-bold text-lg transition-all ${
                          formData.tradingCapital === capital
                            ? 'bg-[#8B4513] text-white border-2 border-[#8B4513]'
                            : 'bg-white text-[#8B4513] border-2 border-[#CD853F] hover:border-[#8B4513]'
                        }`}
                      >
                        {capital}
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
              <div className="text-center space-y-4 mb-12">
                <h1 className="text-5xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>
                  Your Preferences
                </h1>
                <p className="text-xl text-[#8B4513]">
                  Customize your trading experience
                </p>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-4">
                    Primary Markets
                  </label>
                  <div className="grid grid-cols-3 gap-4">
                    {['SGX', 'US', 'HK'].map((market) => (
                      <motion.button
                        key={market}
                        onClick={() => {
                          const markets = formData.primaryMarkets.includes(market)
                            ? formData.primaryMarkets.filter(m => m !== market)
                            : [...formData.primaryMarkets, market]
                          handleFieldChange('primaryMarkets', markets)
                        }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-6 py-4 rounded-xl font-bold text-lg transition-all ${
                          formData.primaryMarkets.includes(market)
                            ? 'bg-[#8B4513] text-white border-2 border-[#8B4513]'
                            : 'bg-white text-[#8B4513] border-2 border-[#CD853F] hover:border-[#8B4513]'
                        }`}
                      >
                        {market}
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-2">
                    Morning Brief Time
                  </label>
                  <input
                    type="time"
                    value={formData.briefTime}
                    onChange={(e) => handleFieldChange('briefTime', e.target.value)}
                    className="w-full px-6 py-4 rounded-xl border-2 border-[#CD853F] bg-white text-[#2F1810] text-lg focus:outline-none focus:border-[#8B4513] transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-lg font-semibold text-[#2F1810] mb-2">
                    Voice Preference
                  </label>
                  <select
                    value={formData.voicePreference}
                    onChange={(e) => handleFieldChange('voicePreference', e.target.value)}
                    className="w-full px-6 py-4 rounded-xl border-2 border-[#CD853F] bg-white text-[#2F1810] text-lg focus:outline-none focus:border-[#8B4513] transition-colors"
                  >
                    <option value="default">Default (Male)</option>
                    <option value="female">Female</option>
                    <option value="casual">Casual</option>
                    <option value="professional">Professional</option>
                  </select>
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
              <div className="text-center space-y-4 mb-12">
                <h1 className="text-5xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>
                  Build Your Watchlist
                </h1>
                <p className="text-xl text-[#8B4513]">
                  Add 3-5 stocks you want to track (SGX tickers)
                </p>
              </div>

              <div className="space-y-6">
                <div className="flex gap-4">
                  <input
                    type="text"
                    value={watchlistInput}
                    onChange={(e) => setWatchlistInput(e.target.value.toUpperCase())}
                    onKeyPress={(e) => e.key === 'Enter' && addToWatchlist()}
                    placeholder="e.g. DBS, OCBC, UOB"
                    className="flex-1 px-6 py-4 rounded-xl border-2 border-[#CD853F] bg-white text-[#2F1810] text-lg focus:outline-none focus:border-[#8B4513] transition-colors"
                    disabled={formData.watchlist.length >= 5}
                  />
                  <motion.button
                    onClick={addToWatchlist}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    disabled={!watchlistInput.trim() || formData.watchlist.length >= 5}
                    className="px-8 py-4 rounded-xl bg-[#8B4513] text-white font-bold text-lg hover:bg-[#A0522D] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Add
                  </motion.button>
                </div>

                {formData.watchlist.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-sm text-[#8B4513] font-semibold">
                      Your Watchlist ({formData.watchlist.length}/5)
                    </p>
                    <div className="flex flex-wrap gap-3">
                      {formData.watchlist.map((symbol) => (
                        <motion.div
                          key={symbol}
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          exit={{ scale: 0 }}
                          className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-[#CD853F] rounded-lg"
                        >
                          <span className="font-bold text-[#2F1810]">{symbol}</span>
                          <button
                            onClick={() => removeFromWatchlist(symbol)}
                            className="text-[#8B4513] hover:text-[#A0522D] font-bold"
                          >
                            ×
                          </button>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {formData.watchlist.length >= 3 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-[#D2691E]/20 border-2 border-[#D2691E] rounded-xl"
                  >
                    <p className="text-lg text-[#2F1810] font-semibold text-center">
                      Great choices, partner! You're ready to ride.
                    </p>
                  </motion.div>
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
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 rounded-xl border-2 border-[#CD853F] text-[#8B4513] font-bold text-lg hover:bg-[#CD853F] hover:text-white transition-colors"
            >
              Back
            </motion.button>
          )}
          <motion.button
            onClick={handleNext}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={!canProceed()}
            className={`px-8 py-4 rounded-xl font-bold text-lg transition-colors ${
              step === 1 ? 'ml-auto' : ''
            } ${
              canProceed()
                ? 'bg-[#8B4513] text-white hover:bg-[#A0522D]'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {step === 4 ? "Let's Ride!" : 'Next'}
          </motion.button>
        </motion.div>
      </div>
    </div>
  )
}

