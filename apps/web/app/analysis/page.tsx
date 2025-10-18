'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { autoFetchAndAnalyze, analyzeLongDocument } from '@/lib/api'

const DOCUMENT_TYPES = [
  { value: '10-K', label: '10-K Annual Report', icon: '📊' },
  { value: '10-Q', label: '10-Q Quarterly Report', icon: '📈' },
  { value: 'earnings_call', label: 'Earnings Call Transcript', icon: '📞' },
  { value: 'annual_report', label: 'Annual Report', icon: '📑' },
  { value: 'presentation', label: 'Investor Presentation', icon: '🎯' },
]

export default function AnalysisPage() {
  const [mode, setMode] = useState<'auto' | 'manual'>('auto')
  const [ticker, setTicker] = useState('')
  const [includeEarningsCall, setIncludeEarningsCall] = useState(true)
  const [documentText, setDocumentText] = useState('')
  const [documentType, setDocumentType] = useState('10-K')
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAutoAnalyze = async () => {
    if (!ticker.trim()) return

    setLoading(true)
    setError(null)
    
    try {
      const userId = localStorage.getItem('userId') || 'demo_user'
      const data = await autoFetchAndAnalyze({
        ticker: ticker.toUpperCase(),
        user_id: userId,
        include_earnings_call: includeEarningsCall
      })
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze document')
      setAnalysis(null)
    } finally {
      setLoading(false)
    }
  }

  const handleManualAnalyze = async () => {
    if (!documentText.trim()) return

    setLoading(true)
    setError(null)
    
    try {
      const userId = localStorage.getItem('userId') || 'demo_user'
      const data = await analyzeLongDocument({
        text: documentText,
        document_type: documentType,
        user_id: userId,
        ticker: ticker.toUpperCase() || undefined
      })
      setAnalysis(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze document')
      setAnalysis(null)
    } finally {
      setLoading(false)
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
                Document Analysis
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                AI-powered analysis of financial documents (Claude 200K context)
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
      <div className="container mx-auto px-6 py-8 max-w-6xl">
        {/* Tier Info Banner */}
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🔮</div>
            <div>
              <h3 className="font-semibold text-purple-900 mb-1">Analysis Limits by Tier</h3>
              <div className="text-sm text-purple-700 space-y-1">
                <p>• <strong>FREE:</strong> 1/month - Basic summary + key metrics</p>
                <p>• <strong>PRO:</strong> 10/month - Summary + risks + opportunities</p>
                <p>• <strong>ENTERPRISE:</strong> Unlimited - Full analysis + competitive positioning</p>
              </div>
            </div>
          </div>
        </div>

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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg p-6 border border-[#E5E5E5] sticky top-24">
              <h2 className="text-lg font-bold text-[#2F1810] mb-4">Analysis Mode</h2>
              
              {/* Mode Toggle */}
              <div className="flex gap-2 mb-6">
                <button
                  onClick={() => setMode('auto')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                    mode === 'auto'
                      ? 'bg-[#8B7355] text-white'
                      : 'bg-[#FAFAF9] text-[#6B5D52] hover:bg-[#F5F5F4]'
                  }`}
                >
                  Auto-Fetch
                </button>
                <button
                  onClick={() => setMode('manual')}
                  className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                    mode === 'manual'
                      ? 'bg-[#8B7355] text-white'
                      : 'bg-[#FAFAF9] text-[#6B5D52] hover:bg-[#F5F5F4]'
                  }`}
                >
                  Manual
                </button>
              </div>

              {mode === 'auto' ? (
                <div className="space-y-4">
                  {/* Ticker */}
                  <div>
                    <label className="block text-sm font-medium text-[#2F1810] mb-2">
                      Stock Symbol
                    </label>
                    <input
                      type="text"
                      value={ticker}
                      onChange={(e) => setTicker(e.target.value.toUpperCase())}
                      placeholder="e.g., AAPL, GOOGL"
                      className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                    />
                  </div>

                  {/* Include Earnings Call */}
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="includeEarnings"
                      checked={includeEarningsCall}
                      onChange={(e) => setIncludeEarningsCall(e.target.checked)}
                      className="w-4 h-4 rounded border-[#E5E5E5] text-[#8B7355] focus:ring-[#8B7355]"
                    />
                    <label htmlFor="includeEarnings" className="text-sm text-[#2F1810]">
                      Include earnings call transcript
                    </label>
                  </div>

                  {/* Analyze Button */}
                  <motion.button
                    onClick={handleAutoAnalyze}
                    disabled={loading || !ticker.trim()}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full px-6 py-3 rounded-lg bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Analyzing...' : 'Auto-Fetch & Analyze'}
                  </motion.button>

                  <p className="text-xs text-[#6B5D52]">
                    We'll automatically search for and analyze the latest 10-K and earnings call
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Ticker (optional) */}
                  <div>
                    <label className="block text-sm font-medium text-[#2F1810] mb-2">
                      Stock Symbol (Optional)
                    </label>
                    <input
                      type="text"
                      value={ticker}
                      onChange={(e) => setTicker(e.target.value.toUpperCase())}
                      placeholder="e.g., AAPL"
                      className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                    />
                  </div>

                  {/* Document Type */}
                  <div>
                    <label className="block text-sm font-medium text-[#2F1810] mb-2">
                      Document Type
                    </label>
                    <select
                      value={documentType}
                      onChange={(e) => setDocumentType(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                    >
                      {DOCUMENT_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Document Text */}
                  <div>
                    <label className="block text-sm font-medium text-[#2F1810] mb-2">
                      Document Text
                    </label>
                    <textarea
                      value={documentText}
                      onChange={(e) => setDocumentText(e.target.value)}
                      placeholder="Paste your document text here..."
                      rows={12}
                      className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20 resize-none font-mono text-sm"
                    />
                  </div>

                  {/* Analyze Button */}
                  <motion.button
                    onClick={handleManualAnalyze}
                    disabled={loading || !documentText.trim()}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full px-6 py-3 rounded-lg bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Analyzing...' : 'Analyze Document'}
                  </motion.button>
                </div>
              )}
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            {loading && (
              <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
                <motion.div
                  className="w-16 h-16 mx-auto mb-4 border-4 border-[#8B7355] border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                <p className="text-[#6B5D52]">Analyzing document with Claude...</p>
                <p className="text-sm text-[#9CA3AF] mt-2">This may take 10-30 seconds for long documents</p>
              </div>
            )}

            {analysis && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Summary Card */}
                {analysis.summary && (
                  <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg p-6 border border-purple-700 text-white">
                    <h2 className="text-xl font-bold mb-2">Summary</h2>
                    {analysis.ticker && (
                      <div className="text-sm opacity-90 mb-4">{analysis.ticker}</div>
                    )}
                    <p className="leading-relaxed">{analysis.summary}</p>
                  </div>
                )}

                {/* Key Metrics */}
                {analysis.key_metrics && (
                  <div className="bg-white rounded-lg border border-[#E5E5E5]">
                    <div className="p-6 border-b border-[#E5E5E5]">
                      <h3 className="text-xl font-bold text-[#2F1810]">Key Metrics</h3>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-2">
                        {Array.isArray(analysis.key_metrics) ? (
                          analysis.key_metrics.map((metric: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-[#4A3F35]">
                              <span className="text-green-600 mt-1">✓</span>
                              <span>{metric}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-[#4A3F35]">{JSON.stringify(analysis.key_metrics)}</li>
                        )}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Risks */}
                {analysis.risks && (
                  <div className="bg-white rounded-lg border border-[#E5E5E5]">
                    <div className="p-6 border-b border-[#E5E5E5]">
                      <h3 className="text-xl font-bold text-[#2F1810]">Risk Factors</h3>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-2">
                        {Array.isArray(analysis.risks) ? (
                          analysis.risks.map((risk: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-[#4A3F35]">
                              <span className="text-red-600 mt-1">⚠️</span>
                              <span>{risk}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-[#4A3F35]">{JSON.stringify(analysis.risks)}</li>
                        )}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Opportunities */}
                {analysis.opportunities && (
                  <div className="bg-white rounded-lg border border-[#E5E5E5]">
                    <div className="p-6 border-b border-[#E5E5E5]">
                      <h3 className="text-xl font-bold text-[#2F1810]">Opportunities</h3>
                    </div>
                    <div className="p-6">
                      <ul className="space-y-2">
                        {Array.isArray(analysis.opportunities) ? (
                          analysis.opportunities.map((opp: string, idx: number) => (
                            <li key={idx} className="flex items-start gap-2 text-[#4A3F35]">
                              <span className="text-blue-600 mt-1">💡</span>
                              <span>{opp}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-[#4A3F35]">{JSON.stringify(analysis.opportunities)}</li>
                        )}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Full Analysis */}
                {analysis.analysis && (
                  <div className="bg-white rounded-lg border border-[#E5E5E5]">
                    <div className="p-6 border-b border-[#E5E5E5]">
                      <h3 className="text-xl font-bold text-[#2F1810]">Detailed Analysis</h3>
                    </div>
                    <div className="p-6">
                      <div className="prose prose-sm max-w-none">
                        <pre className="whitespace-pre-wrap font-sans text-[#4A3F35] leading-relaxed">
                          {analysis.analysis}
                        </pre>
                      </div>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* Empty State */}
            {!analysis && !loading && !error && (
              <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-xl font-bold text-[#2F1810] mb-2">
                  Analyze Financial Documents
                </h3>
                <p className="text-[#6B5D52] mb-6">
                  Get AI-powered insights from 10-Ks, earnings calls, and more
                </p>
                <div className="flex justify-center gap-3">
                  {['AAPL', 'GOOGL', 'MSFT', 'NVDA'].map((sym) => (
                    <motion.button
                      key={sym}
                      onClick={() => {
                        setTicker(sym)
                        setMode('auto')
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
      </div>
    </div>
  )
}

