'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { checkAlerts, createAlert } from '@/lib/api'

const ALERT_TYPES = [
  { value: 'price_above', label: 'Price Above', icon: '⬆️' },
  { value: 'price_below', label: 'Price Below', icon: '⬇️' },
  { value: 'volatility_spike', label: 'Volatility Spike', icon: '⚡', proOnly: true },
  { value: 'sentiment_change', label: 'Sentiment Change', icon: '📊', proOnly: true },
  { value: 'news_event', label: 'Breaking News', icon: '📰', enterpriseOnly: true },
]

export default function AlertsPage() {
  const [activeAlerts, setActiveAlerts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  
  // Form state
  const [symbol, setSymbol] = useState('')
  const [alertType, setAlertType] = useState('price_above')
  const [priceThreshold, setPriceThreshold] = useState('')
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    loadAlerts()
  }, [])

  const loadAlerts = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const userId = localStorage.getItem('userId') || 'demo_user'
      const data = await checkAlerts(userId)
      setActiveAlerts(data.alerts || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAlert = async () => {
    if (!symbol.trim() || !priceThreshold) return

    setCreating(true)
    
    try {
      const userId = localStorage.getItem('userId') || 'demo_user'
      
      const condition: any = {}
      if (alertType === 'price_above' || alertType === 'price_below') {
        condition.price = parseFloat(priceThreshold)
      }
      
      await createAlert({
        user_id: userId,
        symbol: symbol.toUpperCase(),
        alert_type: alertType,
        condition
      })
      
      // Reset form
      setSymbol('')
      setPriceThreshold('')
      setShowCreateForm(false)
      
      // Reload alerts
      await loadAlerts()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create alert')
    } finally {
      setCreating(false)
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
                Market Alerts
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                24/7 monitoring with real-time notifications
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
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">ℹ️</div>
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">Alert Limits by Tier</h3>
              <div className="text-sm text-blue-700 space-y-1">
                <p>• <strong>FREE:</strong> 3 alerts/day (price only)</p>
                <p>• <strong>PRO:</strong> 50 alerts/day (all types)</p>
                <p>• <strong>ENTERPRISE:</strong> Unlimited alerts</p>
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
          {/* Create Alert Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg p-6 border border-[#E5E5E5] sticky top-24">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-[#2F1810]">Create Alert</h2>
                {showCreateForm && (
                  <button
                    onClick={() => setShowCreateForm(false)}
                    className="text-sm text-[#6B5D52] hover:text-[#2F1810]"
                  >
                    Cancel
                  </button>
                )}
              </div>
              
              {!showCreateForm ? (
                <motion.button
                  onClick={() => setShowCreateForm(true)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full px-6 py-3 rounded-lg bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors"
                >
                  + New Alert
                </motion.button>
              ) : (
                <div className="space-y-4">
                  {/* Symbol */}
                  <div>
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

                  {/* Alert Type */}
                  <div>
                    <label className="block text-sm font-medium text-[#2F1810] mb-2">
                      Alert Type
                    </label>
                    <select
                      value={alertType}
                      onChange={(e) => setAlertType(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                    >
                      {ALERT_TYPES.map((type) => (
                        <option 
                          key={type.value} 
                          value={type.value}
                          disabled={type.proOnly || type.enterpriseOnly}
                        >
                          {type.icon} {type.label}
                          {type.proOnly && ' (PRO)'}
                          {type.enterpriseOnly && ' (ENTERPRISE)'}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Condition */}
                  {(alertType === 'price_above' || alertType === 'price_below') && (
                    <div>
                      <label className="block text-sm font-medium text-[#2F1810] mb-2">
                        Price Threshold
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={priceThreshold}
                        onChange={(e) => setPriceThreshold(e.target.value)}
                        placeholder="0.00"
                        className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                      />
                    </div>
                  )}

                  {/* Create Button */}
                  <motion.button
                    onClick={handleCreateAlert}
                    disabled={creating || !symbol.trim() || !priceThreshold}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="w-full px-6 py-3 rounded-lg bg-[#8B7355] text-white font-bold hover:bg-[#6F5D47] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {creating ? 'Creating...' : 'Create Alert'}
                  </motion.button>
                </div>
              )}

              {/* Alert Types Info */}
              <div className="mt-6 pt-6 border-t border-[#E5E5E5]">
                <h3 className="text-sm font-semibold text-[#2F1810] mb-3">Alert Types</h3>
                <div className="space-y-2">
                  {ALERT_TYPES.map((type) => (
                    <div key={type.value} className="flex items-start gap-2 text-sm">
                      <span>{type.icon}</span>
                      <div className="flex-1">
                        <div className="font-medium text-[#2F1810]">
                          {type.label}
                          {type.proOnly && <span className="ml-1 text-xs text-blue-600">(PRO)</span>}
                          {type.enterpriseOnly && <span className="ml-1 text-xs text-purple-600">(ENTERPRISE)</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Active Alerts List */}
          <div className="lg:col-span-2">
            {loading ? (
              <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
                <motion.div
                  className="w-16 h-16 mx-auto mb-4 border-4 border-[#8B7355] border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                />
                <p className="text-[#6B5D52]">Loading alerts...</p>
              </div>
            ) : activeAlerts.length > 0 ? (
              <div className="bg-white rounded-lg border border-[#E5E5E5]">
                <div className="p-6 border-b border-[#E5E5E5]">
                  <h3 className="text-xl font-bold text-[#2F1810]">Active Alerts</h3>
                </div>
                <div className="divide-y divide-[#E5E5E5]">
                  {activeAlerts.map((alert, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      className="p-5 hover:bg-[#FAFAF9] transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-[#8B7355] to-[#6F5D47] rounded-lg flex items-center justify-center text-white font-bold text-sm">
                            {alert.symbol ? alert.symbol.charAt(0) : 'A'}
                          </div>
                          <div>
                            <div className="font-semibold text-[#2F1810] text-lg">{alert.symbol}</div>
                            <div className="text-sm text-[#6B5D52] mt-1">{alert.type}</div>
                            {alert.message && (
                              <div className="text-[#4A3F35] mt-2">{alert.message}</div>
                            )}
                            <div className="text-xs text-[#9CA3AF] mt-2">
                              {alert.timestamp && new Date(alert.timestamp).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        {alert.priority === 'high' && (
                          <div className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
                            High Priority
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg p-12 border border-[#E5E5E5] text-center">
                <div className="text-6xl mb-4">🔔</div>
                <h3 className="text-xl font-bold text-[#2F1810] mb-2">
                  No Active Alerts
                </h3>
                <p className="text-[#6B5D52] mb-6">
                  Create your first alert to start monitoring the markets 24/7
                </p>
                <motion.button
                  onClick={() => setShowCreateForm(true)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-3 bg-[#8B7355] text-white rounded-lg font-medium hover:bg-[#6F5D47] transition-colors"
                >
                  Create Your First Alert
                </motion.button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

