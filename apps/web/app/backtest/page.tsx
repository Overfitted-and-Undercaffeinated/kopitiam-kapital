'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { getBacktestTemplates, runBacktestDetailed } from '@/lib/api'

export default function BacktestPage() {
  const [symbol, setSymbol] = useState('')
  const [templates, setTemplates] = useState<any[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [initialCapital, setInitialCapital] = useState('100000')
  const [loading, setLoading] = useState(false)
  const [loadingTemplates, setLoadingTemplates] = useState(true)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Set default dates (1 year back)
    const end = new Date()
    const start = new Date()
    start.setFullYear(start.getFullYear() - 1)
    
    setEndDate(end.toISOString().split('T')[0])
    setStartDate(start.toISOString().split('T')[0])

    // Load templates
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const data = await getBacktestTemplates()
      setTemplates(data.templates || [])
      if (data.templates && data.templates.length > 0) {
        setSelectedTemplate(data.templates[0].id)
      }
    } catch (err) {
      console.error('Failed to load templates:', err)
    } finally {
      setLoadingTemplates(false)
    }
  }

  const handleRunBacktest = async () => {
    if (!symbol.trim() || !selectedTemplate) return

    setLoading(true)
    setError(null)
    
    try {
      const data = await runBacktestDetailed({
        symbol: symbol.toUpperCase(),
        strategy_template_id: selectedTemplate,
        start_date: startDate,
        end_date: endDate,
        initial_capital: parseFloat(initialCapital)
      })
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run backtest')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value > 0 ? '+' : ''}${(value * 100).toFixed(2)}%`
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9]" style={{ fontFamily: 'var(--font-body)' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#2F1810]">
                Strategy Backtesting
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                Test trading strategies against historical data
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg p-6 border border-[#E5E5E5] sticky top-24">
              <h2 className="text-lg font-bold text-[#2F1810] mb-4">Configuration</h2>
              
              {/* Symbol */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  Stock Symbol
                </label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  placeholder="e.g., AAPL, NVDA"
                  className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                />
              </div>

              {/* Strategy */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  Strategy Template
                </label>
                {loadingTemplates ? (
                  <div className="text-sm text-[#6B5D52]">Loading templates...</div>
                ) : (
                  <select
                    value={selectedTemplate}
                    onChange={(e) => setSelectedTemplate(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                  >
                    {templates.map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name}
                      </option>
                    ))}
                  </select>
                )}
                {selectedTemplate && templates.find(t => t.id === selectedTemplate) && (
                  <p className="mt-2 text-xs text-[#6B5D52]">
                    {templates.find(t => t.id === selectedTemplate)?.description}
                  </p>
                )}
              </div>

              {/* Date Range */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                />
              </div>

              {/* Initial Capital */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  Initial Capital
                </label>
                <input
                  type="number"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(e.target.value)}
                  placeholder="100000"
                  className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                />
              </div>

              {/* Run Button */}
              <motion.button
                onClick={handleRunBacktest}
                disabled={loading || !symbol.trim() || !selectedTemplate}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="w-full px-6 py-3 rounded-lg bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Running Backtest...' : 'Run Backtest'}
              </motion.button>
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
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

            {loading && (
              <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
                <motion.div
                  className="w-16 h-16 mx-auto mb-4 border-4 border-[#8B7355] border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                <p className="text-[#6B5D52]">Running backtest simulation...</p>
                <p className="text-sm text-[#9CA3AF] mt-2">This may take 3-5 seconds</p>
              </div>
            )}

            {results && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Summary Card */}
                <div className="bg-gradient-to-br from-[#8B7355] to-[#6F5D47] rounded-lg p-6 border border-[#6F5D47] text-white">
                  <h2 className="text-xl font-bold mb-4">{results.symbol} - {results.strategy}</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Total Return</div>
                      <div className={`text-2xl font-bold ${results.metrics.total_return_pct > 0 ? 'text-green-300' : 'text-red-300'}`}>
                        {formatPercent(results.metrics.total_return_pct)}
                      </div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Win Rate</div>
                      <div className="text-2xl font-bold">
                        {(results.metrics.win_rate * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Total Trades</div>
                      <div className="text-2xl font-bold">
                        {results.metrics.num_trades}
                      </div>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <div className="text-sm opacity-90 mb-1">Sharpe Ratio</div>
                      <div className="text-2xl font-bold">
                        {results.metrics.sharpe_ratio?.toFixed(2) || 'N/A'}
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 text-xs opacity-75">
                    Period: {results.period}
                  </div>
                </div>

                {/* Detailed Metrics */}
                <div className="bg-white rounded-lg border border-[#E5E5E5]">
                  <div className="p-6 border-b border-[#E5E5E5]">
                    <h3 className="text-xl font-bold text-[#2F1810]">Performance Metrics</h3>
                  </div>
                  <div className="p-6 grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-[#FAFAF9] rounded-lg">
                      <div className="text-sm text-[#6B5D52] mb-1">Final Value</div>
                      <div className="text-xl font-bold text-[#2F1810]">
                        {formatCurrency(results.metrics.final_value)}
                      </div>
                    </div>
                    <div className="p-4 bg-[#FAFAF9] rounded-lg">
                      <div className="text-sm text-[#6B5D52] mb-1">Profit Factor</div>
                      <div className="text-xl font-bold text-[#2F1810]">
                        {results.metrics.profit_factor?.toFixed(2) || 'N/A'}
                      </div>
                    </div>
                    <div className="p-4 bg-[#FAFAF9] rounded-lg">
                      <div className="text-sm text-[#6B5D52] mb-1">Max Drawdown</div>
                      <div className="text-xl font-bold text-red-600">
                        {formatPercent(results.metrics.max_drawdown || 0)}
                      </div>
                    </div>
                    <div className="p-4 bg-[#FAFAF9] rounded-lg">
                      <div className="text-sm text-[#6B5D52] mb-1">Avg Win</div>
                      <div className="text-xl font-bold text-green-600">
                        {formatCurrency(results.metrics.avg_win || 0)}
                      </div>
                    </div>
                    <div className="p-4 bg-[#FAFAF9] rounded-lg">
                      <div className="text-sm text-[#6B5D52] mb-1">Avg Loss</div>
                      <div className="text-xl font-bold text-red-600">
                        {formatCurrency(results.metrics.avg_loss || 0)}
                      </div>
                    </div>
                    <div className="p-4 bg-[#FAFAF9] rounded-lg">
                      <div className="text-sm text-[#6B5D52] mb-1">Sortino Ratio</div>
                      <div className="text-xl font-bold text-[#2F1810]">
                        {results.metrics.sortino_ratio?.toFixed(2) || 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Trade History */}
                {results.metrics.trades && results.metrics.trades.length > 0 && (
                  <div className="bg-white rounded-lg border border-[#E5E5E5]">
                    <div className="p-6 border-b border-[#E5E5E5] flex items-center justify-between">
                      <h3 className="text-xl font-bold text-[#2F1810]">Trade History</h3>
                      <span className="text-sm text-[#6B5D52]">
                        Showing last 10 trades
                      </span>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-[#FAFAF9]">
                          <tr>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-[#2F1810]">Date</th>
                            <th className="px-4 py-3 text-left text-sm font-semibold text-[#2F1810]">Type</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold text-[#2F1810]">Entry</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold text-[#2F1810]">Exit</th>
                            <th className="px-4 py-3 text-right text-sm font-semibold text-[#2F1810]">P&L</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#E5E5E5]">
                          {results.metrics.trades.slice(-10).reverse().map((trade: any, idx: number) => (
                            <tr key={idx} className="hover:bg-[#FAFAF9] transition-colors">
                              <td className="px-4 py-3 text-sm text-[#2F1810]">
                                {new Date(trade.entry_date).toLocaleDateString()}
                              </td>
                              <td className="px-4 py-3 text-sm">
                                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                  trade.type === 'BUY' 
                                    ? 'bg-green-100 text-green-700' 
                                    : 'bg-red-100 text-red-700'
                                }`}>
                                  {trade.type}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-sm text-right text-[#2F1810]">
                                {formatCurrency(trade.entry_price)}
                              </td>
                              <td className="px-4 py-3 text-sm text-right text-[#2F1810]">
                                {formatCurrency(trade.exit_price)}
                              </td>
                              <td className={`px-4 py-3 text-sm text-right font-semibold ${
                                trade.pnl > 0 ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {formatCurrency(trade.pnl)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* Empty State */}
            {!results && !loading && !error && (
              <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
                <div className="text-6xl mb-4">📈</div>
                <h3 className="text-xl font-bold text-[#2F1810] mb-2">
                  Ready to Test Your Strategy
                </h3>
                <p className="text-[#6B5D52] mb-6">
                  Configure your backtest parameters and click "Run Backtest"
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

