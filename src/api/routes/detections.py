"""
Detection and monitoring routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.api.database import get_db
from src.api.models import User, Detection, MonitoringRegion, DetectionType
from src.api.schemas import DetectionResponse, AnalysisRequest, AnalysisResponse
from src.utils.auth import get_current_active_user
from src.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/detections", tags=["Detections"])


@router.post("/scan/{region_id}", status_code=status.HTTP_202_ACCEPTED)
async def scan_region(
    region_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger a scan of a monitoring region"""
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    if not region.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Region is not active"
        )
    
    # Add scanning to background tasks
    background_tasks.add_task(monitoring_service.scan_region, region, db)
    
    return {
        "message": f"Scan initiated for region {region.name}",
        "region_id": region_id
    }


@router.get("/", response_model=List[DetectionResponse])
async def get_detections(
    detection_type: Optional[DetectionType] = None,
    flagged_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all detections for current user"""
    query = db.query(Detection).filter(Detection.user_id == current_user.id)
    
    if detection_type:
        query = query.filter(Detection.detection_type == detection_type)
    
    if flagged_only:
        query = query.filter(Detection.flagged == True)
    
    detections = query.order_by(Detection.created_at.desc()).all()
    
    return detections


@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific detection"""
    detection = db.query(Detection).filter(
        Detection.id == detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detection not found"
        )
    
    return detection


@router.get("/region/{region_id}", response_model=List[DetectionResponse])
async def get_region_detections(
    region_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all detections for a specific region"""
    # Verify region belongs to user
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    detections = db.query(Detection).filter(
        Detection.region_id == region_id
    ).order_by(Detection.created_at.desc()).all()
    
    return detections


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_region(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze detection patterns for a region"""
    # Verify region belongs to user
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == request.region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    # Build query
    query = db.query(Detection).filter(Detection.region_id == request.region_id)
    
    if request.start_date:
        query = query.filter(Detection.created_at >= request.start_date)
    
    if request.end_date:
        query = query.filter(Detection.created_at <= request.end_date)
    
    if request.detection_types:
        query = query.filter(Detection.detection_type.in_(request.detection_types))
    
    detections = query.all()
    
    # Calculate statistics
    total_detections = len(detections)
    encroachment_count = sum(1 for d in detections if d.detection_type == DetectionType.ENCROACHMENT)
    urban_expansion_count = sum(1 for d in detections if d.detection_type == DetectionType.URBAN_EXPANSION)
    environmental_change_count = sum(1 for d in detections if d.detection_type == DetectionType.ENVIRONMENTAL_CHANGE)
    
    average_confidence = sum(d.confidence_score for d in detections) / total_detections if total_detections > 0 else 0
    flagged_count = sum(1 for d in detections if d.flagged)
    
    return AnalysisResponse(
        region_id=request.region_id,
        total_detections=total_detections,
        encroachment_count=encroachment_count,
        urban_expansion_count=urban_expansion_count,
        environmental_change_count=environmental_change_count,
        average_confidence=average_confidence,
        flagged_count=flagged_count,
        detections=detections
    )
