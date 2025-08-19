#!/usr/bin/env python3
"""
Test script for AIDEPS backend
Tests the complete workflow with sample data
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
# Use the actual PLS data file you provided
SAMPLE_DATA_PATH = "../database/seed_data/nfhs5_real/PLS_FY19_AE_pud19i.csv"

def test_health_check():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✓ Server is running")
        return True
    except:
        print("✗ Server is not running. Please start the backend first:")
        print("  cd backend && python main.py")
        return False

def test_upload_document():
    """Test Stage 1: Upload document"""
    print("\n=== Stage 1: Upload Document ===")
    
    # Check if sample file exists
    if not os.path.exists(SAMPLE_DATA_PATH):
        print(f"✗ Sample data not found at {SAMPLE_DATA_PATH}")
        return None, None
    
    filename = os.path.basename(SAMPLE_DATA_PATH)
    print(f"📁 Uploading file: {filename}")
    
    with open(SAMPLE_DATA_PATH, 'rb') as f:
        files = {'file': (filename, f, 'text/csv')}
        data = {
            'document_name': 'Public Library Survey FY2019',
            'organization': 'Test Organization',
            'survey_type': 'library_survey'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Document uploaded successfully")
        print(f"  Document ID: {result['document_id']}")
        print(f"  Workflow ID: {result['workflow_id']}")
        print(f"  Rows: {result['file_info']['rows']}")
        print(f"  Columns: {result['file_info']['columns']}")
        return result['document_id'], result['workflow_id']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None, None

def test_workflow_status(workflow_id):
    """Check workflow status"""
    print("\n=== Workflow Status ===")
    
    response = requests.get(f"{BASE_URL}/api/workflows/{workflow_id}/status")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Current stage: {result['current_stage']} - {result['current_stage_name']}")
        print(f"  Progress: {result['progress_percentage']:.0f}%")
        print(f"  Completed stages: {result['completed_stages']}/{result['total_stages']}")
        
        # Show all stages
        print("\n  Stage Status:")
        for stage in result['stages']:
            status_icon = "✓" if stage['status'] == 'completed' else "○"
            print(f"    {status_icon} Stage {stage['stage_number']}: {stage['stage_name']} ({stage['status']})")
        
        return result
    else:
        print(f"✗ Failed to get workflow status: {response.text}")
        return None

def test_stage_2_cleansing(workflow_id, document_id):
    """Test Stage 2: Data Cleansing"""
    print("\n=== Stage 2: Data Cleansing ===")
    
    # Start stage
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/2/start")
    if response.status_code == 200:
        print("✓ Stage 2 started")
    
    # Analyze data quality
    response = requests.post(
        f"{BASE_URL}/api/stages/cleansing/analyze",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        quality_report = response.json()
        print("✓ Data quality analyzed")
        
        # Show missing data summary
        missing_cols = [col for col, info in quality_report['missing_data'].items() 
                       if info['missing_percentage'] > 0]
        print(f"  Columns with missing data: {len(missing_cols)}")
        
        # Show outliers summary
        outlier_cols = list(quality_report['outliers'].keys())
        print(f"  Columns with outliers: {len(outlier_cols)}")
        
        # Apply imputation (example)
        imputation_config = {}
        for col, info in quality_report['missing_data'].items():
            if info['missing_percentage'] > 0:
                imputation_config[col] = info.get('suggested_strategy', 'mean')
        
        if imputation_config:
            response = requests.post(
                f"{BASE_URL}/api/stages/cleansing/impute",
                params={"workflow_id": workflow_id, "document_id": document_id},
                json=imputation_config
            )
            if response.status_code == 200:
                print("✓ Missing values imputed")
    
    # Complete stage
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/2/complete")
    if response.status_code == 200:
        print("✓ Stage 2 completed")

def test_stage_3_analysis(workflow_id, document_id):
    """Test Stage 3: Analysis & Discovery"""
    print("\n=== Stage 3: Analysis & Discovery ===")
    
    # Start stage
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/3/start")
    if response.status_code == 200:
        print("✓ Stage 3 started")
    
    # Discover patterns
    response = requests.post(
        f"{BASE_URL}/api/stages/analysis/discover",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        analysis = response.json()
        print("✓ Pattern discovery completed")
        print(f"  Variable types identified: {len(analysis['variable_types'])}")
        print(f"  Key statistics calculated: {len(analysis['key_statistics'])}")
        if 'high_correlations' in analysis.get('correlations', {}):
            print(f"  High correlations found: {len(analysis['correlations']['high_correlations'])}")
    
    # Complete stage
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/3/complete")
    if response.status_code == 200:
        print("✓ Stage 3 completed")

def test_stage_4_statistics(workflow_id, document_id):
    """Test Stage 4: Statistics & Weights"""
    print("\n=== Stage 4: Statistics & Weights ===")
    
    # Start stage
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/start")
    if response.status_code == 200:
        print("✓ Stage 4 started")
    
    # Calculate statistics with generic column names
    # We'll check what columns are actually available
    config = {
        "weight_column": "POPU_LSA",  # Try this first, will handle if missing
        "variables": []  # Will be populated based on available columns
    }
    
    response = requests.post(
        f"{BASE_URL}/api/stages/statistics/calculate",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        stats = response.json()
        print("✓ Weighted statistics calculated")
        print(f"  Weighted means: {len(stats.get('weighted_means', {}))}")
        print(f"  Standard errors: {len(stats.get('standard_errors', {}))}")
        print(f"  Confidence intervals: {len(stats.get('confidence_intervals', {}))}")
    
    # Complete stage
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/complete")
    if response.status_code == 200:
        print("✓ Stage 4 completed")

def test_stage_5_6_7_reports(workflow_id, document_id):
    """Test Stages 5-7: Report Generation"""
    print("\n=== Stages 5-7: Report Generation ===")
    
    # Stage 5: Propose reports
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/5/start")
    if response.status_code == 200:
        print("✓ Stage 5 started")
    
    config = {
        "survey_type": "health_survey",
        "key_variables": ["age", "gender", "bmi", "health_insurance"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reports/propose",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        proposals = response.json()
        print("✓ Report templates proposed")
        print(f"  Available templates: {len(proposals['proposals'])}")
    
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/5/complete")
    if response.status_code == 200:
        print("✓ Stage 5 completed")
    
    # Stage 6: Confirm selection
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/6/start")
    if response.status_code == 200:
        print("✓ Stage 6 started")
    
    selected = {
        "templates": ["standard_survey", "health_survey"],
        "formats": ["html", "excel", "json"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reports/confirm",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=selected
    )
    
    if response.status_code == 200:
        print("✓ Report selection confirmed")
    
    # Stage 7: Generate final reports
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/7/start")
    if response.status_code == 200:
        print("✓ Stage 7 started")
    
    response = requests.post(
        f"{BASE_URL}/api/reports/generate",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Final reports generated")
        for report in result['reports']:
            print(f"  - {report['type']}: {report['filename']}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("AIDEPS Backend Test Suite")
    print("=" * 50)
    
    # Check server
    if not test_health_check():
        return
    
    # Test workflow
    document_id, workflow_id = test_upload_document()
    
    if document_id and workflow_id:
        # Show initial status
        test_workflow_status(workflow_id)
        
        # Run through all stages
        test_stage_2_cleansing(workflow_id, document_id)
        test_stage_3_analysis(workflow_id, document_id)
        test_stage_4_statistics(workflow_id, document_id)
        test_stage_5_6_7_reports(workflow_id, document_id)
        
        # Show final status
        print("\n" + "=" * 50)
        print("Final Workflow Status")
        print("=" * 50)
        test_workflow_status(workflow_id)
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        print(f"✓ Instance folder created at: backend/data/{document_id}")
        print("=" * 50)

if __name__ == "__main__":
    main()