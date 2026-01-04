# Cloud-Native Land Detection System

> AWS-based ML system that identifies land encroachment, urban expansion, and environmental changes using satellite data.

## 🌍 Overview

The Cloud-Native Land Detection System is a scalable SaaS platform that continuously monitors land changes, flags illegal encroachment, tracks urban and environmental expansion, and provides actionable insights to governments, real estate firms, and NGOs.

## ✨ Features

- **🛰️ Satellite Data Processing**: Automated ingestion and processing of satellite imagery
- **🤖 ML-Powered Detection**: Advanced machine learning models for:
  - Illegal land encroachment detection
  - Urban expansion tracking
  - Environmental change monitoring (deforestation, water bodies, etc.)
- **👥 Multi-Tenant Architecture**: Support for governments, real estate firms, and NGOs
- **🔔 Real-Time Alerts**: Automated alerting for high-confidence detections
- **📊 Analytics & Insights**: Comprehensive dashboards and reporting
- **☁️ Cloud-Native**: Built on AWS with scalability and reliability in mind
- **🔐 Secure**: JWT-based authentication and role-based access control

## 🏗️ Architecture

### Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (AWS RDS)
- **Cache**: Redis (AWS ElastiCache)
- **ML Framework**: TensorFlow
- **Storage**: AWS S3
- **ML Platform**: AWS SageMaker
- **Container Orchestration**: Amazon ECS/Kubernetes
- **Infrastructure as Code**: Terraform
- **Monitoring**: CloudWatch, Prometheus

### System Components

1. **API Layer**: RESTful API built with FastAPI
2. **ML Pipeline**: TensorFlow models for land detection
3. **Data Processing**: Satellite imagery processing and feature extraction
4. **Monitoring Service**: Continuous region scanning and alerting
5. **Storage Layer**: S3 for satellite data, models, and results
6. **Database Layer**: PostgreSQL for relational data, Redis for caching

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- AWS Account (for production deployment)
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MrAditya-Singh/Cloud-Native-Land-Detection-System.git
   cd Cloud-Native-Land-Detection-System
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Initialize the database**
   ```bash
   python -c "from src.api.database import init_db; init_db()"
   ```

7. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

8. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

### Using Docker Compose

The easiest way to run the entire stack:

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis cache
- FastAPI application

## 📖 API Documentation

### Authentication

#### Register a User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "organization": "Government Agency",
  "role": "government"
}
```

#### Login
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=username&password=securepassword
```

### Monitoring Regions

#### Create a Monitoring Region
```http
POST /api/v1/regions/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Downtown Area",
  "description": "City center monitoring",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "radius_km": 5.0
}
```

#### Get All Regions
```http
GET /api/v1/regions/
Authorization: Bearer <token>
```

#### Scan a Region
```http
POST /api/v1/detections/scan/{region_id}
Authorization: Bearer <token>
```

### Detections

#### Get All Detections
```http
GET /api/v1/detections/
Authorization: Bearer <token>
```

#### Get Flagged Detections Only
```http
GET /api/v1/detections/?flagged_only=true
Authorization: Bearer <token>
```

#### Analyze a Region
```http
POST /api/v1/detections/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "region_id": 1,
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59"
}
```

### Insights

#### Get User Insights
```http
GET /api/v1/insights/
Authorization: Bearer <token>
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=src tests/
```

## 🌐 AWS Deployment

### Prerequisites

- AWS CLI configured
- Terraform installed
- AWS credentials with appropriate permissions

### Deploy Infrastructure

1. **Navigate to Terraform directory**
   ```bash
   cd infrastructure/terraform
   ```

2. **Initialize Terraform**
   ```bash
   terraform init
   ```

3. **Review the plan**
   ```bash
   terraform plan
   ```

4. **Apply the configuration**
   ```bash
   terraform apply
   ```

### Deploy Application

1. **Build and push Docker image to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t land-detection .
   docker tag land-detection:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/land-detection:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/land-detection:latest
   ```

2. **Deploy to ECS**
   - Use the AWS Console or CLI to create an ECS service
   - Configure task definition with the Docker image
   - Set environment variables from Parameter Store/Secrets Manager

## 📊 Monitoring & Metrics

### Prometheus Metrics

Access Prometheus metrics at:
```
http://localhost:8000/metrics
```

### CloudWatch Logs

All application logs are sent to CloudWatch under the log group:
```
/aws/land-detection
```

## 🔧 Configuration

Key configuration options in `config/settings.py`:

- `MODEL_CONFIDENCE_THRESHOLD`: Minimum confidence for detections (default: 0.75)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time
- `BATCH_SIZE`: ML model batch size
- AWS S3 bucket names for different data types

## 🤝 Multi-Tenant Support

The system supports multiple organization types:

- **Government**: Full access to monitoring and enforcement
- **Real Estate**: Monitor properties and development areas
- **NGO**: Environmental monitoring and conservation
- **Admin**: System administration

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Encrypted password storage with bcrypt
- HTTPS/TLS in production
- AWS IAM for service access
- VPC isolation for databases

## 📈 Scalability

- **Horizontal Scaling**: ECS tasks can be scaled based on load
- **Database**: RDS with read replicas for read-heavy workloads
- **Caching**: Redis for frequently accessed data
- **Storage**: S3 for unlimited satellite data storage
- **ML**: SageMaker endpoints for scalable inference

## 🛠️ Development

### Project Structure

```
Cloud-Native-Land-Detection-System/
├── src/
│   ├── api/              # API routes and models
│   │   ├── routes/       # API endpoints
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── database.py   # Database configuration
│   ├── ml/               # Machine learning models
│   │   └── detection_models.py
│   ├── services/         # Business logic
│   │   ├── monitoring_service.py
│   │   └── satellite_service.py
│   └── utils/            # Utilities
│       ├── auth.py       # Authentication
│       └── aws_service.py # AWS integration
├── config/               # Configuration
│   └── settings.py
├── infrastructure/       # Infrastructure as Code
│   ├── terraform/        # Terraform files
│   └── docker/           # Docker configurations
├── tests/                # Test suite
├── docs/                 # Documentation
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image
└── docker-compose.yml    # Local development setup
```

### Adding New Detection Models

1. Create a new detector class in `src/ml/detection_models.py`
2. Inherit from `LandDetectionModel`
3. Implement `predict()` method
4. Add to `LandDetectionPipeline`

### Adding New API Endpoints

1. Create a new router in `src/api/routes/`
2. Define endpoints with FastAPI decorators
3. Include router in `main.py`

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For questions or support, please open an issue on GitHub.

## 🎯 Roadmap

- [ ] Real-time streaming data processing
- [ ] Advanced ML models (LSTM for temporal analysis)
- [ ] Mobile application
- [ ] Integration with more satellite data sources
- [ ] Automated reporting and notifications
- [ ] GraphQL API support
- [ ] Kubernetes deployment templates
- [ ] Advanced visualization dashboard
- [ ] AI-powered change prediction

## 🙏 Acknowledgments

- AWS for cloud infrastructure
- TensorFlow team for ML framework
- FastAPI for the excellent web framework
- The open-source community

---

Built with ❤️ for a sustainable future
