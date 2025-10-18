-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  risk_profile TEXT CHECK (risk_profile IN ('Conservative', 'Moderate', 'Aggressive')) DEFAULT 'Moderate',
  explanation_level TEXT CHECK (explanation_level IN ('beginner', 'intermediate', 'expert')) DEFAULT 'intermediate',
  trading_capital_range TEXT CHECK (trading_capital_range IN ('<10K', '10K-50K', '50K-100K', '100K+')),
  primary_markets TEXT[] DEFAULT '{}',
  brief_time TEXT,
  timezone TEXT DEFAULT 'Asia/Singapore',
  preferred_voice TEXT DEFAULT 'default',
  language TEXT DEFAULT 'en',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Instruments table
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

-- Positions table
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

CREATE INDEX IF NOT EXISTS idx_positions_user ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_open ON positions(user_id, closed_at) WHERE closed_at IS NULL;

-- Events table
CREATE TABLE IF NOT EXISTS events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instrument_id UUID REFERENCES instruments(id),
  type TEXT CHECK (type IN ('price', 'news', 'econ', 'alert', 'earnings')),
  payload_json JSONB NOT NULL,
  ts TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_instrument_ts ON events(instrument_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts DESC);

-- Recommendations table
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

CREATE INDEX IF NOT EXISTS idx_recommendations_user_ts ON recommendations(user_id, ts DESC);

-- P&L Snapshots table
CREATE TABLE IF NOT EXISTS pnl_snapshots (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ DEFAULT NOW(),
  total_pnl DECIMAL NOT NULL,
  json_by_symbol JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pnl_user_ts ON pnl_snapshots(user_id, ts DESC);

-- Notes table (for RAG)
CREATE TABLE IF NOT EXISTS notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  instrument_id UUID REFERENCES instruments(id),
  chunk TEXT NOT NULL,
  source TEXT,
  ts TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notes_user_instrument ON notes(user_id, instrument_id);

-- User watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  instrument_id UUID REFERENCES instruments(id) ON DELETE CASCADE,
  added_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, instrument_id)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user ON user_watchlist(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_instrument ON user_watchlist(instrument_id);

