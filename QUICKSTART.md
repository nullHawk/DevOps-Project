# Quick Start Guide

## Installation & Setup

### 1. Prerequisites

Ensure you have installed:
- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (optional, for containerized setup)
- Git

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/nullHawk/DevOps-Project.git
cd DevOps-Project

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env
```

### 3. Quick Start Options

#### Option A: Local Development (Fastest)

```bash
# Start with existing PostgreSQL instance
# Update DATABASE_URL in .env

# Run the application
poetry run uvicorn app.main:app --reload
```

Access API at: http://localhost:8000

#### Option B: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps
```

Access API at: http://localhost:8000

#### Option C: Just Run Tests

```bash
poetry run pytest tests/ -v
```

## Essential Commands

### Development

```bash
# Run app with auto-reload
poetry run uvicorn app.main:app --reload

# Run tests
poetry run pytest tests/ -v

# Generate coverage report
poetry run pytest tests/ --cov=app --cov-report=html

# Format code
poetry run black app/ tests/
poetry run isort app/ tests/

# Check code quality
poetry run ruff check app/ tests/
```

### Docker

```bash
# Build image
docker build -t todo-api:latest .

# Start with docker-compose
docker-compose up -d
docker-compose down

# View logs
docker-compose logs -f api
```

### Security

```bash
# Security scan
poetry run bandit -r app/

# Dependency check
poetry run pip-audit

# Local smoke test
./scripts/docker-test.sh
```

## First API Call

1. **Register a user**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "password123"
     }'
   ```

2. **Login to get token**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123"
   ```

3. **Create a task**
   ```bash
   TOKEN="your-token-here"
   curl -X POST http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Learn DevOps",
       "priority": "high"
     }'
   ```

4. **View tasks**
   ```bash
   curl -X GET http://localhost:8000/tasks \
     -H "Authorization: Bearer $TOKEN"
   ```

## Useful Links

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Full README**: [README.md](README.md)
- **CI/CD Details**: [CICD_DOCUMENTATION.md](CICD_DOCUMENTATION.md)

## Common Issues

### Database Connection Error
```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Or check DATABASE_URL in .env
```

### Port Already in Use
```bash
# Use different port
poetry run uvicorn app.main:app --port 8001
```

### Dependency Issues
```bash
# Reinstall dependencies
poetry install --no-cache
```

## Next Steps

1. ✅ Run the application locally
2. 📝 Explore API via Swagger UI (http://localhost:8000/docs)
3. 🧪 Run tests: `poetry run pytest tests/ -v`
4. 🔍 Check code quality: `poetry run ruff check app/`
5. 🚀 Push to GitHub to trigger CI/CD pipeline

## File Structure Overview

```
project/
├── app/                    # FastAPI application
├── tests/                  # Test suite
├── .github/workflows/      # CI/CD pipelines
├── scripts/                # Helper scripts
├── Dockerfile              # Container image
├── docker-compose.yml      # Local environment
├── pyproject.toml          # Dependencies
├── README.md               # Full documentation
└── CICD_DOCUMENTATION.md   # CI/CD details
```

For detailed documentation, see [README.md](README.md)
