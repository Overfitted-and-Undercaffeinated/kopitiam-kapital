-- Quick setup SQL for onboarding
-- Run this in Supabase SQL Editor if other migrations don't work

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  risk_profile TEXT CHECK (risk_profile IN ('Conservative', 'Moderate', 'Aggressive')),
  explanation_level TEXT CHECK (explanation_level IN ('beginner', 'intermediate', 'expert')) DEFAULT 'intermediate',
  trading_capital_range TEXT CHECK (trading_capital_range IN ('<10K', '10K-50K', '50K-100K', '100K+')),
  primary_markets TEXT[] DEFAULT '{}',
  brief_time TEXT DEFAULT '08:00',
  preferred_voice TEXT DEFAULT 'default',
  timezone TEXT DEFAULT 'Asia/Singapore',
  language TEXT DEFAULT 'en',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create instruments table
CREATE TABLE IF NOT EXISTS instruments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  symbol TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  mic TEXT,
  asset_class TEXT,
  tick_size DECIMAL,
  lot_size INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  instrument_id UUID REFERENCES instruments(id) ON DELETE CASCADE NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, instrument_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON user_watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_instrument ON user_watchlist(instrument_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments(symbol);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;

-- Create policies for service role access
DROP POLICY IF EXISTS "Service role has full access to users" ON users;
CREATE POLICY "Service role has full access to users" ON users
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to instruments" ON instruments;
CREATE POLICY "Service role has full access to instruments" ON instruments
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to user_watchlist" ON user_watchlist;
CREATE POLICY "Service role has full access to user_watchlist" ON user_watchlist
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Also allow authenticated users to read their own data
DROP POLICY IF EXISTS "Users can view their own data" ON users;
CREATE POLICY "Users can view their own data" ON users
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = id::text);

DROP POLICY IF EXISTS "Users can view their own watchlist" ON user_watchlist;
CREATE POLICY "Users can view their own watchlist" ON user_watchlist
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- Allow reading instruments
DROP POLICY IF EXISTS "Anyone can view instruments" ON instruments;
CREATE POLICY "Anyone can view instruments" ON instruments
  FOR SELECT
  TO authenticated
  USING (true);

-- Insert some sample instruments (optional)
INSERT INTO instruments (symbol, name, asset_class) 
VALUES 
  ('AAPL', 'Apple Inc.', 'equity'),
  ('GOOGL', 'Alphabet Inc.', 'equity'),
  ('MSFT', 'Microsoft Corporation', 'equity'),
  ('TSLA', 'Tesla, Inc.', 'equity'),
  ('DBS', 'DBS Group Holdings', 'equity')
ON CONFLICT (symbol) DO NOTHING;

-- Success message
DO $$ 
BEGIN 
  RAISE NOTICE 'Setup complete! Tables created successfully.';
END $$;

