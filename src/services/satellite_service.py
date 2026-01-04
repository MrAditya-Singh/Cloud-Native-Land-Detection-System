"""
Satellite data processing service
"""
import numpy as np
import cv2
import rasterio
from typing import Optional, Tuple
import logging
from datetime import datetime

from src.utils.aws_service import aws_service
from config.settings import settings

logger = logging.getLogger(__name__)


class SatelliteDataProcessor:
    """Process satellite imagery for analysis"""
    
    @staticmethod
    def load_satellite_image(s3_key: str) -> Optional[np.ndarray]:
        """
        Load satellite image from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Image array or None
        """
        try:
            image_data = aws_service.get_s3_object(
                settings.S3_SATELLITE_DATA_BUCKET,
                s3_key
            )
            
            if image_data is None:
                return None
            
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
        except Exception as e:
            logger.error(f"Error loading satellite image: {e}")
            return None
    
    @staticmethod
    def preprocess_for_analysis(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for ML analysis
        
        Args:
            image: Raw satellite image
            
        Returns:
            Preprocessed image
        """
        # Apply preprocessing steps
        # 1. Denoise
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        # 2. Enhance contrast
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    @staticmethod
    def extract_features(image: np.ndarray) -> dict:
        """
        Extract features from satellite image
        
        Args:
            image: Satellite image
            
        Returns:
            Feature dictionary
        """
        features = {}
        
        # Color histogram
        for i, color in enumerate(['blue', 'green', 'red']):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            features[f'{color}_histogram'] = hist.flatten().tolist()
        
        # NDVI approximation (if image has NIR band, otherwise use green-red)
        # For RGB images, we approximate
        green = image[:, :, 1].astype(float)
        red = image[:, :, 2].astype(float)
        ndvi = (green - red) / (green + red + 1e-8)
        features['ndvi_mean'] = float(np.mean(ndvi))
        features['ndvi_std'] = float(np.std(ndvi))
        
        # Texture features (simplified)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        features['texture_contrast'] = float(np.std(gray))
        
        return features
    
    @staticmethod
    def calculate_area_change(image1: np.ndarray, image2: np.ndarray) -> float:
        """
        Calculate area change between two images
        
        Args:
            image1: First image (older)
            image2: Second image (newer)
            
        Returns:
            Percentage of area changed
        """
        # Convert to grayscale
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        
        # Calculate difference
        diff = cv2.absdiff(gray1, gray2)
        
        # Threshold to find significant changes
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of changed pixels
        changed_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.size
        change_percentage = (changed_pixels / total_pixels) * 100
        
        return change_percentage
    
    @staticmethod
    def detect_land_cover_type(image: np.ndarray) -> dict:
        """
        Detect basic land cover types in image
        
        Args:
            image: Satellite image
            
        Returns:
            Dictionary of land cover percentages
        """
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for different land types
        # Water (blue)
        water_mask = cv2.inRange(hsv, np.array([90, 50, 50]), np.array([130, 255, 255]))
        
        # Vegetation (green)
        vegetation_mask = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
        
        # Urban/Built-up (gray/white)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, urban_mask = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        total_pixels = image.shape[0] * image.shape[1]
        
        return {
            'water_percentage': (np.count_nonzero(water_mask) / total_pixels) * 100,
            'vegetation_percentage': (np.count_nonzero(vegetation_mask) / total_pixels) * 100,
            'urban_percentage': (np.count_nonzero(urban_mask) / total_pixels) * 100
        }
