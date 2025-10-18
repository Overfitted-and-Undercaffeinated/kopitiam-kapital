-- ============================================================================
-- RLS STATUS CHECK SCRIPT
-- Run this to see current RLS configuration
-- ============================================================================

\echo ''
\echo '==================================================================='
\echo 'CHECKING ROW LEVEL SECURITY (RLS) STATUS'
\echo '==================================================================='
\echo ''

-- Check which tables have RLS enabled
\echo '1. TABLES WITH RLS ENABLED:'
\echo '-------------------------------------------------------------------'
SELECT 
    tablename,
    CASE 
        WHEN rowsecurity THEN '✅ ENABLED' 
        ELSE '❌ DISABLED' 
    END as rls_status
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY 
    rowsecurity DESC,
    tablename;

\echo ''
\echo '2. EXISTING RLS POLICIES:'
\echo '-------------------------------------------------------------------'
SELECT 
    tablename,
    policyname,
    CASE cmd
        WHEN 'r' THEN 'SELECT'
        WHEN 'w' THEN 'UPDATE'
        WHEN 'a' THEN 'INSERT'
        WHEN 'd' THEN 'DELETE'
        WHEN '*' THEN 'ALL'
    END as operation,
    roles::text as for_roles
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

\echo ''
\echo '3. TABLES WITHOUT RLS POLICIES:'
\echo '-------------------------------------------------------------------'
SELECT 
    t.tablename
FROM pg_tables t
LEFT JOIN pg_policies p ON t.tablename = p.tablename AND t.schemaname = p.schemaname
WHERE t.schemaname = 'public'
    AND p.policyname IS NULL
    AND t.rowsecurity = true
GROUP BY t.tablename
ORDER BY t.tablename;

\echo ''
\echo '4. GRANTS TO AUTHENTICATED ROLE:'
\echo '-------------------------------------------------------------------'
SELECT 
    table_name,
    string_agg(privilege_type, ', ' ORDER BY privilege_type) as privileges
FROM information_schema.role_table_grants
WHERE grantee = 'authenticated'
    AND table_schema = 'public'
GROUP BY table_name
ORDER BY table_name;

\echo ''
\echo '5. SUMMARY:'
\echo '-------------------------------------------------------------------'
SELECT 
    COUNT(*) FILTER (WHERE rowsecurity = true) as tables_with_rls,
    COUNT(*) FILTER (WHERE rowsecurity = false) as tables_without_rls,
    COUNT(*) as total_tables
FROM pg_tables
WHERE schemaname = 'public';

\echo ''
\echo '==================================================================='
\echo 'RLS CHECK COMPLETE'
\echo '==================================================================='
\echo ''

