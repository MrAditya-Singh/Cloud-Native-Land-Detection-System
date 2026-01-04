"""
Example: Basic satellite data ingestion using the data ingestion system.

This example demonstrates how to:
1. Initialize the ingestion manager
2. Search and download Sentinel-2 and Landsat data
3. Upload data to S3 with AOI-based organization
"""

import os
from datetime import datetime, timedelta
from data_ingestion.manager import IngestionManager


def main():
    """Run basic ingestion example."""
    
    # Define Area of Interest (example: region around San Francisco)
    aoi = {
        "type": "Polygon",
        "coordinates": [[
            [-122.5, 37.7],
            [-122.3, 37.7],
            [-122.3, 37.9],
            [-122.5, 37.9],
            [-122.5, 37.7]
        ]]
    }
    
    # Define time range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Initialize ingestion manager
    print("Initializing ingestion manager...")
    manager = IngestionManager()
    
    # Search and download data
    print(f"\nSearching for satellite data from {start_date.date()} to {end_date.date()}...")
    results = manager.search_and_download(
        aoi=aoi,
        start_date=start_date,
        end_date=end_date,
        sources=['sentinel2', 'landsat'],  # Use both Phase 1 sources
        max_cloud_coverage=20,
        aoi_id='san_francisco_bay',
        upload_to_s3=True
    )
    
    # Display results
    print("\n=== Download Results ===")
    for source, files in results.items():
        print(f"\n{source}:")
        print(f"  Downloaded {len(files)} files")
        for file_path in files[:3]:  # Show first 3 files
            print(f"  - {file_path}")
    
    # Get storage statistics
    if manager.storage:
        print("\n=== Storage Statistics ===")
        stats = manager.get_storage_stats(aoi_id='san_francisco_bay')
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_gb']:.2f} GB")
        print(f"By source:")
        for source, source_stats in stats.get('by_source', {}).items():
            print(f"  {source}: {source_stats['count']} files, "
                  f"{source_stats['size'] / (1024**3):.2f} GB")


if __name__ == '__main__':
    main()
