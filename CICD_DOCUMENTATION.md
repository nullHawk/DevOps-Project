# CI/CD Documentation

## Overview

This document provides detailed information about the CI/CD pipeline, its stages, and how to work with it effectively.

## Pipeline Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Code Push to GitHub                         │
└────────────┬────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  lint-test Job (Parallel)                       │
│  ├─ Ruff Linting                                                │
│  ├─ Black Format Check                                          │
│  ├─ isort Import Check                                          │
│  └─ Pytest with Coverage                                        │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─ PASS ─────────────────────────────────────┐
             │                                             │
             └─ FAIL ─────────────────────────────────────┤
                                                           │
┌──────────────────────────────────────────────────────────┴──────┐
│                  sast-sca Job (Parallel)                        │
│  ├─ Bandit Security Scan                                       │
│  ├─ CodeQL Analysis                                            │
│  ├─ pip-audit Dependency Check                                 │
│  └─ Safety Database Check                                      │
└────────────┬──────────────────────────────────────────────────┘
             │
             ├─ PASS/WARN ──────────────────────────────┐
             │                                           │
             └─ CRITICAL FAIL ──────────────────────────┤
                                                         │
┌──────────────────────────────────────────────────────────┴──────┐
│               docker-build-scan Job (Requires: main)            │
│  ├─ Build Docker Image with Metadata                           │
│  ├─ Tag Image (semantic versions)                              │
│  └─ Trivy Vulnerability Scan                                   │
└────────────┬──────────────────────────────────────────────────┘
             │
             ├─ PASS ─────────────────────────────────┐
             │                                         │
             └─ CRITICAL VULN ──────────────────────┤
                                                     │
┌──────────────────────────────────────────────────────┴──────────┐
│              runtime-smoke-test Job                             │
│  ├─ Start PostgreSQL Service                                   │
│  ├─ Build and Run Container                                   │
│  ├─ Test /health Endpoint                                     │
│  ├─ Test /version Endpoint                                    │
│  └─ Verify API Readiness                                      │
└────────────┬──────────────────────────────────────────────────┘
             │
             ├─ PASS ───────────────────────────────┐
             │                                       │
             └─ FAIL ────────────────────────────────┤
                                                     │
┌──────────────────────────────────────────────────────┴──────────┐
│         publish Job (Only: main branch, all checks pass)        │
│  ├─ Login to DockerHub                                         │
│  ├─ Push Image with Tags                                       │
│  └─ Create Deployment Artifacts                                │
└──────────────────────────────────────────────────────────────────┘
```

## Job Details

### 1. lint-test Job

**Purpose**: Validate code quality, style, and functionality

**Triggers**: All push and PR events

**Steps**:
- Checkout code
- Setup Python 3.11 with dependency cache
- Run Ruff (fast Python linter)
  - Checks for errors, style violations
  - Exit code 1 on violations (blocking)
- Run Black format check
  - Ensures consistent code style
  - Exit code 1 on format violations (blocking)
- Run isort import sorting check
  - Validates import organization
  - Exit code 1 on violations (blocking)
- Run Pytest with coverage
  - Executes all tests in `tests/` directory
  - Generates coverage report
  - Fails if any test fails
- Upload coverage artifacts
  - HTML coverage reports
  - Coverage XML for external tools

**Artifacts**:
- `test-results/htmlcov/` - HTML coverage report
- `test-results/.coverage` - Coverage data file

**Duration**: ~2-3 minutes

**Failure Handling**: Blocks pipeline if failed

### 2. sast-sca Job

**Purpose**: Identify security vulnerabilities and supply chain risks

**Triggers**: All push and PR events (no branch filter)

**Steps**:
- Checkout code
- Setup Python 3.11
- Run Bandit (SAST - Static Application Security Testing)
  - Scans Python code for security issues
  - Generates JSON report
  - Continues on error (non-blocking warnings)
- Upload Bandit report
  - Stored as artifact for review
- Run pip-audit
  - Checks for vulnerable packages
  - Non-blocking (continues on error)
- Initialize CodeQL
  - GitHub's code analysis engine
  - Configures for Python
- Perform CodeQL Analysis
  - Analyzes code for security patterns
  - Results uploaded automatically to GitHub Security tab

**Outputs**:
- SARIF reports uploaded to GitHub Security tab
- Artifacts for offline review

**Duration**: ~3-5 minutes (CodeQL is slower)

**Failure Handling**: Non-blocking for warnings, but blocks on critical findings

### 3. docker-build-scan Job

**Purpose**: Build production Docker image and scan for vulnerabilities

**Triggers**: Push events only (not PR)

**Requires**: Successful completion of lint-test and sast-sca

**Steps**:
- Checkout code
- Setup Docker Buildx
  - Multi-platform build support
  - Advanced caching
- Generate image metadata
  - Branch tags
  - Semantic version tags
  - Commit SHA tags
  - Latest tag (for default branch)
- Build Docker image with metadata
  - Multi-stage build for size optimization
  - Metadata labels for traceability
  - Layer caching for speed
  - Build arguments:
    - `VERSION`: Git branch/tag
    - `GIT_COMMIT`: Full commit SHA
    - `GIT_BRANCH`: Branch name
    - `BUILD_DATE`: ISO 8601 timestamp
- Run Trivy container scan
  - Scans for OS and application vulnerabilities
  - Severity filter: CRITICAL, HIGH
  - SARIF format for GitHub integration
  - Exit code 0 (non-blocking, but reported)
- Upload Trivy results
  - SARIF file uploaded to GitHub Security tab
  - Artifact for manual review

**Outputs**:
- Docker image (local to runner, not pushed)
- Trivy scan results
- Image metadata and tags

**Duration**: ~2-4 minutes (first run slower due to caching)

**Failure Handling**: Non-blocking for vulnerabilities (reported but doesn't fail)

### 4. runtime-smoke-test Job

**Purpose**: Verify container runs correctly and responds to health checks

**Triggers**: Push events only

**Requires**: Successful docker-build-scan

**Services**:
- PostgreSQL 15 Alpine
  - Pre-configured with test database
  - Health checks enabled
  - Port 5432 exposed

**Steps**:
- Checkout code
- Setup Docker Buildx
- Build Docker image for testing
  - Same Dockerfile as docker-build-scan
  - Tags: `todo-api:test`
- Start container with environment
  - Connected to PostgreSQL service
  - Network: host (direct networking)
  - Environment variables set
  - 5-second startup wait
- Test health endpoint
  - Polls `/health` endpoint
  - 30 retry attempts with 1-second interval
  - Expects 200 status code
  - Fail-fast on non-200 response
- Test version endpoint
  - Calls `/version` endpoint
  - Expects JSON response with version info
- Collect container logs (on failure)
  - Useful for debugging
  - Helps identify runtime issues
- Stop container

**Duration**: ~1-2 minutes

**Failure Handling**: Blocks pipeline if health checks fail

### 5. publish Job

**Purpose**: Push validated image to DockerHub registry

**Triggers**: Push to main/master branch only

**Requires**: All previous jobs successful

**Prerequisites**: 
- `DOCKERHUB_USERNAME` secret configured
- `DOCKERHUB_TOKEN` secret configured

**Steps**:
- Checkout code
- Setup Docker Buildx
- Login to Docker Hub
  - Uses secrets for authentication
  - No credentials in logs
- Generate image metadata (same as docker-build-scan)
- Build and push Docker image
  - Push directly to registry
  - Multiple tags applied:
    - Branch name (e.g., `main`)
    - Semantic version (e.g., `v1.0.0`)
    - Commit SHA (e.g., `sha-abc123def456`)
    - Latest (if default branch)
  - Registry cache updated
- Create deployment artifact
  - Image information file
  - Includes image name, tags, commit, branch
- Upload deployment artifact
  - Available for deployment automation
- Create GitHub Release (if tag-based push)
  - Release notes with image details
  - Build information

**Duration**: ~2-3 minutes

**Failure Handling**: Pipeline fails if push fails

## Security Scanning Details

### Bandit (SAST)

Scans Python code for security issues:
- SQL injection patterns
- Hardcoded secrets
- Insecure cryptographic functions
- Dangerous code patterns

**Report**: `bandit-report.json`

**Severity Levels**:
- HIGH: Serious security issue
- MEDIUM: Potential security risk
- LOW: Defensive programming issue

### CodeQL

GitHub's semantic code analysis:
- Data flow analysis
- Control flow analysis
- Taint analysis for injection vulnerabilities

**Configuration**: Python language pack

**Results**: Uploaded to GitHub Security → Code scanning

### pip-audit

Scans installed packages against known vulnerabilities:
- Checks `poetry.lock` against vulnerability database
- Reports CVEs and affected versions
- Suggests remediation

### Trivy

Container image vulnerability scanning:
- Scans OS layer (Alpine base image)
- Scans application dependencies
- Checks for known CVEs

**Severity Levels**:
- CRITICAL: Immediate action required
- HIGH: Should be addressed
- MEDIUM: Consider fixing
- LOW: Low priority
- UNKNOWN: Severity undetermined

## Artifact Retention

GitHub automatically retains artifacts for 90 days by default:

- Test results: Coverage reports, test output
- Security reports: Bandit JSON, Trivy SARIF
- Deployment info: Image metadata, tags

To access artifacts:
1. Go to GitHub Actions
2. Select workflow run
3. Scroll to "Artifacts" section
4. Download desired artifact

## Environment and Secrets

### Required GitHub Secrets

Configure in: Settings → Secrets and variables → Actions

```
DOCKERHUB_USERNAME = your-dockerhub-username
DOCKERHUB_TOKEN = your-dockerhub-personal-access-token
```

**Important**: 
- Create a Personal Access Token (PAT) for DockerHub
- Give it `read:packages` and `write:packages` permissions
- Never commit secrets to repository

### Environment Variables

The pipeline uses these environment variables:

```bash
REGISTRY = docker.io
IMAGE_NAME = ${{ secrets.DOCKERHUB_USERNAME }}/todo-api
PYTHON_VERSION = 3.11
```

## Running Workflows

### Automatic Triggers

Pipeline runs automatically on:
1. **Push to main/master branch**
2. **Pull requests** to main/master
3. All jobs run except `publish` for PRs

### Manual Trigger (workflow_dispatch)

Via GitHub UI:
1. Go to Actions tab
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

Via GitHub CLI:
```bash
gh workflow run ci.yml --ref main
```

### Workflow Status

Check pipeline status:
- GitHub Actions page shows real-time status
- Branch protection rules can require checks to pass
- Commit badges show status

## Debugging Failed Workflows

### 1. Check Logs

Steps to access logs:
1. Go to GitHub Actions
2. Click on the failed workflow run
3. Click on the failed job
4. Expand failed step
5. Review logs for error messages

### 2. Common Failures

**lint-test failures**:
- Code style violations (Black/isort)
- Linting errors (Ruff)
- Test failures

**Solution**: 
- Run locally: `poetry run pytest tests/`
- Format code: `poetry run black app/ tests/`
- Check lints: `poetry run ruff check app/ tests/`

**docker-build-scan failures**:
- Dockerfile syntax errors
- Missing dependencies
- Build context issues

**Solution**:
- Build locally: `docker build -t test:latest .`
- Check Dockerfile: `docker build --check .`

**runtime-smoke-test failures**:
- Application startup errors
- Port binding issues
- Database connection errors

**Solution**:
- Check container logs: `docker logs <container>`
- Verify database setup
- Test locally: `docker-compose up`

**publish failures**:
- Authentication issues
- Registry unavailable
- Insufficient storage

**Solution**:
- Verify secrets configured correctly
- Check DockerHub status
- Review push permissions

### 3. Re-run Failed Jobs

Via GitHub UI:
1. Open failed workflow run
2. Click "Re-run failed jobs"
3. Confirm

Via GitHub CLI:
```bash
gh run rerun <run-id>
```

## Performance Optimization

### Caching Strategies

The pipeline uses several caching mechanisms:

1. **Dependency Cache**
   - Python dependencies cached between runs
   - Cache key: `poetry.lock` hash
   - Saves ~30 seconds per run

2. **Docker Layer Caching**
   - BuildKit caches each layer
   - Reuses layers from previous builds
   - Saves 1-2 minutes on unchanged dependencies

3. **Registry Cache**
   - Buildx pushes cache to registry
   - Mode: `type=registry,mode=max`
   - Enables faster rebuilds across runners

### Fail-Fast Strategy

The pipeline uses `fail-fast: true` in matrix jobs where applicable, stopping all jobs if one fails to save resources.

### Concurrency Control

Uses GitHub Actions concurrency groups to cancel duplicate runs:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This prevents resource waste when multiple pushes occur.

## Integration with GitHub Features

### Branch Protection

Enable in: Settings → Branches → Branch protection rules

Require checks before merging:
- ✓ lint-test
- ✓ sast-sca
- Optionally: code-scanning (CodeQL)

### GitHub Security Tab

All security findings automatically appear in:
- Security → Code scanning alerts (CodeQL, Bandit)
- Security → Dependabot alerts (pip-audit)

### Status Checks

Commit badges show pipeline status:
```markdown
[![CI/CD Pipeline](https://github.com/nullHawk/DevOps-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/nullHawk/DevOps-Project/actions/workflows/ci.yml)
```

## Troubleshooting Guide

### Issue: "Permission denied" when publishing to DockerHub

**Cause**: Invalid credentials

**Solution**:
1. Regenerate DockerHub Personal Access Token
2. Update `DOCKERHUB_TOKEN` secret
3. Ensure token has correct permissions

### Issue: Trivy scan fails with "image not found"

**Cause**: Image not built successfully

**Solution**:
1. Check docker-build-scan logs
2. Fix Dockerfile issues
3. Re-run workflow

### Issue: Tests pass locally but fail in CI

**Cause**: Environment differences

**Solution**:
1. Check CI logs for environment details
2. Ensure all dependencies in `pyproject.toml`
3. Use same Python version (3.11)
4. Check for hardcoded paths or environment assumptions

### Issue: Pipeline timeout

**Cause**: Tests or scans taking too long

**Solution**:
1. Optimize test suite (reduce fixtures, mock external calls)
2. Run CodeQL on schedule instead of every push
3. Use test filtering (pytest markers)

## Best Practices

1. **Keep poetry.lock updated**
   - Ensures reproducible builds
   - Reduces build time due to caching

2. **Monitor security findings**
   - Review CodeQL alerts weekly
   - Address HIGH/CRITICAL issues promptly
   - Suppress false positives with justification

3. **Test coverage targets**
   - Maintain >80% code coverage
   - Use coverage badge in README
   - Trend coverage over time

4. **Semantic versioning**
   - Use tags for releases: `v1.0.0`, `v1.1.0`, etc.
   - Images tagged automatically per version
   - Enables easy rollbacks

5. **Regular maintenance**
   - Update GitHub Actions versions monthly
   - Audit and rotate DockerHub token
   - Review and update security policies

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [CodeQL Documentation](https://codeql.github.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
