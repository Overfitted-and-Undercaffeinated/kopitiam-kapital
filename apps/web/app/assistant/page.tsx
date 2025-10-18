'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import dynamic from 'next/dynamic'

const KopiColt2D = dynamic(() => import('../onboarding/components/KopiColt2D'), {
  ssr: false,
})

interface Message {
  id: string
  role: 'user' | 'assistant'
  shortResponse?: string // What Kopi says aloud
  detailedResponse?: string // Detailed text not read aloud
  userMessage?: string
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

  const generateHardcodedResponse = (userQuestion: string): { short: string; detailed: string } => {
    const question = userQuestion.toLowerCase()
    
    // Hardcoded responses based on keywords
    if (question.includes('apple') || question.includes('aapl')) {
      return {
        short: `Howdy there ${userName}! Given the current market conditions, I'mma say hold off on Apple for now, partner.`,
        detailed: `Here's why I'm cautious on AAPL right now:\n\n• **Valuation Concerns**: Trading at 28x P/E, which is above historical averages\n• **China Headwinds**: iPhone sales in China down 15% YoY due to local competition\n• **Margin Pressure**: Services growth slowing, hardware margins compressing\n• **Technical Setup**: RSI showing overbought conditions at 72\n\nBetter entry would be around $165-170 range. Keep it on your watchlist and I'll holler when conditions improve!`
      }
    } else if (question.includes('dbs') || question.includes('bank')) {
      return {
        short: `Well partner, DBS is lookin' mighty fine right now! I'd say it's a buy at current levels.`,
        detailed: `Here's the bull case for DBS:\n\n• **Strong Earnings**: Beat expectations by 8% last quarter with ROE at 18%\n• **Rising Rates**: Net interest margin expanding, expected to hit 2.1% this year\n• **Dividend Yield**: 5.2% yield with consistent payout history\n• **Valuation**: Trading at 1.2x book value, reasonable for quality\n• **Technical**: Breaking above resistance at $35, momentum building\n\nEntry: $35.20 | Target: $37.50 | Stop: $34.00\nPosition size: 2-3% of portfolio for moderate risk profile`
      }
    } else if (question.includes('sgx') || question.includes('singapore')) {
      return {
        short: `The Straits Times Index is lookin' steady as a mule, ${userName}. Market's in consolidation mode.`,
        detailed: `STI Market Overview:\n\n• **Current Level**: 3,245 points, up 0.3% today\n• **Trend**: Range-bound between 3,200-3,280 for past 3 weeks\n• **Sector Leaders**: Banks leading with DBS, UOB, OCBC all up 1%+\n• **Laggards**: Tech sector down on US chip restrictions\n• **Volume**: Above average at 1.2B shares, showing healthy participation\n• **Outlook**: Watching 3,280 resistance - breakout could target 3,350\n\nBest opportunities right now are in banking sector and quality REITs with stable yields.`
      }
    } else if (question.includes('portfolio') || question.includes('holdings')) {
      return {
        short: `Your portfolio's sittin' pretty at $52,450, up 1.3% today. Nice work, partner!`,
        detailed: `Portfolio Summary:\n\n• **Total Value**: $52,450\n• **Today's P&L**: +$685 (+1.3%)\n• **All-Time Return**: +8.5%\n• **Open Positions**: 5\n\n**Top Performers Today**:\n1. DBS - +$450 (+1.5%)\n2. OCBC - +$95 (+0.8%)\n3. CapitaLand - +$70 (+0.6%)\n\n**Risk Metrics**:\n• Portfolio Beta: 0.85 (lower volatility than market)\n• Max Drawdown: -3.2% (well controlled)\n• Sharpe Ratio: 1.4 (good risk-adjusted returns)\n\nYou're well-diversified across banks and blue chips. Consider adding some growth exposure if risk appetite allows.`
      }
    } else if (question.includes('market') || question.includes('today')) {
      return {
        short: `Markets are ridin' high today, ${userName}! STI up 0.45%, banks gallopin' ahead!`,
        detailed: `Today's Market Highlights:\n\n**Singapore (STI)**:\n• Up 0.45% at 3,259 points\n• Banking sector +1.2% leading the charge\n• Volume: 1.2B shares (above average)\n\n**Regional Markets**:\n• Hong Kong HSI: -0.3%\n• Japan Nikkei: +0.8%\n• South Korea KOSPI: +0.4%\n\n**Key Drivers**:\n• Strong DBS earnings beat boosting banking sector\n• GDP revision upward to 3.2% supporting sentiment\n• Fed Chair speech tonight at 10PM SGT - watch for volatility\n\n**Trading Opportunities**:\n• Banks showing momentum - DBS, UOB looking strong\n• REITs stable with rate outlook improving\n• Tech oversold - potential bounce plays`
      }
    } else if (question.includes('crypto') || question.includes('bitcoin')) {
      return {
        short: `Whoa there, partner! Crypto's wild country. For SGX traders, I'd say stick to what you know best.`,
        detailed: `Crypto Market Assessment:\n\n**My Take**: Not recommending crypto exposure for traditional SGX portfolios\n\n**Reasons**:\n• **High Volatility**: Bitcoin down 40% from peaks, massive swings\n• **Regulatory Uncertainty**: Singapore MAS tightening crypto regulations\n• **Correlation Risk**: Now moving with tech stocks, losing diversification benefit\n• **Better Alternatives**: Singapore banks offering 5%+ dividends with lower risk\n\n**If You Must**:\n• Keep to <5% of portfolio\n• Use dollar-cost averaging\n• Only invest what you can afford to lose\n• Consider Bitcoin/Ethereum only (avoid altcoins)\n\nFor steady income and capital preservation, Singapore blue chips are your best bet, partner.`
      }
    } else {
      return {
        short: `That's a good question, ${userName}! Let me rustle up some info on that for ya.`,
        detailed: `I'm still learnin' the ropes on this one, partner. Here's what I can tell ya:\n\n• **Market Conditions**: Generally favorable for quality stocks\n• **Risk Environment**: Moderate - keep position sizes in check\n• **Opportunities**: Banking sector and dividend plays looking good\n• **Caution Areas**: High-growth tech, speculative plays\n\nFor specific stock recommendations, try asking me about:\n• Singapore blue chips (DBS, UOB, OCBC, CapitaLand)\n• Market outlook and STI trends\n• Your portfolio performance\n• Sector analysis\n\nWhat else can I help you with today?`
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

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 800))

    // Generate response
    const response = generateHardcodedResponse(userQuestion)

    // Add assistant message
    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      shortResponse: response.short,
      detailedResponse: response.detailed,
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
        console.error('Voice generation failed')
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
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-sm border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#2F1810]">
                Ask Kopi Colt
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                Your AI trading companion
              </p>
            </div>
            <motion.a
              href="/dashboard"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-4 py-2 bg-[#8B7355] text-white rounded-lg text-sm font-medium hover:bg-[#6F5D47] transition-colors"
            >
              Back to Dashboard
            </motion.a>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8 max-w-6xl">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-180px)]">
          {/* Kopi Colt Character - Left Side */}
          <div className="lg:col-span-1 flex items-center justify-center">
            <div className="relative">
              <KopiColt2D 
                expression={isProcessing ? 'neutral' : isSpeaking ? 'happy' : 'neutral'}
                step={0}
                isIntro={false}
              />
              
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
          <div className="lg:col-span-2 flex flex-col bg-white rounded-lg shadow-xl border border-[#E5E5E5] overflow-hidden">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                  >
                    <h3 className="text-3xl font-bold text-[#2F1810] mb-4" style={{ fontFamily: 'var(--font-heading)' }}>
                      Howdy, {userName}! 🤠
                    </h3>
                    <p className="text-lg text-[#6B5D52] mb-6">
                      Ask me anything about the markets, your portfolio, or trading ideas!
                    </p>
                    <div className="grid grid-cols-2 gap-3 max-w-xl mx-auto">
                      {[
                        'Should I buy DBS?',
                        'How\'s my portfolio doing?',
                        'What\'s the market outlook?',
                        'Tell me about Apple stock'
                      ].map((suggestion) => (
                        <motion.button
                          key={suggestion}
                          onClick={() => setInputText(suggestion)}
                          whileHover={{ scale: 1.02, y: -2 }}
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-3 bg-[#FAFAF9] hover:bg-[#F5F5F4] rounded-lg text-sm font-medium text-[#2F1810] border border-[#E5E5E5] transition-colors"
                        >
                          {suggestion}
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
                            <pre className="whitespace-pre-wrap font-sans text-[#4A3F35] text-sm leading-relaxed">
                              {message.detailedResponse}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              ))}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-[#E5E5E5] p-4 bg-[#FAFAF9]">
              <div className="flex gap-3">
                <motion.button
                  onClick={isListening ? stopListening : startListening}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`p-4 rounded-xl font-bold transition-all ${
                    isListening
                      ? 'bg-red-500 text-white animate-pulse'
                      : 'bg-white text-[#8B7355] border border-[#E5E5E5] hover:border-[#8B7355]'
                  }`}
                  disabled={isProcessing || isSpeaking}
                >
                  {isListening ? '🎤 Listening...' : '🎤'}
                </motion.button>

                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your question or use voice..."
                  disabled={isProcessing || isSpeaking}
                  className="flex-1 px-5 py-4 rounded-xl border border-[#E5E5E5] bg-white text-[#2F1810] font-medium focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20 transition-all disabled:opacity-50"
                />

                <motion.button
                  onClick={handleSendMessage}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  disabled={!inputText.trim() || isProcessing || isSpeaking}
                  className="px-6 py-4 rounded-xl bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? '...' : 'Send'}
                </motion.button>
              </div>
              <p className="text-xs text-[#6B5D52] mt-2 text-center">
                Press Enter to send • Click 🎤 to use voice input
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

