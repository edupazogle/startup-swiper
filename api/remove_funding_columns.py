"""
Migration script to remove all funding information from the startup database
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'startup_swiper.db'

# Funding columns to remove from startups table
STARTUP_FUNDING_COLUMNS = [
    'prominent_investors',
    'currentInvestmentStage',
    'totalFunding',
    'originalTotalFunding',
    'originalTotalFundingCurrency',
    'lastFundingDate',
    'lastFunding',
    'originalLastFunding',
    'originalLastFundingCurrency',
    'fundingIsUndisclosed'
]

# Funding columns to remove from scouting_reports table
SCOUTING_FUNDING_COLUMNS = [
    'total_funding',
    'funding_currency',
    'latest_round_amount',
    'latest_round_date',
    'latest_round_type'
]

def get_existing_columns(conn, table_name):
    """Get list of columns in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}

def remove_columns_from_table(conn, table_name, columns_to_remove):
    """Remove specified columns from a table"""
    existing_columns = get_existing_columns(conn, table_name)
    columns_to_remove_filtered = [col for col in columns_to_remove if col in existing_columns]
    
    if not columns_to_remove_filtered:
        print(f"  No funding columns found in {table_name}")
        return
    
    # Get all columns except the ones to remove
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    all_columns = [row[1] for row in cursor.fetchall()]
    columns_to_keep = [col for col in all_columns if col not in columns_to_remove_filtered]
    
    # Create list of columns for the new table (excluding removed ones)
    new_columns_list = ', '.join(columns_to_keep)
    
    try:
        # SQLite doesn't support dropping columns directly, so we need to:
        # 1. Create a new table without the funding columns
        # 2. Copy data from old table
        # 3. Drop old table
        # 4. Rename new table
        
        cursor.execute(f"BEGIN TRANSACTION")
        
        # Create new table with same structure but without funding columns
        cursor.execute(f"CREATE TABLE {table_name}_new AS SELECT {new_columns_list} FROM {table_name}")
        
        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}")
        
        # Rename new table to original name
        cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
        
        cursor.execute(f"COMMIT")
        
        print(f"✅ Removed {len(columns_to_remove_filtered)} funding columns from {table_name}:")
        for col in columns_to_remove_filtered:
            print(f"   - {col}")
    except Exception as e:
        cursor.execute(f"ROLLBACK")
        print(f"❌ Error removing columns from {table_name}: {e}")
        raise

def main():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    print(f"🗑️  Removing funding information from database: {DB_PATH}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        # Remove funding columns from startups table
        print("Processing 'startups' table...")
        remove_columns_from_table(conn, 'startups', STARTUP_FUNDING_COLUMNS)
        print()
        
        # Remove funding columns from scouting_reports table if it exists
        existing_tables = set()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        if 'scouting_reports' in existing_tables:
            print("Processing 'scouting_reports' table...")
            remove_columns_from_table(conn, 'scouting_reports', SCOUTING_FUNDING_COLUMNS)
            print()
        else:
            print("⚠️  'scouting_reports' table not found, skipping")
            print()
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
