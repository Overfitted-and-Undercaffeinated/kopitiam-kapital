-- Migration: Add tiers, alerts, and usage tracking
-- Created: 2025-01-19
-- Purpose: Support tiered features (Free/Pro/Enterprise) and monitoring alerts

-- ============================================================================
-- 1. Add tier column to users table
-- ============================================================================

-- Add tier enum type
CREATE TYPE user_tier AS ENUM ('free', 'pro', 'enterprise');

-- Add tier column to users table (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'tier') THEN
        ALTER TABLE users ADD COLUMN tier user_tier DEFAULT 'free' NOT NULL;
        
        -- Add index for tier filtering
        CREATE INDEX idx_users_tier ON users(tier);
        
        -- Add subscription metadata
        ALTER TABLE users ADD COLUMN subscription_started_at TIMESTAMPTZ;
        ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMPTZ;
    END IF;
END $$;

-- ============================================================================
-- 2. Create alerts table
-- ============================================================================

-- Alert types enum
CREATE TYPE alert_type AS ENUM (
    'price_above',
    'price_below',
    'volatility_spike',
    'sentiment_change',
    'news_event',
    'technical_signal'
);

-- Alert priority enum
CREATE TYPE alert_priority AS ENUM ('low', 'medium', 'high', 'critical');

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    type alert_type NOT NULL,
    condition JSONB NOT NULL,
    active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Indexes
    CONSTRAINT alerts_user_symbol_idx UNIQUE (user_id, symbol, type, active)
);

-- Indexes for alerts table
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_symbol ON alerts(symbol);
CREATE INDEX idx_alerts_active ON alerts(active);
CREATE INDEX idx_alerts_type ON alerts(type);

-- ============================================================================
-- 3. Create triggered_alerts table (history)
-- ============================================================================

CREATE TABLE IF NOT EXISTS triggered_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_rule_id UUID REFERENCES alerts(id) ON DELETE SET NULL,
    symbol VARCHAR(10) NOT NULL,
    type alert_type NOT NULL,
    message TEXT NOT NULL,
    priority alert_priority DEFAULT 'medium' NOT NULL,
    current_price DECIMAL(12, 2),
    condition_met JSONB,
    triggered_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    read_at TIMESTAMPTZ,
    
    -- Indexes
    CONSTRAINT triggered_alerts_unique UNIQUE (alert_rule_id, triggered_at)
);

-- Indexes for triggered_alerts
CREATE INDEX idx_triggered_alerts_user_id ON triggered_alerts(user_id);
CREATE INDEX idx_triggered_alerts_triggered_at ON triggered_alerts(triggered_at DESC);
CREATE INDEX idx_triggered_alerts_read_at ON triggered_alerts(read_at);

-- ============================================================================
-- 4. Create usage_tracking table
-- ============================================================================

-- Feature names enum
CREATE TYPE feature_name AS ENUM (
    'monitor_alerts',
    'long_context_analysis',
    'explainer'
);

-- Create usage_tracking table
CREATE TABLE IF NOT EXISTS usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature feature_name NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    count INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Unique constraint for deduplication
    CONSTRAINT usage_tracking_unique UNIQUE (user_id, feature, window_start)
);

-- Indexes for usage_tracking
CREATE INDEX idx_usage_tracking_user_id ON usage_tracking(user_id);
CREATE INDEX idx_usage_tracking_feature ON usage_tracking(feature);
CREATE INDEX idx_usage_tracking_window ON usage_tracking(window_start, window_end);

-- ============================================================================
-- 5. Row Level Security (RLS)
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE triggered_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_tracking ENABLE ROW LEVEL SECURITY;

-- Alerts policies
CREATE POLICY "Users can view their own alerts"
    ON alerts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own alerts"
    ON alerts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts"
    ON alerts FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own alerts"
    ON alerts FOR DELETE
    USING (auth.uid() = user_id);

-- Triggered alerts policies
CREATE POLICY "Users can view their own triggered alerts"
    ON triggered_alerts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service can insert triggered alerts"
    ON triggered_alerts FOR INSERT
    WITH CHECK (true);  -- Service role can insert

-- Usage tracking policies
CREATE POLICY "Users can view their own usage"
    ON usage_tracking FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service can manage usage tracking"
    ON usage_tracking FOR ALL
    USING (true)  -- Service role only
    WITH CHECK (true);

-- ============================================================================
-- 6. Helper functions
-- ============================================================================

-- Function to get user's current tier
CREATE OR REPLACE FUNCTION get_user_tier(p_user_id UUID)
RETURNS user_tier AS $$
DECLARE
    v_tier user_tier;
BEGIN
    SELECT tier INTO v_tier
    FROM users
    WHERE id = p_user_id;
    
    RETURN COALESCE(v_tier, 'free');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check feature access
CREATE OR REPLACE FUNCTION check_feature_access(
    p_user_id UUID,
    p_feature feature_name,
    p_window_start TIMESTAMPTZ,
    p_window_end TIMESTAMPTZ
)
RETURNS TABLE (
    allowed BOOLEAN,
    current_usage INTEGER,
    tier_limit INTEGER
) AS $$
DECLARE
    v_tier user_tier;
    v_usage INTEGER;
    v_limit INTEGER;
BEGIN
    -- Get user tier
    v_tier := get_user_tier(p_user_id);
    
    -- Get current usage
    SELECT COALESCE(SUM(count), 0) INTO v_usage
    FROM usage_tracking
    WHERE user_id = p_user_id
      AND feature = p_feature
      AND window_start >= p_window_start
      AND window_end <= p_window_end;
    
    -- Determine limits based on tier and feature
    IF p_feature = 'monitor_alerts' THEN
        v_limit := CASE v_tier
            WHEN 'free' THEN 3
            WHEN 'pro' THEN 50
            WHEN 'enterprise' THEN NULL  -- Unlimited
        END;
    ELSIF p_feature = 'long_context_analysis' THEN
        v_limit := CASE v_tier
            WHEN 'free' THEN 1
            WHEN 'pro' THEN 10
            WHEN 'enterprise' THEN NULL  -- Unlimited
        END;
    ELSE
        v_limit := NULL;  -- Unlimited for other features
    END IF;
    
    -- Return result
    RETURN QUERY SELECT 
        (v_limit IS NULL OR v_usage < v_limit) AS allowed,
        v_usage AS current_usage,
        v_limit AS tier_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to increment usage
CREATE OR REPLACE FUNCTION increment_usage(
    p_user_id UUID,
    p_feature feature_name,
    p_timestamp TIMESTAMPTZ DEFAULT NOW()
)
RETURNS VOID AS $$
DECLARE
    v_window_start TIMESTAMPTZ;
    v_window_end TIMESTAMPTZ;
BEGIN
    -- Determine window based on feature
    IF p_feature = 'monitor_alerts' THEN
        -- Daily window
        v_window_start := DATE_TRUNC('day', p_timestamp);
        v_window_end := v_window_start + INTERVAL '1 day';
    ELSIF p_feature = 'long_context_analysis' THEN
        -- Monthly window
        v_window_start := DATE_TRUNC('month', p_timestamp);
        v_window_end := v_window_start + INTERVAL '1 month';
    ELSE
        -- Daily window (default)
        v_window_start := DATE_TRUNC('day', p_timestamp);
        v_window_end := v_window_start + INTERVAL '1 day';
    END IF;
    
    -- Insert or update usage count
    INSERT INTO usage_tracking (user_id, feature, window_start, window_end, count)
    VALUES (p_user_id, p_feature, v_window_start, v_window_end, 1)
    ON CONFLICT (user_id, feature, window_start)
    DO UPDATE SET 
        count = usage_tracking.count + 1,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- 7. Create indexes for performance
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON alerts(user_id, active);
CREATE INDEX IF NOT EXISTS idx_triggered_alerts_user_unread ON triggered_alerts(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_usage_tracking_lookup ON usage_tracking(user_id, feature, window_start);

-- ============================================================================
-- 8. Comments for documentation
-- ============================================================================

COMMENT ON TABLE alerts IS 'User-defined alert rules for price, volatility, sentiment, etc.';
COMMENT ON TABLE triggered_alerts IS 'History of triggered alerts (notifications sent to users)';
COMMENT ON TABLE usage_tracking IS 'Track feature usage for tier-based rate limiting';
COMMENT ON COLUMN users.tier IS 'User subscription tier (free/pro/enterprise)';

COMMENT ON FUNCTION get_user_tier IS 'Get user subscription tier';
COMMENT ON FUNCTION check_feature_access IS 'Check if user has access to feature based on tier and usage';
COMMENT ON FUNCTION increment_usage IS 'Increment usage count for a feature';




