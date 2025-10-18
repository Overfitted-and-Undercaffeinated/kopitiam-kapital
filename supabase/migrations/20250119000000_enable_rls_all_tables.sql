-- Enable Row Level Security on All Tables
-- This migration ensures all tables have proper RLS policies

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE pnl_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_watchlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE briefs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Service role has full access to users" ON users;
DROP POLICY IF EXISTS "Service role has full access to instruments" ON instruments;
DROP POLICY IF EXISTS "Service role has full access to user_watchlist" ON user_watchlist;
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can view their own watchlist" ON user_watchlist;
DROP POLICY IF EXISTS "Anyone can view instruments" ON instruments;

-- ============================================================================
-- USERS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_users" ON users
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own profile
CREATE POLICY "users_view_own_profile" ON users
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = id::text);

-- Users can update their own profile
CREATE POLICY "users_update_own_profile" ON users
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = id::text)
  WITH CHECK (auth.uid()::text = id::text);

-- Allow users to insert their own profile (for onboarding)
CREATE POLICY "users_insert_own_profile" ON users
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = id::text);

-- ============================================================================
-- INSTRUMENTS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_instruments" ON instruments
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- All authenticated users can read instruments (they're public data)
CREATE POLICY "authenticated_read_instruments" ON instruments
  FOR SELECT
  TO authenticated
  USING (true);

-- Only service role can insert/update/delete instruments
-- (No additional policies needed as service role already has full access)

-- ============================================================================
-- POSITIONS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_positions" ON positions
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own positions
CREATE POLICY "users_view_own_positions" ON positions
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- Users can create their own positions
CREATE POLICY "users_create_own_positions" ON positions
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = user_id::text);

-- Users can update their own positions
CREATE POLICY "users_update_own_positions" ON positions
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = user_id::text)
  WITH CHECK (auth.uid()::text = user_id::text);

-- Users can delete their own positions
CREATE POLICY "users_delete_own_positions" ON positions
  FOR DELETE
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ============================================================================
-- EVENTS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_events" ON events
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- All authenticated users can read events (market events are public)
CREATE POLICY "authenticated_read_events" ON events
  FOR SELECT
  TO authenticated
  USING (true);

-- Only service role can write events (events are system-generated)

-- ============================================================================
-- RECOMMENDATIONS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_recommendations" ON recommendations
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own recommendations
CREATE POLICY "users_view_own_recommendations" ON recommendations
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- Users can update their own recommendations (e.g., marking as accepted)
CREATE POLICY "users_update_own_recommendations" ON recommendations
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = user_id::text)
  WITH CHECK (auth.uid()::text = user_id::text);

-- Only service role can create recommendations (AI-generated)

-- ============================================================================
-- PNL SNAPSHOTS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_pnl_snapshots" ON pnl_snapshots
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own P&L snapshots
CREATE POLICY "users_view_own_pnl" ON pnl_snapshots
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- Only service role can create/update P&L snapshots (system-generated)

-- ============================================================================
-- NOTES TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_notes" ON notes
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own notes
CREATE POLICY "users_view_own_notes" ON notes
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text OR user_id IS NULL);

-- Users can create their own notes
CREATE POLICY "users_create_own_notes" ON notes
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = user_id::text OR user_id IS NULL);

-- Users can update their own notes
CREATE POLICY "users_update_own_notes" ON notes
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = user_id::text OR user_id IS NULL)
  WITH CHECK (auth.uid()::text = user_id::text OR user_id IS NULL);

-- Users can delete their own notes
CREATE POLICY "users_delete_own_notes" ON notes
  FOR DELETE
  TO authenticated
  USING (auth.uid()::text = user_id::text OR user_id IS NULL);

-- ============================================================================
-- USER WATCHLIST TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_watchlist" ON user_watchlist
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own watchlist
CREATE POLICY "users_view_own_watchlist" ON user_watchlist
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- Users can add to their own watchlist
CREATE POLICY "users_add_to_own_watchlist" ON user_watchlist
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid()::text = user_id::text);

-- Users can remove from their own watchlist
CREATE POLICY "users_remove_from_own_watchlist" ON user_watchlist
  FOR DELETE
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- ============================================================================
-- BRIEFS TABLE POLICIES
-- ============================================================================

-- Service role has full access
CREATE POLICY "service_role_all_briefs" ON briefs
  FOR ALL 
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Users can view their own briefs
CREATE POLICY "users_view_own_briefs" ON briefs
  FOR SELECT
  TO authenticated
  USING (auth.uid()::text = user_id::text);

-- Only service role can create/update briefs (AI-generated)

-- ============================================================================
-- GRANT NECESSARY PERMISSIONS
-- ============================================================================

-- Grant usage on public schema
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;

-- Grant select on all tables to authenticated (will be filtered by RLS)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO authenticated;

-- Grant specific permissions to authenticated users
GRANT INSERT, UPDATE, DELETE ON users TO authenticated;
GRANT INSERT, UPDATE, DELETE ON positions TO authenticated;
GRANT UPDATE ON recommendations TO authenticated;
GRANT INSERT, UPDATE, DELETE ON notes TO authenticated;
GRANT INSERT, DELETE ON user_watchlist TO authenticated;

-- Service role gets all permissions
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON POLICY "service_role_all_users" ON users IS 'Service role (backend API) has full access to users table';
COMMENT ON POLICY "users_view_own_profile" ON users IS 'Users can view their own profile';
COMMENT ON POLICY "users_update_own_profile" ON users IS 'Users can update their own profile';
COMMENT ON POLICY "users_insert_own_profile" ON users IS 'Users can create their own profile during onboarding';

COMMENT ON POLICY "authenticated_read_instruments" ON instruments IS 'All authenticated users can read instruments (public market data)';
COMMENT ON POLICY "users_view_own_positions" ON positions IS 'Users can only view their own positions';
COMMENT ON POLICY "authenticated_read_events" ON events IS 'All authenticated users can read market events';
COMMENT ON POLICY "users_view_own_recommendations" ON recommendations IS 'Users can only view their own recommendations';
COMMENT ON POLICY "users_view_own_pnl" ON pnl_snapshots IS 'Users can only view their own P&L snapshots';
COMMENT ON POLICY "users_view_own_notes" ON notes IS 'Users can view their own notes or public notes';
COMMENT ON POLICY "users_view_own_watchlist" ON user_watchlist IS 'Users can only view their own watchlist';
COMMENT ON POLICY "users_view_own_briefs" ON briefs IS 'Users can only view their own briefs';

