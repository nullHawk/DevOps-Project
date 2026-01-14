#!/bin/bash
# Script to run security checks locally

set -e

echo "Running security checks..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Run Bandit
echo -e "${YELLOW}Running Bandit security check...${NC}"
poetry run bandit -r app/ -ll || {
    echo -e "${RED}⚠ Bandit found potential security issues${NC}"
}
echo -e "${GREEN}✓ Bandit completed${NC}"

# Run pip-audit
echo -e "${YELLOW}Running pip-audit...${NC}"
poetry run pip-audit || {
    echo -e "${RED}⚠ pip-audit found vulnerable dependencies${NC}"
}
echo -e "${GREEN}✓ pip-audit completed${NC}"

echo -e "${GREEN}✅ Security checks complete!${NC}"
