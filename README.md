# MGraph AI Service Html Graph

[![Current Release](https://img.shields.io/badge/release-v0.6.0-blue)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/releases)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688)](https://fastapi.tiangolo.com/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange)](https://aws.amazon.com/lambda/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](LICENSE)
[![CI Pipeline - DEV](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/actions/workflows/ci-pipeline__dev.yml/badge.svg)](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/actions)

A production-ready FastAPI microservice template for building MGraph-AI services. This template provides a complete scaffold with CI/CD pipeline, AWS Lambda deployment, and type-safe architecture.

## 🎯 Purpose

This repository serves as the base template for creating new MGraph-AI services. It includes:
- ✅ Complete FastAPI application structure  
- ✅ Multi-stage CI/CD pipeline (dev, qa, prod)
- ✅ AWS Lambda deployment configuration
- ✅ Type-safe architecture using OSBot-Utils
- ✅ Comprehensive test coverage
- ✅ API key authentication
- ✅ Health check and monitoring endpoints

**Note**: This is a template repository. To create your own service, see [Creating Services from Template](docs/dev/non-functional-requirements/version-1_0_0/README.md).

## 📚 Creating a New Service

To create a new service from this template, see [Creating Services from MGraph-AI__Service__Html__Graph](docs/dev/non-functional-requirements/version-1_0_0/README.md).

## 🚀 Features

- **Type-Safe Architecture**: Built on OSBot-Utils type safety framework
- **Multi-Stage Deployment**: Automated CI/CD pipeline for dev, QA, and production
- **AWS Lambda Ready**: Optimized for serverless deployment
- **API Key Authentication**: Secure access control

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph.git
cd MGraph-AI__Service__Html__Graph

# Install dependencies
pip install -r requirements-test.txt
pip install -e .

# Set environment variables
export FAST_API__AUTH__API_KEY__NAME="x-api-key"
export FAST_API__AUTH__API_KEY__VALUE="your-secret-key"

# Run locally
./scripts/run-locally.sh
# or
uvicorn mgraph_ai_service_html__graph.fast_api.lambda_handler:app --reload --host 0.0.0.0 --port 10011
```

### Basic Usage

```python
import requests

# Set up authentication
headers = {"x-api-key": "your-secret-key"}
base_url = "http://localhost:10011"

# Check service health
response = requests.get(f"{base_url}/health", headers=headers)
print(response.json())

# Get service info
response = requests.get(f"{base_url}/info/version", headers=headers)
print(response.json())
```

## 📦 Installation

### Prerequisites

- Python 3.12+
- AWS CLI (for deployment)
- Docker (for LocalStack testing)

### Using Poetry

```bash
# Install poetry if not already installed
pip install poetry

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-test.txt
pip install -e .
```

## 📖 API Documentation

### Interactive API Documentation

Once the service is running, access the interactive API documentation at:
- Swagger UI: http://localhost:10011/docs
- ReDoc: http://localhost:10011/redoc

### Endpoints Overview

#### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/health/detailed` | GET | Detailed health status |

#### Information Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/info/version` | GET | Get service version |
| `/info/status` | GET | Get service status |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FAST_API__AUTH__API_KEY__NAME` | Header name for API key | Yes | - |
| `FAST_API__AUTH__API_KEY__VALUE` | API key value | Yes | - |
| `AWS_REGION` | AWS region (triggers Lambda mode) | No | - |
| `DEBUG` | Enable debug logging | No | false |

### Configuration File

Create a `.env` file for local development:

```env
FAST_API__AUTH__API_KEY__NAME=x-api-key
FAST_API__AUTH__API_KEY__VALUE=development-key-12345
```

## 🛠️ Development

### Project Structure

```
mgraph_ai_service_html__graph/
├── fast_api/
│   ├── lambda_handler.py      # AWS Lambda entry point
│   ├── Service__Fast_API.py   # FastAPI application setup
│   └── routes/               # API endpoint definitions
├── service/
│   └── info/               # Service information
├── utils/
│   ├── deploy/             # Deployment utilities
│   └── Version.py          # Version management
└── config.py               # Service configuration
```

### Adding New Endpoints

1. Create a new route class in `fast_api/routes/`:

```python
from osbot_fast_api.api.Fast_API_Routes import Fast_API_Routes

class Routes__MyFeature(Fast_API_Routes):
    tag = 'my-feature'
    
    def my_endpoint(self, param: str = "default"):
        return {"result": param}
    
    def setup_routes(self):
        self.add_route_get(self.my_endpoint)
```

2. Register in `Service__Fast_API`:

```python
def setup_routes(self):
    # ... existing routes
    self.add_routes(Routes__MyFeature)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mgraph_ai_service_html__graph

# Run specific test file
pytest tests/unit/fast_api/test_Service__Fast_API__client.py

# Run integration tests (requires LocalStack)
pytest tests/integration/
```

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── fast_api/           # API tests
│   └── service/            # Service tests
└── deploy_aws/             # Deployment tests
```

## 🚀 Deployment

### AWS Lambda Deployment

The service includes automated deployment scripts for multiple environments:

```bash
# Deploy to development
pytest tests/deploy_aws/test_Deploy__Service__to__dev.py

# Deploy to QA
pytest tests/deploy_aws/test_Deploy__Service__to__qa.py

# Deploy to production (manual trigger)
# Use GitHub Actions workflow
```

### CI/CD Pipeline

The project uses GitHub Actions for continuous deployment:

1. **Development Branch** (`dev`)
   - Runs tests with LocalStack
   - Deploys to dev environment
   - Increments minor version

2. **Main Branch** (`main`)
   - Runs comprehensive test suite
   - Deploys to QA environment
   - Increments major version

3. **Production** (manual)
   - Requires manual workflow trigger
   - Deploys to production environment

## 🔒 Security

### Authentication

API key authentication is required for all endpoints:

```python
headers = {"x-api-key": "your-secret-key"}
```

### Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate API keys** - Regular key rotation
3. **Use HTTPS** - Always encrypt in transit
4. **Monitor access** - Log and audit API usage

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Update documentation
- Follow existing code style
- Add type annotations
- Consider security implications

## 🔗 Related Projects

- [OSBot-Utils](https://github.com/owasp-sbot/OSBot-Utils) - Core utilities library
- [OSBot-AWS](https://github.com/owasp-sbot/OSBot-AWS) - AWS integration layer
- [OSBot-Fast-API](https://github.com/owasp-sbot/OSBot-Fast-API) - FastAPI utilities

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Deployed on [AWS Lambda](https://aws.amazon.com/lambda/)

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/the-cyber-boardroom/MGraph-AI__Service__Html__Graph/discussions)

---

Created and maintained by [The Cyber Boardroom](https://github.com/the-cyber-boardroom) team