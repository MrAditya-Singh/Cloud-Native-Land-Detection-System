# Cloud-Native Land Detection System

AWS-based ML system that identifies land encroachment, urban expansion, and environmental changes using satellite data.

## 🚀 Features

### Data Ingestion System (Startup-Optimized)

#### Phase 1: Free & Reliable Sources
- ✅ **Sentinel-2**: 10m multispectral imagery
- ✅ **Landsat-8/9**: Historical and current data

#### Phase 2: Paid Clients
- ✅ **Commercial Providers**: Plug-in architecture for Planet, Maxar, etc.
- ✅ **On-Demand**: High-resolution imagery requests

#### AWS Integration
- ✅ **Amazon S3**: AOI-based storage organization
- ✅ **Automated Download**: Cron or EventBridge scheduling
- ✅ **Scalable**: Production-ready cloud-native architecture

## 📋 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MrAditya-Singh/Cloud-Native-Land-Detection-System.git
cd Cloud-Native-Land-Detection-System

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - Sentinel Hub credentials
# - Landsat USGS credentials
# - AWS credentials
```

### Basic Usage

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

# Initialize and run
manager = IngestionManager()
results = manager.search_and_download(
    aoi=aoi,
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    sources=['sentinel2', 'landsat'],
    aoi_id='my_region'
)
```

## 📖 Documentation

- [Data Ingestion Guide](docs/DATA_INGESTION.md) - Complete documentation
- [Examples](examples/) - Working code examples

## 🏗️ Architecture

```
Data Ingestion System
├── Phase 1 Providers (Free)
│   ├── Sentinel-2 (10m multispectral)
│   └── Landsat-8/9 (historical)
├── Phase 2 Providers (Commercial)
│   ├── Planet Labs
│   ├── Maxar
│   └── Custom providers
├── Storage Layer
│   └── S3 (AOI-based organization)
└── Automation
    ├── Cron Scheduler
    └── EventBridge Scheduler
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=data_ingestion --cov-report=html
```

## 📦 Project Structure

```
Cloud-Native-Land-Detection-System/
├── src/
│   └── data_ingestion/
│       ├── providers/          # Data source providers
│       ├── storage/            # S3 storage management
│       ├── schedulers/         # Automation schedulers
│       ├── config.py           # Configuration management
│       └── manager.py          # Main ingestion manager
├── config/
│   └── data_ingestion.yaml    # System configuration
├── examples/                  # Usage examples
├── tests/                     # Unit tests
├── docs/                      # Documentation
└── requirements.txt           # Dependencies
```

## 🔑 Key Components

### Data Providers
- **Sentinel2Provider**: ESA Sentinel-2 data access
- **LandsatProvider**: USGS Landsat-8/9 data access
- **CommercialProvider**: Extensible interface for commercial sources

### Storage
- **S3Storage**: AWS S3 with AOI-based organization
- Automatic metadata tagging
- Storage statistics and monitoring

### Schedulers
- **CronScheduler**: Unix cron-style scheduling
- **EventBridgeScheduler**: AWS EventBridge automation

## 🌟 Use Cases

1. **Land Encroachment Detection**: Monitor protected areas
2. **Urban Expansion Analysis**: Track city growth patterns
3. **Environmental Monitoring**: Detect deforestation and land use changes
4. **Agricultural Monitoring**: Track crop health and land use

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions and support, please open an issue on GitHub.
