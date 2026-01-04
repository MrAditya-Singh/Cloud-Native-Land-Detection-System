"""
Monitoring regions management routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.models import User, MonitoringRegion
from src.api.schemas import MonitoringRegionCreate, MonitoringRegionResponse
from src.utils.auth import get_current_active_user

router = APIRouter(prefix="/regions", tags=["Monitoring Regions"])


@router.post("/", response_model=MonitoringRegionResponse, status_code=status.HTTP_201_CREATED)
async def create_monitoring_region(
    region: MonitoringRegionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new monitoring region"""
    db_region = MonitoringRegion(
        **region.dict(),
        user_id=current_user.id
    )
    
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    
    return db_region


@router.get("/", response_model=List[MonitoringRegionResponse])
async def get_monitoring_regions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all monitoring regions for current user"""
    regions = db.query(MonitoringRegion).filter(
        MonitoringRegion.user_id == current_user.id
    ).all()
    
    return regions


@router.get("/{region_id}", response_model=MonitoringRegionResponse)
async def get_monitoring_region(
    region_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific monitoring region"""
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    return region


@router.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitoring_region(
    region_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a monitoring region"""
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    db.delete(region)
    db.commit()
    
    return None


@router.put("/{region_id}/activate", response_model=MonitoringRegionResponse)
async def activate_monitoring_region(
    region_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate a monitoring region"""
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    region.is_active = True
    db.commit()
    db.refresh(region)
    
    return region


@router.put("/{region_id}/deactivate", response_model=MonitoringRegionResponse)
async def deactivate_monitoring_region(
    region_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate a monitoring region"""
    region = db.query(MonitoringRegion).filter(
        MonitoringRegion.id == region_id,
        MonitoringRegion.user_id == current_user.id
    ).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring region not found"
        )
    
    region.is_active = False
    db.commit()
    db.refresh(region)
    
    return region
