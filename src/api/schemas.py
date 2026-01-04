"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from src.api.models import UserRole, DetectionType


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    organization: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Monitoring Region Schemas
class MonitoringRegionBase(BaseModel):
    name: str
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(..., gt=0)


class MonitoringRegionCreate(MonitoringRegionBase):
    pass


class MonitoringRegionResponse(MonitoringRegionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    last_scanned: Optional[datetime]
    
    class Config:
        from_attributes = True


# Satellite Image Schemas
class SatelliteImageBase(BaseModel):
    s3_key: str
    source: str
    capture_date: datetime
    latitude: float
    longitude: float
    cloud_coverage: Optional[float] = None
    resolution_meters: Optional[float] = None


class SatelliteImageCreate(SatelliteImageBase):
    pass


class SatelliteImageResponse(SatelliteImageBase):
    id: int
    processed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Detection Schemas
class DetectionBase(BaseModel):
    detection_type: DetectionType
    confidence_score: float = Field(..., ge=0, le=1)
    detected_area_sqkm: Optional[float] = None
    latitude: float
    longitude: float
    details: Optional[dict] = None
    severity: Optional[str] = None


class DetectionCreate(DetectionBase):
    region_id: int
    satellite_image_id: int


class DetectionResponse(DetectionBase):
    id: int
    region_id: int
    satellite_image_id: int
    user_id: int
    flagged: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DetectionWithAlert(DetectionResponse):
    alerts: List['AlertResponse'] = []


# Alert Schemas
class AlertBase(BaseModel):
    title: str
    message: str
    severity: str


class AlertCreate(AlertBase):
    detection_id: int


class AlertResponse(AlertBase):
    id: int
    detection_id: int
    acknowledged: bool
    created_at: datetime
    acknowledged_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Analysis Request/Response
class AnalysisRequest(BaseModel):
    region_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    detection_types: Optional[List[DetectionType]] = None


class AnalysisResponse(BaseModel):
    region_id: int
    total_detections: int
    encroachment_count: int
    urban_expansion_count: int
    environmental_change_count: int
    average_confidence: float
    flagged_count: int
    detections: List[DetectionResponse]


# Insights Response
class InsightResponse(BaseModel):
    total_monitored_regions: int
    total_detections: int
    critical_alerts: int
    recent_changes: List[DetectionResponse]
    top_affected_regions: List[dict]
