#!/bin/bash
#
# AXA Comprehensive Startup Evaluator - Runner Script
#
# This script activates the virtual environment and runs the evaluator
#

set -e

cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}AXA Comprehensive Startup Evaluator${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r api/requirements.txt
else
    source .venv/bin/activate
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Run the fast evaluator
cd api
python3 axa_comprehensive_evaluator_fast.py "$@"

echo ""
echo -e "${GREEN}✓ Evaluation complete!${NC}"
