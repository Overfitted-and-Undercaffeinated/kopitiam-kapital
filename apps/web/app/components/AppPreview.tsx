'use client'

import { motion } from 'framer-motion'

interface AppPreviewProps {
  activeSection: 'morning' | 'dashboard' | 'eod'
}

export default function AppPreview({ activeSection }: AppPreviewProps) {
  return (
    <div className="relative w-full h-full bg-white rounded-3xl overflow-hidden shadow-2xl">
      {/* Morning Brief Preview */}
      <motion.div
        className="absolute inset-0"
        animate={{
          opacity: activeSection === 'morning' ? 1 : 0,
          zIndex: activeSection === 'morning' ? 10 : 0,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <div className="p-8 h-full overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#FFD700] to-[#FFA500] rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-[#2F1810]">Morning Brief</h3>
            </div>
            <div className="text-sm font-semibold text-[#8B4513] bg-[#FFE4B5] px-3 py-1 rounded-full">7:00 AM</div>
          </div>
          
          <div className="space-y-4">
            <div className="p-5 bg-gradient-to-r from-[#FFE4B5] to-[#F5DEB3] rounded-xl shadow-md">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-[#D2691E]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <h4 className="font-bold text-[#2F1810]">Market Outlook</h4>
              </div>
              <p className="text-sm text-[#5D3A1A] mb-2">STI +0.8% | Bullish sentiment ahead of Fed decision</p>
              <div className="h-2 bg-[#D2691E] rounded-full w-3/4 mb-2"></div>
              <div className="h-2 bg-[#CD853F] rounded-full w-1/2"></div>
            </div>
            
            <div className="p-5 bg-gradient-to-r from-[#DEB887] to-[#D2B48C] rounded-xl shadow-md">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-[#A0522D]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
                <h4 className="font-bold text-[#2F1810]">Top News</h4>
              </div>
              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-[#A0522D] rounded-full mt-2"></div>
                  <div className="flex-1">
                    <div className="h-2 bg-[#A0522D] rounded-full w-full mb-1"></div>
                    <div className="h-2 bg-[#A0522D] rounded-full w-3/4"></div>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 bg-[#A0522D] rounded-full mt-2"></div>
                  <div className="flex-1">
                    <div className="h-2 bg-[#A0522D] rounded-full w-5/6 mb-1"></div>
                    <div className="h-2 bg-[#A0522D] rounded-full w-2/3"></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-5 bg-gradient-to-r from-[#F4A460] to-[#DEB887] rounded-xl shadow-md">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-[#8B4513]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <h4 className="font-bold text-[#2F1810]">AI Insights</h4>
              </div>
              <p className="text-sm text-[#5D3A1A] mb-2">3 opportunities detected in your watchlist</p>
              <div className="h-2 bg-[#8B4513] rounded-full w-4/5 mb-2"></div>
              <div className="h-2 bg-[#8B4513] rounded-full w-3/5"></div>
            </div>

            <div className="p-5 bg-gradient-to-r from-[#CD853F] to-[#DEB887] rounded-xl shadow-md">
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-[#5D3A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <h4 className="font-bold text-[#2F1810]">Risk Alerts</h4>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-[#5D3A1A]">Portfolio at 65% capacity</span>
                <span className="text-green-600 font-bold">✓ Safe</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Dashboard Preview */}
      <motion.div
        className="absolute inset-0"
        animate={{
          opacity: activeSection === 'dashboard' ? 1 : 0,
          zIndex: activeSection === 'dashboard' ? 10 : 0,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <div className="p-8 h-full overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#CD853F] to-[#A0522D] rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-[#2F1810]">Live Dashboard</h3>
            </div>
            <div className="flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold text-green-700">Live</span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-xl shadow-md">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-[#5D3A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="text-xs font-semibold text-[#5D3A1A]">Portfolio Value</div>
              </div>
              <div className="text-3xl font-bold text-[#2F1810]">$50,432</div>
              <div className="text-sm text-green-600 font-bold mt-1">+2.4% Today</div>
            </div>
            <div className="p-4 bg-gradient-to-br from-[#D2691E] to-[#F4A460] rounded-xl shadow-md">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-[#5D3A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <div className="text-xs font-semibold text-[#5D3A1A]">Daily P&L</div>
              </div>
              <div className="text-3xl font-bold text-[#2F1810]">+$1,234</div>
              <div className="text-sm text-green-600 font-bold mt-1">+5 positions</div>
            </div>
          </div>
          
          <div className="p-5 bg-gradient-to-r from-[#FFE4B5] to-[#F5DEB3] rounded-xl mb-4 shadow-md">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-[#D2691E]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
                <h4 className="font-bold text-[#2F1810]">Performance Chart</h4>
              </div>
              <span className="text-xs text-green-600 font-bold">↑ 12.5%</span>
            </div>
            <svg className="w-full h-32" viewBox="0 0 400 100">
              <polyline
                points="0,80 50,70 100,85 150,60 200,65 250,45 300,50 350,30 400,40"
                fill="none"
                stroke="#D2691E"
                strokeWidth="3"
              />
              <polyline
                points="0,80 50,70 100,85 150,60 200,65 250,45 300,50 350,30 400,40 400,100 0,100"
                fill="url(#gradient)"
                opacity="0.3"
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#D2691E" />
                  <stop offset="100%" stopColor="transparent" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-[#5D3A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-xs font-semibold text-[#5D3A1A]">Active</span>
              </div>
              <div className="text-2xl font-bold text-[#2F1810]">8</div>
              <div className="text-xs text-[#5D3A1A]">Positions</div>
            </div>
            <div className="p-4 bg-gradient-to-br from-[#F4A460] to-[#DEB887] rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-[#5D3A1A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="text-xs font-semibold text-[#5D3A1A]">Alerts</span>
              </div>
              <div className="text-2xl font-bold text-[#2F1810]">3</div>
              <div className="text-xs text-orange-600 font-bold">New</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* EOD Report Preview */}
      <motion.div
        className="absolute inset-0"
        animate={{
          opacity: activeSection === 'eod' ? 1 : 0,
          zIndex: activeSection === 'eod' ? 10 : 0,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
      >
        <div className="p-8 h-full">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-[#2F1810]">EOD Report</h3>
            <div className="text-sm text-[#8B4513]">5:00 PM</div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gradient-to-r from-[#B8860B] to-[#DAA520] rounded-xl">
              <h4 className="font-bold text-[#2F1810] mb-2">Daily Summary</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-[#5D3A1A]">Total Gain</div>
                  <div className="text-xl font-bold text-green-600">+$1,234</div>
                </div>
                <div>
                  <div className="text-xs text-[#5D3A1A]">Win Rate</div>
                  <div className="text-xl font-bold text-[#2F1810]">75%</div>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-gradient-to-r from-[#CD853F] to-[#DEB887] rounded-xl">
              <h4 className="font-bold text-[#2F1810] mb-2">Best Performers</h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-[#5D3A1A]">DBS</span>
                  <span className="text-green-600 font-bold">+5.2%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[#5D3A1A]">OCBC</span>
                  <span className="text-green-600 font-bold">+3.8%</span>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-gradient-to-r from-[#D2691E] to-[#F4A460] rounded-xl">
              <h4 className="font-bold text-[#2F1810] mb-2">Tomorrow's Plan</h4>
              <div className="h-2 bg-[#8B4513] rounded-full w-4/5 mb-2"></div>
              <div className="h-2 bg-[#8B4513] rounded-full w-3/5 mb-2"></div>
              <div className="h-2 bg-[#8B4513] rounded-full w-2/3"></div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

