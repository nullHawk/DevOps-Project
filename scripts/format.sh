#!/bin/bash
# Script to format code and fix issues

set -e

echo "Formatting code..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Format with Black
echo -e "${YELLOW}Running Black formatter...${NC}"
poetry run black app/ tests/
echo -e "${GREEN}✓ Black completed${NC}"

# Sort imports with isort
echo -e "${YELLOW}Running isort...${NC}"
poetry run isort app/ tests/
echo -e "${GREEN}✓ isort completed${NC}"

# Try to fix Ruff issues
echo -e "${YELLOW}Running Ruff auto-fix...${NC}"
poetry run ruff check app/ tests/ --fix || true
echo -e "${GREEN}✓ Ruff auto-fix completed${NC}"

echo -e "${GREEN}✅ Code formatting complete!${NC}"
