"""
Machine Learning models for land detection
"""
import numpy as np
import tensorflow as tf
from typing import Tuple, Dict, List
import cv2
import logging

logger = logging.getLogger(__name__)


class LandDetectionModel:
    """Base class for land detection ML models"""
    
    def __init__(self, model_path: str = None):
        """Initialize the model"""
        self.model = None
        self.model_path = model_path
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess satellite image for model input
        
        Args:
            image: Raw satellite image
            
        Returns:
            Preprocessed image tensor
        """
        # Resize to model input size
        image = cv2.resize(image, (224, 224))
        
        # Normalize pixel values
        image = image.astype(np.float32) / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """
        Make predictions on satellite image
        
        Args:
            image: Preprocessed image
            
        Returns:
            Dictionary of detection probabilities
        """
        raise NotImplementedError("Subclasses must implement predict method")


class EncroachmentDetector(LandDetectionModel):
    """Model for detecting illegal land encroachment"""
    
    def __init__(self, model_path: str = None):
        super().__init__(model_path)
        self._build_model()
    
    def _build_model(self):
        """Build or load the encroachment detection model"""
        # Simplified CNN model for demonstration
        self.model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Encroachment detection model initialized")
    
    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """Predict encroachment probability"""
        processed = self.preprocess_image(image)
        prediction = self.model.predict(processed, verbose=0)[0][0]
        
        return {
            'encroachment_probability': float(prediction),
            'confidence': float(abs(prediction - 0.5) * 2)  # Confidence based on distance from 0.5
        }


class UrbanExpansionDetector(LandDetectionModel):
    """Model for detecting urban expansion patterns"""
    
    def __init__(self, model_path: str = None):
        super().__init__(model_path)
        self._build_model()
    
    def _build_model(self):
        """Build or load the urban expansion detection model"""
        self.model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(3, activation='softmax')  # Low, Medium, High expansion
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Urban expansion detection model initialized")
    
    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """Predict urban expansion level"""
        processed = self.preprocess_image(image)
        predictions = self.model.predict(processed, verbose=0)[0]
        
        expansion_levels = ['low', 'medium', 'high']
        max_idx = np.argmax(predictions)
        
        return {
            'expansion_level': expansion_levels[max_idx],
            'confidence': float(predictions[max_idx]),
            'probabilities': {
                level: float(prob) for level, prob in zip(expansion_levels, predictions)
            }
        }


class EnvironmentalChangeDetector(LandDetectionModel):
    """Model for detecting environmental changes (deforestation, water bodies, etc.)"""
    
    def __init__(self, model_path: str = None):
        super().__init__(model_path)
        self._build_model()
    
    def _build_model(self):
        """Build or load the environmental change detection model"""
        self.model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(4, activation='softmax')  # Multiple change types
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Environmental change detection model initialized")
    
    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """Predict environmental changes"""
        processed = self.preprocess_image(image)
        predictions = self.model.predict(processed, verbose=0)[0]
        
        change_types = ['deforestation', 'water_body_change', 'vegetation_loss', 'no_change']
        max_idx = np.argmax(predictions)
        
        return {
            'change_type': change_types[max_idx],
            'confidence': float(predictions[max_idx]),
            'probabilities': {
                change: float(prob) for change, prob in zip(change_types, predictions)
            }
        }


class LandDetectionPipeline:
    """Unified pipeline for all land detection models"""
    
    def __init__(self):
        """Initialize all detection models"""
        self.encroachment_detector = EncroachmentDetector()
        self.urban_expansion_detector = UrbanExpansionDetector()
        self.environmental_detector = EnvironmentalChangeDetector()
        
        logger.info("Land detection pipeline initialized")
    
    def analyze_image(self, image: np.ndarray) -> Dict[str, any]:
        """
        Run complete analysis on satellite image
        
        Args:
            image: Satellite image array
            
        Returns:
            Complete analysis results
        """
        results = {
            'encroachment': self.encroachment_detector.predict(image),
            'urban_expansion': self.urban_expansion_detector.predict(image),
            'environmental_change': self.environmental_detector.predict(image)
        }
        
        return results
