from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.modules.monitoring.models import MonitoredProject, PerformanceMetric
from app.schemas.project import (
    MonitoredProjectCreate,
    MonitoredProjectUpdate,
    MonitoredProjectResponse,
    PerformanceMetricResponse
)
from app.modules.monitoring.tasks import ping_single_project_task
from app.services.audit import log_audit_action

router = APIRouter()

@router.post("/", response_model=MonitoredProjectResponse)
async def create_monitored_project(
    project_in: MonitoredProjectCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register a new external project/service URL to monitor.
    """
    new_project = MonitoredProject(
        name=project_in.name,
        url=project_in.url,
        is_active=project_in.is_active,
        check_interval_seconds=project_in.check_interval_seconds,
        expected_status_code=project_in.expected_status_code
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    # Audit log
    await log_audit_action(
        db,
        action="PROJECT_MONITOR_ADDED",
        request=request,
        user_id=current_user.id,
        details={"name": new_project.name, "url": new_project.url, "project_id": new_project.id}
    )
    
    # Enqueue a baseline ping task immediately in the Huey worker
    ping_single_project_task(new_project.id)
    
    return new_project

@router.get("/", response_model=List[MonitoredProjectResponse])
async def list_monitored_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all registered services and their current uptime status.
    """
    result = await db.execute(select(MonitoredProject))
    return result.scalars().all()

@router.get("/{project_id}", response_model=MonitoredProjectResponse)
async def read_project_config(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(MonitoredProject).where(MonitoredProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=MonitoredProjectResponse)
async def update_project_config(
    project_id: int,
    project_in: MonitoredProjectUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(MonitoredProject).where(MonitoredProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    for field, val in project_in.model_dump(exclude_unset=True).items():
        setattr(project, field, val)
        
    await db.commit()
    await db.refresh(project)
    
    # Audit log
    await log_audit_action(
        db,
        action="PROJECT_MONITOR_UPDATED",
        request=request,
        user_id=current_user.id,
        details={"project_id": project_id, "name": project.name, "url": project.url}
    )
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(MonitoredProject).where(MonitoredProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await db.delete(project)
    await db.commit()
    
    # Audit log
    await log_audit_action(
        db,
        action="PROJECT_MONITOR_DELETED",
        request=request,
        user_id=current_user.id,
        details={"project_id": project_id, "name": project.name}
    )
    
    return None

@router.get("/{project_id}/metrics", response_model=List[PerformanceMetricResponse])
async def read_project_metrics(
    project_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get latency history and uptime metrics for a specific monitored service.
    """
    result = await db.execute(
        select(PerformanceMetric)
        .where(PerformanceMetric.project_id == project_id)
        .order_by(desc(PerformanceMetric.timestamp))
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{project_id}/trigger", response_model=dict)
async def trigger_manual_ping(
    project_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually dispatch a background ping task right now (bypassing schedule timer).
    """
    result = await db.execute(select(MonitoredProject).where(MonitoredProject.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Schedule on Huey
    ping_single_project_task(project.id)
    
    # Audit log
    await log_audit_action(
        db,
        action="PROJECT_MONITOR_TRIGGERED",
        request=request,
        user_id=current_user.id,
        details={"project_id": project_id, "name": project.name}
    )
    
    return {"message": "Background check task dispatched to Huey queue."}
