"""
Example: Set up automated data ingestion using cron scheduler.

This example demonstrates how to set up automated satellite data
downloads that run on a schedule.
"""

from datetime import datetime, timedelta
from data_ingestion.manager import IngestionManager


def main():
    """Set up automated ingestion."""
    
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
    
    # Initialize ingestion manager
    print("Initializing ingestion manager...")
    manager = IngestionManager()
    
    # Set up automated ingestion (cron-based)
    print("\nSetting up automated ingestion...")
    manager.setup_automated_ingestion(
        aoi=aoi,
        aoi_id='san_francisco_bay',
        method='cron',
        schedule='0 2 * * *'  # Daily at 2 AM
    )
    
    # List scheduled jobs
    if manager.scheduler:
        jobs = manager.scheduler.list_jobs()
        print("\n=== Scheduled Jobs ===")
        for job in jobs:
            print(f"Task: {job['name']}")
            print(f"Schedule: {job['schedule']}")
            print(f"Next run: {job.get('next_run', 'N/A')}")
        
        # Run scheduler (this will block)
        print("\nStarting scheduler... (Press Ctrl+C to stop)")
        try:
            manager.scheduler.run()
        except KeyboardInterrupt:
            print("\nScheduler stopped.")


if __name__ == '__main__':
    main()
