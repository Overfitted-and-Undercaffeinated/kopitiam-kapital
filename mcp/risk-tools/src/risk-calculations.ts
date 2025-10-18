/**
 * Risk calculation functions
 * Pure mathematical implementations for position sizing, VaR, etc.
 */

export interface PositionSizingParams {
  method: 'kelly' | 'fixed_percent' | 'risk_parity';
  capital: number;
  current_price: number;
  stop_loss?: number;
  win_rate?: number;
  avg_win?: number;
  avg_loss?: number;
  risk_percent?: number;
}

export interface VaRParams {
  returns: number[];
  position_value: number;
  confidence_level?: number;
  holding_period_days?: number;
}

export interface RiskRewardParams {
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  win_rate?: number;
  position_size?: number;
}

/**
 * Calculate position size using various methods
 */
export function calculatePositionSize(params: PositionSizingParams): {
  shares: number;
  position_value: number;
  risk_amount: number;
  method: string;
} {
  const { method, capital, current_price, stop_loss, win_rate, avg_win, avg_loss, risk_percent } = params;

  let shares = 0;
  let risk_amount = 0;

  switch (method) {
    case 'kelly':
      if (!win_rate || !avg_win || !avg_loss) {
        throw new Error('Kelly Criterion requires win_rate, avg_win, and avg_loss');
      }
      
      // Kelly Formula: f = (p * b - q) / b
      // where p = win_rate, q = 1 - p, b = avg_win / avg_loss
      const q = 1 - win_rate;
      const b = Math.abs(avg_win) / Math.abs(avg_loss);
      const kelly_fraction = (win_rate * b - q) / b;
      
      // Use half Kelly for safety (common practice)
      const safe_kelly = Math.max(0, Math.min(kelly_fraction * 0.5, 0.25)); // Cap at 25%
      
      const position_value_kelly = capital * safe_kelly;
      shares = Math.floor(position_value_kelly / current_price);
      risk_amount = capital * safe_kelly;
      break;

    case 'fixed_percent':
      if (!risk_percent || !stop_loss) {
        throw new Error('Fixed percent requires risk_percent and stop_loss');
      }
      
      // Risk amount = capital * risk_percent
      risk_amount = capital * risk_percent;
      
      // Position size based on stop loss distance
      const risk_per_share = Math.abs(current_price - stop_loss);
      shares = Math.floor(risk_amount / risk_per_share);
      break;

    case 'risk_parity':
      // Equal risk across positions (simplified version)
      const default_risk = 0.02; // 2% default
      risk_amount = capital * default_risk;
      
      if (stop_loss) {
        const risk_per_share = Math.abs(current_price - stop_loss);
        shares = Math.floor(risk_amount / risk_per_share);
      } else {
        // Use 5% default stop if not specified
        const default_stop_pct = 0.05;
        shares = Math.floor((capital * default_risk) / (current_price * default_stop_pct));
      }
      break;

    default:
      throw new Error(`Unknown method: ${method}`);
  }

  const position_value = shares * current_price;

  return {
    shares: Math.max(1, shares), // At least 1 share
    position_value,
    risk_amount,
    method
  };
}

/**
 * Calculate Value at Risk (VaR)
 */
export function calculateVaR(params: VaRParams): {
  var_amount: number;
  var_percent: number;
  confidence_level: number;
  worst_case_loss: number;
} {
  const { returns, position_value, confidence_level = 0.95, holding_period_days = 1 } = params;

  if (returns.length === 0) {
    throw new Error('Returns array cannot be empty');
  }

  // Sort returns
  const sorted_returns = [...returns].sort((a, b) => a - b);
  
  // Find percentile (VaR is the loss at the confidence level)
  const index = Math.floor((1 - confidence_level) * sorted_returns.length);
  const var_return = sorted_returns[index];
  
  // Scale by holding period (sqrt of time)
  const scaled_return = var_return * Math.sqrt(holding_period_days);
  
  // Calculate VaR amount
  const var_amount = Math.abs(position_value * scaled_return);
  const var_percent = Math.abs(scaled_return);
  
  // Worst case (minimum return in dataset)
  const worst_case_loss = Math.abs(position_value * sorted_returns[0]);

  return {
    var_amount,
    var_percent,
    confidence_level,
    worst_case_loss
  };
}

/**
 * Calculate Sharpe Ratio
 */
export function calculateSharpeRatio(
  returns: number[],
  risk_free_rate: number = 0.04
): number {
  if (returns.length === 0) return 0;

  const mean_return = returns.reduce((a, b) => a + b, 0) / returns.length;
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean_return, 2), 0) / returns.length;
  const std_dev = Math.sqrt(variance);

  if (std_dev === 0) return 0;

  // Annualized Sharpe (assuming daily returns)
  const excess_return = (mean_return * 252) - risk_free_rate;
  const annualized_std = std_dev * Math.sqrt(252);

  return excess_return / annualized_std;
}

/**
 * Calculate Maximum Drawdown
 */
export function calculateMaxDrawdown(equity_curve: number[]): {
  max_drawdown: number;
  max_drawdown_percent: number;
  peak_value: number;
  trough_value: number;
} {
  if (equity_curve.length === 0) {
    return {
      max_drawdown: 0,
      max_drawdown_percent: 0,
      peak_value: 0,
      trough_value: 0
    };
  }

  let max_dd = 0;
  let peak = equity_curve[0];
  let peak_val = peak;
  let trough_val = peak;

  for (const value of equity_curve) {
    if (value > peak) {
      peak = value;
    }
    
    const drawdown = (peak - value) / peak;
    
    if (drawdown > max_dd) {
      max_dd = drawdown;
      peak_val = peak;
      trough_val = value;
    }
  }

  return {
    max_drawdown: peak_val - trough_val,
    max_drawdown_percent: max_dd,
    peak_value: peak_val,
    trough_value: trough_val
  };
}

/**
 * Optimize stop loss based on ATR
 */
export function optimizeStopLoss(params: {
  entry_price: number;
  atr: number;
  risk_tolerance?: 'conservative' | 'moderate' | 'aggressive';
  direction?: 'BUY' | 'SELL';
}): {
  stop_loss: number;
  atr_multiplier: number;
  distance_percent: number;
} {
  const { entry_price, atr, risk_tolerance = 'moderate', direction = 'BUY' } = params;

  // ATR multipliers by risk tolerance
  const multipliers = {
    conservative: 3.0,  // 3x ATR (wider stop)
    moderate: 2.0,      // 2x ATR (standard)
    aggressive: 1.5     // 1.5x ATR (tighter stop)
  };

  const multiplier = multipliers[risk_tolerance];
  const stop_distance = atr * multiplier;

  let stop_loss: number;
  if (direction === 'BUY') {
    stop_loss = entry_price - stop_distance;
  } else {
    stop_loss = entry_price + stop_distance;
  }

  const distance_percent = Math.abs(stop_distance / entry_price);

  return {
    stop_loss: parseFloat(stop_loss.toFixed(2)),
    atr_multiplier: multiplier,
    distance_percent: parseFloat(distance_percent.toFixed(4))
  };
}

/**
 * Calculate risk/reward ratio and expected value
 */
export function calculateRiskReward(params: RiskRewardParams): {
  risk_reward_ratio: number;
  risk_amount: number;
  reward_amount: number;
  expected_value: number;
  recommendation: string;
} {
  const { entry_price, stop_loss, take_profit, win_rate = 0.5, position_size = 1 } = params;

  const risk_per_share = Math.abs(entry_price - stop_loss);
  const reward_per_share = Math.abs(take_profit - entry_price);

  const risk_amount = risk_per_share * position_size;
  const reward_amount = reward_per_share * position_size;

  const risk_reward_ratio = reward_per_share / risk_per_share;

  // Expected value = (win_rate * reward) - (loss_rate * risk)
  const loss_rate = 1 - win_rate;
  const expected_value = (win_rate * reward_amount) - (loss_rate * risk_amount);

  // Recommendation logic
  let recommendation: string;
  if (risk_reward_ratio >= 2 && expected_value > 0) {
    recommendation = 'Excellent setup - good risk/reward and positive expected value';
  } else if (risk_reward_ratio >= 1.5 && expected_value > 0) {
    recommendation = 'Good setup - acceptable risk/reward';
  } else if (expected_value > 0) {
    recommendation = 'Marginal setup - positive expected value but low risk/reward';
  } else {
    recommendation = 'Poor setup - negative expected value, avoid this trade';
  }

  return {
    risk_reward_ratio: parseFloat(risk_reward_ratio.toFixed(2)),
    risk_amount: parseFloat(risk_amount.toFixed(2)),
    reward_amount: parseFloat(reward_amount.toFixed(2)),
    expected_value: parseFloat(expected_value.toFixed(2)),
    recommendation
  };
}

