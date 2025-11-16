#!/bin/bash
# Quick setup and run script for AXA Grade Generation and Database Import

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 AXA GRADE CALCULATION & DATABASE IMPORT"
echo "════════════════════════════════════════════════════════════════"

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Verify database columns exist
echo ""
echo "Checking database schema..."
python3 << 'EOF'
import sqlite3

db_path = "startup_swiper.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(startups)")
cols = {col[1] for col in cursor.fetchall()}

required = {'axa_grade', 'axa_grade_explanation'}
missing = required - cols

if not missing:
    print("✅ All required columns exist")
else:
    print(f"❌ Missing columns: {missing}")
    print("Running migration...")
    if 'axa_grade' not in cols:
        cursor.execute("ALTER TABLE startups ADD COLUMN axa_grade VARCHAR")
    if 'axa_grade_explanation' not in cols:
        cursor.execute("ALTER TABLE startups ADD COLUMN axa_grade_explanation TEXT")
    try:
        cursor.execute("CREATE INDEX idx_axa_grade ON startups(axa_grade)")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    print("✅ Migration complete")

conn.close()
EOF

# Run the grading script
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Running AXA Grade Calculation..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# Show available options
cat << 'EOF'
Usage:
  ./run_grade_import.sh                    # Grade all startups
  ./run_grade_import.sh --limit 100        # Grade first 100
  ./run_grade_import.sh --dry-run          # Preview only
  ./run_grade_import.sh --limit 50 --verbose  # Verbose mode

Running with default settings (full evaluation)...
EOF

echo ""

# Run the evaluation
python3 evaluator/recalculate_scores.py "$@"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✨ Complete! Grades have been saved to the database"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Verify grades in database: python3 api/models_startup.py"
echo "2. Update frontend TypeScript types"
echo "3. Add grade display to dashboard components"
echo "4. Test API endpoints with new fields"
echo ""
