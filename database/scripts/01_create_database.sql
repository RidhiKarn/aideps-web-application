-- ClickHouse Database Initialization Script
-- Database: aideps (AI Data Preparation System)

-- Drop existing database if exists (clean start)
DROP DATABASE IF EXISTS aideps;

-- Create database
CREATE DATABASE aideps;

USE aideps;

-- 1. Documents table - stores survey dataset metadata
CREATE TABLE IF NOT EXISTS documents (
    document_id UUID DEFAULT generateUUIDv4(),
    document_name String,
    original_filename String,
    upload_date DateTime DEFAULT now(),
    file_path String,
    file_size UInt64,
    file_type String,
    file_hash String,
    user_id String,
    organization String,
    survey_type String,
    survey_year UInt16,
    status String DEFAULT 'uploaded',
    row_count UInt64,
    column_count UInt16,
    metadata String, -- JSON string
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (document_id, upload_date)
PARTITION BY toYYYYMM(upload_date);

-- 2. Workflows table - tracks workflow instances
CREATE TABLE IF NOT EXISTS workflows (
    workflow_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_name String,
    current_stage UInt8 DEFAULT 1,
    total_stages UInt8 DEFAULT 7,
    status String DEFAULT 'active',
    started_at DateTime DEFAULT now(),
    completed_at Nullable(DateTime),
    created_by String,
    last_modified_by String,
    configuration String, -- JSON string
    metadata String -- JSON string
) ENGINE = MergeTree()
ORDER BY (workflow_id, started_at)
PARTITION BY toYYYYMM(started_at);

-- 3. Workflow stages - detailed stage execution history
CREATE TABLE IF NOT EXISTS workflow_stages (
    stage_id UUID DEFAULT generateUUIDv4(),
    workflow_id UUID,
    document_id UUID,
    stage_number UInt8,
    stage_name String,
    stage_type String,
    status String DEFAULT 'pending',
    started_at DateTime DEFAULT now(),  -- Changed from Nullable
    completed_at Nullable(DateTime),
    duration_seconds Nullable(UInt32),
    executed_by Nullable(String),
    input_data String, -- JSON string
    output_data String, -- JSON string
    user_actions String, -- JSON string
    automated_actions String, -- JSON string
    validation_results String, -- JSON string
    error_log Nullable(String),
    retry_count UInt8 DEFAULT 0
) ENGINE = MergeTree()
ORDER BY (workflow_id, stage_number, started_at)
PARTITION BY toYYYYMM(started_at);

-- 4. Data snapshots - versioned data at each stage
CREATE TABLE IF NOT EXISTS data_snapshots (
    snapshot_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    snapshot_type String, -- 'full', 'delta', 'metadata'
    data_version String,
    row_count UInt64,
    column_count UInt16,
    snapshot_path String,
    storage_format String, -- 'parquet', 'csv', 'json'
    compression_type String,
    file_size_bytes UInt64,
    checksum String,
    schema_info String, -- JSON string
    statistics String, -- JSON string with basic stats
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (document_id, workflow_id, stage_number, created_at)
PARTITION BY toYYYYMM(created_at);

-- 5. Stage configurations - user choices and settings per stage
CREATE TABLE IF NOT EXISTS stage_configs (
    config_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    config_type String, -- 'imputation', 'outlier', 'validation', 'weights', 'report'
    config_name String,
    config_data String, -- JSON string
    is_active UInt8 DEFAULT 1,
    created_at DateTime DEFAULT now(),
    created_by String,
    updated_at DateTime DEFAULT now(),
    updated_by String
) ENGINE = MergeTree()
ORDER BY (workflow_id, stage_number, config_type, created_at);

-- 6. Data quality metrics - track quality at each stage
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    metric_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    metric_type String, -- 'completeness', 'consistency', 'validity', 'accuracy'
    metric_name String,
    metric_value Float64,
    metric_details String, -- JSON string
    calculated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (workflow_id, stage_number, calculated_at)
PARTITION BY toYYYYMM(calculated_at);

-- 7. Cleansing operations log
CREATE TABLE IF NOT EXISTS cleansing_operations (
    operation_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    operation_type String, -- 'imputation', 'outlier_removal', 'transformation'
    column_name String,
    operation_method String,
    parameters String, -- JSON string
    rows_affected UInt64,
    values_changed UInt64,
    before_snapshot String, -- JSON sample
    after_snapshot String, -- JSON sample
    executed_at DateTime DEFAULT now(),
    executed_by String
) ENGINE = MergeTree()
ORDER BY (workflow_id, executed_at);

-- 8. Statistical results
CREATE TABLE IF NOT EXISTS statistical_results (
    result_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    analysis_type String, -- 'descriptive', 'weighted', 'correlation', 'regression'
    variable_name String,
    group_by Nullable(String),
    statistic_name String,
    statistic_value Float64,
    standard_error Nullable(Float64),
    confidence_level Nullable(Float32),
    confidence_interval_lower Nullable(Float64),
    confidence_interval_upper Nullable(Float64),
    sample_size UInt64,
    weighted UInt8 DEFAULT 0,
    weight_variable Nullable(String),
    additional_stats String, -- JSON string
    calculated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (workflow_id, analysis_type, variable_name, calculated_at);

-- 9. Generated reports
CREATE TABLE IF NOT EXISTS reports (
    report_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    report_type String, -- 'preliminary', 'final', 'summary', 'detailed'
    report_format String, -- 'pdf', 'html', 'excel', 'json'
    report_template String,
    file_path String,
    file_size_bytes UInt64,
    report_sections String, -- JSON array of sections
    generated_at DateTime DEFAULT now(),
    generated_by String,
    reviewed_by Nullable(String),
    reviewed_at Nullable(DateTime),
    approval_status String DEFAULT 'pending',
    metadata String -- JSON string
) ENGINE = MergeTree()
ORDER BY (workflow_id, generated_at);

-- 10. Audit log - comprehensive audit trail
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id Nullable(UUID),
    stage_number Nullable(UInt8),
    action_category String, -- 'data', 'workflow', 'system', 'user'
    action_type String,
    action_details String, -- JSON string
    user_id String,
    user_role String,
    ip_address String,
    user_agent String,
    session_id String,
    timestamp DateTime DEFAULT now(),
    response_status String,
    response_time_ms UInt32,
    error_details Nullable(String)
) ENGINE = MergeTree()
ORDER BY (document_id, timestamp)
PARTITION BY toYYYYMM(timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- 11. User sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id String,
    user_id String,
    workflow_id Nullable(UUID),
    login_time DateTime,
    last_activity DateTime,
    logout_time Nullable(DateTime),
    ip_address String,
    user_agent String,
    is_active UInt8 DEFAULT 1
) ENGINE = MergeTree()
ORDER BY (user_id, login_time)
TTL last_activity + INTERVAL 30 DAY;

-- 12. Processing queue - for async task management
CREATE TABLE IF NOT EXISTS processing_queue (
    task_id UUID DEFAULT generateUUIDv4(),
    workflow_id UUID,
    stage_number UInt8,
    task_type String,
    priority UInt8 DEFAULT 5, -- 1-10, 1 is highest
    status String DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    payload String, -- JSON string
    retry_count UInt8 DEFAULT 0,
    max_retries UInt8 DEFAULT 3,
    created_at DateTime DEFAULT now(),
    started_at Nullable(DateTime),
    completed_at Nullable(DateTime),
    error_message Nullable(String)
) ENGINE = MergeTree()
ORDER BY (priority, created_at);

-- 13. Variable metadata - track variable properties through workflow
CREATE TABLE IF NOT EXISTS variable_metadata (
    metadata_id UUID DEFAULT generateUUIDv4(),
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    variable_name String,
    variable_type String, -- 'numeric', 'categorical', 'ordinal', 'binary', 'datetime'
    data_type String, -- actual data type
    is_key_variable UInt8 DEFAULT 0,
    is_weight_variable UInt8 DEFAULT 0,
    is_stratification_variable UInt8 DEFAULT 0,
    missing_count UInt64,
    missing_percentage Float32,
    unique_values UInt64,
    min_value Nullable(String),
    max_value Nullable(String),
    mean_value Nullable(Float64),
    median_value Nullable(Float64),
    mode_value Nullable(String),
    standard_deviation Nullable(Float64),
    metadata String, -- JSON string for additional properties
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (workflow_id, stage_number, variable_name);

-- 14. Validation rules
CREATE TABLE IF NOT EXISTS validation_rules (
    rule_id UUID DEFAULT generateUUIDv4(),
    rule_name String,
    rule_type String, -- 'range', 'pattern', 'consistency', 'business'
    applicable_to String, -- 'column', 'row', 'dataset'
    target_columns Array(String),
    rule_expression String,
    error_severity String, -- 'error', 'warning', 'info'
    error_message String,
    is_active UInt8 DEFAULT 1,
    created_at DateTime DEFAULT now(),
    created_by String
) ENGINE = MergeTree()
ORDER BY (rule_type, created_at);

-- 15. Template library
CREATE TABLE IF NOT EXISTS report_templates (
    template_id UUID DEFAULT generateUUIDv4(),
    template_name String,
    template_type String,
    survey_type String,
    template_content String, -- JSON or HTML template
    template_schema String, -- JSON schema
    variables_required Array(String),
    is_active UInt8 DEFAULT 1,
    version String,
    created_at DateTime DEFAULT now(),
    created_by String,
    updated_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (template_type, template_name);

-- Create indexes for better query performance
ALTER TABLE documents ADD INDEX idx_status (status) TYPE minmax GRANULARITY 4;
ALTER TABLE workflows ADD INDEX idx_status (status) TYPE minmax GRANULARITY 4;
ALTER TABLE workflow_stages ADD INDEX idx_status (status) TYPE minmax GRANULARITY 4;
ALTER TABLE audit_log ADD INDEX idx_user (user_id) TYPE minmax GRANULARITY 4;

-- Create materialized views for common aggregations

-- View for current workflow status
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_workflow_current_status
ENGINE = AggregatingMergeTree()
ORDER BY (workflow_id)
AS SELECT 
    workflow_id,
    document_id,
    maxState(current_stage) as current_stage,
    anyLastState(status) as status,
    minState(started_at) as started_at,
    maxState(completed_at) as completed_at
FROM workflows
GROUP BY workflow_id, document_id;

-- View for stage completion metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_stage_metrics
ENGINE = SummingMergeTree()
ORDER BY (stage_number, status)
AS SELECT 
    stage_number,
    stage_name,
    status,
    count() as count,
    avg(duration_seconds) as avg_duration,
    min(duration_seconds) as min_duration,
    max(duration_seconds) as max_duration
FROM workflow_stages
WHERE duration_seconds IS NOT NULL
GROUP BY stage_number, stage_name, status;

-- View for data quality trends
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_quality_trends
ENGINE = AggregatingMergeTree()
ORDER BY (document_id, metric_type, date)
AS SELECT 
    document_id,
    metric_type,
    toStartOfDay(calculated_at) as date,
    avgState(metric_value) as avg_value,
    minState(metric_value) as min_value,
    maxState(metric_value) as max_value
FROM data_quality_metrics
GROUP BY document_id, metric_type, toStartOfDay(calculated_at);