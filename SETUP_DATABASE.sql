-- =====================================================
-- COMPLETE DATABASE SETUP FOR ONBOARDING
-- Copy this entire file and paste into Supabase SQL Editor
-- =====================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS vector;

-- =====================================================
-- USERS TABLE (with onboarding fields)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  risk_profile TEXT CHECK (risk_profile IN ('Conservative', 'Moderate', 'Aggressive')) DEFAULT 'Moderate',
  explanation_level TEXT CHECK (explanation_level IN ('beginner', 'intermediate', 'expert')) DEFAULT 'intermediate',
  trading_capital_range TEXT CHECK (trading_capital_range IN ('<10K', '10K-50K', '50K-100K', '100K+')),
  primary_markets TEXT[] DEFAULT '{}',
  brief_time TEXT DEFAULT '08:00',
  preferred_voice TEXT DEFAULT 'default',
  timezone TEXT DEFAULT 'Asia/Singapore',
  language TEXT DEFAULT 'en',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INSTRUMENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS instruments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  symbol TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  mic TEXT,
  asset_class TEXT CHECK (asset_class IN ('equity', 'commodity', 'forex', 'crypto', 'etf')),
  tick_size DECIMAL,
  lot_size INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- USER WATCHLIST TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS user_watchlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
  instrument_id UUID REFERENCES instruments(id) ON DELETE CASCADE NOT NULL,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, instrument_id)
);

-- =====================================================
-- POSITIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS positions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  instrument_id UUID REFERENCES instruments(id),
  qty DECIMAL NOT NULL,
  avg_price DECIMAL NOT NULL,
  stop DECIMAL,
  target DECIMAL,
  tags TEXT[],
  opened_at TIMESTAMPTZ DEFAULT NOW(),
  closed_at TIMESTAMPTZ,
  pnl DECIMAL
);

-- =====================================================
-- EVENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instrument_id UUID REFERENCES instruments(id),
  type TEXT CHECK (type IN ('price', 'news', 'econ', 'alert', 'earnings')),
  payload_json JSONB NOT NULL,
  ts TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- RECOMMENDATIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS recommendations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  instrument_id UUID REFERENCES instruments(id),
  action TEXT CHECK (action IN ('BUY', 'SELL', 'HOLD')),
  entry DECIMAL NOT NULL,
  stop DECIMAL NOT NULL,
  tp DECIMAL NOT NULL,
  size_pct_nav DECIMAL NOT NULL,
  thesis TEXT NOT NULL,
  risks TEXT NOT NULL,
  confidence DECIMAL CHECK (confidence BETWEEN 0 AND 1),
  sources JSONB,
  accepted BOOLEAN DEFAULT FALSE,
  outcome_pnl DECIMAL,
  ts TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- P&L SNAPSHOTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS pnl_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ DEFAULT NOW(),
  total_pnl DECIMAL NOT NULL,
  json_by_symbol JSONB NOT NULL
);

-- =====================================================
-- NOTES TABLE (for RAG)
-- =====================================================
CREATE TABLE IF NOT EXISTS notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  instrument_id UUID REFERENCES instruments(id),
  chunk TEXT NOT NULL,
  source TEXT,
  embedding vector(1536),
  ts TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- INDEXES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_instruments_symbol ON instruments(symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_user ON user_watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_instrument ON user_watchlist(instrument_id);
CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_open ON positions(user_id, closed_at) WHERE closed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_events_instrument_ts ON events(instrument_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_ts ON recommendations(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_pnl_user_ts ON pnl_snapshots(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_notes_user_instrument ON notes(user_id, instrument_id);
CREATE INDEX IF NOT EXISTS idx_notes_embedding ON notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE pnl_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- RLS POLICIES (Service Role Full Access)
-- =====================================================
DROP POLICY IF EXISTS "Service role has full access to users" ON users;
CREATE POLICY "Service role has full access to users" ON users
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to instruments" ON instruments;
CREATE POLICY "Service role has full access to instruments" ON instruments
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to user_watchlist" ON user_watchlist;
CREATE POLICY "Service role has full access to user_watchlist" ON user_watchlist
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to positions" ON positions;
CREATE POLICY "Service role has full access to positions" ON positions
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to events" ON events;
CREATE POLICY "Service role has full access to events" ON events
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to recommendations" ON recommendations;
CREATE POLICY "Service role has full access to recommendations" ON recommendations
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to pnl_snapshots" ON pnl_snapshots;
CREATE POLICY "Service role has full access to pnl_snapshots" ON pnl_snapshots
  FOR ALL TO service_role USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Service role has full access to notes" ON notes;
CREATE POLICY "Service role has full access to notes" ON notes
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- =====================================================
-- HELPER FUNCTION: Search notes by vector similarity
-- =====================================================
CREATE OR REPLACE FUNCTION search_notes(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10,
  filter_user_id uuid DEFAULT NULL
)
RETURNS TABLE (
  id uuid,
  chunk text,
  source text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    notes.id,
    notes.chunk,
    notes.source,
    1 - (notes.embedding <=> query_embedding) AS similarity
  FROM notes
  WHERE 
    (filter_user_id IS NULL OR notes.user_id = filter_user_id)
    AND 1 - (notes.embedding <=> query_embedding) > match_threshold
  ORDER BY notes.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- =====================================================
-- SAMPLE DATA (Optional - uncomment to add)
-- =====================================================
-- Insert some sample instruments
INSERT INTO instruments (symbol, name, asset_class) 
VALUES 
  ('AAPL', 'Apple Inc.', 'equity'),
  ('GOOGL', 'Alphabet Inc.', 'equity'),
  ('MSFT', 'Microsoft Corporation', 'equity'),
  ('TSLA', 'Tesla, Inc.', 'equity'),
  ('DBS', 'DBS Group Holdings', 'equity'),
  ('BTC', 'Bitcoin', 'crypto'),
  ('ETH', 'Ethereum', 'crypto')
ON CONFLICT (symbol) DO NOTHING;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================
DO $$ 
BEGIN 
  RAISE NOTICE '✅ Database setup complete!';
  RAISE NOTICE '📊 Tables created: users, instruments, user_watchlist, positions, events, recommendations, pnl_snapshots, notes';
  RAISE NOTICE '🔒 Row Level Security enabled with service role policies';
  RAISE NOTICE '🚀 Ready for onboarding!';
END $$;

