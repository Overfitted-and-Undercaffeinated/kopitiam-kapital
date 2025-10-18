-- Collaboration Features Migration
-- Workspaces, chat messages, and shared watchlists

-- ============================================================================
-- WORKSPACES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    tier TEXT NOT NULL DEFAULT 'Pro' CHECK (tier IN ('Pro', 'Enterprise')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    settings JSONB DEFAULT '{}',
    
    -- Metadata
    member_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

-- Index for active workspaces
CREATE INDEX idx_workspaces_active ON public.workspaces(is_active, created_at DESC);

COMMENT ON TABLE public.workspaces IS 'Team workspaces for collaborative trading';

-- ============================================================================
-- WORKSPACE MEMBERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,  -- From auth system
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMPTZ,
    
    -- Permissions
    can_trade BOOLEAN DEFAULT true,
    can_chat BOOLEAN DEFAULT true,
    can_invite BOOLEAN DEFAULT false,
    
    -- Unique constraint
    UNIQUE(workspace_id, user_id)
);

-- Indexes
CREATE INDEX idx_workspace_members_workspace ON public.workspace_members(workspace_id, role);
CREATE INDEX idx_workspace_members_user ON public.workspace_members(user_id);

COMMENT ON TABLE public.workspace_members IS 'Members of team workspaces with roles and permissions';

-- ============================================================================
-- CHAT MESSAGES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id TEXT,  -- NULL for AI messages
    message_type TEXT NOT NULL DEFAULT 'user' CHECK (message_type IN ('user', 'ai', 'system')),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- AI-specific fields
    trade_suggestions JSONB,  -- Array of trade suggestions from AI
    symbols_mentioned TEXT[],  -- Symbols mentioned in message
    
    -- Metadata
    edited_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT false
);

-- Indexes
CREATE INDEX idx_chat_messages_workspace ON public.chat_messages(workspace_id, created_at DESC);
CREATE INDEX idx_chat_messages_user ON public.chat_messages(user_id, created_at DESC);
CREATE INDEX idx_chat_messages_symbols ON public.chat_messages USING GIN(symbols_mentioned);

COMMENT ON TABLE public.chat_messages IS 'Real-time chat messages in workspaces';

-- ============================================================================
-- SHARED WATCHLISTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.shared_watchlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    added_by TEXT NOT NULL,  -- user_id
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Analysis data (cached)
    current_price DECIMAL(12, 4),
    sentiment_score DECIMAL(3, 2),
    last_analyzed_at TIMESTAMPTZ,
    
    -- Metadata
    notes TEXT,
    alerts_enabled BOOLEAN DEFAULT true,
    
    -- Unique constraint
    UNIQUE(workspace_id, symbol)
);

-- Indexes
CREATE INDEX idx_shared_watchlists_workspace ON public.shared_watchlists(workspace_id, added_at DESC);
CREATE INDEX idx_shared_watchlists_symbol ON public.shared_watchlists(symbol);

COMMENT ON TABLE public.shared_watchlists IS 'Shared watchlists for team workspaces';

-- ============================================================================
-- WORKSPACE ANALYTICS TABLE (Optional)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.workspace_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- Activity metrics
    messages_sent INTEGER DEFAULT 0,
    ai_responses INTEGER DEFAULT 0,
    trades_executed INTEGER DEFAULT 0,
    active_members INTEGER DEFAULT 0,
    
    -- Performance metrics
    total_pnl DECIMAL(12, 2),
    win_rate DECIMAL(5, 4),
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(workspace_id, date)
);

CREATE INDEX idx_workspace_analytics_workspace ON public.workspace_analytics(workspace_id, date DESC);

COMMENT ON TABLE public.workspace_analytics IS 'Daily analytics for workspace performance';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shared_watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_analytics ENABLE ROW LEVEL SECURITY;

-- Policies for workspace_members
-- Members can view their own workspaces
CREATE POLICY "Members can view their workspaces"
    ON public.workspace_members FOR SELECT
    USING (auth.uid()::text = user_id);

-- Policies for chat_messages
-- Members can view messages in their workspaces
CREATE POLICY "Members can view workspace chat"
    ON public.chat_messages FOR SELECT
    USING (
        workspace_id IN (
            SELECT workspace_id 
            FROM public.workspace_members 
            WHERE user_id = auth.uid()::text
        )
    );

-- Members can send messages
CREATE POLICY "Members can send messages"
    ON public.chat_messages FOR INSERT
    WITH CHECK (
        workspace_id IN (
            SELECT workspace_id 
            FROM public.workspace_members 
            WHERE user_id = auth.uid()::text 
            AND can_chat = true
        )
    );

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update workspace member count
CREATE OR REPLACE FUNCTION update_workspace_member_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.workspaces
    SET member_count = (
        SELECT COUNT(*) 
        FROM public.workspace_members 
        WHERE workspace_id = COALESCE(NEW.workspace_id, OLD.workspace_id)
    )
    WHERE id = COALESCE(NEW.workspace_id, OLD.workspace_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger for member count updates
DROP TRIGGER IF EXISTS trigger_update_workspace_member_count ON public.workspace_members;
CREATE TRIGGER trigger_update_workspace_member_count
    AFTER INSERT OR DELETE ON public.workspace_members
    FOR EACH ROW
    EXECUTE FUNCTION update_workspace_member_count();

-- Function to update workspace updated_at
CREATE OR REPLACE FUNCTION update_workspace_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for workspace updates
DROP TRIGGER IF EXISTS trigger_update_workspace_timestamp ON public.workspaces;
CREATE TRIGGER trigger_update_workspace_timestamp
    BEFORE UPDATE ON public.workspaces
    FOR EACH ROW
    EXECUTE FUNCTION update_workspace_updated_at();

-- ============================================================================
-- SAMPLE DATA (for development/demo)
-- ============================================================================

-- Insert sample workspace (commented out for production)
/*
INSERT INTO public.workspaces (name, description, tier) VALUES
('Demo Trading Team', 'Sample workspace for demonstration', 'Enterprise');
*/

-- ============================================================================
-- VIEWS (Optional - for easier querying)
-- ============================================================================

-- View for workspace members with details
CREATE OR REPLACE VIEW workspace_members_detailed AS
SELECT 
    wm.*,
    w.name as workspace_name,
    w.tier as workspace_tier
FROM public.workspace_members wm
JOIN public.workspaces w ON wm.workspace_id = w.id;

COMMENT ON VIEW workspace_members_detailed IS 'Workspace members with workspace details';

