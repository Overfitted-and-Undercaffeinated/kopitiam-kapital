/**
 * Get user trading policy from Mem0
 */

export interface TradingPolicy {
  risk_profile: string;
  max_position_size: number;
  preferred_sectors: string[];
  restricted_symbols: string[];
}

export async function getPolicy(userId: string): Promise<TradingPolicy> {
  // TODO: Implement Mem0 API call
  return {
    risk_profile: 'Moderate',
    max_position_size: 0.1,
    preferred_sectors: [],
    restricted_symbols: []
  };
}

