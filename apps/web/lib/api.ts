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

/**
 * Get list of backtest strategy templates
 */
export async function getBacktestTemplates() {
  const response = await fetch(`${API_BASE_URL}/backtest/templates`)
  
  if (!response.ok) {
    throw new Error('Failed to get backtest templates')
  }
  
  return response.json()
}

/**
 * Get specific backtest strategy template
 */
export async function getBacktestTemplate(templateId: string) {
  const response = await fetch(`${API_BASE_URL}/backtest/templates/${templateId}`)
  
  if (!response.ok) {
    throw new Error('Failed to get backtest template')
  }
  
  return response.json()
}

/**
 * Run a backtest with custom parameters
 */
export async function runBacktestDetailed(params: {
  symbol: string
  strategy_definition?: any
  strategy_template_id?: string
  start_date?: string
  end_date?: string
  initial_capital?: number
}) {
  // Build query string from parameters
  const queryParams = new URLSearchParams()
  queryParams.append('symbol', params.symbol)
  
  if (params.strategy_template_id) {
    queryParams.append('strategy_template_id', params.strategy_template_id)
  }
  if (params.start_date) {
    queryParams.append('start_date', params.start_date)
  }
  if (params.end_date) {
    queryParams.append('end_date', params.end_date)
  }
  if (params.initial_capital) {
    queryParams.append('initial_capital', params.initial_capital.toString())
  }
  
  const response = await fetch(`${API_BASE_URL}/backtest/run?${queryParams.toString()}`, {
    method: 'POST',
  })
  
  if (!response.ok) {
    throw new Error('Failed to run backtest')
  }
  
  return response.json()
}

/**
 * Check user alerts
 */
export async function checkAlerts(userId: string) {
  const response = await fetch(`${API_BASE_URL}/alerts/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to check alerts')
  }
  
  return response.json()
}

/**
 * Create a new alert rule
 */
export async function createAlert(params: {
  user_id: string
  symbol: string
  alert_type: string
  condition: any
}) {
  const response = await fetch(`${API_BASE_URL}/alerts/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  
  if (!response.ok) {
    throw new Error('Failed to create alert')
  }
  
  return response.json()
}

/**
 * Analyze a long document
 */
export async function analyzeLongDocument(params: {
  text: string
  document_type: string
  user_id: string
  ticker?: string
}) {
  const response = await fetch(`${API_BASE_URL}/analysis/long-context`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  
  if (!response.ok) {
    throw new Error('Failed to analyze document')
  }
  
  return response.json()
}

/**
 * Auto-fetch and analyze financial documents
 */
export async function autoFetchAndAnalyze(params: {
  ticker: string
  user_id: string
  include_earnings_call?: boolean
}) {
  const response = await fetch(`${API_BASE_URL}/analysis/long-context/auto-fetch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  
  if (!response.ok) {
    throw new Error('Failed to auto-fetch and analyze')
  }
  
  return response.json()
}

/**
 * Get explanation of a trading concept
 */
export async function explainConcept(params: {
  topic: string
  user_id: string
  level_override?: string
  category?: string
}) {
  const response = await fetch(`${API_BASE_URL}/explain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  
  if (!response.ok) {
    throw new Error('Failed to explain concept')
  }
  
  return response.json()
}

/**
 * Execute a recommendation (create position)
 */
export async function executeRecommendation(params: {
  user_id: string
  recommendation_id: string
  fill_price: number
  quantity: number
  notes?: string
}) {
  const response = await fetch(`${API_BASE_URL}/portfolio/execute-recommendation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  
  if (!response.ok) {
    throw new Error('Failed to execute recommendation')
  }
  
  return response.json()
}

/**
 * Close a position
 */
export async function closePosition(params: {
  position_id: string
  close_price: number
  notes?: string
}) {
  const response = await fetch(`${API_BASE_URL}/portfolio/close-position`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  
  if (!response.ok) {
    throw new Error('Failed to close position')
  }
  
  return response.json()
}

/**
 * Get market hours for an exchange
 */
export async function getMarketHours(exchange: string) {
  const response = await fetch(`${API_BASE_URL}/utils/market-hours/${exchange}`)
  
  if (!response.ok) {
    throw new Error('Failed to get market hours')
  }
  
  return response.json()
}

/**
 * Get list of currently active markets
 */
export async function getActiveMarkets() {
  const response = await fetch(`${API_BASE_URL}/utils/active-markets`)
  
  if (!response.ok) {
    throw new Error('Failed to get active markets')
  }
  
  return response.json()
}

