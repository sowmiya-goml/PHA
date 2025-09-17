# MongoDB Connection Testing Guide

## Overview
This guide provides comprehensive instructions for testing MongoDB Atlas connections in the Health Foundary PHA application.

## Quick Connection Test

### Prerequisites
- Python 3.11+
- UV package manager installed
- Access to MongoDB Atlas cluster
- Valid connection credentials

### Running the Test
```bash
# Navigate to project root
cd /path/to/PHA

# Run the connection test
uv run python scripts/test_mongodb_connection.py
```

### Expected Output
```
🧪 Testing MongoDB Atlas connection...
📍 Target: pha.o1mtvpd.mongodb.net/
⏳ Attempting connection...
✅ SUCCESS! Connected in 0.82 seconds
📊 Ping result: {'ok': 1}
📂 Available collections: ['database_connections', 'fhir_apps']

🎉 MongoDB Atlas connection is working correctly!
```

## Connection Configuration

### MongoDB Atlas Settings
- **Cluster**: `pha.o1mtvpd.mongodb.net`
- **Database**: `pha_connections`
- **Connection Type**: MongoDB Atlas (SRV)
- **Authentication**: Username/Password

### Optimized Connection Parameters
```python
MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000,  # 5 seconds
    connectTimeoutMS=10000,         # 10 seconds  
    socketTimeoutMS=10000,          # 10 seconds
    retryWrites=True,
    retryReads=True,
    directConnection=False,
    heartbeatFrequencyMS=5000
)
```

## Troubleshooting

### Common Issues

#### 1. DNS Resolution Timeout
**Symptoms:**
```
⚠️  DNS resolution failed on attempt 1: Network/DNS issue
```

**Solutions:**
- Check internet connection
- Verify DNS settings (try 8.8.8.8, 1.1.1.1)
- Disable VPN if active
- Check firewall settings

#### 2. Connection Timeout  
**Symptoms:**
```
⚠️  Connection timeout on attempt 1: MongoDB Atlas may be slow
```

**Solutions:**
- Verify MongoDB Atlas cluster is running
- Check cluster region (should be ap-south-1)
- Verify IP whitelist includes your IP
- Check for network proxy issues

#### 3. Authentication Failed
**Symptoms:**
```
❌ FAILED: Authentication failed
```

**Solutions:**
- Verify username: `22cs027_db_user`
- Check password validity
- Ensure user has proper database permissions
- Verify connection string format

#### 4. Database Access Issues
**Symptoms:**
```
📂 Available collections: []
```

**Solutions:**
- Check database name: `pha_connections`
- Verify user permissions for database
- Ensure collections exist in Atlas

## Performance Benchmarks

### Expected Connection Times
- **First Connection**: < 2 seconds
- **Subsequent Connections**: < 1 second
- **Ping Response**: < 500ms

### Timeout Settings
- **Server Selection**: 5 seconds
- **Connection**: 10 seconds
- **Socket**: 10 seconds
- **Heartbeat**: 5 seconds

## Manual Testing Steps

### 1. Basic Connectivity Test
```bash
# Test basic connection
uv run python -c "
from pymongo import MongoClient
client = MongoClient('mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA')
print('✅ Connected:', client.admin.command('ping'))
client.close()
"
```

### 2. Database Operations Test
```bash
# Test database operations
uv run python -c "
from pymongo import MongoClient
client = MongoClient('mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA')
db = client['pha_connections']
print('📂 Collections:', db.list_collection_names())
print('📊 Stats:', db.command('dbstats'))
client.close()
"
```

### 3. Application Integration Test
```bash
# Test within application context
uv run uvicorn pha.main:app --host 0.0.0.0 --port 8000
# Check logs for: "✅ Connected to MongoDB"
```

## Environment Configuration

### Required Environment Variables
```env
# MongoDB Atlas Configuration
MONGODB_URL=mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA
DATABASE_NAME=pha_connections

# Connection Timeouts (optional)
DB_CONNECTION_TIMEOUT_MS=10000
DB_SERVER_SELECTION_TIMEOUT_MS=5000
```

### Configuration File Location
- **Development**: `config/.env`
- **Production**: `config/.env.production`
- **Testing**: `config/.env.development`

## Monitoring and Logging

### Application Logs
```
2025-09-17 11:19:36 - pha.db.session - INFO - 🔗 Connecting to MongoDB Atlas cluster: pha.o1mtvpd.mongodb.net/
2025-09-17 11:19:36 - pha.db.session - INFO - Attempting to connect to MongoDB (attempt 1/3)
2025-09-17 11:19:37 - pha.db.session - INFO - ✅ Connected to MongoDB at mongodb+srv://22cs027_db_user:SathyaPainter@pha.o1mtvpd.mongodb.net/?retryWrites=true&w=majority&appName=PHA
```

### MongoDB Atlas Monitoring
- Check cluster metrics in Atlas dashboard
- Monitor connection count
- Review slow operation logs
- Check network access configuration

## Security Considerations

### Connection Security
- Uses TLS encryption (mongodb+srv://)
- Authentication via username/password
- IP whitelist configured in Atlas
- No hardcoded credentials in application code

### Best Practices
- Rotate passwords regularly
- Use environment variables for credentials
- Monitor connection attempts
- Implement connection pooling
- Use proper error handling

## Development vs Production

### Development Settings
```python
# Faster timeouts for development
serverSelectionTimeoutMS=5000
connectTimeoutMS=10000
```

### Production Settings
```python
# More resilient timeouts for production
serverSelectionTimeoutMS=10000
connectTimeoutMS=20000
maxPoolSize=100
minPoolSize=10
```

## Related Documentation
- [Application Architecture](./development/architecture.md)
- [Deployment Guide](./development/deployment.md)
- [API Testing Guide](./api/testing.md)
- [Configuration Management](./development/configuration.md)