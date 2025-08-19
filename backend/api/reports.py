from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import json
import os
from typing import Dict, Optional
from services.database import db_service
from services.report_generator import ReportGenerator
from services.file_manager import FileManager
from config.settings import settings

router = APIRouter()

report_generator = ReportGenerator()

@router.post("/propose")
async def propose_reports(workflow_id: str, document_id: str, config: Dict):
    """Stage 5: Propose report templates based on analysis"""
    
    # Get document and analysis results
    document = await db_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    # Load processed data from previous stages
    stage_3_files = FileManager.get_stage_files(document_id, 3)
    stage_4_files = FileManager.get_stage_files(document_id, 4)
    
    # Generate report proposals
    proposals = report_generator.propose_reports(
        data_type=config.get("survey_type", "health_survey"),
        variables=config.get("key_variables", []),
        analysis_results=config.get("analysis_results", {})
    )
    
    # Save proposals to Stage 5
    FileManager.save_stage_metadata(document_id, 5, {
        "proposals": proposals,
        "user_preferences": config
    })
    
    # Update workflow status
    await db_service.update_stage_status(
        workflow_id, 5, 'in_progress',
        data={'output_data': proposals}
    )
    
    return {
        "success": True,
        "proposals": proposals,
        "message": "Report templates proposed. Please review and confirm."
    }

@router.post("/confirm")
async def confirm_report_selection(workflow_id: str, document_id: str, 
                                  selected_reports: Dict):
    """Stage 6: User confirmation of report selection"""
    
    # Save user confirmation
    FileManager.save_stage_metadata(document_id, 6, {
        "selected_reports": selected_reports,
        "confirmed_at": pd.Timestamp.now().isoformat()
    })
    
    # Update workflow status
    await db_service.update_stage_status(
        workflow_id, 6, 'completed',
        data={'user_actions': selected_reports}
    )
    
    return {
        "success": True,
        "message": "Report selection confirmed. Proceeding to generate final reports."
    }

@router.post("/generate")
async def generate_final_reports(workflow_id: str, document_id: str):
    """Stage 7: Generate final reports"""
    
    # Load data from all stages
    instance_path = FileManager.get_instance_path(document_id)
    
    # Load original data
    data_path = FileManager.get_instance_path(document_id, 1) + "/data.csv"
    df = pd.read_csv(data_path)
    
    # Get confirmed report configuration
    stage_6_metadata = FileManager.get_stage_files(document_id, 6).get("stage_metadata.json")
    
    # Generate reports
    generated_reports = []
    
    # 1. Generate HTML report
    html_report = report_generator.generate_html_report(
        df=df,
        document_id=document_id,
        workflow_id=workflow_id
    )
    
    html_path = FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=7,
        filename="final_report.html",
        data=html_report.encode('utf-8')
    )
    generated_reports.append({
        "type": "html",
        "path": html_path,
        "filename": "final_report.html"
    })
    
    # 2. Generate Excel report
    excel_path = FileManager.get_instance_path(document_id, 7) + "/final_report.xlsx"
    report_generator.generate_excel_report(df, excel_path)
    generated_reports.append({
        "type": "excel",
        "path": excel_path,
        "filename": "final_report.xlsx"
    })
    
    # 3. Generate summary JSON
    summary = report_generator.generate_summary_json(df)
    json_path = FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=7,
        filename="summary.json",
        data=summary.encode('utf-8')
    )
    generated_reports.append({
        "type": "json",
        "path": json_path,
        "filename": "summary.json"
    })
    
    # Save report metadata
    FileManager.save_stage_metadata(document_id, 7, {
        "generated_reports": generated_reports,
        "generation_time": pd.Timestamp.now().isoformat()
    })
    
    # Update workflow status
    await db_service.update_stage_status(
        workflow_id, 7, 'completed',
        data={'output_data': {'reports': generated_reports}}
    )
    
    # Mark workflow as completed
    await db_service.client.execute(
        "ALTER TABLE workflows UPDATE status = 'completed', completed_at = now() "
        "WHERE workflow_id = %(workflow_id)s",
        {'workflow_id': workflow_id}
    )
    
    return {
        "success": True,
        "reports": generated_reports,
        "message": "Final reports generated successfully"
    }

@router.get("/download/{document_id}/{report_type}")
async def download_report(document_id: str, report_type: str):
    """Download a generated report"""
    
    # Get report path
    stage_7_files = FileManager.get_stage_files(document_id, 7)
    
    filename_map = {
        "html": "final_report.html",
        "excel": "final_report.xlsx",
        "pdf": "final_report.pdf",
        "json": "summary.json"
    }
    
    filename = filename_map.get(report_type)
    if not filename or filename not in stage_7_files:
        raise HTTPException(404, f"Report type {report_type} not found")
    
    file_path = stage_7_files[filename]
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

@router.get("/templates")
async def get_available_templates():
    """Get list of available report templates"""
    
    templates = report_generator.get_available_templates()
    
    return {
        "templates": templates,
        "default": "standard_survey"
    }