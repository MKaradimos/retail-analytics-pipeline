#!/bin/bash
# Quick setup script for Retail Analytics Pipeline

set -e

echo "=========================================="
echo "Retail Analytics Pipeline - Quick Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Warning: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker found${NC}"
echo -e "${GREEN}✓ Docker Compose found${NC}"
echo ""

# Step 1: Environment setup
echo -e "${BLUE}Step 1: Setting up environment...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${YELLOW}! .env file already exists, skipping${NC}"
fi
echo ""

# Step 2: Generate sample data
echo -e "${BLUE}Step 2: Generating sample data...${NC}"
python3 data/generate_sample_data.py
echo ""

# Step 3: Build Docker images
echo -e "${BLUE}Step 3: Building Docker images...${NC}"
docker-compose build
echo -e "${GREEN}✓ Docker images built${NC}"
echo ""

# Step 4: Start services
echo -e "${BLUE}Step 4: Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for PostgreSQL to be ready
echo -e "${BLUE}Waiting for PostgreSQL to be ready...${NC}"
sleep 10
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Step 5: Summary
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Services running:"
echo "  • PostgreSQL: localhost:5432"
echo "  • pgAdmin:    http://localhost:5050"
echo ""
echo "Next steps:"
echo "  1. Run pipeline:     make run"
echo "  2. View logs:        make logs"
echo "  3. Access database:  make psql"
echo "  4. Stop services:    make down"
echo ""
echo "For more commands: make help"
echo ""
echo -e "${BLUE}Happy analyzing! 📊${NC}"
