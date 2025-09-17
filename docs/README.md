# PHA Backend Documentation

Welcome to the PHA (Personal Health Assistant) Backend documentation.

## 📚 Documentation Structure

### API Documentation
- [API Testing Guide](api/testing.md) - Comprehensive API endpoint testing
- [Endpoint Reference](api/endpoints.md) - Detailed endpoint documentation

### Development
- [Migration Guide](development/migration.md) - Project structure migration details
- [Flow Summary](development/flow_summary.md) - System flow and architecture
- [Setup Guide](development/setup.md) - Development environment setup
- [MongoDB Connection Testing](development/mongodb-connection-testing.md) - Database connection testing guide

### Architecture
- [System Architecture](architecture.md) - Overall system design
- [Improved Architecture](architecture_improved.md) - Enhanced architecture proposals

### Deployment
- [Production Deployment](deployment/production.md) - Production setup guide
- [Docker Setup](deployment/docker.md) - Containerized deployment

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install Dependencies**
   ```bash
   uv pip install -e .
   ```

3. **Run the Application**
   ```bash
   python scripts/start.py
   ```

4. **Access Documentation**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🏗️ Project Structure

```
PHA/
├── src/pha/           # Main application package
├── tests/             # Test suite
├── docs/              # Documentation (you are here)
├── scripts/           # Utility scripts
└── config/            # Configuration files
```

## 📖 Key Features

- **Multi-Database Support**: PostgreSQL, MySQL, MongoDB, Oracle, SQL Server
- **AI-Powered Queries**: AWS Bedrock integration for healthcare query generation
- **Schema Extraction**: Unified schema analysis across database types
- **Healthcare Focus**: Specialized endpoints for healthcare data processing
- **Production Ready**: Comprehensive testing and deployment configurations

## 🔗 External Links

- [GitHub Repository](https://github.com/sowmiya-goml/PHA)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Project Board](https://github.com/sowmiya-goml/PHA/projects)

For questions or support, please check the relevant documentation sections above or create an issue in the GitHub repository.