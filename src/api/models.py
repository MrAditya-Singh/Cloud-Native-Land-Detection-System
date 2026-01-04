"""
Database models for the Land Detection System
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User roles for multi-tenant access"""
    GOVERNMENT = "government"
    REAL_ESTATE = "real_estate"
    NGO = "ngo"
    ADMIN = "admin"


class DetectionType(str, enum.Enum):
    """Types of land detection"""
    ENCROACHMENT = "encroachment"
    URBAN_EXPANSION = "urban_expansion"
    ENVIRONMENTAL_CHANGE = "environmental_change"


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    monitoring_regions = relationship("MonitoringRegion", back_populates="user")
    detections = relationship("Detection", back_populates="user")


class MonitoringRegion(Base):
    """Regions being monitored for land changes"""
    __tablename__ = "monitoring_regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_km = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_scanned = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="monitoring_regions")
    detections = relationship("Detection", back_populates="region")


class SatelliteImage(Base):
    """Satellite imagery metadata"""
    __tablename__ = "satellite_images"
    
    id = Column(Integer, primary_key=True, index=True)
    s3_key = Column(String, nullable=False, unique=True)
    source = Column(String, nullable=False)  # Landsat, Sentinel, etc.
    capture_date = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    cloud_coverage = Column(Float)
    resolution_meters = Column(Float)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    detections = relationship("Detection", back_populates="satellite_image")


class Detection(Base):
    """Land detection results"""
    __tablename__ = "detections"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("monitoring_regions.id"))
    satellite_image_id = Column(Integer, ForeignKey("satellite_images.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    detection_type = Column(SQLEnum(DetectionType), nullable=False)
    confidence_score = Column(Float, nullable=False)
    detected_area_sqkm = Column(Float)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    details = Column(JSON)  # Additional metadata
    flagged = Column(Boolean, default=False)
    severity = Column(String)  # Low, Medium, High, Critical
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    region = relationship("MonitoringRegion", back_populates="detections")
    satellite_image = relationship("SatelliteImage", back_populates="detections")
    user = relationship("User", back_populates="detections")
    alerts = relationship("Alert", back_populates="detection")


class Alert(Base):
    """Alerts for flagged detections"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id"))
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    
    # Relationships
    detection = relationship("Detection", back_populates="alerts")
