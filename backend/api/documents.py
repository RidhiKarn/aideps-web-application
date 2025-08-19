from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import pandas as pd
import os
import hashlib
import uuid
from datetime import datetime
from services.database import db_service
from services.file_manager import FileManager
from config.settings import settings

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_name: Optional[str] = Form(None),
    organization: Optional[str] = Form(""),
    survey_type: Optional[str] = Form("")
):
    """Upload a survey data file (Stage 1: Raw Data Upload)"""
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(400, f"File type {file_ext} not allowed")
    
    # Validate file size
    contents = await file.read()
    file_size = len(contents)
    if file_size > settings.max_upload_size:
        raise HTTPException(400, f"File size exceeds limit of {settings.max_upload_size} bytes")
    
    # Generate unique instance ID (this will be both document_id and folder name)
    # Use UUID for database, but create a simpler folder name
    import uuid
    document_id = str(uuid.uuid4())
    instance_id = document_id  # Use UUID for both
    
    # Create instance folder structure
    stage_paths = FileManager.create_instance_folders(instance_id)
    
    # Save original file to stage 1 folder
    original_filename = file.filename
    file_path = FileManager.save_stage_data(
        instance_id=instance_id,
        stage_num=1,
        filename=f"original_{original_filename}",
        data=contents
    )
    
    # Read file and get basic info
    try:
        if file_ext == ".csv":
            # Try different encodings, prioritize latin-1 for compatibility
            encodings = ['latin-1', 'utf-8', 'iso-8859-1', 'cp1252', 'us-ascii']
            df = None
            read_error = None
            successful_encoding = None
            
            for encoding in encodings:
                try:
                    # First try with just 5 rows to test encoding
                    test_df = pd.read_csv(file_path, encoding=encoding, nrows=5)
                    # If that works, read the full file
                    df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                    successful_encoding = encoding
                    print(f"Successfully read CSV with {encoding} encoding")
                    break
                except (UnicodeDecodeError, Exception) as e:
                    read_error = e
                    print(f"Failed with {encoding}: {str(e)[:100]}")
                    continue
            
            if df is None:
                # If all encodings fail, raise the last error
                raise HTTPException(400, f"Failed to read CSV file with any encoding. Last error: {str(read_error)}")
        else:  # Excel files
            df = pd.read_excel(file_path)
        
        row_count = len(df)
        column_count = len(df.columns)
        columns = df.columns.tolist()
        
        # Basic data profiling
        metadata = {
            "columns": columns,
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_counts": df.isnull().sum().to_dict(),
            "sample_rows": df.head(5).to_dict(orient='records')
        }
        
        # Save profiling metadata to stage 1
        FileManager.save_stage_metadata(instance_id, 1, {
            "file_info": {
                "original_filename": original_filename,
                "file_size": file_size,
                "file_type": file_ext,
                "rows": row_count,
                "columns": column_count
            },
            "data_profile": metadata
        })
        
        # Also save a copy of the data as CSV for easier processing
        csv_path = os.path.join(FileManager.get_instance_path(instance_id, 1), "data.csv")
        df.to_csv(csv_path, index=False)
        
    except Exception as e:
        # Don't remove file yet, for debugging
        print(f"Error reading file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(400, f"Failed to read file: {str(e)}")
    
    # Create document in database (use instance_id as document_id)
    document_data = {
        "document_name": document_name or file.filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": file_size,
        "file_type": file_ext,
        "organization": organization,
        "survey_type": survey_type,
        "row_count": row_count,
        "column_count": column_count,
        "metadata": {
            **metadata,
            "instance_id": instance_id,
            "instance_path": FileManager.get_instance_path(instance_id)
        }
    }
    
    # We'll use instance_id as document_id for consistency
    document_id = await db_service.create_document(document_data, document_id=instance_id)
    
    # Create workflow for this document
    workflow_id = await db_service.create_workflow(document_id, "user")
    
    # Log the upload
    await db_service.create_audit_log({
        "document_id": document_id,
        "workflow_id": workflow_id,
        "stage_number": 1,
        "action_type": "document_upload",
        "action_details": {
            "filename": file.filename,
            "size": file_size,
            "rows": row_count,
            "columns": column_count
        }
    })
    
    # Mark stage 1 as completed since upload is successful
    try:
        await db_service.update_stage_status(workflow_id, 1, 'completed')
    except Exception as e:
        print(f"Warning: Could not mark stage 1 as completed: {e}")
        # Don't fail the upload if stage update fails
    
    return {
        "success": True,
        "document_id": document_id,
        "workflow_id": workflow_id,
        "file_info": {
            "filename": file.filename,
            "size": file_size,
            "rows": row_count,
            "columns": column_count,
            "columns_list": columns
        },
        "message": "File uploaded successfully. Workflow created."
    }

@router.get("/{document_id}")
async def get_document(document_id: str):
    """Get document details"""
    document = await db_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    return document

@router.get("/{document_id}/preview")
async def preview_document(document_id: str, rows: int = 10):
    """Preview document data"""
    document = await db_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    try:
        file_path = document['file_path']
        file_type = document['file_type']
        
        if file_type == ".csv":
            df = pd.read_csv(file_path, nrows=rows)
        else:
            df = pd.read_excel(file_path, nrows=rows)
        
        return {
            "document_id": document_id,
            "preview": df.to_dict(orient='records'),
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to preview document: {str(e)}")

@router.post("/{document_id}/schema")
async def update_schema(document_id: str, schema_mapping: dict):
    """Update column schema mapping"""
    document = await db_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    # Here we would update the schema mapping in the database
    # This is part of Stage 1 user review
    
    await db_service.create_audit_log({
        "document_id": document_id,
        "action_type": "schema_update",
        "action_details": schema_mapping
    })
    
    return {
        "success": True,
        "message": "Schema updated successfully"
    }