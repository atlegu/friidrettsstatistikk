-- Migration: Remove unused indexes
-- Date: 2026-01-27
--
-- This migration removes indexes that are unused according to Supabase Performance Advisor.
--
-- Before running, you can check index usage with:
-- SELECT
--   schemaname,
--   relname AS table_name,
--   indexrelname AS index_name,
--   idx_scan AS times_used,
--   pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
-- FROM pg_stat_user_indexes
-- WHERE idx_scan = 0
--   AND schemaname = 'public'
-- ORDER BY pg_relation_size(indexrelid) DESC;

-- Common unused indexes to remove (verify these exist before running):

-- Remove duplicate indexes on foreign keys (if primary keys already cover them)
-- Example: DROP INDEX IF EXISTS idx_results_athlete;  -- if covered by another index

-- Remove indexes on low-cardinality columns
-- Example: DROP INDEX IF EXISTS idx_results_status;  -- status has only a few values

-- Remove indexes that duplicate the primary key
-- Example: DROP INDEX IF EXISTS idx_athletes_id;  -- primary key already indexed

-- IMPORTANT: Review the actual unused indexes in your Supabase dashboard
-- Go to: Database → Performance → Indexes → Unused Indexes
-- Then uncomment and run the appropriate DROP statements below.

-- Example removals (uncomment after verifying):
-- DROP INDEX IF EXISTS public.idx_results_approved;
-- DROP INDEX IF EXISTS public.idx_results_outdoor;

-- To identify actual unused indexes in your database, run this query first:
SELECT
  schemaname || '.' || indexrelname AS full_index_name,
  relname AS table_name,
  idx_scan AS times_used,
  idx_tup_read AS tuples_read,
  idx_tup_fetch AS tuples_fetched,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC
LIMIT 20;
