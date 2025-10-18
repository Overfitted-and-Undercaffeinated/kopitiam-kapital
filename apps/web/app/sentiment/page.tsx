'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { getSentiment } from '@/lib/api'

export default function SentimentPage() {
  const [symbol, setSymbol] = useState('')
  const [loading, setLoading] = useState(false)
  const [sentimentData, setSentimentData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    if (!symbol.trim()) return

    setLoading(true)
    setError(null)
    
    try {
      const userId = localStorage.getItem('userId') || 'demo_user'
      const data = await getSentiment(symbol.toUpperCase(), userId)
      setSentimentData(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch sentiment')
      setSentimentData(null)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentColor = (score: number) => {
    if (score >= 0.55) return 'text-green-600 bg-green-100'
    if (score <= 0.45) return 'text-red-600 bg-red-100'
    return 'text-yellow-600 bg-yellow-100'
  }

  const getSentimentLabel = (score: number) => {
    if (score >= 0.55) return 'Bullish 🟢'
    if (score <= 0.45) return 'Bearish 🔴'
    return 'Neutral 🟡'
  }

  const extractPublisherName = (url: string, title: string) => {
    if (!url) return title || 'News Source'
    
    try {
      const domain = new URL(url).hostname.toLowerCase()
      
      // Map common domains to publisher names
      const publisherMap: { [key: string]: string } = {
        'cnbc.com': 'CNBC',
        'reuters.com': 'Reuters',
        'bloomberg.com': 'Bloomberg',
        'wsj.com': 'Wall Street Journal',
        'ft.com': 'Financial Times',
        'marketwatch.com': 'MarketWatch',
        'yahoo.com': 'Yahoo Finance',
        'investing.com': 'Investing.com',
        'seekingalpha.com': 'Seeking Alpha',
        'benzinga.com': 'Benzinga',
        'fool.com': 'Motley Fool',
        'nasdaq.com': 'NASDAQ',
        'finance.yahoo.com': 'Yahoo Finance',
        'markets.businessinsider.com': 'Business Insider',
        'businessinsider.com': 'Business Insider',
        'forbes.com': 'Forbes',
        'barrons.com': 'Barron\'s',
        'investor.com': 'Investor.com',
        'thestreet.com': 'TheStreet',
        'zacks.com': 'Zacks',
        'morningstar.com': 'Morningstar'
      }
      
      // Check for exact matches first
      for (const [domainKey, publisherName] of Object.entries(publisherMap)) {
        if (domain.includes(domainKey)) {
          return publisherName
        }
      }
      
      // Extract from domain if no match
      const parts = domain.split('.')
      if (parts.length >= 2) {
        const mainDomain = parts[parts.length - 2]
        return mainDomain.charAt(0).toUpperCase() + mainDomain.slice(1)
      }
      
      return title || 'News Source'
    } catch {
      return title || 'News Source'
    }
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9]" style={{ fontFamily: 'var(--font-body)' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#2F1810]">
                Sentiment Analysis
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                Multi-source market sentiment from news, Reddit & social media
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

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Search Input */}
        <div className="bg-white rounded-lg p-6 border border-[#E5E5E5] mb-6">
          <label className="block text-sm font-medium text-[#2F1810] mb-2">
            Stock Symbol
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
              placeholder="Enter symbol (e.g., NVDA, AAPL, DBS)"
              className="flex-1 px-4 py-3 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] font-medium focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20 transition-all"
            />
            <motion.button
              onClick={handleAnalyze}
              disabled={loading || !symbol.trim()}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-8 py-3 rounded-lg bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </motion.button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6"
          >
            <p className="font-medium">Error: {error}</p>
            <p className="text-sm mt-1">Make sure the AI backend is running at http://localhost:8000</p>
          </motion.div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
            <motion.div
              className="w-16 h-16 mx-auto mb-4 border-4 border-[#8B7355] border-t-transparent rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            />
            <p className="text-[#6B5D52]">Analyzing sentiment from multiple sources...</p>
            <p className="text-sm text-[#9CA3AF] mt-2">This may take 3-8 seconds</p>
          </div>
        )}

        {/* Sentiment Results */}
        {sentimentData && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overall Score */}
            <div className="bg-gradient-to-br from-[#8B7355] to-[#6F5D47] rounded-lg p-8 border border-[#6F5D47] text-white">
              <div className="text-center">
                <h2 className="text-xl font-bold mb-2">{sentimentData.symbol}</h2>
                <div className="text-6xl font-bold mb-2">
                  {(sentimentData.overall_score * 100).toFixed(0)}%
                </div>
                <div className="text-2xl font-medium">
                  {getSentimentLabel(sentimentData.overall_score)}
                </div>
                {sentimentData.direction && (
                  <div className="mt-2 text-lg opacity-90 capitalize">
                    Direction: {sentimentData.direction}
                  </div>
                )}
                {sentimentData.confidence !== undefined && (
                  <div className="mt-1 text-sm opacity-75">
                    Confidence: {(sentimentData.confidence * 100).toFixed(0)}%
                  </div>
                )}
              </div>

              {/* Badges */}
              <div className="flex justify-center gap-3 mt-6">
                {sentimentData.trending && (
                  <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">
                    🔥 Trending
                  </div>
                )}
                {sentimentData.contrarian_signal && (
                  <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">
                    ⚠️ Contrarian Signal
                  </div>
                )}
              </div>
            </div>

            {/* Source Breakdown */}
            <div className="bg-white rounded-lg border border-[#E5E5E5]">
              <div className="p-6 border-b border-[#E5E5E5]">
                <h3 className="text-xl font-bold text-[#2F1810]">Source Breakdown</h3>
              </div>
              <div className="p-6 space-y-4">
                {sentimentData.sentiment_breakdown && Object.entries(sentimentData.sentiment_breakdown).map(([source, score]: [string, any]) => (
                  <div key={source} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-[#FAFAF9] rounded-lg flex items-center justify-center text-xl">
                        {source === 'news' && '📰'}
                        {source === 'reddit' && '🤖'}
                        {source === 'stocktwits' && '💬'}
                      </div>
                      <div>
                        <div className="font-semibold text-[#2F1810] capitalize">{source}</div>
                        {sentimentData.volume && sentimentData.volume[source] && (
                          <div className="text-sm text-[#6B5D52]">
                            {sentimentData.volume[source]} items
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getSentimentColor(score)}`}>
                          {(score * 100).toFixed(0)}%
                        </div>
                        <div className="text-sm text-[#6B5D52]">
                          {getSentimentLabel(score)}
                        </div>
                      </div>
                      <div className="w-32 bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-3 rounded-full transition-all duration-500"
                          style={{ width: `${score * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Sources */}
            {sentimentData.top_sources && sentimentData.top_sources.length > 0 && (
              <div className="bg-white rounded-lg border border-[#E5E5E5]">
                <div className="p-6 border-b border-[#E5E5E5]">
                  <h3 className="text-xl font-bold text-[#2F1810]">Top Sources</h3>
                </div>
                <div className="divide-y divide-[#E5E5E5]">
                  {sentimentData.top_sources.slice(0, 5).map((source: any, idx: number) => (
                    <div key={idx} className="p-4 hover:bg-[#FAFAF9] transition-colors">
                      <div className="flex items-start gap-3">
                        <div className={`mt-1 w-2 h-2 rounded-full ${getSentimentColor(source.sentiment_score || 0.5)}`} />
                        <div className="flex-1">
                          <h4 className="font-semibold text-[#2F1810] mb-1">
                            {extractPublisherName(source.url, source.title)}
                          </h4>
                          {source.title && source.title !== extractPublisherName(source.url, source.title) && (
                            <div className="text-sm text-[#6B5D52] mb-1 italic">
                              {source.title.length > 80 ? source.title.substring(0, 80) + '...' : source.title}
                            </div>
                          )}
                          {source.url && (
                            <a
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-[#8B7355] hover:underline"
                            >
                              View Source →
                            </a>
                          )}
                          {source.published_date && (
                            <div className="text-sm text-[#6B5D52] mt-1">
                              {new Date(source.published_date).toLocaleDateString()}
                            </div>
                          )}
                          {source.sentiment_reasoning && source.sentiment_reasoning !== 'No reasoning available' && (
                            <div className="text-sm text-[#6B5D52] mt-1 italic">
                              {source.sentiment_reasoning.substring(0, 150)}...
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Empty State */}
        {!sentimentData && !loading && !error && (
          <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-bold text-[#2F1810] mb-2">
              Analyze Market Sentiment
            </h3>
            <p className="text-[#6B5D52] mb-6">
              Enter a stock symbol above to get multi-source sentiment analysis
            </p>
            <div className="flex justify-center gap-3">
              {['NVDA', 'AAPL', 'TSLA', 'DBS'].map((sym) => (
                <motion.button
                  key={sym}
                  onClick={() => {
                    setSymbol(sym)
                    setTimeout(() => handleAnalyze(), 100)
                  }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-2 bg-[#FAFAF9] hover:bg-[#F5F5F4] rounded-lg text-sm font-medium text-[#2F1810] border border-[#E5E5E5] transition-colors"
                >
                  Try {sym}
                </motion.button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

