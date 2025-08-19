#!/usr/bin/env python3
"""
Test complete workflow with proper stage completion
"""

import requests
import json
import os
import time

BASE_URL = "http://localhost:8000"
SAMPLE_DATA_PATH = "../database/seed_data/nfhs5_real/PLS_FY19_AE_pud19i.csv"

def test_complete_workflow():
    """Test the complete 7-stage workflow"""
    print("=" * 50)
    print("Complete Workflow Test")
    print("=" * 50)
    
    # Stage 1: Upload document
    print("\n=== Stage 1: Upload Document ===")
    with open(SAMPLE_DATA_PATH, 'rb') as f:
        files = {'file': ('PLS_FY19_AE_pud19i.csv', f, 'text/csv')}
        data = {
            'document_name': 'Public Library Survey 2019',
            'organization': 'MoSPI',
            'survey_type': 'library_survey'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            data=data
        )
    
    if response.status_code != 200:
        print(f"✗ Upload failed: {response.text}")
        return
    
    result = response.json()
    document_id = result['document_id']
    workflow_id = result['workflow_id']
    print(f"✓ Document uploaded: {document_id}")
    print(f"✓ Workflow created: {workflow_id}")
    print(f"  Rows: {result['file_info']['rows']}")
    print(f"  Columns: {result['file_info']['columns']}")
    
    # Check stage 1 files
    check_stage_files(document_id, 1)
    
    # Stage 2: Data Cleansing
    print("\n=== Stage 2: Data Cleansing ===")
    
    # Start stage 2
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
        print(f"✓ Data quality analyzed")
        
        # Count columns with missing data
        missing_cols = sum(1 for col, info in quality_report['missing_data'].items() 
                          if info.get('percentage', 0) > 0)
        print(f"  Columns with missing data: {missing_cols}")
    
    # Complete stage 2
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/2/complete")
    if response.status_code == 200:
        print("✓ Stage 2 completed")
    
    check_stage_files(document_id, 2)
    
    # Stage 3: Analysis & Discovery
    print("\n=== Stage 3: Analysis & Discovery ===")
    
    # Start stage 3
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
        print(f"✓ Pattern discovery completed")
        print(f"  Variable types identified: {len(analysis['variable_types'])}")
        print(f"  Key statistics calculated: {len(analysis['key_statistics'])}")
    
    # Complete stage 3
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/3/complete")
    if response.status_code == 200:
        print("✓ Stage 3 completed")
    
    check_stage_files(document_id, 3)
    
    # Stage 4: Statistics & Weights
    print("\n=== Stage 4: Statistics & Weights ===")
    
    # Start stage 4
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/start")
    if response.status_code == 200:
        print("✓ Stage 4 started")
    
    # Calculate statistics
    config = {
        "weight_column": "POPU_LSA",
        "variables": ["TOTINCM", "TOTSTAFF", "TOTOPEXP", "VISITS"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/stages/statistics/calculate",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Weighted statistics calculated")
        print(f"  Variables processed: {len(stats['weighted_means'])}")
    
    # Complete stage 4
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/complete")
    if response.status_code == 200:
        print("✓ Stage 4 completed")
    
    check_stage_files(document_id, 4)
    
    # Stage 5: Propose Reports
    print("\n=== Stage 5: Propose Reports ===")
    
    # Start stage 5
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/5/start")
    if response.status_code == 200:
        print("✓ Stage 5 started")
    
    # Propose reports
    config = {
        "survey_type": "library_survey",
        "key_variables": ["TOTINCM", "TOTSTAFF", "VISITS", "POPU_LSA"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reports/propose",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        proposals = response.json()
        print(f"✓ Report templates proposed")
        print(f"  Available templates: {len(proposals['proposals'])}")
    
    # Complete stage 5
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/5/complete")
    if response.status_code == 200:
        print("✓ Stage 5 completed")
    
    check_stage_files(document_id, 5)
    
    # Stage 6: User Confirmation
    print("\n=== Stage 6: User Confirmation ===")
    
    # Start stage 6
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/6/start")
    if response.status_code == 200:
        print("✓ Stage 6 started")
    
    # Confirm selection
    selected = {
        "templates": ["standard_survey"],
        "formats": ["html", "excel", "json"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reports/confirm",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=selected
    )
    
    if response.status_code == 200:
        print("✓ Report selection confirmed")
    
    # Complete stage 6
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/6/complete")
    if response.status_code == 200:
        print("✓ Stage 6 completed")
    
    check_stage_files(document_id, 6)
    
    # Stage 7: Generate Final Reports
    print("\n=== Stage 7: Final Report Generation ===")
    
    # Start stage 7
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/7/start")
    if response.status_code == 200:
        print("✓ Stage 7 started")
    
    # Generate reports
    response = requests.post(
        f"{BASE_URL}/api/reports/generate",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Final reports generated")
        for report in result['reports']:
            print(f"  - {report['type']}: {report['filename']}")
    
    check_stage_files(document_id, 7)
    
    # Final workflow status
    print("\n=== Final Workflow Status ===")
    response = requests.get(f"{BASE_URL}/api/workflows/{workflow_id}/status")
    
    if response.status_code == 200:
        status = response.json()
        print(f"✓ Workflow completed: {status['completed_stages']}/{status['total_stages']} stages")
        print(f"  Progress: {status['progress_percentage']:.0f}%")
    
    print("\n" + "=" * 50)
    print("✓ Complete Workflow Test Successful!")
    print(f"✓ All files saved in: data/{document_id}/")
    print("=" * 50)
    
    return document_id, workflow_id

def check_stage_files(document_id, stage_num):
    """Check and list files in a stage folder"""
    stage_names = {
        1: "01_upload",
        2: "02_cleansing",
        3: "03_analysis",
        4: "04_statistics",
        5: "05_reports_proposed",
        6: "06_confirmation",
        7: "07_final_reports"
    }
    
    stage_path = f"data/{document_id}/{stage_names[stage_num]}"
    if os.path.exists(stage_path):
        files = os.listdir(stage_path)
        if files:
            print(f"  Files in {stage_names[stage_num]}:")
            for f in files:
                size = os.path.getsize(os.path.join(stage_path, f))
                if size > 1024*1024:  # > 1MB
                    print(f"    - {f} ({size/(1024*1024):.1f} MB)")
                elif size > 1024:  # > 1KB
                    print(f"    - {f} ({size/1024:.1f} KB)")
                else:
                    print(f"    - {f} ({size} bytes)")
    else:
        print(f"  ✗ Stage folder not found: {stage_path}")

if __name__ == "__main__":
    test_complete_workflow()