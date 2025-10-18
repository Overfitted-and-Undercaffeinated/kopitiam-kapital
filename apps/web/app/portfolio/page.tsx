'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { closePosition } from '@/lib/api'

// Mock portfolio data - in production this would come from the backend
const mockPositions = [
  { 
    id: '1',
    symbol: 'DBS', 
    name: 'DBS Group Holdings', 
    qty: 100, 
    entry: 35.2, 
    current: 35.73, 
    stop: 34.5,
    target: 37.0,
    pnl: 53,
    pnl_pct: 1.51
  },
  { 
    id: '2',
    symbol: '9CI', 
    name: 'CapitaLand Investment', 
    qty: 500, 
    entry: 3.15, 
    current: 3.21, 
    stop: 3.05,
    target: 3.35,
    pnl: 30,
    pnl_pct: 1.90
  },
  { 
    id: '3',
    symbol: 'O39', 
    name: 'OCBC Bank', 
    qty: 150, 
    entry: 13.5, 
    current: 13.68, 
    stop: 13.2,
    target: 14.2,
    pnl: 27,
    pnl_pct: 1.33
  },
  { 
    id: '4',
    symbol: 'U11', 
    name: 'UOB', 
    qty: 80, 
    entry: 30.8, 
    current: 31.15, 
    stop: 30.0,
    target: 32.5,
    pnl: 28,
    pnl_pct: 1.14
  },
]

export default function PortfolioPage() {
  const [positions] = useState(mockPositions)
  const [selectedPosition, setSelectedPosition] = useState<any>(null)
  const [showCloseModal, setShowCloseModal] = useState(false)
  const [closePrice, setClosePrice] = useState('')
  const [notes, setNotes] = useState('')
  const [closing, setClosing] = useState(false)

  const totalValue = positions.reduce((sum, pos) => sum + (pos.current * pos.qty), 0)
  const totalPnL = positions.reduce((sum, pos) => sum + pos.pnl, 0)
  const totalPnLPct = (totalPnL / (totalValue - totalPnL)) * 100

  const handleClosePosition = async () => {
    if (!selectedPosition || !closePrice) return

    setClosing(true)
    
    try {
      await closePosition({
        position_id: selectedPosition.id,
        close_price: parseFloat(closePrice),
        notes: notes || undefined
      })
      
      // Reset and close modal
      setShowCloseModal(false)
      setSelectedPosition(null)
      setClosePrice('')
      setNotes('')
      
      // In production, refresh positions from backend
      alert('Position closed successfully!')
    } catch (err) {
      alert('Failed to close position: ' + (err instanceof Error ? err.message : 'Unknown error'))
    } finally {
      setClosing(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9]" style={{ fontFamily: 'var(--font-body)' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b border-[#E5E5E5]">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#2F1810]">
                Portfolio Management
              </h1>
              <p className="text-sm text-[#6B5D52] mt-0.5">
                Track and manage your positions
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
        {/* Portfolio Summary */}
        <div className="bg-gradient-to-br from-[#8B7355] to-[#6F5D47] rounded-lg p-6 border border-[#6F5D47] text-white mb-6">
          <h2 className="text-xl font-bold mb-4">Portfolio Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="text-sm opacity-90 mb-1">Total Value</div>
              <div className="text-3xl font-bold">
                {formatCurrency(totalValue)}
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="text-sm opacity-90 mb-1">Total P&L</div>
              <div className={`text-3xl font-bold ${totalPnL >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                {totalPnL >= 0 ? '+' : ''}{formatCurrency(totalPnL)}
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="text-sm opacity-90 mb-1">P&L %</div>
              <div className={`text-3xl font-bold ${totalPnLPct >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                {totalPnLPct >= 0 ? '+' : ''}{totalPnLPct.toFixed(2)}%
              </div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
              <div className="text-sm opacity-90 mb-1">Open Positions</div>
              <div className="text-3xl font-bold">
                {positions.length}
              </div>
            </div>
          </div>
        </div>

        {/* Positions Table */}
        <div className="bg-white rounded-lg border border-[#E5E5E5]">
          <div className="p-6 border-b border-[#E5E5E5]">
            <h3 className="text-xl font-bold text-[#2F1810]">Active Positions</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-[#FAFAF9]">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-[#2F1810]">Symbol</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-[#2F1810]">Qty</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-[#2F1810]">Entry</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-[#2F1810]">Current</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-[#2F1810]">Stop</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-[#2F1810]">Target</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-[#2F1810]">P&L</th>
                  <th className="px-6 py-3 text-center text-sm font-semibold text-[#2F1810]">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E5E5]">
                {positions.map((position, idx) => (
                  <motion.tr
                    key={position.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="hover:bg-[#FAFAF9] transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-semibold text-[#2F1810]">{position.symbol}</div>
                        <div className="text-sm text-[#6B5D52]">{position.name}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-[#2F1810]">{position.qty}</td>
                    <td className="px-6 py-4 text-right text-[#2F1810]">
                      {formatCurrency(position.entry)}
                    </td>
                    <td className="px-6 py-4 text-right text-[#2F1810] font-semibold">
                      {formatCurrency(position.current)}
                    </td>
                    <td className="px-6 py-4 text-right text-red-600">
                      {formatCurrency(position.stop)}
                    </td>
                    <td className="px-6 py-4 text-right text-green-600">
                      {formatCurrency(position.target)}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className={`font-semibold ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.pnl >= 0 ? '+' : ''}{formatCurrency(position.pnl)}
                      </div>
                      <div className={`text-sm ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {position.pnl_pct >= 0 ? '+' : ''}{position.pnl_pct.toFixed(2)}%
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <motion.button
                        onClick={() => {
                          setSelectedPosition(position)
                          setClosePrice(position.current.toString())
                          setShowCloseModal(true)
                        }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded-lg text-sm font-medium hover:bg-red-200 transition-colors"
                      >
                        Close
                      </motion.button>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Note */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">
            <strong>Note:</strong> This is a demo portfolio. In production, positions would sync from your broker via API.
          </p>
        </div>
      </div>

      {/* Close Position Modal */}
      {showCloseModal && selectedPosition && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
          >
            <h3 className="text-xl font-bold text-[#2F1810] mb-4">
              Close Position: {selectedPosition.symbol}
            </h3>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  Close Price
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={closePrice}
                  onChange={(e) => setClosePrice(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-[#2F1810] mb-2">
                  Notes (Optional)
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="Add any notes about this trade..."
                  className="w-full px-4 py-2 rounded-lg border border-[#E5E5E5] bg-white text-[#2F1810] focus:outline-none focus:border-[#8B7355] focus:ring-2 focus:ring-[#8B7355]/20 resize-none"
                />
              </div>

              {closePrice && (
                <div className="p-3 bg-[#FAFAF9] rounded-lg">
                  <div className="text-sm text-[#6B5D52] mb-1">Estimated P&L</div>
                  <div className={`text-2xl font-bold ${
                    (parseFloat(closePrice) - selectedPosition.entry) * selectedPosition.qty >= 0
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}>
                    {formatCurrency((parseFloat(closePrice) - selectedPosition.entry) * selectedPosition.qty)}
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowCloseModal(false)
                  setSelectedPosition(null)
                  setClosePrice('')
                  setNotes('')
                }}
                className="flex-1 px-6 py-3 rounded-lg bg-[#FAFAF9] text-[#2F1810] font-bold hover:bg-[#F5F5F4] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleClosePosition}
                disabled={closing || !closePrice}
                className="flex-1 px-6 py-3 rounded-lg bg-red-600 text-white font-bold hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {closing ? 'Closing...' : 'Close Position'}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}

