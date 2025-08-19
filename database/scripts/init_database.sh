#!/bin/bash

# ClickHouse Database Initialization Script
# This script creates the aideps database and all required tables

echo "========================================="
echo "AI Data Preparation System (AIDEPS)"
echo "ClickHouse Database Initialization"
echo "========================================="

# Configuration
CLICKHOUSE_HOST="localhost"
CLICKHOUSE_PORT="9000"
CLICKHOUSE_USER="default"
CLICKHOUSE_PASSWORD="clickhouse"
DATABASE_NAME="aideps"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to execute SQL file
execute_sql_file() {
    local sql_file=$1
    local description=$2
    
    echo -e "${YELLOW}Executing: ${description}${NC}"
    
    clickhouse-client \
        --host=${CLICKHOUSE_HOST} \
        --port=${CLICKHOUSE_PORT} \
        --user=${CLICKHOUSE_USER} \
        --password=${CLICKHOUSE_PASSWORD} \
        --queries-file=${sql_file} \
        --multiquery
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${description} completed successfully${NC}"
    else
        echo -e "${RED}✗ Error executing ${description}${NC}"
        exit 1
    fi
}

# Check if clickhouse-client is installed
if ! command -v clickhouse-client &> /dev/null; then
    echo -e "${RED}Error: clickhouse-client is not installed${NC}"
    echo "Please install ClickHouse client first"
    exit 1
fi

# Test connection to ClickHouse
echo "Testing ClickHouse connection..."
clickhouse-client \
    --host=${CLICKHOUSE_HOST} \
    --port=${CLICKHOUSE_PORT} \
    --user=${CLICKHOUSE_USER} \
    --password=${CLICKHOUSE_PASSWORD} \
    --query="SELECT 1" &> /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Cannot connect to ClickHouse server${NC}"
    echo "Please ensure ClickHouse is running and accessible"
    exit 1
fi

echo -e "${GREEN}✓ ClickHouse connection successful${NC}"
echo ""

# Create database and tables
echo "Creating database and tables..."
execute_sql_file "01_create_database.sql" "Database and table creation"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Database initialization completed!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Database: ${DATABASE_NAME}"
echo "Host: ${CLICKHOUSE_HOST}:${CLICKHOUSE_PORT}"
echo ""
echo "You can now connect using:"
echo "  clickhouse-client --host=${CLICKHOUSE_HOST} --port=${CLICKHOUSE_PORT} --user=${CLICKHOUSE_USER} --password=${CLICKHOUSE_PASSWORD} --database=${DATABASE_NAME}"