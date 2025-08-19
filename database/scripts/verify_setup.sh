#!/bin/bash

# Verify ClickHouse Database Setup

echo "========================================="
echo "Verifying AIDEPS Database Setup"
echo "========================================="

# Configuration
CLICKHOUSE_HOST="localhost"
CLICKHOUSE_PORT="9000"
CLICKHOUSE_USER="default"
CLICKHOUSE_PASSWORD="clickhouse"

# Run verification queries
clickhouse-client \
    --host=${CLICKHOUSE_HOST} \
    --port=${CLICKHOUSE_PORT} \
    --user=${CLICKHOUSE_USER} \
    --password=${CLICKHOUSE_PASSWORD} \
    --queries-file=verify_database.sql \
    --multiquery \
    --format=Pretty

echo ""
echo "Verification complete!"