#!/usr/bin/env python3
"""
Test script to check if stage processing saves files correctly
"""

import requests
import json
import os
import time

BASE_URL = "http://localhost:8000"
SAMPLE_DATA_PATH = "../database/seed_data/nfhs5_real/PLS_FY19_AE_pud19i.csv"

def upload_document():
    """Upload document and return IDs"""
    print("Uploading document...")
    
    with open(SAMPLE_DATA_PATH, 'rb') as f:
        files = {'file': ('PLS_FY19_AE_pud19i.csv', f, 'text/csv')}
        data = {
            'document_name': 'Test PLS Data',
            'organization': 'Test Org',
            'survey_type': 'library_survey'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Upload successful: {result['document_id']}")
        return result['document_id'], result['workflow_id']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None, None

def test_stage_2_cleansing(workflow_id, document_id):
    """Test Stage 2: Data Cleansing"""
    print("\n=== Testing Stage 2: Data Cleansing ===")
    
    # Start stage
    print("Starting stage 2...")
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/2/start")
    print(f"Start response: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    
    # Analyze data quality
    print("Analyzing data quality...")
    response = requests.post(
        f"{BASE_URL}/api/stages/cleansing/analyze",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        quality_report = response.json()
        print(f"✓ Quality analysis complete")
        print(f"  Columns analyzed: {len(quality_report.get('missing_data', {}))}")
        
        # Check if files were saved
        stage_2_path = f"data/{document_id}/02_cleansing"
        if os.path.exists(stage_2_path):
            files = os.listdir(stage_2_path)
            print(f"  Files in stage 2 folder: {files}")
        else:
            print(f"  Stage 2 folder not found!")
    else:
        print(f"✗ Quality analysis failed: {response.status_code}")
        print(f"  Error: {response.text}")
    
    # Try imputation
    print("Testing imputation...")
    imputation_config = {
        "POPU_LSA": "mean",
        "TOTINCM": "median"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/stages/cleansing/impute",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=imputation_config
    )
    
    if response.status_code == 200:
        print(f"✓ Imputation complete")
        # Check files again
        stage_2_path = f"data/{document_id}/02_cleansing"
        if os.path.exists(stage_2_path):
            files = os.listdir(stage_2_path)
            print(f"  Files after imputation: {files}")
    else:
        print(f"✗ Imputation failed: {response.status_code}")
        print(f"  Error: {response.text}")

def test_stage_3_analysis(workflow_id, document_id):
    """Test Stage 3: Analysis & Discovery"""
    print("\n=== Testing Stage 3: Analysis & Discovery ===")
    
    # Start stage
    print("Starting stage 3...")
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/3/start")
    print(f"Start response: {response.status_code}")
    
    # Discover patterns
    print("Discovering patterns...")
    response = requests.post(
        f"{BASE_URL}/api/stages/analysis/discover",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        analysis = response.json()
        print(f"✓ Pattern discovery complete")
        print(f"  Variable types: {len(analysis.get('variable_types', {}))}")
        
        # Check if files were saved
        stage_3_path = f"data/{document_id}/03_analysis"
        if os.path.exists(stage_3_path):
            files = os.listdir(stage_3_path)
            print(f"  Files in stage 3 folder: {files}")
        else:
            print(f"  Stage 3 folder not found!")
    else:
        print(f"✗ Pattern discovery failed: {response.status_code}")
        print(f"  Error: {response.text}")

def test_stage_4_statistics(workflow_id, document_id):
    """Test Stage 4: Statistics & Weights"""
    print("\n=== Testing Stage 4: Statistics & Weights ===")
    
    # Start stage
    print("Starting stage 4...")
    response = requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/start")
    print(f"Start response: {response.status_code}")
    
    # Calculate statistics
    print("Calculating statistics...")
    config = {
        "weight_column": "POPU_LSA",
        "variables": ["TOTINCM", "TOTSTAFF", "TOTOPEXP"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/stages/statistics/calculate",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        stats = response.json()
        print(f"✓ Statistics calculated")
        print(f"  Weighted means: {len(stats.get('weighted_means', {}))}")
        
        # Check if files were saved
        stage_4_path = f"data/{document_id}/04_statistics"
        if os.path.exists(stage_4_path):
            files = os.listdir(stage_4_path)
            print(f"  Files in stage 4 folder: {files}")
        else:
            print(f"  Stage 4 folder not found!")
    else:
        print(f"✗ Statistics calculation failed: {response.status_code}")
        print(f"  Error: {response.text}")

def check_all_folders(document_id):
    """Check contents of all stage folders"""
    print("\n=== Checking All Stage Folders ===")
    
    instance_path = f"data/{document_id}"
    if not os.path.exists(instance_path):
        print(f"✗ Instance folder not found: {instance_path}")
        return
    
    for i in range(1, 8):
        stage_names = {
            1: "01_upload",
            2: "02_cleansing",
            3: "03_analysis",
            4: "04_statistics",
            5: "05_reports_proposed",
            6: "06_confirmation",
            7: "07_final_reports"
        }
        
        stage_folder = os.path.join(instance_path, stage_names[i])
        if os.path.exists(stage_folder):
            files = os.listdir(stage_folder)
            if files:
                print(f"✓ Stage {i} ({stage_names[i]}): {len(files)} files")
                for f in files:
                    size = os.path.getsize(os.path.join(stage_folder, f))
                    print(f"    - {f} ({size:,} bytes)")
            else:
                print(f"○ Stage {i} ({stage_names[i]}): empty")
        else:
            print(f"✗ Stage {i} ({stage_names[i]}): folder missing")

def main():
    print("=" * 50)
    print("Stage Processing Test")
    print("=" * 50)
    
    # Upload document
    document_id, workflow_id = upload_document()
    
    if document_id and workflow_id:
        # Test each stage
        test_stage_2_cleansing(workflow_id, document_id)
        test_stage_3_analysis(workflow_id, document_id)
        test_stage_4_statistics(workflow_id, document_id)
        
        # Check all folders
        check_all_folders(document_id)
        
        print("\n" + "=" * 50)
        print("Test Complete")
        print(f"Instance folder: data/{document_id}")
        print("=" * 50)

if __name__ == "__main__":
    main()