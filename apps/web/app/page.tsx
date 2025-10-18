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
  const [activeSection, setActiveSection] = useState<'morning' | 'dashboard' | 'eod'>('morning')
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end']
  })

  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.8])

  // Track scroll position to change preview
  useEffect(() => {
    const handleScroll = () => {
      if (!featuresRef.current) return
      
      const sections = featuresRef.current.querySelectorAll('[data-section]')
      const scrollPos = window.scrollY + window.innerHeight / 2
      
      sections.forEach((section) => {
        const element = section as HTMLElement
        const top = element.offsetTop
        const bottom = top + element.offsetHeight
        
        if (scrollPos >= top && scrollPos <= bottom) {
          const sectionName = element.dataset.section as 'morning' | 'dashboard' | 'eod'
          setActiveSection(sectionName)
        }
      })
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div ref={containerRef} className="relative bg-[#FFF8DC]">
      {/* Hero Section with 3D Scene */}
      <motion.section 
        className="min-h-screen flex flex-col items-center justify-center p-8 bg-gradient-to-br from-[#D2691E] via-[#F4A460] to-[#DEB887] relative overflow-hidden"
        style={{ opacity, scale }}
      >
        {/* Three.js 3D Background */}
        <ThreeScene />

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="z-10 max-w-5xl w-full text-center space-y-8 relative"
        >
          <motion.h1 
            className="text-7xl md:text-8xl font-bold text-[#2F1810] drop-shadow-lg"
            style={{ fontFamily: 'system-ui, -apple-system, sans-serif', fontWeight: 900 }}
          >
            Kopitiam Capital
          </motion.h1>
          
          <p className="text-3xl text-[#5D3A1A] font-bold drop-shadow">
            Your AI-powered pocket analyst for SGX trading
          </p>
          
          <p className="text-xl text-[#8B4513] font-semibold">
            Morning briefs • Real-time insights • End-of-day analysis
          </p>

          <motion.a
            href="/dashboard"
            whileHover={{ scale: 1.05, boxShadow: '0 20px 60px rgba(139, 69, 19, 0.4)' }}
            whileTap={{ scale: 0.95 }}
            className="inline-block group rounded-2xl bg-gradient-to-r from-[#8B4513] to-[#A0522D] hover:from-[#A0522D] hover:to-[#8B4513] px-16 py-8 transition-all shadow-2xl"
          >
            <h2 className="text-4xl font-bold text-[#FFF8DC] mb-2 drop-shadow-lg">
              Start Trading{' '}
              <motion.span 
                className="inline-block"
                animate={{ x: [0, 10, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                →
              </motion.span>
            </h2>
            <p className="text-xl text-[#FFE4B5]">
              Begin your journey to smarter trading
            </p>
          </motion.a>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          className="absolute bottom-10 z-10"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="text-4xl text-[#2F1810] opacity-70">↓</div>
        </motion.div>
      </motion.section>

      {/* Features Grid with Sticky Central Preview */}
      <section ref={featuresRef} className="relative bg-gradient-to-b from-[#FFF8DC] to-[#FFE4B5] py-32 px-8">
        <div className="max-w-7xl mx-auto relative">
          {/* Sticky Central App Preview - Stays visible while scrolling */}
          <div className="sticky top-32 left-0 right-0 mx-auto w-full max-w-4xl h-[700px] pointer-events-none z-0 mb-[-700px]">
            <motion.div
              initial={{ opacity: 0, scale: 0.8, rotateY: -15 }}
              animate={{ opacity: 0.6, scale: 1, rotateY: 0 }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="w-full h-full"
              style={{ perspective: '1000px' }}
            >
              <AppPreview activeSection={activeSection} />
            </motion.div>
          </div>

          <div className="relative z-10">
          <AnimatedSection>
            <h2 className="text-6xl font-bold text-center mb-6 text-[#2F1810]">
              Everything you need to trade
            </h2>
            <p className="text-2xl text-center text-[#8B4513] mb-20 font-semibold">
              Powered by AI, Built for Winners
            </p>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <AnimatedSection delay={0.1}>
              <motion.div 
                data-section="morning"
                className="group p-10 rounded-3xl bg-gradient-to-br from-[#CD853F] to-[#DEB887] hover:shadow-2xl cursor-pointer overflow-hidden relative"
                whileHover={{ y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-[#DEB887] to-[#CD853F] opacity-0 group-hover:opacity-100"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
                <div className="relative z-10">
                  <div className="w-20 h-20 mb-6 bg-[#FFF8DC] rounded-full flex items-center justify-center text-4xl font-bold text-[#D2691E]">
                    AM
                  </div>
                  <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">Morning Brief</h3>
                  <p className="text-lg text-[#5D3A1A] font-medium">
                    Rise and shine with AI-curated market insights, news, and opportunities tailored for SGX traders.
                  </p>
                </div>
              </motion.div>
            </AnimatedSection>

            <AnimatedSection delay={0.2}>
              <motion.div 
                data-section="dashboard"
                className="group p-10 rounded-3xl bg-gradient-to-br from-[#D2691E] to-[#F4A460] hover:shadow-2xl cursor-pointer overflow-hidden relative"
                whileHover={{ y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-[#F4A460] to-[#D2691E] opacity-0 group-hover:opacity-100"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
                <div className="relative z-10">
                  <div className="w-20 h-20 mb-6 bg-[#FFF8DC] rounded-full flex items-center justify-center">
                    <svg className="w-12 h-12 text-[#D2691E]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">Live Dashboard</h3>
                  <p className="text-lg text-[#5D3A1A] font-medium">
                    Track your portfolio in real-time with AI-powered insights and recommendations as the market moves.
                  </p>
                </div>
              </motion.div>
            </AnimatedSection>

            <AnimatedSection delay={0.3}>
              <motion.div 
                data-section="eod"
                className="group p-10 rounded-3xl bg-gradient-to-br from-[#B8860B] to-[#DAA520] hover:shadow-2xl cursor-pointer overflow-hidden relative"
                whileHover={{ y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-[#DAA520] to-[#B8860B] opacity-0 group-hover:opacity-100"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
                <div className="relative z-10">
                  <div className="w-20 h-20 mb-6 bg-[#FFF8DC] rounded-full flex items-center justify-center text-4xl font-bold text-[#B8860B]">
                    PM
                  </div>
                  <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">EOD Report</h3>
                  <p className="text-lg text-[#5D3A1A] font-medium">
                    Review your day's performance and get AI-generated plans for tomorrow's trading opportunities.
                  </p>
                </div>
              </motion.div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* Spacer to allow more scrolling with preview visible */}
      <section className="min-h-screen bg-gradient-to-b from-[#FFE4B5] to-[#FFF8DC] py-32 px-8 relative">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-5xl font-bold text-[#2F1810] mb-6">
              See your data come alive
            </h2>
            <p className="text-2xl text-[#8B4513] font-semibold mb-12">
              Real-time insights that adapt to your trading style
            </p>
            <motion.div
              className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto"
            >
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-8 bg-gradient-to-br from-white to-[#FFE4B5] rounded-2xl shadow-lg"
              >
                <div className="w-16 h-16 mb-4 bg-gradient-to-br from-[#D2691E] to-[#F4A460] rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-[#2F1810] mb-2">Instant Updates</h3>
                <p className="text-[#5D3A1A]">Real-time market data and alerts</p>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-8 bg-gradient-to-br from-white to-[#FFE4B5] rounded-2xl shadow-lg"
              >
                <div className="w-16 h-16 mb-4 bg-gradient-to-br from-[#8B4513] to-[#A0522D] rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-[#2F1810] mb-2">Personalized</h3>
                <p className="text-[#5D3A1A]">AI learns your preferences</p>
              </motion.div>
              <motion.div
                whileHover={{ scale: 1.05 }}
                className="p-8 bg-gradient-to-br from-white to-[#FFE4B5] rounded-2xl shadow-lg"
              >
                <div className="w-16 h-16 mb-4 bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-[#2F1810] mb-2">Anywhere</h3>
                <p className="text-[#5D3A1A]">Access on any device</p>
              </motion.div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* AI Features */}
      <section className="min-h-screen bg-gradient-to-br from-[#D2691E] to-[#8B4513] py-32 px-8 relative overflow-hidden">
        {/* Desert pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-full h-full" style={{
            backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(0,0,0,.1) 35px, rgba(0,0,0,.1) 70px)'
          }} />
        </div>

        <div className="max-w-7xl mx-auto relative z-10">
          <AnimatedSection>
            <h2 className="text-6xl font-bold text-center mb-12 text-[#FFF8DC]">
              AI-Powered Trading Intelligence
            </h2>
            <p className="text-2xl text-center text-[#FFE4B5] mb-20 font-semibold">
              Built with cutting-edge AI to give you an edge in the markets
            </p>
          </AnimatedSection>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-16">
            <AnimatedSection delay={0.1}>
              <motion.div
                className="bg-gradient-to-br from-[#FFF8DC] to-[#FFE4B5] p-12 rounded-3xl shadow-2xl"
                whileHover={{ scale: 1.05, rotate: 2 }}
              >
                <div className="w-16 h-16 mb-6 bg-[#D2691E] rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">Smart Analysis</h3>
                <p className="text-lg text-[#5D3A1A] font-medium">
                  Our AI analyzes market trends, news sentiment, and technical indicators to deliver actionable insights.
                </p>
              </motion.div>
            </AnimatedSection>

            <AnimatedSection delay={0.2}>
              <motion.div
                className="bg-gradient-to-br from-[#FFE4B5] to-[#F5DEB3] p-12 rounded-3xl shadow-2xl"
                whileHover={{ scale: 1.05, rotate: -2 }}
              >
                <div className="w-16 h-16 mb-6 bg-[#8B4513] rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">Trade Ideas</h3>
                <p className="text-lg text-[#5D3A1A] font-medium">
                  Get personalized trading opportunities based on your portfolio, risk tolerance, and market conditions.
                </p>
              </motion.div>
            </AnimatedSection>

            <AnimatedSection delay={0.3}>
              <motion.div
                className="bg-gradient-to-br from-[#F5DEB3] to-[#DEB887] p-12 rounded-3xl shadow-2xl"
                whileHover={{ scale: 1.05, rotate: 2 }}
              >
                <div className="w-16 h-16 mb-6 bg-[#A0522D] rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">Real-time Alerts</h3>
                <p className="text-lg text-[#5D3A1A] font-medium">
                  Never miss an opportunity with instant notifications for price movements and market events.
                </p>
              </motion.div>
            </AnimatedSection>

            <AnimatedSection delay={0.4}>
              <motion.div
                className="bg-gradient-to-br from-[#DEB887] to-[#D2B48C] p-12 rounded-3xl shadow-2xl"
                whileHover={{ scale: 1.05, rotate: -2 }}
              >
                <div className="w-16 h-16 mb-6 bg-[#CD853F] rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-3xl font-bold mb-4 text-[#2F1810]">Risk Management</h3>
                <p className="text-lg text-[#5D3A1A] font-medium">
                  AI-powered risk analysis helps you size positions correctly and protect your portfolio effectively.
                </p>
              </motion.div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="min-h-screen bg-gradient-to-br from-[#8B4513] via-[#A0522D] to-[#CD853F] flex items-center justify-center px-8 relative overflow-hidden">
        <AnimatedSection>
          <div className="text-center space-y-12 relative z-10">
            <h2 className="text-7xl font-bold text-[#FFF8DC] mb-8 drop-shadow-lg">
              Ready to trade smarter?
            </h2>
            <p className="text-3xl text-[#FFE4B5] mb-12 font-semibold">
              Join Kopitiam Capital and start making informed trading decisions
            </p>
            <motion.a
              href="/dashboard"
              whileHover={{ scale: 1.1, boxShadow: '0 30px 80px rgba(255, 248, 220, 0.5)' }}
              whileTap={{ scale: 0.9 }}
              className="inline-block bg-gradient-to-r from-[#FFF8DC] to-[#FFE4B5] text-[#2F1810] px-16 py-8 rounded-2xl text-3xl font-bold hover:shadow-2xl transition-all"
            >
              Get Started Now →
            </motion.a>
          </div>
        </AnimatedSection>
      </section>
    </div>
  )
}
