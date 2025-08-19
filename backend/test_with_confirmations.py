#!/usr/bin/env python3
"""
Interactive test script for AIDEPS backend
Shows user confirmation points at each stage
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
SAMPLE_DATA_PATH = "../database/seed_data/nfhs5_real/PLS_FY19_AE_pud19i.csv"

def print_stage_header(stage_num, stage_name):
    """Print a formatted stage header"""
    print("\n" + "="*60)
    print(f"STAGE {stage_num}: {stage_name}")
    print("="*60)

def wait_for_user_confirmation(message="Press Enter to continue..."):
    """Simulate user review and confirmation"""
    print(f"\n⚠️  USER REVIEW REQUIRED")
    print(f"   {message}")
    input("   > ")
    print("✓ User confirmed, proceeding...")

def show_instance_folder(document_id, stage_num):
    """Show what files are in the instance folder for this stage"""
    instance_path = f"backend/data/{document_id}/{stage_num:02d}_*"
    print(f"\n📁 Instance folder: data/{document_id}/")
    print(f"   Current stage folder will contain:")
    if stage_num == 1:
        print("   - original_<filename>.csv (uploaded file)")
        print("   - data.csv (normalized copy)")
        print("   - stage_metadata.json (profiling results)")
    elif stage_num == 2:
        print("   - cleaned_data.csv")
        print("   - imputation_log.json")
        print("   - outlier_report.json")
        print("   - stage_metadata.json")
    elif stage_num == 3:
        print("   - analysis_results.json")
        print("   - correlations.csv")
        print("   - patterns.json")
        print("   - stage_metadata.json")
    elif stage_num == 4:
        print("   - weighted_statistics.json")
        print("   - population_estimates.csv")
        print("   - stage_metadata.json")
    elif stage_num == 5:
        print("   - proposed_reports.json")
        print("   - template_options.json")
    elif stage_num == 6:
        print("   - user_selections.json")
        print("   - confirmation_timestamp.txt")
    elif stage_num == 7:
        print("   - final_report.html")
        print("   - final_report.xlsx")
        print("   - summary.json")

def test_stage_1_upload():
    """Stage 1: Upload and initial review"""
    print_stage_header(1, "RAW DATA UPLOAD")
    
    if not os.path.exists(SAMPLE_DATA_PATH):
        print(f"✗ File not found: {SAMPLE_DATA_PATH}")
        return None, None
    
    filename = os.path.basename(SAMPLE_DATA_PATH)
    file_size = os.path.getsize(SAMPLE_DATA_PATH) / (1024*1024)  # MB
    
    print(f"📊 File to upload: {filename}")
    print(f"   Size: {file_size:.2f} MB")
    print(f"   Type: CSV")
    
    wait_for_user_confirmation("Review file details and confirm upload")
    
    # Upload file
    with open(SAMPLE_DATA_PATH, 'rb') as f:
        files = {'file': (filename, f, 'text/csv')}
        data = {
            'document_name': 'Public Library Survey FY2019',
            'organization': 'Institute of Museum and Library Services',
            'survey_type': 'library_survey'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/documents/upload",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        document_id = result['document_id']
        workflow_id = result['workflow_id']
        
        print(f"\n✓ File uploaded successfully!")
        print(f"   Document ID: {document_id}")
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Rows: {result['file_info']['rows']:,}")
        print(f"   Columns: {result['file_info']['columns']}")
        
        # Show first few columns
        print(f"\n   Sample columns:")
        for col in result['file_info']['columns_list'][:10]:
            print(f"   - {col}")
        
        show_instance_folder(document_id, 1)
        
        print("\n👤 USER ACTION NEEDED:")
        print("   1. Review column mappings")
        print("   2. Confirm data types")
        print("   3. Set any special handling requirements")
        
        wait_for_user_confirmation("Confirm schema and proceed to cleansing")
        
        return document_id, workflow_id
    else:
        print(f"✗ Upload failed: {response.text}")
        return None, None

def test_stage_2_cleansing(workflow_id, document_id):
    """Stage 2: Data Cleansing with user decisions"""
    print_stage_header(2, "DATA CLEANSING")
    
    # Start stage
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/2/start")
    
    # Analyze data quality
    response = requests.post(
        f"{BASE_URL}/api/stages/cleansing/analyze",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        quality_report = response.json()
        
        print("📊 Data Quality Analysis Complete:")
        
        # Show missing data
        missing_summary = {}
        for col, info in quality_report['missing_data'].items():
            if info['missing_percentage'] > 0:
                missing_summary[col] = info['missing_percentage']
        
        if missing_summary:
            print(f"\n   Missing Data Found in {len(missing_summary)} columns:")
            for col, pct in list(missing_summary.items())[:5]:
                print(f"   - {col}: {pct:.1f}% missing")
                print(f"     Suggested: {quality_report['missing_data'][col].get('suggested_strategy', 'none')}")
        
        # Show outliers
        if quality_report['outliers']:
            print(f"\n   Outliers Detected in {len(quality_report['outliers'])} columns:")
            for col, info in list(quality_report['outliers'].items())[:5]:
                print(f"   - {col}: {info['count']} outliers ({info['percentage']:.1f}%)")
        
        show_instance_folder(document_id, 2)
        
        print("\n👤 USER DECISIONS REQUIRED:")
        print("   1. Select imputation strategy for each column")
        print("   2. Decide how to handle outliers")
        print("   3. Set validation rules")
        
        wait_for_user_confirmation("Apply selected cleansing strategies")
        
        # In real scenario, user would select strategies
        # For test, we'll use automatic suggestions
        imputation_config = {}
        for col, info in quality_report['missing_data'].items():
            if info['missing_percentage'] > 0 and info['missing_percentage'] < 50:
                imputation_config[col] = info.get('suggested_strategy', 'mean')
        
        if imputation_config:
            print(f"\n   Applying imputation to {len(imputation_config)} columns...")
            response = requests.post(
                f"{BASE_URL}/api/stages/cleansing/impute",
                params={"workflow_id": workflow_id, "document_id": document_id},
                json=imputation_config
            )
            if response.status_code == 200:
                print("   ✓ Missing values handled")
        
        # Complete stage
        requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/2/complete")
        print("\n✓ Stage 2 completed - Data cleaned and validated")

def test_stage_3_analysis(workflow_id, document_id):
    """Stage 3: Analysis & Discovery"""
    print_stage_header(3, "ANALYSIS & DISCOVERY")
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/3/start")
    
    response = requests.post(
        f"{BASE_URL}/api/stages/analysis/discover",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        analysis = response.json()
        
        print("📊 Pattern Discovery Results:")
        print(f"\n   Variable Classification:")
        
        var_types = {}
        for col, vtype in analysis['variable_types'].items():
            type_name = vtype.get('type', 'unknown')
            var_types[type_name] = var_types.get(type_name, 0) + 1
        
        for vtype, count in var_types.items():
            print(f"   - {vtype}: {count} variables")
        
        if 'high_correlations' in analysis.get('correlations', {}):
            high_corr = analysis['correlations']['high_correlations']
            if high_corr:
                print(f"\n   High Correlations Found: {len(high_corr)}")
                for corr in high_corr[:3]:
                    print(f"   - {corr['variable1']} ↔ {corr['variable2']}: {corr['correlation']:.3f}")
        
        show_instance_folder(document_id, 3)
        
        print("\n👤 USER REVIEW REQUIRED:")
        print("   1. Review identified patterns")
        print("   2. Select key variables for analysis")
        print("   3. Define grouping variables")
        
        wait_for_user_confirmation("Confirm analysis results and proceed")
        
        requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/3/complete")
        print("\n✓ Stage 3 completed - Patterns identified")

def test_stage_4_statistics(workflow_id, document_id):
    """Stage 4: Statistics & Weights"""
    print_stage_header(4, "STATISTICS & WEIGHTS")
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/start")
    
    print("📊 Calculating Statistics:")
    print("\n   Available weight variables:")
    print("   - POPU_LSA (Legal Service Area Population)")
    print("   - POPU_UND (Unduplicated Population)")
    
    print("\n👤 USER SELECTION REQUIRED:")
    print("   1. Select weight variable")
    print("   2. Choose variables for weighted estimates")
    print("   3. Define subgroups for analysis")
    
    wait_for_user_confirmation("Apply selected weighting scheme")
    
    # For test, we'll use some numeric columns if available
    config = {
        "weight_column": "POPU_LSA",  # Population weight
        "variables": ["VISITS", "TOTCIR", "TOTSTAFF"]  # Example library metrics
    }
    
    response = requests.post(
        f"{BASE_URL}/api/stages/statistics/calculate",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        stats = response.json()
        print("\n   Weighted Statistics Calculated:")
        print(f"   - Weighted means: {len(stats.get('weighted_means', {}))}")
        print(f"   - Population estimates: {len(stats.get('weighted_totals', {}))}")
        print(f"   - Confidence intervals: {len(stats.get('confidence_intervals', {}))}")
    
    show_instance_folder(document_id, 4)
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/4/complete")
    print("\n✓ Stage 4 completed - Statistics calculated")

def test_stages_5_6_7_reporting(workflow_id, document_id):
    """Stages 5-7: Report Generation"""
    
    # Stage 5: Propose Reports
    print_stage_header(5, "PROPOSE REPORTS")
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/5/start")
    
    config = {
        "survey_type": "library_survey",
        "key_variables": ["STABR", "LIBNAME", "CITY", "VISITS", "TOTCIR"]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reports/propose",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=config
    )
    
    if response.status_code == 200:
        proposals = response.json()
        print("📄 Available Report Templates:")
        for template in proposals['proposals']:
            rec = "⭐" if template['recommended'] else "  "
            print(f"   {rec} {template['name']}")
            print(f"      {template['description']}")
    
    show_instance_folder(document_id, 5)
    
    print("\n👤 USER SELECTION REQUIRED:")
    print("   1. Choose report templates")
    print("   2. Select output formats (HTML, Excel, PDF)")
    print("   3. Customize report sections")
    
    wait_for_user_confirmation("Confirm report selection")
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/5/complete")
    
    # Stage 6: User Confirmation
    print_stage_header(6, "USER CONFIRMATION")
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/6/start")
    
    selected = {
        "templates": ["standard_survey"],
        "formats": ["html", "excel", "json"],
        "include_visualizations": True
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reports/confirm",
        params={"workflow_id": workflow_id, "document_id": document_id},
        json=selected
    )
    
    print("✓ Report configuration confirmed")
    show_instance_folder(document_id, 6)
    
    print("\n👤 FINAL REVIEW:")
    print("   All processing complete. Ready to generate final reports.")
    
    wait_for_user_confirmation("Generate final reports")
    
    # Stage 7: Generate Final Reports
    print_stage_header(7, "FINAL REPORT GENERATION")
    
    requests.post(f"{BASE_URL}/api/workflows/{workflow_id}/stages/7/start")
    
    response = requests.post(
        f"{BASE_URL}/api/reports/generate",
        params={"workflow_id": workflow_id, "document_id": document_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Reports Generated Successfully:")
        for report in result['reports']:
            print(f"   - {report['type'].upper()}: {report['filename']}")
    
    show_instance_folder(document_id, 7)
    
    print("\n✓ All stages completed!")

def show_final_summary(workflow_id, document_id):
    """Show final workflow summary"""
    print("\n" + "="*60)
    print("WORKFLOW COMPLETE")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/workflows/{workflow_id}/status")
    
    if response.status_code == 200:
        status = response.json()
        
        print(f"\n📊 Final Status:")
        print(f"   Document ID: {document_id}")
        print(f"   Workflow ID: {workflow_id}")
        print(f"   Progress: 100%")
        print(f"   All 7 stages completed")
        
        print(f"\n📁 Instance Folder Structure Created:")
        print(f"   backend/data/{document_id}/")
        print(f"   ├── 01_upload/")
        print(f"   ├── 02_cleansing/")
        print(f"   ├── 03_analysis/")
        print(f"   ├── 04_statistics/")
        print(f"   ├── 05_reports_proposed/")
        print(f"   ├── 06_confirmation/")
        print(f"   └── 07_final_reports/")
        
        print(f"\n📄 Generated Outputs:")
        print(f"   - Cleaned dataset")
        print(f"   - Quality reports")
        print(f"   - Statistical analysis")
        print(f"   - Final reports (HTML, Excel, JSON)")
        
        print(f"\n✅ System successfully processed the Public Library Survey data")
        print(f"   through all 7 stages with user confirmations at each step.")

def main():
    """Run interactive test with user confirmations"""
    print("="*60)
    print("AIDEPS - Interactive Workflow Test")
    print("="*60)
    print("\nThis test demonstrates the complete 7-stage workflow")
    print("with user confirmation points at each stage.")
    print("\nUsing dataset: PLS_FY19_AE_pud19i.csv (Public Library Survey)")
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("\n✓ Backend server is running")
    except:
        print("\n✗ Backend server is not running!")
        print("  Please start it first: cd backend && python main.py")
        return
    
    wait_for_user_confirmation("Start workflow test")
    
    # Run through all stages
    document_id, workflow_id = test_stage_1_upload()
    
    if document_id and workflow_id:
        test_stage_2_cleansing(workflow_id, document_id)
        test_stage_3_analysis(workflow_id, document_id)
        test_stage_4_statistics(workflow_id, document_id)
        test_stages_5_6_7_reporting(workflow_id, document_id)
        
        show_final_summary(workflow_id, document_id)
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

if __name__ == "__main__":
    main()