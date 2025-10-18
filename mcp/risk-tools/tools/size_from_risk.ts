/**
 * Calculate position size from risk parameters
 */

export interface PositionSizeParams {
  nav: number;
  entry: number;
  stop: number;
  risk_pct: number;
}

export function calculatePositionSize(params: PositionSizeParams): number {
  const { nav, entry, stop, risk_pct } = params;
  
  const riskAmount = nav * (risk_pct / 100);
  const priceRisk = Math.abs(entry - stop);
  
  if (priceRisk === 0) {
    return 0;
  }
  
  const positionSize = riskAmount / priceRisk;
  return positionSize;
}

