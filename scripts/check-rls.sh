#!/bin/bash
# Script to check Row Level Security (RLS) status for all tables

echo "=== Checking RLS Status for All Tables ==="
echo ""

# Connect to Supabase and check RLS status
supabase db remote --db-url "$DATABASE_URL" execute "
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;
"

echo ""
echo "=== Checking Existing RLS Policies ==="
echo ""

supabase db remote --db-url "$DATABASE_URL" execute "
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
"

