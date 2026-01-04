"""
Insights and analytics routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.models import User
from src.api.schemas import InsightResponse
from src.utils.auth import get_current_active_user
from src.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/", response_model=InsightResponse)
async def get_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive insights for the current user"""
    insights = monitoring_service.get_insights(current_user.id, db)
    
    return InsightResponse(**insights, top_affected_regions=[])
