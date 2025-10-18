/**
 * API client for Kopitiam Capital AI backend
 * 
 * NOTE: For brief endpoints, use @/lib/aiBackend instead
 * This file contains legacy/placeholder endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8000'

/**
 * Generate trading recommendation
 */
export async function generateRecommendation(userId: string, symbol: string) {
  const response = await fetch(`${API_BASE_URL}/ai/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      symbol,
      user_id: userId 
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate recommendation')
  }
  
  return response.json()
}

/**
 * Get sentiment analysis for a symbol
 */
export async function getSentiment(symbol: string, userId?: string) {
  const url = new URL(`${API_BASE_URL}/sentiment/${symbol}`)
  if (userId) {
    url.searchParams.append('user_id', userId)
  }
  
  const response = await fetch(url.toString())
  
  if (!response.ok) {
    throw new Error('Failed to get sentiment')
  }
  
  return response.json()
}

/**
 * Run backtest for a symbol with a strategy
 */
export async function runBacktest(
  symbol: string, 
  strategyTemplateId: string = 'rsi_oversold'
) {
  const response = await fetch(`${API_BASE_URL}/backtest/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      strategy_template_id: strategyTemplateId
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to run backtest')
  }
  
  return response.json()
}

/**
 * Orchestrate AI request (smart endpoint)
 */
export async function orchestrateRequest(
  query: string,
  userId: string
) {
  const response = await fetch(`${API_BASE_URL}/ai/orchestrate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      user_id: userId,
      context: {}
    }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to orchestrate request')
  }
  
  return response.json()
}

