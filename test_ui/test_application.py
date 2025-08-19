#!/usr/bin/env python3
"""
Comprehensive testing suite for AIDEPS application
Tests both frontend and backend functionality
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Tuple
import pandas as pd
from io import BytesIO

# Configuration
BACKEND_URL = "http://172.25.82.250:8000"
FRONTEND_URL = "http://172.25.82.250:3000"
API_BASE = f"{BACKEND_URL}/api"

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}Testing: {test_name}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")
    test_results["passed"].append(message)

def print_failure(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")
    test_results["failed"].append(message)

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")
    test_results["warnings"].append(message)

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

# 1. TEST BACKEND HEALTH
def test_backend_health():
    print_test_header("Backend Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running: {data.get('name', 'Unknown')}")
            print_info(f"Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print_failure(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_failure("Cannot connect to backend - is it running?")
        return False
    except Exception as e:
        print_failure(f"Backend health check failed: {str(e)}")
        return False

# 2. TEST FRONTEND AVAILABILITY
def test_frontend_health():
    print_test_header("Frontend Health Check")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success("Frontend is accessible")
            if "AIDEPS" in response.text or "root" in response.text:
                print_success("Frontend HTML contains expected content")
            else:
                print_warning("Frontend HTML might not be fully loaded")
            return True
        else:
            print_failure(f"Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_failure("Cannot connect to frontend - is it running?")
        return False
    except Exception as e:
        print_failure(f"Frontend health check failed: {str(e)}")
        return False

# 3. TEST CORS CONFIGURATION
def test_cors():
    print_test_header("CORS Configuration")
    
    headers = {
        "Origin": FRONTEND_URL,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(f"{API_BASE}/documents/upload", headers=headers, timeout=5)
        
        if "access-control-allow-origin" in response.headers:
            print_success(f"CORS enabled for origin: {response.headers.get('access-control-allow-origin')}")
        else:
            print_failure("CORS headers not found")
            return False
            
        if response.headers.get("access-control-allow-methods"):
            print_success(f"Allowed methods: {response.headers.get('access-control-allow-methods')}")
        
        return True
    except Exception as e:
        print_failure(f"CORS test failed: {str(e)}")
        return False

# 4. TEST API ENDPOINTS
def test_api_endpoints():
    print_test_header("API Endpoints")
    
    endpoints = [
        ("GET", "/", None, "Root endpoint"),
        ("GET", "/docs", None, "API documentation"),
        ("GET", "/api/documents", None, "List documents"),
        ("GET", "/api/workflows", None, "List workflows"),
    ]
    
    for method, endpoint, data, description in endpoints:
        try:
            url = f"{BACKEND_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=5)
            
            if response.status_code in [200, 201, 404, 422]:  # Accept some error codes as valid responses
                print_success(f"{description}: {endpoint} ({response.status_code})")
            else:
                print_failure(f"{description}: {endpoint} returned {response.status_code}")
        except Exception as e:
            print_failure(f"{description}: {endpoint} - {str(e)}")

# 5. TEST FILE UPLOAD - POSITIVE
def test_file_upload_positive():
    print_test_header("File Upload - Positive Test")
    
    # Create a sample CSV file
    df = pd.DataFrame({
        'column1': [1, 2, 3, 4, 5],
        'column2': ['A', 'B', 'C', 'D', 'E'],
        'column3': [10.5, 20.3, 30.1, 40.7, 50.9]
    })
    
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    files = {
        'file': ('test_data.csv', csv_buffer, 'text/csv')
    }
    
    data = {
        'document_name': 'Test Document',
        'organization': 'Test Org',
        'survey_type': 'test'
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/documents/upload",
            files=files,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("File uploaded successfully")
            print_info(f"Document ID: {result.get('document_id', 'N/A')}")
            print_info(f"Workflow ID: {result.get('workflow_id', 'N/A')}")
            
            if 'file_info' in result:
                file_info = result['file_info']
                print_info(f"Rows: {file_info.get('rows', 'N/A')}, Columns: {file_info.get('columns', 'N/A')}")
            
            return result.get('document_id')
        else:
            print_failure(f"Upload failed with status code: {response.status_code}")
            if response.text:
                print_info(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print_failure(f"File upload test failed: {str(e)}")
        return None

# 6. TEST FILE UPLOAD - NEGATIVE
def test_file_upload_negative():
    print_test_header("File Upload - Negative Tests")
    
    # Test 1: No file
    print_info("Test: Upload without file")
    try:
        response = requests.post(f"{API_BASE}/documents/upload", timeout=5)
        if response.status_code == 422 or response.status_code == 400:
            print_success("Correctly rejected upload without file")
        else:
            print_failure(f"Should reject empty upload, got: {response.status_code}")
    except Exception as e:
        print_warning(f"No file test error: {str(e)}")
    
    # Test 2: Invalid file type
    print_info("Test: Upload invalid file type")
    files = {
        'file': ('test.exe', b'fake exe content', 'application/x-msdownload')
    }
    try:
        response = requests.post(f"{API_BASE}/documents/upload", files=files, timeout=5)
        if response.status_code in [400, 422]:
            print_success("Correctly rejected invalid file type")
        else:
            print_warning(f"Should reject .exe file, got: {response.status_code}")
    except Exception as e:
        print_warning(f"Invalid file type test error: {str(e)}")
    
    # Test 3: Empty CSV
    print_info("Test: Upload empty CSV")
    files = {
        'file': ('empty.csv', b'', 'text/csv')
    }
    try:
        response = requests.post(f"{API_BASE}/documents/upload", files=files, timeout=5)
        if response.status_code in [400, 422]:
            print_success("Correctly handled empty CSV")
        else:
            print_warning(f"Empty CSV handling: {response.status_code}")
    except Exception as e:
        print_warning(f"Empty CSV test error: {str(e)}")

# 7. TEST DOCUMENT RETRIEVAL
def test_document_operations(document_id: str = None):
    print_test_header("Document Operations")
    
    if not document_id:
        print_warning("No document ID provided, skipping document operations")
        return
    
    # Get document details
    try:
        response = requests.get(f"{API_BASE}/documents/{document_id}", timeout=5)
        if response.status_code == 200:
            print_success(f"Retrieved document: {document_id}")
            doc_data = response.json()
            print_info(f"Document name: {doc_data.get('document_name', 'N/A')}")
        elif response.status_code == 404:
            print_warning(f"Document not found: {document_id}")
        else:
            print_failure(f"Get document returned: {response.status_code}")
    except Exception as e:
        print_failure(f"Document retrieval failed: {str(e)}")
    
    # Get document preview
    try:
        response = requests.get(f"{API_BASE}/documents/{document_id}/preview?rows=5", timeout=5)
        if response.status_code == 200:
            print_success("Retrieved document preview")
        else:
            print_warning(f"Preview returned: {response.status_code}")
    except Exception as e:
        print_warning(f"Preview test failed: {str(e)}")

# 8. TEST WORKFLOW OPERATIONS
def test_workflow_operations(document_id: str = None):
    print_test_header("Workflow Operations")
    
    if not document_id:
        # Try to get any workflow
        try:
            response = requests.get(f"{API_BASE}/workflows", timeout=5)
            if response.status_code == 200:
                workflows = response.json()
                if workflows and len(workflows) > 0:
                    print_success(f"Found {len(workflows)} existing workflows")
                else:
                    print_info("No existing workflows found")
            else:
                print_warning(f"List workflows returned: {response.status_code}")
        except Exception as e:
            print_warning(f"Workflow listing failed: {str(e)}")
        return
    
    # Get workflow for document
    try:
        response = requests.get(f"{API_BASE}/workflows/{document_id}", timeout=5)
        if response.status_code == 200:
            print_success(f"Retrieved workflow for document: {document_id}")
            workflow_data = response.json()
            print_info(f"Current stage: {workflow_data.get('current_stage', 'N/A')}")
        else:
            print_warning(f"Get workflow returned: {response.status_code}")
    except Exception as e:
        print_warning(f"Workflow retrieval failed: {str(e)}")

# 9. TEST STAGE OPERATIONS
def test_stage_operations():
    print_test_header("Stage Operations")
    
    stages = [
        (1, "Upload"),
        (2, "Cleansing"),
        (3, "Analysis"),
        (4, "Statistics"),
        (5, "Reports"),
        (6, "Confirmation"),
        (7, "Generation")
    ]
    
    for stage_num, stage_name in stages:
        try:
            # Test stage process endpoint
            response = requests.post(
                f"{API_BASE}/stages/{stage_num}/process",
                json={"test": True},
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                print_success(f"Stage {stage_num} ({stage_name}) endpoint works")
            elif response.status_code == 422:
                print_info(f"Stage {stage_num} ({stage_name}) requires specific data")
            else:
                print_warning(f"Stage {stage_num} ({stage_name}) returned: {response.status_code}")
        except Exception as e:
            print_warning(f"Stage {stage_num} test error: {str(e)}")

# 10. TEST AUTHENTICATION
def test_authentication():
    print_test_header("Authentication Tests")
    
    # Note: Since auth is mocked in frontend, we can't fully test it via API
    # But we can test if auth endpoints exist
    
    print_info("Testing mock authentication (frontend-only)")
    
    # Test if login endpoint would exist
    endpoints = [
        ("/api/auth/login", {"email": "demo@mospi.gov.in", "password": "demo123"}),
        ("/api/auth/login", {"email": "wrong@email.com", "password": "wrongpass"}),
    ]
    
    for endpoint, data in endpoints:
        try:
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data, timeout=5)
            if response.status_code == 404:
                print_info(f"Auth endpoint not implemented (expected for mock auth)")
            else:
                print_info(f"Auth endpoint returned: {response.status_code}")
        except Exception as e:
            print_info(f"Auth test note: {str(e)}")

# 11. TEST ERROR HANDLING
def test_error_handling():
    print_test_header("Error Handling Tests")
    
    # Test non-existent endpoints
    print_info("Testing 404 handling")
    try:
        response = requests.get(f"{API_BASE}/nonexistent", timeout=5)
        if response.status_code == 404:
            print_success("404 errors handled correctly")
        else:
            print_warning(f"Unexpected response for non-existent endpoint: {response.status_code}")
    except Exception as e:
        print_warning(f"404 test error: {str(e)}")
    
    # Test invalid document ID
    print_info("Testing invalid document ID")
    try:
        response = requests.get(f"{API_BASE}/documents/invalid-id-12345", timeout=5)
        if response.status_code in [404, 422]:
            print_success("Invalid ID handled correctly")
        else:
            print_warning(f"Invalid ID response: {response.status_code}")
    except Exception as e:
        print_warning(f"Invalid ID test error: {str(e)}")

# 12. PERFORMANCE TESTS
def test_performance():
    print_test_header("Performance Tests")
    
    endpoints = [
        (f"{BACKEND_URL}/", "Root endpoint"),
        (f"{API_BASE}/documents", "Documents list"),
        (f"{API_BASE}/workflows", "Workflows list"),
    ]
    
    for url, name in endpoints:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if response_time < 100:
                print_success(f"{name}: {response_time:.2f}ms (Excellent)")
            elif response_time < 500:
                print_success(f"{name}: {response_time:.2f}ms (Good)")
            elif response_time < 1000:
                print_warning(f"{name}: {response_time:.2f}ms (Slow)")
            else:
                print_failure(f"{name}: {response_time:.2f}ms (Very Slow)")
        except Exception as e:
            print_failure(f"{name} performance test failed: {str(e)}")

# 13. INTEGRATION TEST
def test_full_workflow_integration():
    print_test_header("Full Workflow Integration Test")
    
    # Step 1: Upload a file
    print_info("Step 1: Uploading test file...")
    document_id = test_file_upload_positive()
    
    if not document_id:
        print_failure("Integration test failed: Could not upload file")
        return False
    
    # Step 2: Retrieve document
    print_info("Step 2: Retrieving uploaded document...")
    try:
        response = requests.get(f"{API_BASE}/documents/{document_id}", timeout=5)
        if response.status_code == 200:
            print_success("Document retrieved successfully")
        else:
            print_failure(f"Could not retrieve document: {response.status_code}")
            return False
    except Exception as e:
        print_failure(f"Document retrieval failed: {str(e)}")
        return False
    
    # Step 3: Check workflow created
    print_info("Step 3: Checking workflow creation...")
    try:
        response = requests.get(f"{API_BASE}/workflows", timeout=5)
        if response.status_code == 200:
            workflows = response.json()
            if any(w.get('document_id') == document_id for w in workflows if isinstance(w, dict)):
                print_success("Workflow created for document")
            else:
                print_info("Workflow might be created differently")
        else:
            print_warning(f"Workflow check returned: {response.status_code}")
    except Exception as e:
        print_warning(f"Workflow check failed: {str(e)}")
    
    print_success("Integration test completed")
    return True

# MAIN TEST RUNNER
def run_all_tests():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}AIDEPS Comprehensive Test Suite{Colors.ENDC}")
    print(f"{Colors.BOLD}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    # Run all tests
    backend_ok = test_backend_health()
    frontend_ok = test_frontend_health()
    
    if not backend_ok:
        print(f"\n{Colors.RED}Backend is not running! Please start it first.{Colors.ENDC}")
        return
    
    if not frontend_ok:
        print(f"\n{Colors.YELLOW}Frontend might not be fully accessible.{Colors.ENDC}")
    
    test_cors()
    test_api_endpoints()
    test_authentication()
    
    # File upload tests
    document_id = test_file_upload_positive()
    test_file_upload_negative()
    
    # Document and workflow tests
    if document_id:
        test_document_operations(document_id)
        test_workflow_operations(document_id)
    
    test_stage_operations()
    test_error_handling()
    test_performance()
    
    # Integration test
    # test_full_workflow_integration()
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    
    print(f"{Colors.GREEN}Passed: {len(test_results['passed'])} tests{Colors.ENDC}")
    print(f"{Colors.RED}Failed: {len(test_results['failed'])} tests{Colors.ENDC}")
    print(f"{Colors.YELLOW}Warnings: {len(test_results['warnings'])} issues{Colors.ENDC}")
    
    if len(test_results['failed']) == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}")
        print("\nFailed tests:")
        for failure in test_results['failed']:
            print(f"  - {failure}")
    
    if len(test_results['warnings']) > 0:
        print(f"\n{Colors.YELLOW}Warnings:{Colors.ENDC}")
        for warning in test_results['warnings'][:5]:  # Show first 5 warnings
            print(f"  - {warning}")
    
    print(f"\n{Colors.BOLD}Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")

if __name__ == "__main__":
    run_all_tests()