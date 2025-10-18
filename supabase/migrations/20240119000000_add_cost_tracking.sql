-- API cost tracking table
CREATE TABLE api_costs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  service TEXT NOT NULL,  -- 'gpt-4o', 'exa-search', etc.
  cost_usd DECIMAL NOT NULL,
  tokens_input INTEGER DEFAULT 0,
  tokens_output INTEGER DEFAULT 0,
  units INTEGER DEFAULT 0,  -- For non-token services
  metadata JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_costs_user_ts ON api_costs(user_id, timestamp DESC);
CREATE INDEX idx_api_costs_service ON api_costs(service);

-- Add model versioning to recommendations
ALTER TABLE recommendations 
ADD COLUMN model_version TEXT,
ADD COLUMN prompt_hash TEXT,
ADD COLUMN disclaimer TEXT;

-- Add manual position entry fields
ALTER TABLE positions
ADD COLUMN recommendation_id UUID REFERENCES recommendations(id),
ADD COLUMN entry_notes TEXT;

COMMENT ON TABLE api_costs IS 'Track API usage costs per user and service';
COMMENT ON COLUMN recommendations.model_version IS 'Agent version that generated this (e.g., recommend_v1.2)';
COMMENT ON COLUMN recommendations.prompt_hash IS 'SHA256 hash of prompt template used';
COMMENT ON COLUMN positions.recommendation_id IS 'Link to recommendation that generated this position';

