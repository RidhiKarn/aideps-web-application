from fastapi import APIRouter, HTTPException
from typing import Optional
from services.database import db_service
from config.settings import settings

router = APIRouter()

@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details and current status"""
    workflow = await db_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Get all stages status
    stages = await db_service.get_workflow_stages(workflow_id)
    
    return {
        **workflow,
        "stages": stages,
        "stage_names": settings.stage_names
    }

@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get current workflow status"""
    workflow = await db_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    stages = await db_service.get_workflow_stages(workflow_id)
    
    # Calculate progress
    completed_stages = sum(1 for s in stages if s['status'] == 'completed')
    progress_percentage = (completed_stages / settings.total_stages) * 100
    
    return {
        "workflow_id": workflow_id,
        "current_stage": workflow['current_stage'],
        "current_stage_name": settings.stage_names.get(workflow['current_stage']),
        "total_stages": settings.total_stages,
        "completed_stages": completed_stages,
        "progress_percentage": progress_percentage,
        "status": workflow['status'],
        "stages": stages
    }

@router.post("/{workflow_id}/stages/{stage_number}/start")
async def start_stage(workflow_id: str, stage_number: int):
    """Start processing a specific stage"""
    workflow = await db_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Validate stage number
    if stage_number < 1 or stage_number > settings.total_stages:
        raise HTTPException(400, f"Invalid stage number. Must be between 1 and {settings.total_stages}")
    
    # Check if previous stages are completed (except for stage 1)
    if stage_number > 1:
        stages = await db_service.get_workflow_stages(workflow_id)
        prev_stage = next((s for s in stages if s['stage_number'] == stage_number - 1), None)
        if not prev_stage or prev_stage['status'] != 'completed':
            raise HTTPException(400, f"Previous stage {stage_number - 1} must be completed first")
    
    # Update stage status to in_progress
    await db_service.update_stage_status(workflow_id, stage_number, 'in_progress')
    
    # Log the action
    await db_service.create_audit_log({
        "workflow_id": workflow_id,
        "stage_number": stage_number,
        "action_type": "stage_started",
        "action_details": {
            "stage_name": settings.stage_names.get(stage_number)
        }
    })
    
    return {
        "success": True,
        "message": f"Stage {stage_number} started",
        "stage_name": settings.stage_names.get(stage_number)
    }

@router.post("/{workflow_id}/stages/{stage_number}/complete")
async def complete_stage(workflow_id: str, stage_number: int, completion_data: dict = None):
    """Mark a stage as completed"""
    workflow = await db_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Update stage status
    await db_service.update_stage_status(
        workflow_id, 
        stage_number, 
        'completed',
        data=completion_data
    )
    
    # Log the action
    await db_service.create_audit_log({
        "workflow_id": workflow_id,
        "stage_number": stage_number,
        "action_type": "stage_completed",
        "action_details": {
            "stage_name": settings.stage_names.get(stage_number),
            "completion_data": completion_data or {}
        }
    })
    
    return {
        "success": True,
        "message": f"Stage {stage_number} completed",
        "next_stage": stage_number + 1 if stage_number < settings.total_stages else None
    }

@router.post("/{workflow_id}/stages/{stage_number}/review")
async def review_stage(workflow_id: str, stage_number: int, review_data: dict):
    """Submit user review for a stage"""
    workflow = await db_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Update stage with user review data
    await db_service.update_stage_status(
        workflow_id,
        stage_number,
        'reviewed',
        data={'user_actions': review_data}
    )
    
    # Log the review
    await db_service.create_audit_log({
        "workflow_id": workflow_id,
        "stage_number": stage_number,
        "action_type": "stage_reviewed",
        "action_details": review_data
    })
    
    return {
        "success": True,
        "message": f"Stage {stage_number} review submitted"
    }

@router.post("/{workflow_id}/navigate/{stage_number}")
async def navigate_to_stage(workflow_id: str, stage_number: int):
    """Navigate to a specific stage (only completed or current stages)"""
    workflow = await db_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    
    # Check if navigation is allowed
    if stage_number > workflow['current_stage']:
        raise HTTPException(400, "Cannot navigate to future stages")
    
    stages = await db_service.get_workflow_stages(workflow_id)
    target_stage = next((s for s in stages if s['stage_number'] == stage_number), None)
    
    if not target_stage:
        raise HTTPException(404, "Stage not found")
    
    return {
        "success": True,
        "stage": target_stage,
        "can_edit": stage_number == workflow['current_stage']
    }

@router.get("/{workflow_id}/history")
async def get_workflow_history(workflow_id: str):
    """Get complete workflow history from audit log"""
    # This would query the audit_log table
    # For now, returning a simple response
    return {
        "workflow_id": workflow_id,
        "history": []
    }