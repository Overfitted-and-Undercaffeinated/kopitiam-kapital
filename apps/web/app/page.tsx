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
  const [activeSection, setActiveSection] = useState<'hero' | 'blank' | 'intro' | 'morning' | 'dashboard' | 'sentiment' | 'eod' | 'overnight' | 'cta'>('hero')
  
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
          const sectionName = (entry.target as HTMLElement).dataset.section as 'hero' | 'blank' | 'intro' | 'morning' | 'dashboard' | 'sentiment' | 'eod' | 'overnight' | 'cta'
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
    <div ref={containerRef} className="relative bg-[#FFF8DC]" style={{ fontFamily: 'var(--font-body)' }}>
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
            style={{ fontFamily: 'var(--font-heading)', fontWeight: 400 }}
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
                  fontFamily: 'var(--font-heading)',
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
                  style={{ fontFamily: 'var(--font-heading)' }}
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

            {/* Sentiment Analysis view */}
            {activeSection === 'sentiment' && (
              <motion.div
                className="w-[32rem] h-[50rem] bg-white rounded-3xl overflow-hidden shadow-2xl"
                initial={{ rotateY: -90, opacity: 0 }}
                animate={{ rotateY: 0, opacity: 1 }}
                exit={{ rotateY: 90, opacity: 0 }}
                transition={{ duration: 0.6, ease: 'easeOut' }}
              >
                <div className="p-8 h-full overflow-y-auto">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-[#9B59B6] to-[#8E44AD] rounded-full flex items-center justify-center">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-[#2F1810]">Sentiment Analysis</h3>
                    </div>
                    <div className="text-sm font-semibold text-[#8E44AD] bg-[#F4ECF7] px-3 py-1 rounded-full">Live</div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="p-5 bg-gradient-to-r from-[#E8DAEF] to-[#F4ECF7] rounded-xl shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <h4 className="font-bold text-[#2F1810]">Top Trending</h4>
                        </div>
                        <span className="text-xs text-green-600 font-bold bg-green-50 px-2 py-1 rounded">+85%</span>
                      </div>
                      <p className="text-sm text-[#5D3A1A] mb-2">DBS Group Holdings announces strong Q3 results</p>
                      <div className="flex gap-2 text-xs">
                        <span className="bg-[#9B59B6]/20 text-[#8E44AD] px-2 py-1 rounded">Reddit</span>
                        <span className="bg-[#9B59B6]/20 text-[#8E44AD] px-2 py-1 rounded">Twitter</span>
                      </div>
                    </div>
                    
                    <div className="p-5 bg-gradient-to-r from-[#D7BDE2] to-[#E8DAEF] rounded-xl shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                          <h4 className="font-bold text-[#2F1810]">Community Buzz</h4>
                        </div>
                        <span className="text-xs text-blue-600 font-bold bg-blue-50 px-2 py-1 rounded">+72%</span>
                      </div>
                      <p className="text-sm text-[#5D3A1A] mb-2">Singapore tech stocks gaining momentum</p>
                      <div className="flex gap-2 text-xs">
                        <span className="bg-[#9B59B6]/20 text-[#8E44AD] px-2 py-1 rounded">Forums</span>
                      </div>
                    </div>

                    <div className="p-5 bg-gradient-to-r from-[#C39BD3] to-[#D7BDE2] rounded-xl shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                          <h4 className="font-bold text-[#2F1810]">Rising Interest</h4>
                        </div>
                        <span className="text-xs text-purple-600 font-bold bg-purple-50 px-2 py-1 rounded">+68%</span>
                      </div>
                      <p className="text-sm text-[#5D3A1A] mb-2">REITs discussion heating up amid rate changes</p>
                      <div className="flex gap-2 text-xs">
                        <span className="bg-[#9B59B6]/20 text-[#8E44AD] px-2 py-1 rounded">Reddit</span>
                      </div>
                    </div>

                    <div className="p-5 bg-gradient-to-r from-[#AF7AC5] to-[#C39BD3] rounded-xl shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-indigo-500 rounded-full"></div>
                          <h4 className="font-bold text-[#2F1810]">Watch Alert</h4>
                        </div>
                        <span className="text-xs text-indigo-600 font-bold bg-indigo-50 px-2 py-1 rounded">+61%</span>
                      </div>
                      <p className="text-sm text-[#5D3A1A] mb-2">Banking sector outlook improving</p>
                      <div className="flex gap-2 text-xs">
                        <span className="bg-[#9B59B6]/20 text-[#8E44AD] px-2 py-1 rounded">News</span>
                      </div>
                    </div>

                    <div className="p-5 bg-gradient-to-r from-[#9B59B6] to-[#AF7AC5] rounded-xl shadow-md">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                          <h4 className="font-bold text-white">Emerging Topic</h4>
                        </div>
                        <span className="text-xs text-yellow-600 font-bold bg-yellow-50 px-2 py-1 rounded">+54%</span>
                      </div>
                      <p className="text-sm text-white/90 mb-2">Green energy stocks catching attention</p>
                      <div className="flex gap-2 text-xs">
                        <span className="bg-white/20 text-white px-2 py-1 rounded">Social</span>
                      </div>
                    </div>
                  </div>
                </div>
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
                    className="bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <h4 className="text-2xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>24/7 AI Market Watch</h4>
                    </div>
                    <p className="text-white/90 text-base leading-relaxed mb-4">Never sleep on opportunities. Our AI monitors markets round the clock.</p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Real-time price tracking</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Overnight monitoring</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Global market coverage</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#D2691E] to-[#CD853F] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                      </div>
                      <h4 className="text-2xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>Smart Alerts, Zero Noise</h4>
                    </div>
                    <p className="text-white/90 text-base leading-relaxed mb-4">Only the alerts that matter. No spam, just signal.</p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>AI-filtered notifications</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Priority-based delivery</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Custom thresholds</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <h4 className="text-2xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>Your Level, Your View</h4>
                    </div>
                    <p className="text-white/90 text-base leading-relaxed mb-4">Interface adapts to your trading experience. Beginner or pro.</p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Beginner-friendly mode</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Advanced analytics</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Customizable layouts</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.6}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#8B4513] to-[#A0522D] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                      </div>
                      <h4 className="text-2xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>Risk-Smart Recommendations</h4>
                    </div>
                    <p className="text-white/90 text-base leading-relaxed mb-4">Suggestions calibrated to your risk tolerance. Always.</p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Portfolio risk analysis</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Position sizing tools</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Stop-loss suggestions</span>
                      </div>
                    </div>
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
              {/* Left Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.2}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#FFD700] to-[#FFA500] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Start Your Day Right</h3>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Wake up to AI-curated market insights, breaking news, and SGX opportunities.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Delivered at 7:00 AM</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Before market opens</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Voice & text options</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.3}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#D2691E] to-[#CD853F] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Market Overview</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Get the big picture with STI trends, sentiment analysis, and key economic events.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>STI index forecast</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Sector movers</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Global market impact</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Watchlist Alerts</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Personalized updates on your tracked stocks with AI-generated insights.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Overnight price changes</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>News impact analysis</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Action recommendations</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>AI Opportunities</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Daily curated opportunities based on technical signals and market patterns.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Technical breakouts</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Entry/exit points</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Risk/reward ratios</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>
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
              {/* Left Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.2}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#CD853F] to-[#A0522D] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Real-Time Tracking</h3>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Track portfolio performance live with instant updates and dynamic charts.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Live P&L updates</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Interactive charts</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Position breakdowns</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.3}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#D2691E] to-[#F4A460] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Smart Alerts</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Get notified instantly when important events affect your portfolio.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Price target hits</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Breaking news alerts</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Risk threshold warnings</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Adaptive Interface</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Experience a dashboard that adapts to your skill level and preferences.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Customizable widgets</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Multiple view modes</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Dark/light themes</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>AI Recommendations</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Get context-aware suggestions as market conditions change throughout the day.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Profit-taking signals</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Rebalancing suggestions</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Timing optimization</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>
            </div>
          </div>
        </section>

        {/* Slide 5: Pocket Sentiment Analysis */}
        <section 
          data-section="sentiment"
          className="min-h-[120vh] bg-[#9B59B6] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.2}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#E74C3C] to-[#C0392B] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Social Scraping</h3>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      AI-powered web scraping across Reddit, Twitter, forums using Exa for comprehensive coverage.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Reddit communities</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Social media feeds</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Trading forums</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.3}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#3498DB] to-[#2980B9] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>AI Scoring</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Groq-powered sentiment analysis scores every article and discussion in real-time.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Real-time scoring</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Context understanding</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Emotion detection</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#F39C12] to-[#E67E22] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Top 5 Articles</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Get the highest-scored articles and discussions delivered to your dashboard.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Ranked by relevance</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Source attribution</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Click to read full</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#27AE60] to-[#229954] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Trend Detection</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Spot emerging trends before they hit mainstream news channels.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Early signals</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Momentum tracking</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Viral prediction</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>
            </div>
          </div>
        </section>

        {/* Slide 6: EOD Report */}
        <section 
          data-section="eod"
          className="min-h-[120vh] bg-[#B8860B] flex items-center justify-center px-8 py-40 relative"
        >
          <div className="max-w-7xl mx-auto w-full">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-20 items-center">
              {/* Left Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.2}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Daily Debrief</h3>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Review your day's wins and losses with comprehensive performance analysis.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Delivered at 5:00 PM</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Complete P&L breakdown</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Trade by trade review</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.3}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Performance Metrics</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Track key metrics and compare against your historical performance.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Win/loss ratios</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Average returns</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Risk-adjusted returns</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#D2691E] to-[#CD853F] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>AI Insights</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      AI analyzes your performance and identifies patterns to improve trading.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Pattern recognition</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Behavioral analysis</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Improvement suggestions</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-white rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#8B4513] to-[#A0522D] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-[#2F1810]" style={{ fontFamily: 'var(--font-heading)' }}>Tomorrow's Plan</h4>
                    </div>
                    <p className="text-[#2F1810] font-medium leading-relaxed mb-4">
                      Get a customized action plan for the next trading day based on market conditions.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Strategy recommendations</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Key levels to watch</span>
                      </div>
                      <div className="flex items-center gap-2 text-[#5D3A1A] text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Priority setups</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>
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
              {/* Left Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.2}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#2C3E50] to-[#34495E] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#6C7A89] to-[#95A5A6] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                      </div>
                      <h3 className="text-2xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>We Never Sleep</h3>
                    </div>
                    <p className="text-white/90 font-medium leading-relaxed mb-4">
                      While you rest, our AI monitors your positions 24/7 across all global markets.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>24/7 position monitoring</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Asia market tracking</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>After-hours coverage</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.3}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#34495E] to-[#2C3E50] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#E74C3C] to-[#C0392B] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>Critical Alerts</h4>
                    </div>
                    <p className="text-white/90 font-medium leading-relaxed mb-4">
                      Instant notifications for major price movements and breaking news events.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Price threshold alerts</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Breaking news detection</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Smart notification timing</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>

              {/* Center - Empty space for sticky preview */}
              <div></div>

              {/* Right Cards */}
              <div className="space-y-8">
                <AnimatedSection delay={0.4}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#2C3E50] to-[#34495E] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#3498DB] to-[#2980B9] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>Global Coverage</h4>
                    </div>
                    <p className="text-white/90 font-medium leading-relaxed mb-4">
                      Track global market movements that could impact your SGX positions.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>US futures tracking</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>European market watch</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Commodity correlations</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>

                <AnimatedSection delay={0.5}>
                  <motion.div 
                    className="bg-gradient-to-br from-[#34495E] to-[#2C3E50] rounded-2xl p-8 pointer-events-auto h-[280px] flex flex-col shadow-xl"
                    whileHover={{ scale: 1.02, y: -3 }}
                    transition={{ duration: 0.4, ease: 'easeOut' }}
                  >
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-[#27AE60] to-[#229954] rounded-xl flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold text-white" style={{ fontFamily: 'var(--font-heading)' }}>Auto Risk Management</h4>
                    </div>
                    <p className="text-white/90 font-medium leading-relaxed mb-4">
                      AI automatically adjusts risk parameters based on overnight market volatility.
                    </p>
                    <div className="mt-auto space-y-2">
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Gap risk protection</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Volatility monitoring</span>
                      </div>
                      <div className="flex items-center gap-2 text-white/80 text-sm">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        <span>Morning prep report</span>
                      </div>
                    </div>
                  </motion.div>
                </AnimatedSection>
              </div>
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
              <h2 className="text-7xl font-bold text-[#FFF8DC] mb-8 drop-shadow-lg" style={{ fontFamily: 'var(--font-heading)' }}>
                Ready to Trade Smarter?
            </h2>
              <p className="text-3xl text-[#FFE4B5] mb-12 font-semibold">
                Join Kopitiam Capital and start making informed trading decisions
              </p>
              <div className="flex items-center justify-center">
                <motion.a
                  href="/onboarding"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="inline-block bg-[#FFF8DC] text-[#2F1810] px-16 py-8 rounded-2xl text-3xl font-bold transition-all shadow-2xl"
                  style={{ fontFamily: 'var(--font-heading)' }}
                >
                  Get Started →
                </motion.a>
              </div>
        </div>
          </AnimatedSection>
        </section>
      </div>
    </div>
  )
}
