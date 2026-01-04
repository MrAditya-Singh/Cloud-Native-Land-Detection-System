"""
Example: Commercial provider usage (Phase 2).

This example demonstrates how to use commercial data providers
for paid clients requiring high-resolution imagery.
"""

from datetime import datetime, timedelta
from data_ingestion.manager import IngestionManager


def main():
    """Demonstrate commercial provider usage."""
    
    # Define Area of Interest
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
    
    # Time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Initialize ingestion manager
    print("Initializing ingestion manager with commercial providers...")
    manager = IngestionManager()
    
    # Check available commercial providers
    commercial_providers = [
        name for name in manager.providers.keys()
        if name not in ['sentinel2', 'landsat']
    ]
    
    if commercial_providers:
        print(f"\nAvailable commercial providers: {', '.join(commercial_providers)}")
        
        # Search using commercial providers
        print("\nSearching for commercial satellite data...")
        results = manager.search_and_download(
            aoi=aoi,
            start_date=start_date,
            end_date=end_date,
            sources=commercial_providers,
            max_cloud_coverage=10,  # Stricter cloud coverage for high-res
            aoi_id='premium_client_001',
            upload_to_s3=True
        )
        
        # Display results
        print("\n=== Commercial Data Results ===")
        for source, files in results.items():
            print(f"{source}: {len(files)} files downloaded")
    else:
        print("\nNo commercial providers enabled.")
        print("\nTo enable commercial providers:")
        print("1. Set PLANET_API_KEY or MAXAR_API_KEY in .env file")
        print("2. Enable commercial providers in config/data_ingestion.yaml")
        print("3. Implement provider-specific search and download methods")
    
    # Example: On-demand high-resolution request
    print("\n=== On-Demand Request Example ===")
    print("For on-demand high-resolution imagery acquisition:")
    print("- Contact commercial provider (Planet, Maxar, etc.)")
    print("- Specify AOI, desired resolution, and acquisition date")
    print("- Provider schedules satellite tasking")
    print("- Data delivered within agreed SLA")


if __name__ == '__main__':
    main()
