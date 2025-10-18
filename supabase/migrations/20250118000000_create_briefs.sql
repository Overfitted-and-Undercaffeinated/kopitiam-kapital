-- Create briefs table for morning briefs and EOD reports
CREATE TABLE briefs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type TEXT CHECK (type IN ('morning', 'eod')) NOT NULL,
  date DATE NOT NULL,
  content JSONB NOT NULL, -- Structured content including summary, market_overview, key_points, etc.
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_briefs_user_type_date ON briefs(user_id, type, date DESC);
CREATE INDEX idx_briefs_user_date ON briefs(user_id, date DESC);

-- Add unique constraint to prevent duplicate briefs for same user/type/date
CREATE UNIQUE INDEX idx_briefs_unique ON briefs(user_id, type, date);

