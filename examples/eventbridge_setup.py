"""
Example: Set up EventBridge-based automated ingestion.

This example shows how to configure AWS EventBridge for
automated data ingestion in a production environment.
"""

from data_ingestion.manager import IngestionManager


def main():
    """Set up EventBridge automation."""
    
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
    
    # Set up EventBridge automation
    print("\nSetting up EventBridge automation...")
    manager.setup_automated_ingestion(
        aoi=aoi,
        aoi_id='san_francisco_bay',
        method='eventbridge',
        schedule='cron(0 2 * * ? *)'  # Daily at 2 AM UTC (EventBridge cron format)
    )
    
    # List EventBridge rules
    if hasattr(manager.scheduler, 'list_rules'):
        rules = manager.scheduler.list_rules(name_prefix='land-detection')
        print("\n=== EventBridge Rules ===")
        for rule in rules:
            print(f"Name: {rule['name']}")
            print(f"Schedule: {rule['schedule']}")
            print(f"State: {rule['state']}")
            print(f"ARN: {rule['arn']}")
    
    print("\nEventBridge automation configured successfully!")
    print("\nNext steps:")
    print("1. Create a Lambda function to handle the ingestion")
    print("2. Add the Lambda function as a target to the EventBridge rule")
    print("3. Configure Lambda with appropriate IAM permissions")


if __name__ == '__main__':
    main()
