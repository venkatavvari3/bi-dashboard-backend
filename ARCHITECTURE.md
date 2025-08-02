# BI Dashboard Backend - Modular Architecture

This project has been refactored to follow API development industry best practices with a clean, modular architecture.

## 📁 Project Structure

```
bi-dashboard-backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── scheduled_report_sender.py  # External script (unchanged)
└── app/                   # Main application package
    ├── __init__.py
    ├── core/              # Core configuration and settings
    │   ├── __init__.py
    │   └── config.py      # Application settings and environment variables
    ├── db/                # Database related modules
    │   ├── __init__.py
    │   └── database.py    # Database connection and operations
    ├── models/            # Pydantic models and schemas
    │   ├── __init__.py
    │   └── schemas.py     # Request/Response models
    ├── services/          # Business logic services
    │   ├── __init__.py
    │   ├── auth_service.py       # Authentication and authorization
    │   ├── email_service.py      # Email functionality
    │   ├── data_service.py       # Data retrieval and processing
    │   └── subscription_service.py # Report subscription management
    └── api/               # API route handlers
        ├── __init__.py
        ├── auth.py        # Authentication endpoints
        ├── data.py        # Data endpoints
        ├── email.py       # Email endpoints
        └── subscriptions.py # Subscription endpoints
```

## 🚀 Key Improvements

### 1. **Separation of Concerns**
- **API Routes** (`app/api/`): Handle HTTP requests/responses
- **Services** (`app/services/`): Contain business logic
- **Models** (`app/models/`): Define data structures
- **Database** (`app/db/`): Handle data persistence
- **Configuration** (`app/core/`): Manage settings

### 2. **Clean Architecture Principles**
- **Dependency Injection**: Used throughout for loose coupling
- **Single Responsibility**: Each module has a specific purpose
- **Interface Segregation**: Clean service interfaces
- **Open/Closed Principle**: Easy to extend without modification

### 3. **Professional API Standards**
- **Router-based organization**: Logical grouping of endpoints
- **Consistent error handling**: Standardized HTTP responses
- **Type safety**: Full Pydantic model validation
- **Documentation ready**: Automatic OpenAPI/Swagger docs

### 4. **Maintainability Features**
- **Modular imports**: Easy to test individual components
- **Configuration management**: Centralized environment variables
- **Consistent naming**: Following Python conventions
- **Clear dependencies**: Explicit service dependencies

## 🔧 Configuration

All configuration is managed through environment variables in `app/core/config.py`:

- `SECRET`: JWT secret key
- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `EMAIL_ADDRESS`: SMTP email address
- `EMAIL_PASSWORD`: SMTP email password

## 📚 API Endpoints

### Authentication
- `POST /api/login` - User login (username/password or Google OAuth)

### Data
- `GET /api/data` - Get sales data with persona filtering
- `GET /api/products` - Get all products
- `GET /api/stores` - Get all stores
- `GET /api/ppdata` - Get PP data with persona filtering
- `GET /api/ppproducts` - Get PP products
- `GET /api/ppstores` - Get PP stores

### Email
- `POST /api/email_me` - Send email with optional image attachment

### Subscriptions
- `POST /api/schedule_report` - Schedule report subscription

## 🧪 Testing

```bash
# Test application import
python -c "from main import app; print('✅ Application loaded successfully')"

# Run the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔄 Migration Benefits

1. **Easier Testing**: Each service can be tested independently
2. **Better Debugging**: Clear separation makes issues easier to isolate
3. **Team Collaboration**: Different developers can work on different modules
4. **Scalability**: Easy to add new features without touching existing code
5. **Code Reuse**: Services can be reused across different endpoints
6. **Documentation**: Self-documenting code structure

## 🛠️ Development Workflow

1. **Adding New Features**: Create new services in `app/services/`
2. **New API Endpoints**: Add routes in appropriate `app/api/` modules
3. **Data Models**: Define in `app/models/schemas.py`
4. **Configuration Changes**: Update `app/core/config.py`
5. **Database Changes**: Extend `app/db/database.py`

This modular architecture follows industry best practices and makes the codebase more maintainable, testable, and scalable.
