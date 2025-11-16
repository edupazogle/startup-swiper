#!/usr/bin/env python3
"""
Migration script to add missing AXA evaluation columns to the startups table.
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import engine

def add_axa_columns():
    """Add missing axa_fit_summary and axa_rule_scores columns"""
    
    with engine.connect() as conn:
        # Check if columns exist first
        try:
            # Try to query the columns - if they don't exist, we'll get an error
            result = conn.execute(text("PRAGMA table_info(startups)"))
            columns = {row[1] for row in result}
            
            if "axa_fit_summary" not in columns:
                print("Adding column: axa_fit_summary...")
                conn.execute(text("ALTER TABLE startups ADD COLUMN axa_fit_summary TEXT"))
                print("✓ Added axa_fit_summary")
            else:
                print("✓ Column axa_fit_summary already exists")
            
            if "axa_rule_scores" not in columns:
                print("Adding column: axa_rule_scores...")
                conn.execute(text("ALTER TABLE startups ADD COLUMN axa_rule_scores JSON"))
                print("✓ Added axa_rule_scores")
            else:
                print("✓ Column axa_rule_scores already exists")
            
            conn.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    add_axa_columns()
