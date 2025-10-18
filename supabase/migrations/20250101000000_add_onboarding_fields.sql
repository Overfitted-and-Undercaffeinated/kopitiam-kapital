-- Add new columns to users table for onboarding
ALTER TABLE users 
  ADD COLUMN IF NOT EXISTS name TEXT,
  ADD COLUMN IF NOT EXISTS trading_capital_range TEXT CHECK (trading_capital_range IN ('<10K', '10K-50K', '50K-100K', '100K+')),
  ADD COLUMN IF NOT EXISTS primary_markets TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS brief_time TEXT;

-- Create user_watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  instrument_id UUID REFERENCES instruments(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, instrument_id)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user ON user_watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_instrument ON user_watchlist(instrument_id);

