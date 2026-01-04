# Deployment Guide

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [AWS Deployment](#aws-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)

## Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Steps

1. **Clone and Setup**
   ```bash
   git clone https://github.com/MrAditya-Singh/Cloud-Native-Land-Detection-System.git
   cd Cloud-Native-Land-Detection-System
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start Database Services**
   ```bash
   # Start PostgreSQL
   # Start Redis
   ```

4. **Initialize Database**
   ```bash
   python -c "from src.api.database import init_db; init_db()"
   ```

5. **Run Application**
   ```bash
   uvicorn main:app --reload
   ```

## Docker Deployment

### Using Docker Compose (Recommended for Development)

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- API on port 8000

### Building Docker Image

```bash
docker build -t land-detection:latest .
```

### Running Container

```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@db:5432/land_detection \
  -e REDIS_URL=redis://redis:6379/0 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  land-detection:latest
```

## AWS Deployment

### Infrastructure Setup with Terraform

1. **Install Terraform**
   ```bash
   # Download from terraform.io
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   ```

3. **Deploy Infrastructure**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform plan
   terraform apply
   ```

This creates:
- VPC with public/private subnets
- RDS PostgreSQL database
- ElastiCache Redis cluster
- S3 buckets for data storage
- ECS cluster
- SageMaker notebook instance
- CloudWatch log groups
- IAM roles and security groups

### Application Deployment to ECS

1. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name land-detection
   ```

2. **Build and Push Image**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Build image
   docker build -t land-detection .
   
   # Tag image
   docker tag land-detection:latest \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com/land-detection:latest
   
   # Push image
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/land-detection:latest
   ```

3. **Create ECS Task Definition**
   ```json
   {
     "family": "land-detection",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "land-detection",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/land-detection:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "DATABASE_URL", "value": "postgresql://..."},
           {"name": "REDIS_URL", "value": "redis://..."},
           {"name": "AWS_REGION", "value": "us-east-1"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/aws/land-detection",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

4. **Create ECS Service**
   ```bash
   aws ecs create-service \
     --cluster land-detection-cluster \
     --service-name land-detection-service \
     --task-definition land-detection \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
   ```

### Setting Up Load Balancer

1. **Create Application Load Balancer**
2. **Create Target Group** (port 8000)
3. **Register ECS Service** with target group
4. **Configure health checks** on `/health`

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (EKS, GKE, or local)
- kubectl configured
- Helm (optional)

### Create Kubernetes Manifests

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: land-detection
spec:
  replicas: 3
  selector:
    matchLabels:
      app: land-detection
  template:
    metadata:
      labels:
        app: land-detection
    spec:
      containers:
      - name: land-detection
        image: <your-image>
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: land-detection-secrets
              key: database-url
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: aws-credentials
              key: access-key-id
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

**service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: land-detection-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: land-detection
```

### Deploy

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

## Environment Variables

Key environment variables to configure:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `AWS_REGION`: AWS region
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_SATELLITE_DATA_BUCKET`: S3 bucket for satellite data
- `S3_ML_MODELS_BUCKET`: S3 bucket for ML models
- `S3_RESULTS_BUCKET`: S3 bucket for results
- `SECRET_KEY`: JWT secret key
- `SAGEMAKER_ENDPOINT_NAME`: SageMaker endpoint name

## Monitoring

### CloudWatch
- Enable Container Insights for ECS
- Create alarms for key metrics
- Set up log retention policies

### Prometheus
- Access metrics at `/metrics` endpoint
- Configure Prometheus to scrape metrics
- Set up Grafana dashboards

## Scaling

### Auto Scaling in ECS
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/land-detection-cluster/land-detection-service \
  --min-capacity 2 \
  --max-capacity 10
```

### Auto Scaling Policy
```bash
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/land-detection-cluster/land-detection-service \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Backup and Recovery

### Database Backups
- RDS automated backups enabled
- Retention period: 7 days
- Manual snapshots for major changes

### S3 Versioning
- Enabled on all buckets
- Lifecycle policies for cost optimization

## Security Best Practices

1. Use AWS Secrets Manager for credentials
2. Enable VPC endpoints for AWS services
3. Use IAM roles instead of access keys
4. Enable CloudTrail for audit logging
5. Implement WAF rules for API protection
6. Regular security updates and patching
7. Enable encryption at rest and in transit

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check security group rules
   - Verify database credentials
   - Ensure database is running

2. **S3 Access Denied**
   - Check IAM permissions
   - Verify bucket policies
   - Check bucket names in configuration

3. **High Memory Usage**
   - Increase container memory limits
   - Check for memory leaks
   - Review batch sizes

### Logs

View logs:
```bash
# ECS
aws logs tail /aws/land-detection --follow

# Kubernetes
kubectl logs -f deployment/land-detection
```
