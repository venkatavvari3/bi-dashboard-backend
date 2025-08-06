# BI Dashboard Backend API

A modern, modular FastAPI backend for business intelligence dashboards with persona-based data filtering, email notifications, and report scheduling capabilities.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-supported-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

- **🔐 Multi-Authentication Support**: Username/password and Google OAuth integration
- **👤 Persona-Based Filtering**: Role-based data access control
- **📊 Data Analytics**: Sales data, products, and store information APIs
- **📧 Email Integration**: Send reports with image attachments
- **⏰ Report Scheduling**: Automated report subscriptions
- **🏗️ Modular Architecture**: Clean, maintainable, and scalable codebase
- **📖 Auto Documentation**: Interactive Swagger/OpenAPI docs
- **🔒 JWT Security**: Secure token-based authentication

## 🏗️ Architecture

This project follows industry best practices with a clean, modular architecture:

```
bi-dashboard-backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── run_dev.py             # Development server script
├── test_architecture.py   # Architecture verification script
└── app/                   # Main application package
    ├── core/              # Core configuration
    │   └── config.py      # Settings and environment variables
    ├── db/                # Database layer
    │   └── database.py    # Connection and query management
    ├── models/            # Data models
    │   └── schemas.py     # Pydantic request/response models
    ├── services/          # Business logic
    │   ├── auth_service.py       # Authentication & authorization
    │   ├── email_service.py      # Email functionality
    │   ├── data_service.py       # Data processing & retrieval
    │   └── subscription_service.py # Report subscriptions
    └── api/               # API endpoints
        ├── auth.py        # Authentication routes
        ├── data.py        # Data retrieval routes
        ├── email.py       # Email routes
        └── subscriptions.py # Subscription routes
```

## 🛠️ Installation

### Option 1: Docker (Recommended)

Docker provides the easiest way to get started with isolated, reproducible environments.

#### Prerequisites
- Docker
- Docker Compose

#### Quick Start with Docker

```bash
# Clone the repository
git clone <repository-url>
cd bi-dashboard-backend

# Start development environment
docker-compose --profile dev up --build

# Or use the helper script (Linux/Mac)
./docker.sh dev

# Or use the PowerShell script (Windows)
.\docker.ps1 dev
```

The application will be available at:
- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **MailHog (Email Testing)**: http://localhost:8025

#### Docker Helper Scripts

Use the provided scripts for common operations:

**Linux/Mac:**
```bash
./docker.sh dev          # Start development
./docker.sh test         # Run tests
./docker.sh prod         # Start production
./docker.sh help         # Show all commands
```

**Windows:**
```powershell
.\docker.ps1 dev         # Start development
.\docker.ps1 test        # Run tests
.\docker.ps1 prod        # Start production
.\docker.ps1 help        # Show all commands
```

See [DOCKER.md](DOCKER.md) for comprehensive Docker documentation.

### Option 2: Local Python Installation

#### Prerequisites

- Python 3.8+
- PostgreSQL database
- Gmail account (for email features)

#### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bi-dashboard-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   
   Create a `.env` file or set the following environment variables:
   
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   
   # Security
   SECRET=your_super_secret_jwt_key_here
   
   # Google OAuth
   GOOGLE_CLIENT_ID=your_google_client_id
   
   # Email Configuration
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

4. **Database Setup**
   
   Ensure your PostgreSQL database has the required tables:
   - `persona_users` - User persona mappings
   - `fact_sales`, `dim_date`, `dim_product`, `dim_customer`, `dim_store` - Sales data
   - `orders`, `order_items`, `products`, `stores`, `customers` - PP data
   - `subscriptions` - Report subscriptions (auto-created)

## 🚀 Quick Start

### Development Server

```bash
# Using the development script
python run_dev.py

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify Installation

```bash
# Test the modular architecture
python test_architecture.py

# Test basic import
python -c "from main import app; print('✅ Application ready!')"
```

### Access the API

- **API Server**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 📡 API Endpoints

### Authentication
```
POST /api/login           # User login (username/password or Google OAuth)
```

### Data Retrieval
```
GET  /api/data           # Sales data with persona filtering
GET  /api/products       # Product catalog
GET  /api/stores         # Store information
GET  /api/ppdata         # PP sales data with persona filtering
GET  /api/ppproducts     # PP product catalog
GET  /api/ppstores       # PP store information
```

### Email & Reports
```
POST /api/email_me       # Send email with optional image attachment
POST /api/schedule_report # Schedule automated reports
```

## 🔐 Authentication

### Username/Password Login
```json
POST /api/login
{
  "username": "your_username",
  "password": "password"
}
```

### Google OAuth Login
```json
POST /api/login
{
  "credential": "google_oauth_token"
}
```

### Using JWT Token
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/data
```

## 👤 Persona-Based Access

The system supports persona-based data filtering:

- **Srini**: Access to New York sales data / California PP data
- **Venkat**: Access to San Francisco sales data / Nevada PP data
- **Default**: Access to all data

## 📧 Email Features

Send reports with image attachments:

```json
POST /api/email_me
{
  "to": "recipient@example.com",
  "message": "Your report is attached",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

## ⏰ Report Scheduling

Schedule automated reports:

```json
POST /api/schedule_report
{
  "repeatFrequency": "daily",
  "scheduledTime": "09:00",
  "reportFormat": "PDF",
  "email": "user@example.com"
}
```

## 🧪 Testing

This project includes a comprehensive test suite with unit and integration tests.

### Docker Testing (Recommended)

```bash
# Run all tests in Docker
./docker.sh test

# Run tests with coverage
./docker.sh test-coverage

# Windows
.\docker.ps1 test
.\docker.ps1 test-coverage
```

### Local Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx faker

# Run test suite
python run_tests.py

# Or directly with pytest
pytest tests/ -v --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py              # Test fixtures and configuration
├── utils.py                 # Test utilities
├── unit/                    # Unit tests
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_auth_service.py
│   ├── test_email_service.py
│   ├── test_data_service.py
│   └── test_subscription_service.py
└── integration/             # Integration tests
    ├── test_auth_api.py
    ├── test_data_api.py
    └── test_email_api.py
```

### Manual Testing

```bash
# Test individual components
python -c "from app.services.auth_service import AuthService; print('Auth service OK')"
python -c "from app.services.data_service import DataService; print('Data service OK')"
python -c "from app.services.email_service import EmailService; print('Email service OK')"

# Test health endpoint
curl http://localhost:8000/

# Test authentication (replace with actual credentials)
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"password"}'
```

## 🔧 Configuration

All configuration is managed through the `app/core/config.py` file using environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET` | JWT secret key | ✅ |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | ✅ |
| `EMAIL_ADDRESS` | Gmail address for sending emails | ✅ |
| `EMAIL_PASSWORD` | Gmail app password | ✅ |

## 🚀 Deployment

### Docker Production Deployment (Recommended)

#### Simple Production Setup

```bash
# Build and run production container
docker-compose --profile prod up --build -d

# Or use helper script
./docker.sh prod          # Linux/Mac
.\docker.ps1 prod         # Windows
```

#### Production with Database

```bash
# Start with PostgreSQL and Redis
docker-compose --profile prod --profile prod-db up --build -d

# Or use helper script
./docker.sh prod-db       # Linux/Mac
.\docker.ps1 prod-db      # Windows
```

#### Environment Configuration

Create a `.env` file for production:

```env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/bidashboard

# Security
SECRET_KEY=your-super-secret-key-here

# Email Configuration
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# PostgreSQL (for Docker Compose)
POSTGRES_DB=bidashboard
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-postgres-password
```

#### Production Features

- **Multi-worker setup**: 4 worker processes for high performance
- **Health checks**: Automatic container health monitoring
- **Non-root user**: Enhanced security
- **Minimal image**: Production-optimized container size
- **Graceful shutdown**: Proper signal handling

### Manual Docker Deployment

```bash
# Build production image
docker build --target production -t bi-dashboard:prod .

# Run production container
docker run -d \
  --name bi-dashboard \
  -p 8000:8000 \
  -e DATABASE_URL="your-database-url" \
  -e SECRET_KEY="your-secret-key" \
  bi-dashboard:prod
```

### Traditional Deployment

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Cloud Platform Deployment

The Docker setup is compatible with major cloud platforms:

- **AWS ECS/Fargate**: Use the production image
- **Google Cloud Run**: Direct deployment from container
- **Azure Container Instances**: Single-command deployment
- **DigitalOcean App Platform**: Dockerfile-based deployment
- **Heroku**: Container registry deployment

### CI/CD Integration

The project includes GitHub Actions for automated testing and deployment:

```yaml
# .github/workflows/ci.yml included
# - Runs on Python 3.9, 3.10, 3.11
# - Comprehensive test suite
# - Coverage reporting
# - Architecture validation
```

See [DOCKER.md](DOCKER.md) for detailed Docker documentation and deployment strategies.

## 🤝 Development

### Adding New Features

1. **New API Endpoint**: Add to appropriate router in `app/api/`
2. **Business Logic**: Create service in `app/services/`
3. **Data Models**: Define in `app/models/schemas.py`
4. **Database Operations**: Extend `app/db/database.py`

### Code Style
- Follow PEP 8 conventions
- Use type hints
- Document functions with docstrings
- Keep functions focused and small

## 📝 Changelog

### v2.0.0 (Current)
- ✅ Complete modular architecture refactor
- ✅ Separation of concerns implementation
- ✅ Industry best practices adoption
- ✅ Improved error handling
- ✅ Type safety with Pydantic models
- ✅ Comprehensive documentation

### v1.0.0 (Legacy)
- ✅ Monolithic FastAPI application
- ✅ Basic authentication and data endpoints
- ✅ Email functionality
- ✅ Report scheduling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the [API Documentation](http://localhost:8000/docs)
- Review the [Architecture Guide](ARCHITECTURE.md)

---

**Made with ❤️ using FastAPI and modern Python practices**