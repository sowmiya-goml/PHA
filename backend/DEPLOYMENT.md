# PHA Database Connection Manager - Deployment Guide

## 🚀 Deployment Options

### 1. Local Development

#### Prerequisites
- Python 3.11+
- uv package manager
- Git

#### Setup Steps
```bash
# Clone repository
git clone https://github.com/sowmiya-goml/PHA.git
cd PHA/backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your configurations

# Start development server
uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Test Commands
```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app tests/

# Run specific test file
uv run pytest tests/test_connections.py -v
```

---

### 2. Production Deployment

#### Environment Configuration
Create a production `.env` file:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb+srv://prod_user:secure_password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=pha_connections_prod

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-super-secure-production-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Performance
DB_CONNECTION_TIMEOUT_MS=10000
```

#### Production Server Command
```bash
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Gunicorn (Alternative)
```bash
# Install gunicorn
uv add gunicorn

# Run with Gunicorn
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

### 3. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ ./app/

# Install dependencies
RUN uv sync --frozen

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Start server
CMD ["uv", "run", "python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Run
```bash
# Build image
docker build -t pha-backend .

# Run container
docker run -d \
  --name pha-backend \
  -p 8000:8000 \
  --env-file .env \
  pha-backend
```

#### Docker Compose
```yaml
version: '3.8'

services:
  pha-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=${MONGODB_URL}
      - DATABASE_NAME=${DATABASE_NAME}
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

### 4. Cloud Deployment

#### Heroku Deployment

1. **Create Heroku App**
```bash
heroku create pha-backend-prod
```

2. **Add Buildpack**
```bash
heroku buildpacks:add heroku/python
```

3. **Set Environment Variables**
```bash
heroku config:set MONGODB_URL="your-mongodb-url"
heroku config:set DATABASE_NAME="pha_connections"
heroku config:set SECRET_KEY="your-secret-key"
```

4. **Create Procfile**
```bash
echo "web: uv run python -m uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

5. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### Railway Deployment

1. **Connect Repository**
   - Go to Railway.app
   - Connect your GitHub repository

2. **Configure Environment Variables**
   ```
   MONGODB_URL=your-mongodb-url
   DATABASE_NAME=pha_connections
   SECRET_KEY=your-secret-key
   PORT=8000
   ```

3. **Deploy Command**
   ```bash
   uv run python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

#### Render Deployment

1. **Create render.yaml**
```yaml
services:
  - type: web
    name: pha-backend
    env: python
    buildCommand: "pip install uv && uv sync"
    startCommand: "uv run python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: MONGODB_URL
        value: your-mongodb-url
      - key: DATABASE_NAME
        value: pha_connections
      - key: SECRET_KEY
        generateValue: true
```

---

### 5. Kubernetes Deployment

#### Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pha-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pha-backend
  template:
    metadata:
      labels:
        app: pha-backend
    spec:
      containers:
      - name: pha-backend
        image: pha-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: pha-secrets
              key: mongodb-url
        - name: DATABASE_NAME
          value: "pha_connections"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pha-backend-service
spec:
  selector:
    app: pha-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

#### Secret YAML
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pha-secrets
type: Opaque
data:
  mongodb-url: <base64-encoded-mongodb-url>
  secret-key: <base64-encoded-secret-key>
```

---

## 🔧 Configuration Management

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URL` | MongoDB connection string | - | ✅ |
| `DATABASE_NAME` | Database name for connections | `pha_connections` | ✅ |
| `HOST` | Server host | `0.0.0.0` | ❌ |
| `PORT` | Server port | `8000` | ❌ |
| `SECRET_KEY` | Application secret key | - | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` | ❌ |
| `DB_CONNECTION_TIMEOUT_MS` | Database timeout | `10000` | ❌ |

### Security Configuration

#### Production Security Checklist
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS/TLS in production
- [ ] Configure CORS for specific origins
- [ ] Implement rate limiting
- [ ] Use environment-specific MongoDB clusters
- [ ] Enable MongoDB authentication
- [ ] Set up IP whitelisting for MongoDB Atlas
- [ ] Configure proper firewall rules
- [ ] Use secrets management (AWS Secrets Manager, etc.)

#### CORS Configuration
```python
# In app/main.py - Update for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring & Logging

### Health Checks
The application includes health check endpoints:
- `/health` - Basic health status
- `/` - API information and status

### Application Metrics
Consider adding monitoring with:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **New Relic**: Application performance monitoring

### Logging Configuration
```python
# Add to app/core/config.py
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # json or text
```

---

## 🚀 Performance Optimization

### Production Optimizations

1. **Connection Pooling**
```python
# MongoDB connection with pool
client = MongoClient(
    settings.MONGODB_URL,
    maxPoolSize=50,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000
)
```

2. **Async Optimization**
```python
# Use async/await throughout
async def get_connections():
    return await service.get_all_connections()
```

3. **Caching** (Future Enhancement)
```python
# Redis caching for schema results
from redis import Redis
redis_client = Redis(host='localhost', port=6379, db=0)
```

### Resource Requirements

#### Minimum Requirements
- **CPU**: 1 vCPU
- **Memory**: 512MB RAM
- **Storage**: 1GB
- **Network**: 100Mbps

#### Recommended Requirements
- **CPU**: 2 vCPUs
- **Memory**: 1GB RAM
- **Storage**: 5GB
- **Network**: 1Gbps

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy PHA Backend

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install uv
      run: pip install uv
    - name: Install dependencies
      run: uv sync
    - name: Run tests
      run: uv run pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
```

---

## 📋 Maintenance

### Database Backups
```bash
# MongoDB Atlas automatic backups are enabled by default
# For manual backups:
mongodump --uri="your-mongodb-uri" --out=./backup-$(date +%Y%m%d)
```

### Log Rotation
```bash
# Configure log rotation for production
sudo logrotate /etc/logrotate.d/pha-backend
```

### Updates & Patches
```bash
# Update dependencies
uv update

# Run tests after updates
uv run pytest

# Deploy updates
git push origin main
```

---

## 🐛 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check network connectivity
   - Verify Atlas IP whitelist
   - Confirm credentials

2. **High Memory Usage**
   - Monitor document sampling size
   - Check for memory leaks
   - Optimize query patterns

3. **Slow Response Times**
   - Enable connection pooling
   - Optimize database queries
   - Add caching layer

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uv run python -m uvicorn app.main:app --reload
```

---

**Last Updated**: September 2025  
**Version**: 1.0.0
