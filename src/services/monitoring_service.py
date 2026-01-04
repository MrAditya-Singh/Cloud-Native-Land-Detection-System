"""
Land monitoring service for continuous tracking and alerting
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.api.models import MonitoringRegion, Detection, Alert, SatelliteImage, DetectionType
from src.api.schemas import DetectionCreate, AlertCreate
from src.ml.detection_models import LandDetectionPipeline
from src.services.satellite_service import SatelliteDataProcessor
from config.settings import settings

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring land changes"""
    
    def __init__(self):
        """Initialize monitoring service"""
        self.ml_pipeline = LandDetectionPipeline()
        self.satellite_processor = SatelliteDataProcessor()
    
    def scan_region(self, region: MonitoringRegion, db: Session) -> List[Detection]:
        """
        Scan a monitoring region for changes
        
        Args:
            region: Monitoring region to scan
            db: Database session
            
        Returns:
            List of detections found
        """
        logger.info(f"Scanning region: {region.name} (ID: {region.id})")
        
        # Get recent satellite images for this region
        satellite_images = self._get_recent_satellite_images(region, db)
        
        if not satellite_images:
            logger.warning(f"No satellite images found for region {region.id}")
            return []
        
        detections = []
        
        for sat_image in satellite_images:
            # Load and process image
            image = self.satellite_processor.load_satellite_image(sat_image.s3_key)
            
            if image is None:
                continue
            
            # Preprocess
            processed_image = self.satellite_processor.preprocess_for_analysis(image)
            
            # Run ML analysis
            analysis_results = self.ml_pipeline.analyze_image(processed_image)
            
            # Create detections based on results
            new_detections = self._create_detections_from_analysis(
                analysis_results,
                region,
                sat_image,
                db
            )
            
            detections.extend(new_detections)
            
            # Mark image as processed
            sat_image.processed = True
        
        # Update region last scanned time
        region.last_scanned = datetime.utcnow()
        db.commit()
        
        logger.info(f"Found {len(detections)} detections in region {region.id}")
        
        return detections
    
    def _get_recent_satellite_images(
        self,
        region: MonitoringRegion,
        db: Session,
        days: int = 7
    ) -> List[SatelliteImage]:
        """Get recent unprocessed satellite images for a region"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query images within region bounds (simplified - in production use spatial queries)
        lat_range = 0.1  # ~11km
        lon_range = 0.1
        
        images = db.query(SatelliteImage).filter(
            and_(
                SatelliteImage.latitude.between(
                    region.latitude - lat_range,
                    region.latitude + lat_range
                ),
                SatelliteImage.longitude.between(
                    region.longitude - lon_range,
                    region.longitude + lon_range
                ),
                SatelliteImage.capture_date >= cutoff_date,
                SatelliteImage.processed == False
            )
        ).all()
        
        return images
    
    def _create_detections_from_analysis(
        self,
        analysis: dict,
        region: MonitoringRegion,
        satellite_image: SatelliteImage,
        db: Session
    ) -> List[Detection]:
        """Create detection records from ML analysis results"""
        detections = []
        
        # Check encroachment
        if analysis['encroachment']['encroachment_probability'] > settings.MODEL_CONFIDENCE_THRESHOLD:
            detection = Detection(
                region_id=region.id,
                satellite_image_id=satellite_image.id,
                user_id=region.user_id,
                detection_type=DetectionType.ENCROACHMENT,
                confidence_score=analysis['encroachment']['confidence'],
                latitude=satellite_image.latitude,
                longitude=satellite_image.longitude,
                details=analysis['encroachment'],
                severity=self._calculate_severity(analysis['encroachment']['confidence'])
            )
            
            # Flag high-confidence encroachments
            if detection.confidence_score > 0.9:
                detection.flagged = True
                self._create_alert(detection, db)
            
            db.add(detection)
            detections.append(detection)
        
        # Check urban expansion
        urban_result = analysis['urban_expansion']
        if urban_result['expansion_level'] in ['medium', 'high']:
            detection = Detection(
                region_id=region.id,
                satellite_image_id=satellite_image.id,
                user_id=region.user_id,
                detection_type=DetectionType.URBAN_EXPANSION,
                confidence_score=urban_result['confidence'],
                latitude=satellite_image.latitude,
                longitude=satellite_image.longitude,
                details=urban_result,
                severity=urban_result['expansion_level']
            )
            
            if urban_result['expansion_level'] == 'high':
                detection.flagged = True
                self._create_alert(detection, db)
            
            db.add(detection)
            detections.append(detection)
        
        # Check environmental changes
        env_result = analysis['environmental_change']
        if env_result['change_type'] != 'no_change' and env_result['confidence'] > settings.MODEL_CONFIDENCE_THRESHOLD:
            detection = Detection(
                region_id=region.id,
                satellite_image_id=satellite_image.id,
                user_id=region.user_id,
                detection_type=DetectionType.ENVIRONMENTAL_CHANGE,
                confidence_score=env_result['confidence'],
                latitude=satellite_image.latitude,
                longitude=satellite_image.longitude,
                details=env_result,
                severity=self._calculate_severity(env_result['confidence'])
            )
            
            if env_result['change_type'] == 'deforestation':
                detection.flagged = True
                self._create_alert(detection, db)
            
            db.add(detection)
            detections.append(detection)
        
        db.commit()
        return detections
    
    def _calculate_severity(self, confidence: float) -> str:
        """Calculate severity level based on confidence"""
        if confidence >= 0.95:
            return "Critical"
        elif confidence >= 0.85:
            return "High"
        elif confidence >= 0.75:
            return "Medium"
        else:
            return "Low"
    
    def _create_alert(self, detection: Detection, db: Session):
        """Create an alert for a flagged detection"""
        alert = Alert(
            detection_id=detection.id,
            title=f"{detection.detection_type.value.replace('_', ' ').title()} Detected",
            message=f"High-confidence {detection.detection_type.value} detected at ({detection.latitude}, {detection.longitude})",
            severity=detection.severity
        )
        db.add(alert)
        db.commit()
        
        logger.warning(f"Alert created for detection {detection.id}")
    
    def get_insights(self, user_id: int, db: Session) -> dict:
        """Get insights for a user's monitored regions"""
        # Get total monitored regions
        total_regions = db.query(func.count(MonitoringRegion.id)).filter(
            and_(
                MonitoringRegion.user_id == user_id,
                MonitoringRegion.is_active == True
            )
        ).scalar()
        
        # Get total detections
        total_detections = db.query(func.count(Detection.id)).filter(
            Detection.user_id == user_id
        ).scalar()
        
        # Get critical alerts
        critical_alerts = db.query(func.count(Alert.id)).join(Detection).filter(
            and_(
                Detection.user_id == user_id,
                Alert.severity == "Critical",
                Alert.acknowledged == False
            )
        ).scalar()
        
        # Get recent changes (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_changes = db.query(Detection).filter(
            and_(
                Detection.user_id == user_id,
                Detection.created_at >= cutoff_date
            )
        ).order_by(Detection.created_at.desc()).limit(10).all()
        
        return {
            'total_monitored_regions': total_regions,
            'total_detections': total_detections,
            'critical_alerts': critical_alerts,
            'recent_changes': recent_changes
        }


# Singleton instance
monitoring_service = MonitoringService()
