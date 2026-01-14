#!/bin/bash
# Script to run linting and formatting locally

set -e

echo "Running code quality checks..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Run Ruff
echo -e "${YELLOW}Running Ruff linter...${NC}"
poetry run ruff check app/ tests/ || exit 1
echo -e "${GREEN}✓ Ruff passed${NC}"

# Run Black check
echo -e "${YELLOW}Running Black formatter check...${NC}"
poetry run black --check app/ tests/ || {
    echo -e "${RED}✗ Black check failed. Run 'poetry run black app/ tests/' to fix.${NC}"
    exit 1
}
echo -e "${GREEN}✓ Black passed${NC}"

# Run isort check
echo -e "${YELLOW}Running isort import check...${NC}"
poetry run isort --check-only app/ tests/ || {
    echo -e "${RED}✗ isort check failed. Run 'poetry run isort app/ tests/' to fix.${NC}"
    exit 1
}
echo -e "${GREEN}✓ isort passed${NC}"

# Run tests
echo -e "${YELLOW}Running unit tests...${NC}"
poetry run pytest tests/ --cov=app --cov-report=term-missing || exit 1
echo -e "${GREEN}✓ Tests passed${NC}"

echo -e "${GREEN}✅ All checks passed!${NC}"
