# Data Ingestion System - Cloud-Native Land Detection

## Overview

This data ingestion system provides automated satellite data acquisition for the Cloud-Native Land Detection System. It supports multiple data sources, AWS S3 storage with AOI-based organization, and automated scheduling.

## Features

### Phase 1: Free & Reliable Data Sources ✅
- **Sentinel-2**: 10m multispectral imagery from ESA
- **Landsat-8/9**: Historical and current data from USGS

### Phase 2: Commercial Providers (Paid Clients) ✅
- Plug-in architecture for commercial providers (Planet, Maxar, etc.)
- On-demand high-resolution imagery requests
- Extensible provider interface

### AWS Integration ✅
- **Amazon S3**: AOI-based storage organization
- **Automated Download**: Via cron or AWS EventBridge
- **Scalable Architecture**: Production-ready cloud-native design

## Installation

### Prerequisites
- Python 3.8+
- AWS account with S3 access (for cloud storage)
- Credentials for satellite data providers

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install the package:

```bash
pip install -e .
```

## Configuration

### 1. Environment Variables

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Sentinel Hub
SENTINEL_USERNAME=your_username
SENTINEL_PASSWORD=your_password

# Landsat USGS
LANDSAT_USERNAME=your_username
LANDSAT_PASSWORD=your_password

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=land-detection-satellite-data

# Commercial Providers (Phase 2)
PLANET_API_KEY=your_planet_key
MAXAR_API_KEY=your_maxar_key
```

### 2. Configuration File

The system uses `config/data_ingestion.yaml` for configuration. Key settings:

```yaml
data_ingestion:
  phase1:
    sentinel2:
      enabled: true
      resolution: "10m"
      max_cloud_coverage: 20
    
    landsat:
      enabled: true
      missions: ["landsat-8", "landsat-9"]

  phase2:
    commercial_providers:
      enabled: false  # Enable for paid clients

aws:
  s3:
    enabled: true
    bucket_name: "land-detection-satellite-data"
    aoi_based_storage: true
  
  automation:
    method: "cron"  # or "eventbridge"
    schedule: "0 2 * * *"  # Daily at 2 AM
```

## Usage

### Basic Data Ingestion

```python
from datetime import datetime, timedelta
from data_ingestion.manager import IngestionManager

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

# Initialize manager
manager = IngestionManager()

# Search and download
results = manager.search_and_download(
    aoi=aoi,
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    sources=['sentinel2', 'landsat'],
    aoi_id='my_region',
    upload_to_s3=True
)
```

### Automated Ingestion (Cron)

```python
manager = IngestionManager()

manager.setup_automated_ingestion(
    aoi=aoi,
    aoi_id='my_region',
    method='cron',
    schedule='0 2 * * *'  # Daily at 2 AM
)

# Run scheduler
manager.scheduler.run()
```

### Automated Ingestion (EventBridge)

```python
manager = IngestionManager()

manager.setup_automated_ingestion(
    aoi=aoi,
    aoi_id='my_region',
    method='eventbridge',
    schedule='cron(0 2 * * ? *)'  # EventBridge format
)
```

### Commercial Providers (Phase 2)

```python
# Enable commercial providers in config
# Set API keys in .env file

manager = IngestionManager()

results = manager.search_and_download(
    aoi=aoi,
    start_date=start_date,
    end_date=end_date,
    sources=['planet', 'maxar'],  # Commercial sources
    max_cloud_coverage=10,
    aoi_id='premium_client'
)
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_ingestion.py`: Simple data download
- `automated_ingestion.py`: Cron-based automation
- `eventbridge_setup.py`: AWS EventBridge setup
- `commercial_provider_usage.py`: Phase 2 commercial providers

## Storage Structure

Data is organized in S3 using AOI-based structure:

```
s3://bucket-name/
├── aoi_001/
│   ├── sentinel2/
│   │   ├── 2024-01-01/
│   │   │   └── scene.tif
│   │   └── 2024-01-02/
│   └── landsat/
│       └── 2024-01-01/
└── aoi_002/
    └── ...
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Ingestion Manager                       │
├─────────────────────────────────────────────────┤
│  Phase 1 Providers    │  Phase 2 Providers      │
│  - Sentinel-2         │  - Planet Labs          │
│  - Landsat-8/9        │  - Maxar                │
│                       │  - Custom providers     │
├─────────────────────────────────────────────────┤
│  Storage Layer                                  │
│  - S3 with AOI-based organization               │
├─────────────────────────────────────────────────┤
│  Scheduling Layer                               │
│  - Cron Scheduler                               │
│  - EventBridge Scheduler                        │
└─────────────────────────────────────────────────┘
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=data_ingestion --cov-report=html
```

## API Reference

### IngestionManager

Main interface for data ingestion.

**Methods:**
- `search_and_download()`: Search and download satellite data
- `setup_automated_ingestion()`: Configure automated downloads
- `get_storage_stats()`: Get S3 storage statistics

### Data Providers

**Sentinel2Provider**: Sentinel-2 data access
**LandsatProvider**: Landsat-8/9 data access
**CommercialProvider**: Base class for commercial providers

### Storage

**S3Storage**: Amazon S3 storage with AOI-based organization

**Methods:**
- `upload_file()`: Upload data to S3
- `download_file()`: Download data from S3
- `list_files()`: List stored files
- `get_storage_stats()`: Get storage statistics

### Schedulers

**CronScheduler**: Unix cron-style scheduling
**EventBridgeScheduler**: AWS EventBridge automation

## AWS Permissions

Required IAM permissions for S3 and EventBridge:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutRule",
        "events:PutTargets",
        "events:DeleteRule",
        "events:RemoveTargets",
        "events:EnableRule",
        "events:DisableRule"
      ],
      "Resource": "arn:aws:events:*:*:rule/land-detection-*"
    }
  ]
}
```

## Extending the System

### Adding a New Commercial Provider

1. Create a new provider class inheriting from `CommercialProvider`
2. Implement `search()` and `download()` methods
3. Add to the provider factory in `providers/commercial.py`
4. Update configuration file

Example:

```python
from .commercial import CommercialProvider

class MyProvider(CommercialProvider):
    def search(self, aoi, start_date, end_date, **kwargs):
        # Implement search logic
        pass
    
    def download(self, product, output_path, **kwargs):
        # Implement download logic
        pass
```

## Troubleshooting

### Common Issues

1. **Authentication errors**: Verify credentials in `.env` file
2. **S3 permissions**: Check IAM permissions
3. **API rate limits**: Implement retry logic or reduce frequency
4. **Network timeouts**: Increase timeout values in provider config

## License

See LICENSE file for details.

## Support

For issues and questions, please open an issue on the repository.
