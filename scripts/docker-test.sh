#!/bin/bash
# Script to test Docker build locally

set -e

echo "Testing Docker build..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get git information
GIT_COMMIT=$(git rev-parse HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VERSION="1.0.0"

echo -e "${YELLOW}Building Docker image...${NC}"
docker build \
  -t todo-api:test \
  --build-arg VERSION=$VERSION \
  --build-arg GIT_COMMIT=$GIT_COMMIT \
  --build-arg GIT_BRANCH=$GIT_BRANCH \
  --build-arg BUILD_DATE=$BUILD_DATE \
  .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi

# Test image
echo -e "${YELLOW}Testing image...${NC}"
docker run --rm todo-api:test python -c "import app; print('Import successful')"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image test passed${NC}"
else
    echo -e "${RED}✗ Image test failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker build test complete!${NC}"
