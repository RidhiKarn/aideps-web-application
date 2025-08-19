#!/bin/bash

# Master test runner for AIDEPS application
# Runs all test suites and generates a report

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

TEST_DIR="/mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/test_ui"
REPORT_FILE="${TEST_DIR}/test_report_$(date +%Y%m%d_%H%M%S).txt"

echo -e "${BOLD}${BLUE}================================================${NC}"
echo -e "${BOLD}${BLUE}    AIDEPS COMPREHENSIVE TEST SUITE${NC}"
echo -e "${BOLD}${BLUE}================================================${NC}"
echo ""

# Function to run a test and capture results
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${BOLD}Running: ${test_name}${NC}"
    echo "----------------------------------------"
    
    # Run test and capture output
    if eval $test_command > /tmp/test_output.txt 2>&1; then
        echo -e "${GREEN}✓ ${test_name} completed${NC}"
        echo "=== ${test_name} ===" >> $REPORT_FILE
        cat /tmp/test_output.txt >> $REPORT_FILE
        echo "" >> $REPORT_FILE
        return 0
    else
        echo -e "${RED}✗ ${test_name} failed${NC}"
        echo "=== ${test_name} FAILED ===" >> $REPORT_FILE
        cat /tmp/test_output.txt >> $REPORT_FILE
        echo "" >> $REPORT_FILE
        return 1
    fi
}

# Initialize report
echo "AIDEPS Test Report - $(date)" > $REPORT_FILE
echo "================================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Check if services are running
echo -e "${BOLD}${BLUE}1. Service Status Check${NC}"
echo "----------------------------------------"

# Check backend
if curl -s http://172.25.82.250:8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
    echo "Backend: RUNNING" >> $REPORT_FILE
else
    echo -e "${RED}✗ Backend is not running${NC}"
    echo "Backend: NOT RUNNING" >> $REPORT_FILE
    echo -e "${YELLOW}Please start the backend first:${NC}"
    echo "cd /mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/backend && python main.py"
fi

# Check frontend
if curl -s http://172.25.82.250:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
    echo "Frontend: RUNNING" >> $REPORT_FILE
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    echo "Frontend: NOT RUNNING" >> $REPORT_FILE
    echo -e "${YELLOW}Please start the frontend first:${NC}"
    echo "cd /mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/frontend && npm start"
fi

echo ""

# Run test suites
echo -e "${BOLD}${BLUE}2. Running Test Suites${NC}"
echo "----------------------------------------"

# Python API tests
run_test "API Tests" "python3 ${TEST_DIR}/test_application.py"

# Navigation tests
run_test "Navigation Tests" "bash ${TEST_DIR}/test_ui_navigation.sh"

# Frontend component tests
run_test "Component Tests" "python3 ${TEST_DIR}/test_components.py"

# Integration tests
run_test "Integration Tests" "python3 ${TEST_DIR}/test_integration.py"

# Performance tests
run_test "Performance Tests" "python3 ${TEST_DIR}/test_performance.py"

echo ""
echo -e "${BOLD}${BLUE}3. Test Summary${NC}"
echo "----------------------------------------"

# Count results from report
passed=$(grep -c "✓" $REPORT_FILE 2>/dev/null || echo 0)
failed=$(grep -c "✗" $REPORT_FILE 2>/dev/null || echo 0)
warnings=$(grep -c "⚠" $REPORT_FILE 2>/dev/null || echo 0)

echo -e "${GREEN}Passed: ${passed} tests${NC}"
echo -e "${RED}Failed: ${failed} tests${NC}"
echo -e "${YELLOW}Warnings: ${warnings} issues${NC}"

echo ""
echo -e "${BOLD}${BLUE}Test report saved to:${NC}"
echo "$REPORT_FILE"

echo ""
if [ $failed -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}✗ SOME TESTS FAILED${NC}"
    echo "Review the report for details: $REPORT_FILE"
    exit 1
fi