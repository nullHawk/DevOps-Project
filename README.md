# To-Do API - Advanced DevOps CI/CD Project

[![CI/CD Pipeline](https://github.com/nullHawk/DevOps-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/nullHawk/DevOps-Project/actions/workflows/ci.yml)

A production-grade To-Do API built with FastAPI, PostgreSQL, and Docker, featuring advanced CI/CD pipelines on GitHub Actions with comprehensive security, quality, and testing gates.

## Project Overview

This project demonstrates a complete DevOps implementation including:

- **FastAPI Application**: RESTful To-Do API with user authentication, task management, and status tracking
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Containerization**: Multi-stage Docker builds with security best practices
- **CI/CD**: Advanced GitHub Actions pipeline with:
  - Linting and code style checks (Ruff, Black, isort)
  - Unit testing with coverage reporting
  - Security scanning (Bandit, CodeQL)
  - Dependency vulnerability checks (pip-audit, Safety)
  - Container image scanning (Trivy)
  - Runtime smoke tests
  - Automated publishing to DockerHub

## Tech Stack

- **Language**: Python 3.11
- **Web Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0+
- **Task Runner**: Poetry
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Security Tools**: Bandit, CodeQL, Trivy

## Project Structure

```
.
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application and routes
│   ├── config.py             # Configuration management
│   ├── database.py           # Database setup and session management
│   ├── models.py             # SQLAlchemy ORM models
│   ├── schemas.py            # Pydantic schemas for validation
│   ├── security.py           # Authentication and security utilities
│   └── crud.py               # Database CRUD operations
├── tests/
│   ├── conftest.py           # Pytest fixtures and configuration
│   ├── test_health.py        # Health endpoint tests
│   ├── test_auth.py          # Authentication tests
│   └── test_tasks.py         # Task endpoint tests
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD pipeline definition
├── Dockerfile                # Multi-stage production Docker image
├── docker-compose.yml        # Local development environment
├── pyproject.toml            # Poetry dependencies and configuration
├── .env.example              # Example environment file
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 15+ (or use docker-compose)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/nullHawk/DevOps-Project.git
   cd DevOps-Project
   ```

2. **Install dependencies with Poetry**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start PostgreSQL (optional: use docker-compose)**
   ```bash
   docker-compose up -d postgres
   ```
   Or use your own PostgreSQL instance and update `DATABASE_URL` in `.env`.

5. **Initialize the database**
   ```bash
   poetry run alembic upgrade head
   # Or let the app create tables on first run
   ```

6. **Run the development server**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Using Docker Compose

For a complete local environment with PostgreSQL:

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Health & Monitoring
- `GET /health` - Health check endpoint
- `GET /version` - API version information

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get access token

#### Tasks
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks for current user
- `GET /tasks?status=<status>` - Filter tasks by status (todo, in_progress, completed)
- `GET /tasks/{task_id}` - Get specific task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `GET /tasks/summary/stats` - Get task statistics

#### Users
- `GET /users/me` - Get current user information

### Authentication

All protected endpoints require Bearer token authentication:

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=securepassword123"

# Use token in requests
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Task Management Examples

```bash
# Create a task (replace TOKEN with actual token)
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "high",
    "due_date": "2024-01-20T18:00:00"
  }'

# Get all tasks
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/tasks?status=in_progress" \
  -H "Authorization: Bearer TOKEN"

# Update task status
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Get task summary
curl -X GET http://localhost:8000/tasks/summary/stats \
  -H "Authorization: Bearer TOKEN"
```

## Testing

### Run All Tests

```bash
# Run tests with coverage
poetry run pytest tests/ --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_tasks.py -v

# Run with specific markers
poetry run pytest tests/ -k "test_create_task" -v
```

### Generate Coverage Report

```bash
poetry run pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Structure

- `tests/conftest.py` - Pytest fixtures and test database setup
- `tests/test_health.py` - Health and version endpoint tests
- `tests/test_auth.py` - User authentication tests
- `tests/test_tasks.py` - Task CRUD operation tests

## Code Quality and Linting

### Run Linters

```bash
# Ruff - Fast Python linter
poetry run ruff check app/ tests/

# Black - Code formatter
poetry run black app/ tests/

# isort - Import sorter
poetry run isort app/ tests/
```

### Auto-fix Issues

```bash
# Fix with Black
poetry run black app/ tests/

# Fix imports with isort
poetry run isort app/ tests/

# Fix some Ruff issues
poetry run ruff check app/ tests/ --fix
```

## Security Analysis

### Local Security Scanning

```bash
# Bandit - Security issue detection
poetry run bandit -r app/

# pip-audit - Dependency vulnerability check
poetry run pip-audit

# Safety - Dependency vulnerability database
poetry run safety check
```

## Docker Build and Deployment

### Build Docker Image

```bash
# Build with default arguments
docker build -t todo-api:latest .

# Build with custom metadata
docker build \
  -t todo-api:v1.0.0 \
  --build-arg VERSION=1.0.0 \
  --build-arg GIT_COMMIT=$(git rev-parse HEAD) \
  --build-arg GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD) \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  .
```

### Run Docker Container

```bash
docker run \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/todo_db" \
  -e SECRET_KEY="your-secret-key" \
  todo-api:latest
```

### Multi-stage Build Benefits

The Dockerfile uses a multi-stage build to:
- **Reduce image size** by excluding build dependencies
- **Improve security** with minimal attack surface
- **Enable caching** of dependencies for faster rebuilds

## CI/CD Pipeline

### Pipeline Overview

The GitHub Actions CI/CD pipeline (``.github/workflows/ci.yml`) includes:

#### 1. **lint-test Job**
   - Checks out code
   - Sets up Python 3.11
   - Runs Ruff linter
   - Runs Black formatter check
   - Runs isort import check
   - Executes unit tests with coverage
   - Uploads coverage artifacts

#### 2. **sast-sca Job** (Security Analysis)
   - Runs Bandit for security issues
   - Executes CodeQL analysis
   - Runs pip-audit for dependency vulnerabilities
   - Uploads SARIF reports to GitHub Security

#### 3. **docker-build-scan Job**
   - Builds Docker image with metadata
   - Scans image with Trivy for vulnerabilities
   - Uploads scan results
   - Caches layers for faster rebuilds

#### 4. **runtime-smoke-test Job**
   - Starts container with PostgreSQL
   - Tests `/health` endpoint
   - Tests `/version` endpoint
   - Verifies API readiness

#### 5. **publish Job**
   - Authenticates to DockerHub
   - Pushes image with semantic versioning tags
   - Creates GitHub releases

### Triggering the Pipeline

```bash
# Automatic on push to main/master
git push origin main

# Manual trigger via GitHub UI
# Settings → Actions → CI/CD Pipeline → Run workflow

# Manual trigger via CLI
gh workflow run ci.yml
```

### Pipeline Configuration for Secrets

Configure the following secrets in GitHub repository settings:

1. `DOCKERHUB_USERNAME` - Your Docker Hub username
2. `DOCKERHUB_TOKEN` - Docker Hub Personal Access Token

```bash
# Via GitHub CLI
gh secret set DOCKERHUB_USERNAME -b "your-username"
gh secret set DOCKERHUB_TOKEN -b "your-token"
```

### Docker Image Tagging Strategy

The pipeline automatically tags images with:
- `latest` - Latest build on main branch
- `main` - Branch name
- `sha-<commit>` - Git commit SHA
- `v1.0.0` - Semantic version tags (when available)

### Security Findings

Security findings are automatically uploaded to GitHub Security tab:
- **SAST**: CodeQL and Bandit findings
- **SCA**: Dependency vulnerabilities
- **Container Scan**: Image vulnerabilities (Trivy)

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Verify connection string
echo $DATABASE_URL

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

### API Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Use different port
poetry run uvicorn app.main:app --port 8001
```

### Test Failures

```bash
# Run tests with verbose output
poetry run pytest tests/ -vv

# Run specific test with debugging
poetry run pytest tests/test_tasks.py::test_create_task -vv

# Drop and recreate test database
rm test.db*
poetry run pytest tests/
```

### Docker Build Failures

```bash
# Build with verbose output
docker build --progress=plain -t todo-api:latest .

# Check Dockerfile syntax
docker build --check -t todo-api:latest .

# Clear Docker cache for clean build
docker build --no-cache -t todo-api:latest .
```

### CI/CD Workflow Issues

1. **Check workflow logs**: GitHub Actions → Workflows → CI/CD Pipeline → Latest run
2. **View job output**: Click on failing job for detailed logs
3. **Debug locally**: Run equivalent commands in `lint-test` and `docker-build-scan` jobs

## Performance Optimization

### Database Query Optimization

- Indexes on `user_id` and `status` for fast filtering
- Connection pooling via SQLAlchemy
- Pre-ping connections for reliability

### API Response Optimization

- Database session caching per request
- Minimal data transfer with selective field queries
- Health checks without database hits

### Docker Image Optimization

- Multi-stage build reduces final image size
- Alpine base image (slim variant) for smaller footprint
- Dependency caching in layer structure

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://user:password@localhost:5432/todo_db | PostgreSQL connection string |
| `SECRET_KEY` | your-secret-key-change-in-production | JWT signing key (change in production!) |
| `DEBUG` | False | Enable debug mode (never in production) |
| `APP_VERSION` | 1.0.0 | Application version |
| `ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |

## Security Considerations

### Authentication

- Passwords are hashed using bcrypt
- JWT tokens for API authentication
- Bearer token scheme for protected endpoints
- Token expiration for security

### Database Security

- Connection pooling with health checks
- Environment variable management for credentials
- No hardcoded secrets in code

### Container Security

- Non-root user execution (uid 1000)
- Read-only root filesystem support
- Health checks for availability
- Minimal attack surface with slim base image

### Secrets Management

- Use GitHub Secrets for DockerHub credentials
- Never commit `.env` with real values
- Rotate secrets regularly
- Use least privilege principle

## Development Workflow

### Feature Development

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test locally
poetry run pytest tests/ --cov=app

# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create pull request on GitHub
# CI pipeline runs automatically on PR
```

### Code Quality Checklist

Before committing:

```bash
# Format code
poetry run black app/ tests/
poetry run isort app/ tests/

# Run linters
poetry run ruff check app/ tests/ --fix

# Run tests
poetry run pytest tests/ --cov=app

# Security check
poetry run bandit -r app/
poetry run pip-audit
```

## Production Deployment

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: todo-api
  template:
    metadata:
      labels:
        app: todo-api
    spec:
      containers:
      - name: api
        image: docker.io/username/todo-api:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and ensure all tests pass
4. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues and questions:

1. Check existing GitHub Issues
2. Review CI/CD logs for build failures
3. Contact the DevOps team

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

---

**Last Updated**: January 2026
**Version**: 1.0.0
