/**
 * API client for Kopitiam Capital AI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function generateRecommendation(userId: string, symbol?: string) {
  const response = await fetch(`${API_BASE_URL}/ai/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, symbol }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to generate recommendation')
  }
  
  return response.json()
}

export async function getMorningBrief(userId: string) {
  const response = await fetch(`${API_BASE_URL}/ai/morning`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to get morning brief')
  }
  
  return response.json()
}

export async function getEODReport(userId: string) {
  const response = await fetch(`${API_BASE_URL}/ai/eod`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to get EOD report')
  }
  
  return response.json()
}

export async function analyzeFiling(ticker: string, filingType: string) {
  const response = await fetch(`${API_BASE_URL}/ai/longctx`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ticker, filing_type: filingType }),
  })
  
  if (!response.ok) {
    throw new Error('Failed to analyze filing')
  }
  
  return response.json()
}

