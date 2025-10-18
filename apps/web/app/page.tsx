'use client'

import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef, useState, useEffect } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import Three.js scene to avoid SSR issues
const ThreeScene = dynamic(() => import('./components/ThreeScene'), {
  ssr: false,
})

const AppPreview = dynamic(() => import('./components/AppPreview'), {
  ssr: false,
})

// Animated section wrapper
function AnimatedSection({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.6, delay }}
    >
      {children}
    </motion.div>
  )
}

export default function Home() {
  const containerRef = useRef<HTMLDivElement>(null)
  const featuresRef = useRef<HTMLDivElement>(null)
  const [activeSection, setActiveSection] = useState<'hero' | 'blank' | 'intro' | 'morning' | 'dashboard' | 'eod' | 'overnight' | 'cta'>('hero')
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end']
  })

  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.8])

  // Track scroll position to change preview using IntersectionObserver
  useEffect(() => {
    const options = {
      root: null,
      rootMargin: '-50% 0px -50% 0px', // Trigger when section is in the middle of viewport
      threshold: 0
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const sectionName = (entry.target as HTMLElement).dataset.section as 'hero' | 'blank' | 'intro' | 'morning' | 'dashboard' | 'eod' | 'overnight' | 'cta'
          if (sectionName) {
            setActiveSection(sectionName)
          }
        }
      })
    }, options)

    // Observe all sections including hero
    const allSections = containerRef.current?.querySelectorAll('[data-section]')
    allSections?.forEach((section) => observer.observe(section))

    return () => {
      allSections?.forEach((section) => observer.unobserve(section))
    }
  }, [])

  return (
    <div ref={containerRef} className="relative bg-[#FFF8DC]" style={{ fontFamily: 'Inter, system-ui, -apple-system, sans-serif' }}>
      {/* Fixed 3D Background that persists throughout the page */}
      <motion.div 
        className="fixed inset-0 pointer-events-none"
        style={{ 
          opacity: useTransform(scrollYProgress, [0, 0.15, 0.4, 1], [1, 0.4, 0.2, 0.05]),
          zIndex: 0
        }}
      >
        <ThreeScene />
      </motion.div>

      {/* Hero Section */}
      <motion.section
        data-section="hero"
        className="min-h-screen flex flex-col items-center justify-center p-8 relative"
        style={{ 
          scale
        }}
      >

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-5xl w-full text-center space-y-8 relative"
          style={{ zIndex: 10 }}
        >
          <motion.h1 
            className="text-7xl md:text-8xl font-bold text-white drop-shadow-[0_4px_12px_rgba(0,0,0,0.5)]"
            style={{ fontFamily: 'var(--font-bowlby)', fontWeight: 400 }}
          >
            Kopitiam Capital
          </motion.h1>
          
          <p className="text-3xl text-white font-bold drop-shadow-[0_2px_8px_rgba(0,0,0,0.4)]">
            Your AI-powered pocket analyst for SGX trading
          </p>
          
          <p className="text-xl text-white font-semibold drop-shadow-[0_2px_6px_rgba(0,0,0,0.3)]">
            Morning briefs • Real-time insights • End-of-day analysis
          </p>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-10"
          style={{ zIndex: 10 }}
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="text-4xl text-white opacity-70 drop-shadow-lg">↓</div>
        </motion.div>
      </motion.section>

      {/* Features - Multiple Slides with Sticky Central Element */}
      <div ref={featuresRef} className="relative">
        {/* Sticky Central Element - Only shows after scrolling past hero, overlays on CTA */}
        {activeSection !== 'hero' && (
          <motion.div 
            className="fixed inset-0 flex items-center justify-center pointer-events-none z-40"
            style={{ perspective: '1500px' }}
          >
            {/* Blank state with overlay text - HUGE and centered */}
            {activeSection === 'blank' && (
              <motion.h2
                className="font-bold text-[#2F1810] text-center px-8"
                style={{ 
                  fontFamily: 'var(--font-bowlby)',
                  fontSize: 'clamp(3rem, 10vw, 8rem)',
                  lineHeight: 1.1
                }}
                initial={{ rotateY: -90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                exit={{ rotateY: 90, opacity: 0 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              >
                FINANCE DEMOCRATISED
              </motion.h2>
            )}

            {/* Intro state - Container appears, text shrinks into it */}
            {activeSection === 'intro' && (
              <motion.div
                className="w-[32rem] h-[50rem] bg-white rounded-3xl flex items-center justify-center overflow-hidden shadow-2xl"
                initial={{ rotateY: -90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                exit={{ rotateY: 90, opacity: 0 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              >
                <motion.h2
                  className="font-bold text-[#2F1810] text-center px-8"
                  style={{ fontFamily: 'var(--font-bowlby)' }}
                  initial={{ fontSize: 'clamp(3rem, 10vw, 8rem)', lineHeight: 1.1 }}
                  animate={{ fontSize: '2.5rem', lineHeight: 1.2 }}
                  transition={{ duration: 0.8, ease: [0.4, 0, 0.2, 1] }}
                >
                  FINANCE<br />DEMOCRATISED
                </motion.h2>
              </motion.div>
            )}

            {/* App previews for specific sections */}
            {(activeSection === 'morning' || activeSection === 'dashboard' || activeSection === 'eod') && (
              <motion.div
                className="w-[32rem] h-[50rem]"
                key={activeSection}
                initial={{ rotateY: -90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                exit={{ rotateY: 90, opacity: 0 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              >
                <AppPreview activeSection={activeSection} />
              </motion.div>
            )}

            {/* Overnight monitoring view */}
            {activeSection === 'overnight' && (
              <motion.div
                className="w-[32rem] h-[50rem] bg-gradient-to-br from-[#1a1a2e] to-[#16213e] rounded-3xl overflow-hidden shadow-2xl"
                initial={{ rotateY: -90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                exit={{ rotateY: 90, opacity: 0 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              >
                <div className="p-8 h-full relative">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-2xl font-bold text-white">Overnight Watch</h3>
                    <div className="text-sm text-gray-400">24/7</div>
                  </div>
                  
                  {/* Moon and stars animation */}
                  <div className="absolute top-8 right-8">
                    <motion.div
                      className="w-16 h-16 bg-yellow-100 rounded-full shadow-lg"
                      animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    />
                  </div>

                  <div className="space-y-4 mt-8">
                    <div className="p-4 bg-white/10 backdrop-blur-sm rounded-xl">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                        <h4 className="font-bold text-white">Active Monitoring</h4>
                      </div>
                      <p className="text-sm text-gray-300">Tracking 12 positions</p>
                    </div>
                    
                    <div className="p-4 bg-white/10 backdrop-blur-sm rounded-xl">
                      <h4 className="font-bold text-white mb-2">Market Movements</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-300">Asia Markets</span>
                          <span className="text-green-400">+0.8%</span>
                        </div>
                        <div className="flex justify-between items-center text-sm">
                          <span className="text-gray-300">US Futures</span>
                          <span className="text-red-400">-0.3%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-4 bg-white/10 backdrop-blur-sm rounded-xl">
                      <h4 className="font-bold text-white mb-2">Smart Alerts</h4>
                      <p className="text-sm text-gray-300">2 notifications pending for morning</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Slide 1: Blank section - triggers blank sticky element */}
        <section 
          data-section="blank"
          className="min-h-[120vh] bg-[#FFF8DC] flex items-center justify-center px-8 py-40 relative"
        >
        </section>

        {/* Slide 2: Intro section - Finance Democratised shrinks, 4 boxes appear */}
        <section 
          data-section="intro"
          className="min-h-[120vh] bg-[#FFF8DC] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.3}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-2xl p-8  pointer-events-auto min-h-[180px]"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <h4 className="text-xl font-bold mb-3 text-white" style={{ fontFamily: 'var(--font-bowlby)' }}>24/7 AI Market Watch</h4>
                    <p className="text-white/90 text-base">Never sleep on opportunities. Our AI monitors markets round the clock.</p>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#D2691E] to-[#CD853F] rounded-2xl p-8  pointer-events-auto min-h-[180px]"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <h4 className="text-xl font-bold mb-3 text-white" style={{ fontFamily: 'var(--font-bowlby)' }}>Smart Alerts, Zero Noise</h4>
                    <p className="text-white/90 text-base">Only the alerts that matter. No spam, just signal.</p>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-2xl p-8  pointer-events-auto min-h-[180px]"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <h4 className="text-xl font-bold mb-3 text-white" style={{ fontFamily: 'var(--font-bowlby)' }}>Your Level, Your View</h4>
                    <p className="text-white/90 text-base">Interface adapts to your trading experience. Beginner or pro.</p>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.6}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#8B4513] to-[#A0522D] rounded-2xl p-8  pointer-events-auto min-h-[180px]"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <h4 className="text-xl font-bold mb-3 text-white" style={{ fontFamily: 'var(--font-bowlby)' }}>Risk-Smart Recommendations</h4>
                    <p className="text-white/90 text-base">Suggestions calibrated to your risk tolerance. Always.</p>
                  </motion.div>
                </AnimatedSection>
              </div>
            </div>
          </div>
        </section>

        {/* Slide 3: Morning Brief */}
        <section 
          data-section="morning"
          className="min-h-[120vh] bg-[#FFF8DC] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Card */}
              <AnimatedSection delay={0.2}>
                <motion.div 
                  className="bg-white rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h3 className="text-2xl font-bold mb-4 text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>Start Your Day Right</h3>
                  <p className="text-[#2F1810] font-medium leading-relaxed">
                    Wake up to AI-curated market insights, breaking news, and SGX opportunities. Your morning edge, delivered before the opening bell.
                  </p>
                </motion.div>
              </AnimatedSection>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Card */}
              <AnimatedSection delay={0.4}>
                <motion.div 
                  className="bg-white rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h4 className="text-xl font-bold mb-3 text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>What You Get</h4>
                  <ul className="space-y-2 text-[#2F1810] font-medium">
                    <li>• Pre-market analysis</li>
                    <li>• Top SGX news digest</li>
                    <li>• Custom watchlist updates</li>
                    <li>• Risk alerts & opportunities</li>
                  </ul>
                </motion.div>
              </AnimatedSection>
            </div>
          </div>
        </section>

        {/* Slide 4: Live Dashboard */}
        <section 
          data-section="dashboard"
          className="min-h-[120vh] bg-[#D2691E] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Card */}
              <AnimatedSection delay={0.2}>
                <motion.div 
                  className="bg-white rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h3 className="text-2xl font-bold mb-4 text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>Real-Time Intelligence</h3>
                  <p className="text-[#2F1810] font-medium leading-relaxed">
                    Track portfolio performance live with AI-powered alerts, trend analysis, and smart recommendations as the market evolves.
                  </p>
                </motion.div>
              </AnimatedSection>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Card */}
              <AnimatedSection delay={0.4}>
                <motion.div 
                  className="bg-white rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h4 className="text-xl font-bold mb-3 text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>Adaptive Interface</h4>
                  <p className="text-[#2F1810] font-medium leading-relaxed">
                    Experience a dashboard that adapts to your skill level. Clean for beginners, powerful for pros. Risk-calibrated suggestions, always.
                  </p>
                </motion.div>
              </AnimatedSection>
            </div>
          </div>
        </section>

        {/* Slide 5: EOD Report */}
        <section 
          data-section="eod"
          className="min-h-[120vh] bg-[#B8860B] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Card */}
              <AnimatedSection delay={0.2}>
                <motion.div 
                  className="bg-white rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h3 className="text-2xl font-bold mb-4 text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>Daily Debrief</h3>
                  <p className="text-[#2F1810] font-medium leading-relaxed">
                    Review your day's wins and losses. AI analyzes your performance, identifies patterns, and crafts tomorrow's game plan.
                  </p>
                </motion.div>
              </AnimatedSection>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Card */}
              <AnimatedSection delay={0.4}>
                <motion.div 
                  className="bg-white rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h4 className="text-xl font-bold mb-3 text-[#2F1810]" style={{ fontFamily: 'var(--font-bowlby)' }}>Continuous Growth</h4>
                  <p className="text-[#2F1810] font-medium leading-relaxed">
                    Learn what worked, what flopped, and how to level up. Every day is a lesson. Every lesson is profit.
                  </p>
                </motion.div>
              </AnimatedSection>
            </div>
          </div>
        </section>

        {/* Slide 6: Overnight Monitoring */}
        <section 
          data-section="overnight"
          className="min-h-[120vh] bg-[#1a1a2e] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Card */}
              <AnimatedSection delay={0.2}>
                <motion.div 
                  className="bg-gradient-to-br from-[#2C3E50] to-[#34495E] rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h3 className="text-2xl font-bold mb-4 text-white" style={{ fontFamily: 'var(--font-bowlby)' }}>We Never Sleep</h3>
                  <p className="text-white/90 font-medium leading-relaxed">
                    While you rest, our AI monitors your positions 24/7. Asia markets move, we watch. News breaks, we alert.
                  </p>
                </motion.div>
              </AnimatedSection>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Card */}
              <AnimatedSection delay={0.4}>
                <motion.div 
                  className="bg-gradient-to-br from-[#34495E] to-[#2C3E50] rounded-2xl p-8  pointer-events-auto"
                  whileHover={{ scale: 1.02, y: -3 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                >
                  <h4 className="text-xl font-bold mb-3 text-white" style={{ fontFamily: 'var(--font-bowlby)' }}>Wake Up Informed</h4>
                  <p className="text-white/90 font-medium leading-relaxed">
                    Critical price movements? You'll know. Major news? We'll tell you. Risk events? Already handled. Sleep easy.
                  </p>
                </motion.div>
              </AnimatedSection>
            </div>
          </div>
        </section>

        {/* Slide 7: CTA Section - Overlays sticky element */}
        <section 
          data-section="cta"
          className="min-h-screen bg-[#A0522D] flex items-center justify-center px-8 relative overflow-hidden z-50"
        >
          <AnimatedSection>
            <div className="text-center space-y-12 relative z-10">
              <h2 className="text-7xl font-bold text-[#FFF8DC] mb-8 drop-shadow-lg" style={{ fontFamily: 'var(--font-bowlby)' }}>
                Ready to Trade Smarter?
            </h2>
              <p className="text-3xl text-[#FFE4B5] mb-12 font-semibold">
                Join Kopitiam Capital and start making informed trading decisions
              </p>
              <motion.a
                href="/dashboard"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="inline-block bg-[#FFF8DC] text-[#2F1810] px-16 py-8 rounded-2xl text-3xl font-bold transition-all"
                style={{ fontFamily: 'var(--font-bowlby)' }}
              >
                Get Started →
              </motion.a>
        </div>
          </AnimatedSection>
        </section>
      </div>
    </div>
  )
}
