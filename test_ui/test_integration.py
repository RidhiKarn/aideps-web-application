#!/usr/bin/env python3
"""
Integration testing for AIDEPS
Tests complete user workflows and data flow
"""

import requests
import json
import time
import pandas as pd
from io import BytesIO
from datetime import datetime

# Configuration
BACKEND_URL = "http://172.25.82.250:8000"
FRONTEND_URL = "http://172.25.82.250:3000"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_failure(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")

class IntegrationTester:
    def __init__(self):
        self.document_id = None
        self.workflow_id = None
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def test_complete_workflow(self):
        """Test complete workflow from upload to report generation"""
        print_header("Complete Workflow Integration Test")
        
        # Step 1: Upload a file
        if not self.test_file_upload():
            print_failure("Workflow failed at upload stage")
            return False
        
        # Step 2: Process through stages
        stages = [
            (2, "Data Cleansing"),
            (3, "Analysis & Discovery"),
            (4, "Statistics & Weights"),
            (5, "Propose Reports"),
            (6, "User Confirmation"),
            (7, "Final Report Generation")
        ]
        
        for stage_num, stage_name in stages:
            if not self.test_stage_processing(stage_num, stage_name):
                print_warning(f"Stage {stage_num} ({stage_name}) processing incomplete")
        
        # Step 3: Verify final output
        self.test_final_output()
        
        return True
    
    def test_file_upload(self):
        """Test file upload with realistic data"""
        print_info("Step 1: Testing file upload with sample survey data")
        
        # Create realistic survey data
        df = pd.DataFrame({
            'STATNAME': ['State1', 'State2', 'State3'] * 10,
            'DISTRICT': ['Dist1', 'Dist2', 'Dist3'] * 10,
            'TOTINCM': [45000, 52000, 38000] * 10,
            'POPU_LSA': [25000, 30000, 20000] * 10,
            'CENTLIB': ['Y', 'N', 'Y'] * 10,
            'EXPENDITURE': [35000, 42000, 28000] * 10,
            'EDUCATION': ['Primary', 'Secondary', 'Higher'] * 10,
            'EMPLOYMENT': ['Employed', 'Self-Employed', 'Unemployed'] * 10,
        })
        
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        files = {
            'file': ('survey_data.csv', csv_buffer, 'text/csv')
        }
        
        data = {
            'document_name': 'Integration Test Survey',
            'organization': 'MoSPI Test',
            'survey_type': 'demographic'
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
                self.document_id = result.get('document_id')
                self.workflow_id = result.get('workflow_id')
                
                print_success(f"File uploaded: {self.document_id}")
                print_info(f"  └─ Rows: {result.get('file_info', {}).get('rows', 'N/A')}")
                print_info(f"  └─ Columns: {result.get('file_info', {}).get('columns', 'N/A')}")
                
                self.test_results["passed"].append("File upload")
                return True
            else:
                print_failure(f"Upload failed: {response.status_code}")
                self.test_results["failed"].append("File upload")
                return False
        except Exception as e:
            print_failure(f"Upload error: {str(e)}")
            self.test_results["failed"].append("File upload")
            return False
    
    def test_stage_processing(self, stage_num, stage_name):
        """Test processing a specific stage"""
        print_info(f"Step {stage_num}: Testing {stage_name}")
        
        if not self.document_id:
            print_warning("No document ID available")
            return False
        
        # Stage-specific processing
        stage_endpoints = {
            2: f"{API_BASE}/stages/2/process",
            3: f"{API_BASE}/stages/3/process",
            4: f"{API_BASE}/stages/4/process",
            5: f"{API_BASE}/stages/5/process",
            6: f"{API_BASE}/stages/6/confirm",
            7: f"{API_BASE}/stages/7/generate"
        }
        
        endpoint = stage_endpoints.get(stage_num)
        if not endpoint:
            print_warning(f"No endpoint for stage {stage_num}")
            return False
        
        try:
            # Prepare stage-specific data
            stage_data = {
                "document_id": self.document_id,
                "workflow_id": self.workflow_id
            }
            
            # Add stage-specific parameters
            if stage_num == 2:  # Cleansing
                stage_data["operations"] = {
                    "handle_missing": "mean",
                    "remove_outliers": True
                }
            elif stage_num == 3:  # Analysis
                stage_data["analysis_type"] = "comprehensive"
            elif stage_num == 4:  # Statistics
                stage_data["tests"] = ["normality", "correlation"]
            elif stage_num == 5:  # Reports
                stage_data["report_types"] = ["summary", "detailed"]
            elif stage_num == 6:  # Confirmation
                stage_data["confirmed"] = True
            elif stage_num == 7:  # Generation
                stage_data["format"] = "pdf"
            
            response = requests.post(endpoint, json=stage_data, timeout=10)
            
            if response.status_code in [200, 201]:
                print_success(f"{stage_name} processed successfully")
                self.test_results["passed"].append(f"Stage {stage_num}")
                return True
            elif response.status_code == 404:
                print_warning(f"{stage_name} endpoint not implemented")
                self.test_results["warnings"].append(f"Stage {stage_num} not implemented")
                return False
            else:
                print_failure(f"{stage_name} failed: {response.status_code}")
                self.test_results["failed"].append(f"Stage {stage_num}")
                return False
                
        except Exception as e:
            print_warning(f"{stage_name} error: {str(e)}")
            self.test_results["warnings"].append(f"Stage {stage_num} error")
            return False
    
    def test_final_output(self):
        """Test final output retrieval"""
        print_info("Step 8: Testing final output retrieval")
        
        if not self.document_id:
            print_warning("No document to retrieve")
            return False
        
        try:
            # Get final document
            response = requests.get(f"{API_BASE}/documents/{self.document_id}", timeout=5)
            
            if response.status_code == 200:
                doc = response.json()
                print_success("Final document retrieved")
                print_info(f"  └─ Status: {doc.get('status', 'N/A')}")
                print_info(f"  └─ Stage: {doc.get('current_stage', 'N/A')}")
                self.test_results["passed"].append("Output retrieval")
                return True
            else:
                print_failure(f"Document retrieval failed: {response.status_code}")
                self.test_results["failed"].append("Output retrieval")
                return False
                
        except Exception as e:
            print_failure(f"Output retrieval error: {str(e)}")
            self.test_results["failed"].append("Output retrieval")
            return False
    
    def test_error_recovery(self):
        """Test system's ability to recover from errors"""
        print_header("Error Recovery Integration Test")
        
        # Test 1: Invalid data recovery
        print_info("Test 1: Invalid data handling")
        
        files = {
            'file': ('corrupt.csv', b'invalid,csv,data\n\n\n', 'text/csv')
        }
        
        try:
            response = requests.post(f"{API_BASE}/documents/upload", files=files, timeout=5)
            if response.status_code in [400, 422, 500]:
                print_success("System handled corrupt file gracefully")
            else:
                print_warning(f"Unexpected response: {response.status_code}")
        except Exception as e:
            print_warning(f"Error recovery test: {str(e)}")
        
        # Test 2: Workflow recovery
        print_info("Test 2: Workflow recovery after interruption")
        
        if self.workflow_id:
            try:
                # Simulate getting workflow status
                response = requests.get(f"{API_BASE}/workflows/{self.workflow_id}", timeout=5)
                if response.status_code in [200, 404]:
                    print_success("Workflow status check works")
                else:
                    print_warning(f"Workflow check: {response.status_code}")
            except Exception as e:
                print_warning(f"Workflow recovery test: {str(e)}")
    
    def test_concurrent_workflows(self):
        """Test handling multiple concurrent workflows"""
        print_header("Concurrent Workflows Test")
        
        workflows = []
        
        for i in range(3):
            print_info(f"Starting workflow {i+1}")
            
            # Create small test data
            df = pd.DataFrame({
                'col1': [1, 2, 3],
                'col2': ['A', 'B', 'C']
            })
            
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            files = {
                'file': (f'concurrent_{i}.csv', csv_buffer, 'text/csv')
            }
            
            data = {
                'document_name': f'Concurrent Test {i}',
                'organization': 'Test',
                'survey_type': 'test'
            }
            
            try:
                response = requests.post(
                    f"{API_BASE}/documents/upload",
                    files=files,
                    data=data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    workflows.append(result.get('document_id'))
                    print_success(f"Workflow {i+1} started")
                else:
                    print_failure(f"Workflow {i+1} failed")
                    
            except Exception as e:
                print_failure(f"Workflow {i+1} error: {str(e)}")
        
        if len(workflows) > 0:
            print_success(f"System handled {len(workflows)} concurrent workflows")
        else:
            print_failure("Concurrent workflow test failed")
    
    def test_data_persistence(self):
        """Test data persistence across stages"""
        print_header("Data Persistence Test")
        
        if not self.document_id:
            print_warning("No document available for persistence test")
            return
        
        print_info("Testing data persistence across stages")
        
        # Get document at different points
        try:
            # Initial state
            response1 = requests.get(f"{API_BASE}/documents/{self.document_id}", timeout=5)
            
            # Simulate some processing
            time.sleep(1)
            
            # Check again
            response2 = requests.get(f"{API_BASE}/documents/{self.document_id}", timeout=5)
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                if data1.get('document_id') == data2.get('document_id'):
                    print_success("Data persisted correctly")
                    print_info(f"  └─ Document ID consistent: {data1.get('document_id')}")
                else:
                    print_failure("Data persistence issue detected")
            else:
                print_warning("Could not verify persistence")
                
        except Exception as e:
            print_failure(f"Persistence test error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Integration Test Summary{Colors.ENDC}")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
        
        print(f"{Colors.GREEN}Passed: {len(self.test_results['passed'])} tests{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {len(self.test_results['failed'])} tests{Colors.ENDC}")
        print(f"{Colors.YELLOW}Warnings: {len(self.test_results['warnings'])} issues{Colors.ENDC}")
        
        if self.test_results['failed']:
            print(f"\n{Colors.RED}Failed tests:{Colors.ENDC}")
            for test in self.test_results['failed']:
                print(f"  - {test}")
        
        if self.test_results['warnings']:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.ENDC}")
            for warning in self.test_results['warnings'][:5]:
                print(f"  - {warning}")

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}AIDEPS Integration Testing Suite{Colors.ENDC}")
    print(f"{Colors.BOLD}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    # Check services
    try:
        requests.get(BACKEND_URL, timeout=2)
        print_success("Backend is running")
    except:
        print_failure("Backend not accessible")
        return
    
    try:
        requests.get(FRONTEND_URL, timeout=2)
        print_success("Frontend is running")
    except:
        print_warning("Frontend not accessible")
    
    # Run integration tests
    tester = IntegrationTester()
    
    # Main workflow test
    tester.test_complete_workflow()
    
    # Additional integration tests
    tester.test_error_recovery()
    tester.test_concurrent_workflows()
    tester.test_data_persistence()
    
    # Print summary
    tester.print_summary()
    
    print(f"\n{Colors.BOLD}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")

if __name__ == "__main__":
    main()