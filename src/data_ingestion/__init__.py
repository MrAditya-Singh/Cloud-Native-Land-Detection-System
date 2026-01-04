"""
Data Ingestion Package for Cloud-Native Land Detection System

This package handles data ingestion from multiple satellite sources:
- Phase 1: Free sources (Sentinel-2, Landsat-8/9)
- Phase 2: Commercial providers (Planet, Maxar, etc.)

AWS Integration:
- S3 storage with AOI-based organization
- Automated scheduling via cron or EventBridge
"""

__version__ = "0.1.0"
