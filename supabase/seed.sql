-- Seed data for development and testing

-- Insert sample instruments
INSERT INTO instruments (symbol, name, asset_class, tick_size, lot_size) VALUES
  ('AAPL', 'Apple Inc.', 'equity', 0.01, 1),
  ('MSFT', 'Microsoft Corporation', 'equity', 0.01, 1),
  ('GOOGL', 'Alphabet Inc.', 'equity', 0.01, 1),
  ('TSLA', 'Tesla Inc.', 'equity', 0.01, 1),
  ('STI', 'Straits Times Index', 'equity', 0.01, 1),
  ('DBS', 'DBS Group Holdings', 'equity', 0.01, 100),
  ('OCBC', 'Oversea-Chinese Banking Corp', 'equity', 0.01, 100)
ON CONFLICT (symbol) DO NOTHING;

-- Insert sample user
INSERT INTO users (email, risk_profile, explanation_level) VALUES
  ('demo@kopitiam.capital', 'Moderate', 'intermediate')
ON CONFLICT (email) DO NOTHING;

-- Note: In production, you would populate this with real data

