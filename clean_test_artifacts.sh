#!/bin/bash
# Script to clean up test artifacts

set -e  # Exit on error

# Colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Cleaning Test Artifacts ===${NC}"
echo -e "${BLUE}===========================${NC}\n"

# List of test artifacts to remove
TEST_ARTIFACTS=(
    "email_validator.py"
    "hello.py"
    "app.py"
    "test_app.py"
    "csv_parser.py"
    "state.json"
)

# Remove each test artifact
for file in "${TEST_ARTIFACTS[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}Removing:${NC} $file"
        rm -f "$file"
    else
        echo -e "${YELLOW}Skipping:${NC} $file (not found)"
    fi
done

# Clean __pycache__ directories
echo -e "\n${YELLOW}Cleaning Python cache files...${NC}"
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete

echo -e "\n${GREEN}Clean up complete!${NC}" 