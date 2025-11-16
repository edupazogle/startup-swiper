#!/usr/bin/env python3
"""
Migration script to add axa_grade and axa_grade_explanation columns to startups table
"""

import sqlite3
from pathlib import Path

# Try to find the database
possible_paths = [
    Path(__file__).parent.parent / "startup_swiper.db",
    Path(__file__).parent / "startup_swiper.db",
    Path(__file__).parent / "startup_database.db",
]

def find_db():
    for path in possible_paths:
        if path.exists():
            return path
    return None

def migrate():
    """Add new columns to startups table"""
    db_path = find_db()
    
    if not db_path:
        print(f"❌ Database not found. Checked:")
        for path in possible_paths:
            print(f"   - {path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"📦 Connected to database: {db_path}")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(startups)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        columns_to_add = {
            'axa_grade': 'VARCHAR',
            'axa_grade_explanation': 'TEXT'
        }
        
        added_count = 0
        for col_name, col_type in columns_to_add.items():
            if col_name in existing_columns:
                print(f"✅ Column '{col_name}' already exists")
            else:
                print(f"➕ Adding column '{col_name}' ({col_type})...")
                cursor.execute(f"ALTER TABLE startups ADD COLUMN {col_name} {col_type}")
                added_count += 1
                print(f"   ✅ Added '{col_name}'")
        
        # Create index for axa_grade if not exists
        try:
            cursor.execute("CREATE INDEX idx_axa_grade ON startups(axa_grade)")
            print(f"✅ Created index on 'axa_grade'")
        except sqlite3.OperationalError as e:
            if "already exists" in str(e):
                print(f"✅ Index on 'axa_grade' already exists")
            else:
                raise
        
        conn.commit()
        print(f"\n✨ Migration complete! Added {added_count} columns")
        print(f"📊 Database location: {db_path}")
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = migrate()
    exit(0 if success else 1)
