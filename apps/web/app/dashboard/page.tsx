'use client'

import { useState, useEffect } from 'react'

// Check if market is closed (SGX closes at 5pm SGT)
function isMarketClosed() {
  const now = new Date()
  const hours = now.getHours()
  return hours >= 17 || hours < 9 // After 5pm or before 9am
}

export default function Dashboard() {
  const [showEOD, setShowEOD] = useState(false)

  useEffect(() => {
    setShowEOD(isMarketClosed())
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="container mx-auto px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Kopitiam Capital</h1>
          <p className="text-gray-600">Your AI-powered trading companion</p>
        </div>
      </header>

      <div className="container mx-auto p-8 space-y-8">
        {/* Morning Brief */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">📰 Morning Brief</h2>
          <p className="text-gray-600">Market overview and news summary</p>
          <div className="mt-4 space-y-2">
            <div className="p-4 bg-blue-50 rounded">
              <h3 className="font-semibold">Market Outlook</h3>
              <p className="text-sm text-gray-600">AI analysis will appear here</p>
            </div>
          </div>
        </section>

        {/* Portfolio Dashboard */}
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-6">📊 Portfolio Dashboard</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Portfolio Value</h3>
              <p className="text-3xl font-bold">$0.00</p>
            </div>
            <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Today's P&L</h3>
              <p className="text-3xl font-bold text-green-600">+$0.00</p>
            </div>
            <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Open Positions</h3>
              <p className="text-3xl font-bold">0</p>
            </div>
          </div>
          
          {/* Trading Ideas */}
          <div className="mt-6">
            <h3 className="text-xl font-semibold mb-4">💡 Trading Ideas</h3>
            <p className="text-gray-600">AI-generated trading ideas will appear here</p>
          </div>
        </section>

        {/* EOD Report - Only shows after market close */}
        {showEOD && (
          <section className="bg-white rounded-lg shadow p-6 border-2 border-blue-500">
            <h2 className="text-2xl font-bold mb-4">🌙 End-of-Day Report</h2>
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded">
                <h3 className="font-semibold mb-2">Market Summary</h3>
                <p className="text-sm text-gray-600">
                  Daily market analysis and performance summary
                </p>
              </div>
              
              <div className="p-4 bg-green-50 rounded">
                <h3 className="font-semibold mb-2">Portfolio Performance</h3>
                <p className="text-sm text-gray-600">
                  Your positions and performance review
                </p>
              </div>
              
              <div className="p-4 bg-purple-50 rounded">
                <h3 className="font-semibold mb-2">Tomorrow's Watch List</h3>
                <p className="text-sm text-gray-600">
                  AI-recommended stocks to watch tomorrow
                </p>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}
