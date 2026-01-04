# Cloud-Native Land Detection System

> 🛰️ AWS-based ML system that identifies land encroachment, urban expansion, and environmental changes using satellite data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![AWS](https://img.shields.io/badge/AWS-Powered-orange.svg)](https://aws.amazon.com/)

## 🌍 Overview

A scalable SaaS platform that continuously monitors land changes, flags illegal encroachment, tracks urban and environmental expansion, and provides actionable insights to governments, real estate firms, and NGOs.

## ✨ Key Features

- **🤖 ML-Powered Detection**: Advanced deep learning models for automated land change detection
- **🛰️ Satellite Data Processing**: Automated ingestion and analysis of satellite imagery
- **🔔 Real-Time Alerts**: Instant notifications for high-confidence detections
- **👥 Multi-Tenant Support**: Designed for governments, real estate firms, and NGOs
- **📊 Analytics Dashboard**: Comprehensive insights and reporting
- **☁️ Cloud-Native**: Built on AWS with scalability and reliability
- **🔐 Enterprise Security**: JWT authentication and role-based access control

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
git clone https://github.com/MrAditya-Singh/Cloud-Native-Land-Detection-System.git
cd Cloud-Native-Land-Detection-System
cp .env.example .env
docker-compose up -d
```

Access the API at: http://localhost:8000/docs

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Initialize database
python -c "from src.api.database import init_db; init_db()"

# Run application
uvicorn main:app --reload
```

## 📖 Documentation

- **[Complete Documentation](docs/README.md)** - Full system documentation
- **[API Reference](docs/API.md)** - API endpoints and usage
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Deployment instructions

## 🏗️ Architecture

### Technology Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 (AWS RDS)
- **Cache**: Redis 7 (AWS ElastiCache)
- **ML**: TensorFlow, OpenCV
- **Storage**: AWS S3
- **ML Platform**: AWS SageMaker
- **Orchestration**: Amazon ECS/Kubernetes
- **IaC**: Terraform
- **Monitoring**: CloudWatch, Prometheus

### Detection Capabilities

1. **Illegal Encroachment Detection**
   - Identifies unauthorized land use
   - Flags potential violations
   - Confidence-based alerting

2. **Urban Expansion Tracking**
   - Monitors city growth patterns
   - Tracks development areas
   - Analyzes expansion rates

3. **Environmental Change Monitoring**
   - Deforestation detection
   - Water body changes
   - Vegetation loss tracking

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_auth.py
```

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Login and get token
- `GET /api/v1/auth/me` - Get current user

### Monitoring Regions
- `POST /api/v1/regions/` - Create monitoring region
- `GET /api/v1/regions/` - List all regions
- `GET /api/v1/regions/{id}` - Get specific region
- `PUT /api/v1/regions/{id}/activate` - Activate region

### Detections
- `POST /api/v1/detections/scan/{region_id}` - Scan region
- `GET /api/v1/detections/` - List detections
- `POST /api/v1/detections/analyze` - Analyze region
- `GET /api/v1/insights/` - Get user insights

## 🔧 Configuration

Key environment variables:

```env
# AWS
AWS_REGION=us-east-1
S3_SATELLITE_DATA_BUCKET=land-detection-satellite-data
S3_ML_MODELS_BUCKET=land-detection-ml-models

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/land_detection

# ML
MODEL_CONFIDENCE_THRESHOLD=0.75
SAGEMAKER_ENDPOINT_NAME=land-detection-endpoint

# Security
SECRET_KEY=your-secret-key
```

## 📊 System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Load Balancer (ALB)                  │
└────────────────────┬────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │    FastAPI App      │
          │    (ECS/K8s)        │
          └──────────┬──────────┘
                     │
       ┌─────────────┼─────────────┐
       │             │             │
   ┌───▼───┐    ┌───▼───┐    ┌───▼────┐
   │  RDS  │    │ Redis │    │   S3   │
   │ (DB)  │    │(Cache)│    │(Storage)│
   └───────┘    └───────┘    └────────┘
                     │
              ┌──────▼──────┐
              │  SageMaker  │
              │ (ML Models) │
              └─────────────┘
```

## 🔒 Security Features

- JWT-based authentication
- Role-based access control (RBAC)
- Encrypted password storage (bcrypt)
- VPC isolation for databases
- AWS IAM for service access
- HTTPS/TLS encryption

## 📈 Scalability

- **Horizontal scaling** with ECS/Kubernetes
- **Database replication** for read-heavy workloads
- **Caching layer** with Redis
- **Unlimited storage** with S3
- **Auto-scaling** based on metrics

## 🤝 Multi-Tenant Support

The system supports multiple organization types:

- **Government** 🏛️: Full monitoring and enforcement access
- **Real Estate** 🏗️: Property and development monitoring
- **NGO** 🌱: Environmental conservation tracking
- **Admin** 👑: System administration

## 🛠️ Development

### Project Structure

```
Cloud-Native-Land-Detection-System/
├── src/
│   ├── api/              # API routes and models
│   ├── ml/               # ML models and pipelines
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── config/               # Configuration
├── infrastructure/       # Terraform & Docker
├── tests/                # Test suite
├── docs/                 # Documentation
└── main.py              # Application entry point
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

For questions or support, please open an issue on GitHub.

## 🎯 Roadmap

- [x] Core ML detection models
- [x] Multi-tenant authentication
- [x] RESTful API
- [x] AWS infrastructure setup
- [ ] Real-time data streaming
- [ ] Advanced LSTM models
- [ ] Mobile application
- [ ] GraphQL API
- [ ] Kubernetes deployment
- [ ] Advanced visualization dashboard

---

**Built with ❤️ for a sustainable future** 🌍
