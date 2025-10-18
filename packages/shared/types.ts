/**
 * Shared TypeScript types for Kopitiam Capital
 */

export interface Source {
  title: string;
  url: string;
  published?: string;
}

export interface TradingIdea {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  entry: number;
  stop: number;
  target: number;
  thesis: string;
  risks: string;
  confidence: number;
  sources: Source[];
}

export interface MarketEvent {
  type: 'price' | 'news' | 'econ' | 'alert' | 'earnings';
  symbol?: string;
  timestamp: Date;
  data: any;
}

export interface PnLSnapshot {
  timestamp: Date;
  totalPnl: number;
  bySymbol: Record<string, number>;
}

export interface MorningBrief {
  summary: string;
  marketOverview: string;
  portfolioStatus: any;
  recommendations: TradingIdea[];
  audioUrl?: string;
}

export interface EODReport {
  summary: string;
  performance: any;
  recommendations: TradingIdea[];
  audioUrl?: string;
}

