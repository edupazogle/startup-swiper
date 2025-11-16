#!/bin/bash

echo "=========================================="
echo "Preparing for Full Evaluation Run"
echo "=========================================="
echo ""

# Clean up old results
echo "1. Cleaning up old evaluation results..."
rm -f evaluator/downloads/axa_evaluation_results.json
rm -f evaluator/test_results*.json
echo "   ✓ Removed old results"

# Clean up checkpoints
echo "2. Cleaning up checkpoints..."
rm -f evaluator/checkpoint_*.json
echo "   ✓ Removed checkpoints"

# Clean up logs
echo "3. Cleaning up logs..."
mkdir -p evaluator/logs
rm -f evaluator/logs/*
echo "   ✓ Cleared logs"

# Create downloads directory
echo "4. Ensuring directories exist..."
mkdir -p evaluator/downloads
echo "   ✓ Directories ready"

# Check database
echo "5. Checking database..."
python3 << 'EOFPYTHON'
import sys
sys.path.insert(0, 'api')
from database import SessionLocal
from models_startup import Startup

db = SessionLocal()
total = db.query(Startup).count()
with_descriptions = db.query(Startup).filter(
    (Startup.company_description.isnot(None)) | (Startup.shortDescription.isnot(None))
).count()

print(f"   Total startups in database: {total}")
print(f"   Startups with descriptions: {with_descriptions}")
print(f"   Will evaluate: {with_descriptions}")

db.close()
EOFPYTHON

echo ""
echo "=========================================="
echo "Ready to run full evaluation!"
echo "=========================================="
echo ""
echo "Command to run:"
echo ""
echo "  python3 evaluator/axa_enhanced_evaluator.py \\"
echo "    --workers 15 \\"
echo "    --batch-size 3 \\"
echo "    --output evaluator/downloads/axa_evaluation_results.json"
echo ""
echo "Monitor with:"
echo "  python3 evaluator/monitor_progress_visual.py"
echo ""
echo "=========================================="
