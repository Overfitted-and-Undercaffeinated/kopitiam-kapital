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

  const fetchRealAIResponse = async (userQuestion: string): Promise<{ short: string; detailed: string }> => {
    const AI_API_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000'
    const userId = localStorage.getItem('userId') || 'demo_user'
    
    try {
      console.log('🤖 Calling AI Orchestrator:', { query: userQuestion, userId })
      
      const response = await fetch(`${AI_API_URL}/ai/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userQuestion,
          user_id: userId,
          context: {
            userName: userName,
            timestamp: new Date().toISOString()
          }
        }),
        signal: AbortSignal.timeout(30000) // 30 second timeout
      })
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('✅ AI Response received:', data)
      
      // Extract response text - the orchestrator returns a response field
      const responseText = data.response || data.text || data.message || 'No response from AI'
      
      // Split response into short (first paragraph) and detailed (full text)
      const paragraphs = responseText.split('\n\n').filter((p: string) => p.trim().length > 0)
      const short = paragraphs[0] || responseText.substring(0, 200)
      const detailed = responseText
      
      return { short, detailed }
      
    } catch (error) {
      console.error('❌ AI API Error:', error)
      
      // Fallback to a friendly error message
      return {
        short: `Whoa there, ${userName}! My AI brain's takin' a coffee break. Let me give ya what I remember...`,
        detailed: `I'm havin' trouble connectin' to the main AI engine right now, partner. This might be because:\n\n• The backend server isn't runnin' (try: cd apps/ai && uvicorn main:app --reload)\n• Network connection issues\n• API timeout (your question might need more thinkin' time)\n\nIn the meantime, here's some general advice:\n\n• For stock recommendations, I typically analyze sentiment from multiple sources (news, Reddit, social media)\n• I run backtests to validate strategies before recommendin' 'em\n• I personalize recommendations based on your risk profile in Mem0\n\nTry askin' me again in a moment, or check that the AI backend is runnin'!`
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
      `}</style>
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

      {/* Quick Access Navigation */}
      <div className="bg-white/90 backdrop-blur-sm border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6">
          <div className="flex gap-1 overflow-x-auto py-2">
            <a href="/sentiment" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-white hover:text-[#2F1810] transition-colors whitespace-nowrap">
              📊 Sentiment
            </a>
            <a href="/backtest" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-white hover:text-[#2F1810] transition-colors whitespace-nowrap">
              📈 Backtest
            </a>
            <a href="/alerts" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-white hover:text-[#2F1810] transition-colors whitespace-nowrap">
              🔔 Alerts
            </a>
            <a href="/analysis" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-white hover:text-[#2F1810] transition-colors whitespace-nowrap">
              📄 Analysis
            </a>
            <a href="/portfolio" className="px-4 py-2 rounded-lg text-sm font-medium text-[#6B5D52] hover:bg-white hover:text-[#2F1810] transition-colors whitespace-nowrap">
              💼 Portfolio
            </a>
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

