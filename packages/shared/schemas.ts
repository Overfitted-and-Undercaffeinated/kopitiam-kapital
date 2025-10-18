import { z } from 'zod';

export const RecommendationSchema = z.object({
  direction: z.enum(['BUY', 'SELL', 'HOLD']),
  entry: z.number().positive(),
  stop: z.number().positive(),
  target: z.number().positive(),
  size_pct_nav: z.number().min(0).max(100),
  thesis: z.string().min(50).max(500),
  risks: z.string().min(30).max(300),
  confidence: z.number().min(0).max(1),
  sources: z.array(z.object({
    title: z.string(),
    url: z.string().url(),
    published: z.string().optional(),
  })).min(1),
});

export type Recommendation = z.infer<typeof RecommendationSchema>;

export const PositionSchema = z.object({
  symbol: z.string(),
  qty: z.number(),
  avgPrice: z.number().positive(),
  stop: z.number().positive().optional(),
  target: z.number().positive().optional(),
  openedAt: z.date(),
  closedAt: z.date().optional(),
  pnl: z.number().optional(),
});

export type Position = z.infer<typeof PositionSchema>;

export const UserProfileSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  riskProfile: z.enum(['Conservative', 'Moderate', 'Aggressive']),
  explanationLevel: z.enum(['beginner', 'intermediate', 'expert']),
  timezone: z.string().default('Asia/Singapore'),
  preferredVoice: z.string().default('default'),
  language: z.string().default('en'),
});

export type UserProfile = z.infer<typeof UserProfileSchema>;

export const AlertSchema = z.object({
  type: z.enum(['price', 'news', 'econ', 'alert', 'earnings']),
  title: z.string(),
  message: z.string(),
  severity: z.enum(['info', 'warning', 'success', 'error']),
  timestamp: z.date(),
});

export type Alert = z.infer<typeof AlertSchema>;

