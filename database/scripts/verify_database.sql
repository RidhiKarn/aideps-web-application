-- Verify Database Setup
-- This script checks if all tables are created properly

USE aideps;

-- Show all tables in the database
SELECT '========== Tables in aideps database ==========' as info;
SHOW TABLES;

-- Count tables
SELECT '========== Table Count ==========' as info;
SELECT count(*) as table_count FROM system.tables WHERE database = 'aideps';

-- Check each table structure
SELECT '========== Table Structures ==========' as info;

SELECT '--- documents table ---' as table_info;
DESCRIBE TABLE documents;

SELECT '--- workflows table ---' as table_info;
DESCRIBE TABLE workflows;

SELECT '--- workflow_stages table ---' as table_info;
DESCRIBE TABLE workflow_stages;

SELECT '--- data_snapshots table ---' as table_info;
DESCRIBE TABLE data_snapshots;

SELECT '--- stage_configs table ---' as table_info;
DESCRIBE TABLE stage_configs;

SELECT '--- data_quality_metrics table ---' as table_info;
DESCRIBE TABLE data_quality_metrics;

SELECT '--- cleansing_operations table ---' as table_info;
DESCRIBE TABLE cleansing_operations;

SELECT '--- statistical_results table ---' as table_info;
DESCRIBE TABLE statistical_results;

SELECT '--- reports table ---' as table_info;
DESCRIBE TABLE reports;

SELECT '--- audit_log table ---' as table_info;
DESCRIBE TABLE audit_log;

-- Check materialized views
SELECT '========== Materialized Views ==========' as info;
SELECT name FROM system.tables 
WHERE database = 'aideps' 
AND engine LIKE '%MaterializedView%';

-- Check table engines
SELECT '========== Table Engines ==========' as info;
SELECT 
    name as table_name,
    engine
FROM system.tables 
WHERE database = 'aideps'
ORDER BY name;