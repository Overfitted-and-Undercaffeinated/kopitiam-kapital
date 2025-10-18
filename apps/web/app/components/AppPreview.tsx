'use client'

import { motion } from 'framer-motion'

interface AppPreviewProps {
  activeSection: 'morning' | 'dashboard' | 'eod'
}

export default function AppPreview({ activeSection }: AppPreviewProps) {
  return (
    <div className="relative w-full h-full max-w-4xl mx-auto" style={{ perspective: '2000px' }}>
      {/* Morning Brief Preview */}
      <motion.div
        className="absolute inset-0 bg-white rounded-3xl shadow-[0_20px_80px_rgba(0,0,0,0.3)] overflow-hidden border-4 border-[#8B4513]"
        initial={{ opacity: 0, scale: 0.8, rotateY: -25, x: -100 }}
        animate={{
          opacity: activeSection === 'morning' ? 1 : 0,
          scale: activeSection === 'morning' ? 1 : 0.8,
          rotateY: activeSection === 'morning' ? 0 : -25,
          x: activeSection === 'morning' ? 0 : -100,
          zIndex: activeSection === 'morning' ? 10 : 0,
        }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div className="p-8 h-full">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-[#2F1810]">Morning Brief</h3>
            <div className="text-sm text-[#8B4513]">7:00 AM</div>
          </div>
          
          <div className="space-y-4">
            <div className="p-4 bg-gradient-to-r from-[#FFE4B5] to-[#F5DEB3] rounded-xl">
              <h4 className="font-bold text-[#2F1810] mb-2">Market Outlook</h4>
              <div className="h-2 bg-[#D2691E] rounded-full w-3/4 mb-2"></div>
              <div className="h-2 bg-[#CD853F] rounded-full w-1/2"></div>
            </div>
            
            <div className="p-4 bg-gradient-to-r from-[#DEB887] to-[#D2B48C] rounded-xl">
              <h4 className="font-bold text-[#2F1810] mb-2">Top News</h4>
              <div className="space-y-2">
                <div className="h-2 bg-[#A0522D] rounded-full w-full"></div>
                <div className="h-2 bg-[#A0522D] rounded-full w-5/6"></div>
                <div className="h-2 bg-[#A0522D] rounded-full w-2/3"></div>
              </div>
            </div>
            
            <div className="p-4 bg-gradient-to-r from-[#F4A460] to-[#DEB887] rounded-xl">
              <h4 className="font-bold text-[#2F1810] mb-2">AI Insights</h4>
              <div className="h-2 bg-[#8B4513] rounded-full w-4/5 mb-2"></div>
              <div className="h-2 bg-[#8B4513] rounded-full w-3/5"></div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Dashboard Preview */}
      <motion.div
        className="absolute inset-0 bg-white rounded-3xl shadow-[0_20px_80px_rgba(0,0,0,0.3)] overflow-hidden border-4 border-[#D2691E]"
        initial={{ opacity: 0, scale: 0.8, rotateY: 25, x: 100 }}
        animate={{
          opacity: activeSection === 'dashboard' ? 1 : 0,
          scale: activeSection === 'dashboard' ? 1 : 0.8,
          rotateY: activeSection === 'dashboard' ? 0 : 25,
          x: activeSection === 'dashboard' ? 0 : 100,
          zIndex: activeSection === 'dashboard' ? 10 : 0,
        }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        style={{ transformStyle: 'preserve-3d' }}
      >
        <div className="p-8 h-full">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold text-[#2F1810]">Live Dashboard</h3>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-[#8B4513]">Live</span>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-gradient-to-br from-[#CD853F] to-[#DEB887] rounded-xl">
              <div className="text-xs text-[#5D3A1A] mb-1">Portfolio</div>
              <div className="text-2xl font-bold text-[#2F1810]">$50,432</div>
              <div className="text-xs text-green-600">+2.4%</div>
            </div>
            <div className="p-4 bg-gradient-to-br from-[#D2691E] to-[#F4A460] rounded-xl">
              <div className="text-xs text-[#5D3A1A] mb-1">P&L</div>
              <div className="text-2xl font-bold text-[#2F1810]">+$1,234</div>
              <div className="text-xs text-green-600">Today</div>
            </div>
            <div className="p-4 bg-gradient-to-br from-[#B8860B] to-[#DAA520] rounded-xl">
              <div className="text-xs text-[#5D3A1A] mb-1">Positions</div>
              <div className="text-2xl font-bold text-[#2F1810]">8</div>
              <div className="text-xs text-[#5D3A1A]">Active</div>
            </div>
          </div>
          
          <div className="p-4 bg-gradient-to-r from-[#FFE4B5] to-[#F5DEB3] rounded-xl">
            <h4 className="font-bold text-[#2F1810] mb-3">Chart</h4>
            <svg className="w-full h-32" viewBox="0 0 400 100">
              <polyline
                points="0,80 50,70 100,85 150,60 200,65 250,45 300,50 350,30 400,40"
                fill="none"
                stroke="#D2691E"
                strokeWidth="3"
              />
              <polyline
                points="0,80 50,70 100,85 150,60 200,65 250,45 300,50 350,30 400,40"
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
        </div>
      </motion.div>

      {/* EOD Report Preview */}
      <motion.div
        className="absolute inset-0 bg-white rounded-3xl shadow-[0_20px_80px_rgba(0,0,0,0.3)] overflow-hidden border-4 border-[#B8860B]"
        initial={{ opacity: 0, scale: 0.8, rotateX: 25, y: 100 }}
        animate={{
          opacity: activeSection === 'eod' ? 1 : 0,
          scale: activeSection === 'eod' ? 1 : 0.8,
          rotateX: activeSection === 'eod' ? 0 : 25,
          y: activeSection === 'eod' ? 0 : 100,
          zIndex: activeSection === 'eod' ? 10 : 0,
        }}
        transition={{ duration: 0.7, ease: 'easeOut' }}
        style={{ transformStyle: 'preserve-3d' }}
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

