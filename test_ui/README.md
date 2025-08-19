# AIDEPS Comprehensive Test Suite

This directory contains a complete testing framework for the AIDEPS application, covering all aspects of functionality, performance, and integration.

## Test Files

### 1. `test_application.py`
**Purpose**: Core API and backend functionality testing
- Backend health checks
- API endpoint validation
- File upload testing (positive & negative cases)
- Document operations
- Workflow operations
- Stage operations
- Error handling
- CORS configuration

### 2. `test_ui_navigation.sh`
**Purpose**: UI navigation and route testing
- All frontend routes accessibility
- Protected route behavior
- Static asset loading
- Error page handling
- API route verification

### 3. `test_components.py`
**Purpose**: Component-level testing
- React component verification
- Material-UI integration
- Chart components (Recharts)
- Form components
- Navigation components
- State management (Zustand)
- Notification system

### 4. `test_integration.py`
**Purpose**: End-to-end integration testing
- Complete workflow testing (7 stages)
- Data persistence across stages
- Error recovery mechanisms
- Concurrent workflow handling
- Data flow validation

### 5. `test_performance.py`
**Purpose**: Performance and load testing
- Response time measurement
- File upload performance (various sizes)
- Concurrent request handling
- Stress testing
- Memory leak detection
- Caching effectiveness

### 6. `run_all_tests.sh`
**Purpose**: Master test runner
- Runs all test suites sequentially
- Generates comprehensive report
- Service status verification
- Results aggregation

## Prerequisites

### Required Services
```bash
# Backend must be running
cd /mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/backend
python main.py

# Frontend must be running
cd /mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/frontend
npm start
```

### Python Dependencies
```bash
pip install requests pandas
```

## Running Tests

### Run All Tests
```bash
cd /mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/test_ui
bash run_all_tests.sh
```

### Run Individual Test Suites

#### API Tests
```bash
python3 test_application.py
```

#### Navigation Tests
```bash
bash test_ui_navigation.sh
```

#### Component Tests
```bash
python3 test_components.py
```

#### Integration Tests
```bash
python3 test_integration.py
```

#### Performance Tests
```bash
python3 test_performance.py
```

## Test Coverage

### Positive Tests ✅
- Valid file uploads
- Correct authentication
- Successful stage transitions
- Valid API requests
- Proper navigation flow
- Component rendering
- Data persistence

### Negative Tests ❌
- Invalid file uploads
- Wrong credentials
- Missing required fields
- Invalid API requests
- Non-existent routes
- Error recovery
- Concurrent operation conflicts

### Performance Tests ⚡
- Response time benchmarks
- Load handling (concurrent users)
- Large file processing
- Memory usage patterns
- Caching effectiveness
- Stress limits

## Test Results Interpretation

### Response Time Ratings
- **Excellent**: < 100ms ✨
- **Good**: 100-500ms ✅
- **Acceptable**: 500-1000ms ⚠️
- **Slow**: 1000-2000ms 🐌
- **Very Slow**: > 2000ms ❌

### Status Codes
- **200/201**: Success ✅
- **400/422**: Validation error (expected for negative tests) ⚠️
- **404**: Not found (may be expected) ℹ️
- **500**: Server error ❌

## Test Reports

Test reports are automatically generated in:
```
/mnt/c/Users/priya/claude/misc/ai_data_prep_rep_gen/test_ui/test_report_YYYYMMDD_HHMMSS.txt
```

## Continuous Testing

For continuous testing during development:

```bash
# Watch mode (requires inotify-tools)
while true; do
    clear
    python3 test_application.py
    sleep 5
done
```

## Troubleshooting

### Common Issues

1. **Services not running**
   - Start backend and frontend first
   - Check ports 8000 and 3000 are available

2. **CORS errors**
   - Ensure backend has proper CORS configuration
   - Check origin headers in requests

3. **Timeout errors**
   - Increase timeout values in test scripts
   - Check network connectivity

4. **Import errors**
   - Install required Python packages
   - Use Python 3.6+

## Performance Benchmarks

Expected performance metrics:

| Operation | Target | Acceptable |
|-----------|--------|------------|
| API Root | < 50ms | < 200ms |
| File Upload (1MB) | < 500ms | < 2000ms |
| Document Retrieval | < 100ms | < 500ms |
| Stage Processing | < 1000ms | < 5000ms |
| Concurrent Users | 20 | 10 |

## Contributing

To add new tests:

1. Create test file in this directory
2. Follow naming convention: `test_*.py` or `test_*.sh`
3. Use consistent output format (✓/✗/⚠/ℹ)
4. Add to `run_all_tests.sh`
5. Update this README

## Test Automation

For CI/CD integration:

```yaml
# Example GitHub Actions workflow
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: |
          docker-compose up -d
      - name: Run tests
        run: |
          cd test_ui
          bash run_all_tests.sh
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: test_ui/test_report_*.txt
```

## Summary

This comprehensive test suite ensures:
- ✅ All functionality works correctly
- ✅ Performance meets requirements
- ✅ System handles errors gracefully
- ✅ Integration between components is solid
- ✅ User experience is smooth

Run these tests regularly to maintain application quality!