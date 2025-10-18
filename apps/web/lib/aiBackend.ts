/**
 * AI Backend Integration
 * Connects frontend to the AI backend (FastAPI) running on port 8000
 */

const AI_API = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000'

export interface BackendBriefResponse {
  type: 'morning' | 'eod'
  text: string
  audio_base64: string | null
  symbols_analyzed: string[]
  sentiment_summary?: {
    average_sentiment: number
    bullish_count: number
    bearish_count: number
    trending_count: number
  }
  performance_summary?: {
    gainers: number
    losers: number
    average_change: number
    sentiment_improved: number
    sentiment_declined: number
  }
  generated_at: string
}

export interface FrontendBrief {
  id: string
  type: 'morning' | 'eod'
  date: string
  content: {
    summary: string
    market_overview: string
    key_points: string[]
    recommendations?: string[]
    portfolio_summary?: {
      total_value: string
      daily_pnl: string
      positions: number
    }
  }
}

/**
 * Parse backend brief text into structured format
 */
function parseBriefText(text: string, type: 'morning' | 'eod'): FrontendBrief['content'] {
  // Split by double newlines to get paragraphs
  const paragraphs = text.split('\n\n').map(p => p.trim()).filter(p => p.length > 0)
  
  // Extract summary (first paragraph after greeting)
  const summary = paragraphs[0] || text.substring(0, 200)
  
  // Extract market overview (second paragraph usually)
  const market_overview = paragraphs[1] || ''
  
  // Extract key points (look for bullet points or numbered items)
  const key_points: string[] = []
  const bulletRegex = /^[•\-\*]\s+(.+)$/gm
  let match
  while ((match = bulletRegex.exec(text)) !== null) {
    key_points.push(match[1].trim())
  }
  
  // If no bullet points found, extract sentences as key points
  if (key_points.length === 0) {
    paragraphs.slice(2, 5).forEach(p => {
      if (p.length > 20 && p.length < 300) {
        key_points.push(p)
      }
    })
  }
  
  // Extract recommendations for morning briefs
  const recommendations: string[] = []
  if (type === 'morning') {
    const recRegex = /(?:buy|sell|hold|entry|target)[\s:]+([^\n]+)/gi
    while ((match = recRegex.exec(text)) !== null) {
      recommendations.push(match[0].trim())
    }
  }
  
  return {
    summary,
    market_overview,
    key_points: key_points.slice(0, 5), // Max 5 key points
    recommendations: recommendations.length > 0 ? recommendations.slice(0, 3) : undefined
  }
}

/**
 * Transform backend response to frontend format
 */
function transformBriefResponse(backend: BackendBriefResponse): FrontendBrief {
  const content = parseBriefText(backend.text, backend.type)
  
  // Add performance summary for EOD briefs
  if (backend.type === 'eod' && backend.performance_summary) {
    content.portfolio_summary = {
      total_value: '$0', // TODO: Get from user portfolio
      daily_pnl: `${backend.performance_summary.average_change > 0 ? '+' : ''}${backend.performance_summary.average_change.toFixed(2)}%`,
      positions: backend.performance_summary.gainers + backend.performance_summary.losers
    }
  }
  
  return {
    id: backend.generated_at,
    type: backend.type,
    date: new Date(backend.generated_at).toISOString().split('T')[0],
    content
  }
}

/**
 * Fetch morning brief from AI backend
 */
export async function getMorningBrief(
  userId: string,
  watchlist: string[] = ['MSFT', 'AAPL', 'NVDA'],
  market: string = 'US'
): Promise<FrontendBrief> {
  console.log('📡 [aiBackend] Calling getMorningBrief')
  console.log('  API URL:', AI_API)
  console.log('  Payload:', { watchlist, market, user_id: userId, include_voice: false })
  
  try {
    const response = await fetch(`${AI_API}/briefs/morning`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        watchlist,
        market,
        user_id: userId,
        include_voice: false
      }),
      // 60 second timeout for brief generation
      signal: AbortSignal.timeout(60000)
    })
    
    console.log('📡 [aiBackend] Morning brief response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ [aiBackend] Morning brief failed:', errorText)
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data: BackendBriefResponse = await response.json()
    console.log('✅ [aiBackend] Morning brief received:', {
      type: data.type,
      symbols_analyzed: data.symbols_analyzed,
      text_length: data.text.length,
      generated_at: data.generated_at
    })
    
    const transformed = transformBriefResponse(data)
    console.log('✅ [aiBackend] Morning brief transformed successfully')
    return transformed
    
  } catch (error) {
    console.error('❌ [aiBackend] Failed to fetch morning brief:', error)
    throw error
  }
}

/**
 * Fetch EOD brief from AI backend
 */
export async function getEODBrief(
  userId: string,
  watchlist: string[] = ['MSFT', 'AAPL', 'NVDA'],
  market: string = 'US'
): Promise<FrontendBrief> {
  console.log('📡 [aiBackend] Calling getEODBrief')
  console.log('  API URL:', AI_API)
  console.log('  Payload:', { watchlist, market, user_id: userId, include_voice: false })
  
  try {
    const response = await fetch(`${AI_API}/briefs/eod`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        watchlist,
        market,
        user_id: userId,
        include_voice: false
      }),
      signal: AbortSignal.timeout(60000)
    })
    
    console.log('📡 [aiBackend] EOD brief response status:', response.status)
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error('❌ [aiBackend] EOD brief failed:', errorText)
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data: BackendBriefResponse = await response.json()
    console.log('✅ [aiBackend] EOD brief received:', {
      type: data.type,
      symbols_analyzed: data.symbols_analyzed,
      text_length: data.text.length,
      generated_at: data.generated_at
    })
    
    const transformed = transformBriefResponse(data)
    console.log('✅ [aiBackend] EOD brief transformed successfully')
    return transformed
    
  } catch (error) {
    console.error('❌ [aiBackend] Failed to fetch EOD brief:', error)
    throw error
  }
}

/**
 * Fetch both morning and EOD briefs
 */
export async function getAllBriefs(
  userId: string,
  watchlist: string[] = ['DBS', 'OCBC', 'UOB'],
  market: string = 'SGX'
): Promise<{
  morning: FrontendBrief | null
  eod: FrontendBrief | null
}> {
  try {
    const [morning, eod] = await Promise.allSettled([
      getMorningBrief(userId, watchlist, market),
      getEODBrief(userId, watchlist, market)
    ])
    
    return {
      morning: morning.status === 'fulfilled' ? morning.value : null,
      eod: eod.status === 'fulfilled' ? eod.value : null
    }
  } catch (error) {
    console.error('Failed to fetch briefs:', error)
    return { morning: null, eod: null }
  }
}

/**
 * Get user's watchlist from localStorage or defaults
 */
export function getUserWatchlist(): string[] {
  if (typeof window === 'undefined') return ['DBS', 'OCBC', 'UOB']
  
  const stored = localStorage.getItem('watchlist')
  if (stored) {
    try {
      return JSON.parse(stored)
    } catch {
      return ['DBS', 'OCBC', 'UOB']
    }
  }
  return ['DBS', 'OCBC', 'UOB']
}

/**
 * Save user's watchlist to localStorage
 */
export function saveUserWatchlist(watchlist: string[]): void {
  if (typeof window === 'undefined') return
  localStorage.setItem('watchlist', JSON.stringify(watchlist))
}

