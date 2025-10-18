'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'
import BacktestChart from '@/components/BacktestChart'

const KopiColt2D = dynamic(() => import('../onboarding/components/KopiColt2D'), {
  ssr: false,
})

const BacktestCharacterScene = dynamic(() => import('../backtest/components/BacktestCharacterScene'), {
  ssr: false,
})

  const ThreeScene = dynamic(() => import('../components/ThreeScene'), {
  ssr: false,
})

interface Message {
  id: string
  role: 'user' | 'assistant'
  shortResponse?: string // What Kopi says aloud
  detailedResponse?: string // Detailed text not read aloud
  userMessage?: string
  metadata?: any // Chart data and other metadata
  timestamp: Date
}

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [userName, setUserName] = useState('Partner')
  
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const recognitionRef = useRef<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Get user name from localStorage
  useEffect(() => {
    const storedName = localStorage.getItem('userName')
    if (storedName) {
      setUserName(storedName)
    }
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputText(transcript)
        setIsListening(false)
      }

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }

      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true)
      recognitionRef.current.start()
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }

  const fetchRealAIResponse = async (userQuestion: string): Promise<{ short: string; detailed: string; metadata?: any }> => {
    const AI_API_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000'
    const userId = localStorage.getItem('userId') || 'demo_user'
    
    try {
      console.log('🤖 Calling AI Chat Assistant:', { message: userQuestion, userId })
      
      // Use URLSearchParams for form data
      const params = new URLSearchParams({
        message: userQuestion,
        user_id: userId,
      })
      
      const response = await fetch(`${AI_API_URL}/assistant/chat?${params}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(60000) // 60 second timeout for backtests
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('✅ AI Response received:', data)
      
      // Extract response from new chat orchestrator format
      const short = data.short_response || data.shortResponse || 'No response'
      const detailed = data.detailed_response || data.detailedResponse || 'No detailed response'
      const metadata = data.metadata || {}
      
      return { short, detailed, metadata }
      
    } catch (error) {
      console.error('❌ AI API Error:', error)
      
      // Fallback to a friendly error message
      return {
        short: `Whoa there, ${userName}! My AI brain's takin' a coffee break. Let me give ya what I remember...`,
        detailed: `I'm havin' trouble connectin' to the main AI engine right now, partner. This might be because:\n\n• The backend server isn't runnin' (try: cd apps/ai && uvicorn main:app --reload)\n• Network connection issues\n• API timeout (backtests can take 30-60 seconds)\n\nIn the meantime, here's what I can do:\n\n• Backtest trading strategies on historical data\n• Analyze sentiment from multiple sources (news, social media)\n• Generate trading recommendations\n• Explain trading concepts\n• Research market trends\n\nTry askin' me again in a moment, or check that the AI backend is runnin'!`,
        metadata: {}
      }
    }
  }

  const handleSendMessage = async () => {
    if (!inputText.trim() || isProcessing) return

    const userQuestion = inputText.trim()
    setInputText('')
    setIsProcessing(true)

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      userMessage: userQuestion,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMsg])

    // Fetch real AI response from backend
    const response = await fetchRealAIResponse(userQuestion)

    // Add assistant message
    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      shortResponse: response.short,
      detailedResponse: response.detailed,
      metadata: response.metadata,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, assistantMsg])

    // Speak the short response
    await speakResponse(response.short)
    setIsProcessing(false)
  }

  const speakResponse = async (text: string) => {
    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }

      setIsSpeaking(true)

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
        setIsSpeaking(false)
        return
      }

      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      const audio = new Audio(audioUrl)
      audioRef.current = audio

      audio.onended = () => {
        setIsSpeaking(false)
        audioRef.current = null
        URL.revokeObjectURL(audioUrl)
      }

      audio.onerror = () => {
        setIsSpeaking(false)
        audioRef.current = null
      }

      await audio.play()
    } catch (error) {
      console.error('Voice playback error:', error)
      setIsSpeaking(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF8DC] via-[#FFE4B5] to-[#FFDAB9] relative overflow-hidden">
      {/* Custom CSS to override KopiColt2D positioning for assistant page */}
      <style jsx>{`
        .assistant-kopi-override :global(.fixed) {
          position: absolute !important;
          bottom: auto !important;
          right: auto !important;
          left: 50% !important;
          top: 50% !important;
          transform: translate(-50%, -50%) !important;
        }
        
        /* Cowboy theme animations */
        @keyframes tumbleweed {
          0% { transform: translateX(-100px) rotate(0deg); }
          100% { transform: translateX(calc(100vw + 100px)) rotate(360deg); }
        }
        
        @keyframes dustParticle {
          0% { opacity: 0; transform: translateY(0px) scale(0.5); }
          50% { opacity: 1; transform: translateY(-20px) scale(1); }
          100% { opacity: 0; transform: translateY(-40px) scale(0.5); }
        }
        
        @keyframes spurJingle {
          0%, 100% { transform: rotate(0deg); }
          25% { transform: rotate(5deg); }
          75% { transform: rotate(-5deg); }
        }
        
        .tumbleweed {
          animation: tumbleweed 20s linear infinite;
        }
        
        .dust-particle {
          animation: dustParticle 3s ease-out infinite;
        }
        
        .spur-jingle {
          animation: spurJingle 0.5s ease-in-out;
        }
      `}</style>
      
      {/* 3D Background Scene */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <ThreeScene />
      </div>
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-sm border-b-2 border-[#8B4513] shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <motion.div
                whileHover={{ rotate: 10 }}
                className="text-3xl"
              >
                🤠
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold text-[#2F1810] flex items-center gap-2">
                  Ask Kopi Colt
                  <motion.span
                    animate={{ rotate: [0, 10, -10, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-lg"
                  >
                    ⭐
                  </motion.span>
                </h1>
                <p className="text-sm text-[#6B5D52] mt-0.5 flex items-center gap-1">
                  <span>Your AI trading companion</span>
                  <motion.span
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    🚀
                  </motion.span>
                </p>
              </div>
            </div>
            <motion.a
              href="/dashboard"
              whileHover={{ scale: 1.05, rotate: 2 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 bg-gradient-to-r from-[#8B4513] to-[#A0522D] text-white rounded-xl text-sm font-bold hover:from-[#A0522D] hover:to-[#8B4513] transition-all shadow-lg border-2 border-white/20 spur-jingle"
            >
              <span className="flex items-center gap-2">
                🏠 Back to Dashboard
              </span>
            </motion.a>
          </div>
        </div>
      </header>

      {/* Quick Access Navigation */}
      <div className="bg-white/90 backdrop-blur-sm border-b-2 border-[#8B4513] shadow-md">
        <div className="container mx-auto px-6">
          <div className="flex gap-2 overflow-x-auto py-3">
            {[
              { href: '/sentiment', icon: '📊', label: 'Sentiment', color: 'from-blue-500 to-blue-600' },
              { href: '/backtest', icon: '📈', label: 'Backtest', color: 'from-green-500 to-green-600' },
              { href: '/alerts', icon: '🔔', label: 'Alerts', color: 'from-orange-500 to-orange-600' },
              { href: '/analysis', icon: '📄', label: 'Analysis', color: 'from-purple-500 to-purple-600' },
              { href: '/portfolio', icon: '💼', label: 'Portfolio', color: 'from-amber-500 to-amber-600' }
            ].map((item, index) => (
              <motion.a
                key={item.href}
                href={item.href}
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.95 }}
                className={`px-4 py-2 rounded-xl text-sm font-bold text-white bg-gradient-to-r ${item.color} hover:shadow-lg transition-all whitespace-nowrap border-2 border-white/20`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <span className="flex items-center gap-2">
                  <motion.span
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.5 }}
                  >
                    {item.icon}
                  </motion.span>
                  {item.label}
                </span>
              </motion.a>
            ))}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-180px)]">
          {/* Kopi Colt Character - Left Side */}
          <div className="lg:col-span-1 flex items-center justify-center relative assistant-kopi-override">
            <div className="relative w-full h-full">
              <div className="absolute inset-0 flex items-center justify-center">
                <KopiColt2D 
                  expression={isProcessing ? 'neutral' : isSpeaking ? 'happy' : 'neutral'}
                  step={0}
                  isIntro={false}
                />
              </div>
              
              {/* Status indicator */}
              <motion.div
                className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 bg-white rounded-full shadow-lg border border-[#E5E5E5]"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="flex items-center gap-2">
                  {isSpeaking && (
                    <>
                      <motion.div
                        className="w-2 h-2 bg-green-500 rounded-full"
                        animate={{ scale: [1, 1.5, 1] }}
                        transition={{ repeat: Infinity, duration: 1 }}
                      />
                      <span className="text-sm font-medium text-[#2F1810]">Speaking...</span>
                    </>
                  )}
                  {isProcessing && !isSpeaking && (
                    <>
                      <motion.div
                        className="w-2 h-2 bg-blue-500 rounded-full"
                        animate={{ scale: [1, 1.5, 1] }}
                        transition={{ repeat: Infinity, duration: 1 }}
                      />
                      <span className="text-sm font-medium text-[#2F1810]">Thinking...</span>
                    </>
                  )}
                  {!isSpeaking && !isProcessing && (
                    <>
                      <div className="w-2 h-2 bg-gray-400 rounded-full" />
                      <span className="text-sm font-medium text-[#6B5D52]">Ready</span>
                    </>
                  )}
                </div>
              </motion.div>
            </div>
          </div>

          {/* Chat Interface - Right Side */}
          <div className="lg:col-span-2 flex flex-col bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl border-2 border-[#8B4513]/20 overflow-hidden relative">
            {/* Decorative Elements */}
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-[#8B4513] via-[#A0522D] to-[#8B4513]" />
            <div className="absolute top-2 left-4 w-3 h-3 bg-[#8B4513] rounded-full" />
            <div className="absolute top-2 left-8 w-2 h-2 bg-[#A0522D] rounded-full" />
            <div className="absolute top-2 left-12 w-2 h-2 bg-[#8B4513] rounded-full" />
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="relative"
                  >
                    {/* Cowboy Hat Decoration */}
                    <motion.div
                      className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-4xl"
                      animate={{ rotate: [0, 5, -5, 0] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      🤠
                    </motion.div>
                    
                    <h3 className="text-4xl font-bold text-[#2F1810] mb-4" style={{ fontFamily: 'var(--font-heading)' }}>
                      Howdy, {userName}!
                    </h3>
                    <p className="text-xl text-[#6B5D52] mb-8">
                      Ask me anything about the markets, your portfolio, or trading ideas!
                    </p>
                    
                    {/* Decorative Border */}
                    <div className="flex items-center justify-center mb-6">
                      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#8B4513] to-transparent" />
                      <motion.span
                        className="mx-4 text-2xl"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        ⭐
                      </motion.span>
                      <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[#8B4513] to-transparent" />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                      {[
                        { text: 'Should I buy DBS?', icon: '📈', color: 'from-green-500 to-green-600' },
                        { text: 'How\'s my portfolio doing?', icon: '💼', color: 'from-blue-500 to-blue-600' },
                        { text: 'What\'s the market outlook?', icon: '📊', color: 'from-purple-500 to-purple-600' },
                        { text: 'Tell me about Apple stock', icon: '🍎', color: 'from-red-500 to-red-600' }
                      ].map((suggestion, index) => (
                        <motion.button
                          key={suggestion.text}
                          onClick={() => setInputText(suggestion.text)}
                          whileHover={{ scale: 1.05, y: -3, rotate: 1 }}
                          whileTap={{ scale: 0.95 }}
                          className={`px-6 py-4 bg-gradient-to-r ${suggestion.color} text-white rounded-xl text-sm font-bold shadow-lg hover:shadow-xl transition-all border-2 border-white/20`}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.5 + index * 0.1 }}
                        >
                          <span className="flex items-center gap-2">
                            <motion.span
                              whileHover={{ rotate: 360 }}
                              transition={{ duration: 0.5 }}
                            >
                              {suggestion.icon}
                            </motion.span>
                            {suggestion.text}
                          </span>
                        </motion.button>
                      ))}
                    </div>
                  </motion.div>
                </div>
              )}

              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'user' ? (
                    <div className="max-w-[80%] bg-[#8B7355] text-white rounded-2xl px-5 py-3">
                      <p className="text-sm font-medium">{message.userMessage}</p>
                    </div>
                  ) : (
                    <div className="max-w-[90%] space-y-3">
                      {/* Short spoken response */}
                      <div className="bg-gradient-to-br from-[#CD853F] to-[#DEB887] text-white rounded-2xl px-5 py-4 shadow-md">
                        <div className="flex items-start gap-3">
                          <div className="text-2xl">🗣️</div>
                          <p className="text-sm font-medium leading-relaxed">{message.shortResponse}</p>
                        </div>
                      </div>

                      {/* Detailed text response */}
                      {message.detailedResponse && (
                        <div className="bg-[#FAFAF9] rounded-2xl px-5 py-4 border border-[#E5E5E5]">
                          <div className="prose prose-sm max-w-none">
                            <div 
                              className="font-sans text-[#4A3F35] text-sm leading-relaxed"
                              dangerouslySetInnerHTML={{ 
                                __html: message.detailedResponse.replace(/\n/g, '<br>') 
                              }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Backtest Charts */}
                      {message.metadata?.chart_data && message.metadata.chart_data.length > 0 && (
                        <div className="mt-4">
                          {message.metadata.chart_data.map((chartData: any, index: number) => {
                            // Extract metrics from the backtest result
                            const backtestResult = chartData.backtest_result || {}
                            const visuals = backtestResult.visuals || {}
                            
                            // Debug logging
                            console.log('📊 Rendering chart for:', chartData.symbol)
                            console.log('📊 Chart data:', chartData)
                            console.log('📊 Backtest result:', backtestResult)
                            
                            // Determine if result is good or bad
                            const totalReturn = backtestResult.total_return_pct > 0
                            const goodWinRate = backtestResult.win_rate > 0.5
                            const goodSharpe = !backtestResult.sharpe_ratio || backtestResult.sharpe_ratio > 0
                            const goodCriteria = [totalReturn, goodWinRate, goodSharpe].filter(Boolean).length
                            const isGoodResult = goodCriteria >= 2
                            
                            return (
                              <div key={index} className="mb-6 space-y-4">
                                {/* Character Visualization */}
                                <div className="bg-white rounded-lg border border-[#E5E5E5] overflow-hidden">
                                  <div className="p-4 border-b border-[#E5E5E5] text-center">
                                    <h4 className="text-lg font-bold text-[#2F1810]">
                                      {isGoodResult ? '🎉 Yee-Haw! Riding the Bull!' : '⚔️ Battle Mode: Fighting the Bear'}
                                    </h4>
                                    <p className="text-xs text-[#6B5D52] mt-1">
                                      {isGoodResult 
                                        ? 'This strategy shows strong performance!' 
                                        : 'This strategy needs improvement. Kopikolt is ready to fight back!'}
                                    </p>
                                  </div>
                                  <div className="bg-gradient-to-b from-[#FFF8DC] to-[#FAFAF9]" style={{ height: '350px' }}>
                                    <BacktestCharacterScene isGoodResult={isGoodResult} />
                                  </div>
                                </div>
                                
                                {/* Backtest Chart */}
                                <BacktestChart
                                  symbol={chartData.symbol}
                                  strategyName={message.metadata.strategy_name || 'Trading Strategy'}
                                  equityCurve={chartData.equity_curve || []}
                                  drawdownSeries={visuals.drawdown_series}
                                  metrics={{
                                    total_return: backtestResult.total_return || 0,
                                    total_return_pct: backtestResult.total_return_pct || 0,
                                    win_rate: backtestResult.win_rate || 0,
                                    sharpe_ratio: backtestResult.sharpe_ratio || 0,
                                    max_drawdown: backtestResult.max_drawdown || 0,
                                    num_trades: backtestResult.num_trades || 0,
                                    winning_trades: backtestResult.winning_trades || 0,
                                    losing_trades: backtestResult.losing_trades || 0,
                                    profit_factor: backtestResult.profit_factor || 0,
                                    avg_win: backtestResult.avg_win || 0,
                                    avg_loss: backtestResult.avg_loss || 0,
                                  }}
                                />
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              ))}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t-2 border-[#8B4513]/20 p-6 bg-gradient-to-r from-[#FAFAF9] to-[#F5F5F4]">
              <div className="flex gap-4">
                <motion.button
                  onClick={isListening ? stopListening : startListening}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  whileTap={{ scale: 0.9 }}
                  className={`p-4 rounded-2xl font-bold transition-all shadow-lg ${
                    isListening
                      ? 'bg-gradient-to-r from-red-500 to-red-600 text-white animate-pulse border-2 border-red-400'
                      : 'bg-gradient-to-r from-white to-gray-50 text-[#8B7355] border-2 border-[#8B4513] hover:border-red-500 hover:text-red-600'
                  }`}
                  disabled={isProcessing || isSpeaking}
                >
                  <motion.span
                    animate={isListening ? { scale: [1, 1.2, 1] } : {}}
                    transition={{ duration: 0.5, repeat: isListening ? Infinity : 0 }}
                  >
                    {isListening ? '🎤 Listening...' : '🎤'}
                  </motion.span>
                </motion.button>

                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your question or use voice..."
                  disabled={isProcessing || isSpeaking}
                  className="flex-1 px-6 py-4 rounded-2xl border-2 border-[#8B4513]/30 bg-white text-[#2F1810] font-medium focus:outline-none focus:border-[#8B7355] focus:ring-4 focus:ring-[#8B7355]/20 transition-all disabled:opacity-50 shadow-lg"
                />

                <motion.button
                  onClick={handleSendMessage}
                  whileHover={{ scale: 1.05, rotate: 2 }}
                  whileTap={{ scale: 0.95 }}
                  disabled={!inputText.trim() || isProcessing || isSpeaking}
                  className="px-8 py-4 rounded-2xl bg-gradient-to-r from-[#8B4513] to-[#A0522D] text-white font-bold hover:from-[#A0522D] hover:to-[#8B4513] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg border-2 border-white/20"
                >
                  <span className="flex items-center gap-2">
                    {isProcessing ? (
                      <>
                        <motion.span
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                        >
                          ⚡
                        </motion.span>
                        Processing...
                      </>
                    ) : (
                      <>
                        🚀 Send
                      </>
                    )}
                  </span>
                </motion.button>
              </div>
              <div className="flex items-center justify-center mt-3">
                <div className="flex items-center gap-2 text-xs text-[#6B5D52]">
                  <motion.span
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    ⭐
                  </motion.span>
                  Press Enter to send • Click 🎤 to use voice input
                  <motion.span
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                  >
                    ⭐
                  </motion.span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

