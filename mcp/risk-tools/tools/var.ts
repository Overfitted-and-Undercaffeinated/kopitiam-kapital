/**
 * Calculate Value at Risk (VaR)
 */

export function calculateVaR1d95(returns: number[]): number {
  // TODO: Implement 1-day 95% VaR calculation
  // Sort returns and find the 5th percentile
  if (returns.length === 0) {
    return 0;
  }
  
  const sorted = [...returns].sort((a, b) => a - b);
  const index = Math.floor(returns.length * 0.05);
  
  return sorted[index];
}

