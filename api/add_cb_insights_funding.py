"""
Migration script to add CB Insights funding data to the startup database
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'startup_swiper.db'

# New columns to add to startups table
STARTUP_FUNDING_COLUMNS = [
    ('total_funding', 'FLOAT', 'Total funding in millions USD from CB Insights'),
    ('total_equity_funding', 'FLOAT', 'Equity-only funding in millions USD from CB Insights'),
    ('last_funding_date', 'DATETIME', 'Date of most recent funding round from CB Insights'),
    ('last_funding_date_str', 'TEXT', 'ISO format date string'),
    ('funding_source', 'TEXT', 'Data source (CB Insights API v2)'),
    ('valuation', 'FLOAT', 'Latest valuation in millions USD from CB Insights'),
    ('latest_revenue_min', 'FLOAT', 'Latest minimum revenue in USD from CB Insights'),
    ('latest_revenue_max', 'FLOAT', 'Latest maximum revenue in USD from CB Insights'),
    ('revenue_date', 'DATETIME', 'Date of revenue data from CB Insights'),
]

def column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row[1] for row in cursor.fetchall()}
    return column_name in columns

def add_columns_to_table(conn, table_name, columns):
    """Add columns to a table"""
    cursor = conn.cursor()
    
    for col_name, col_type, description in columns:
        if column_exists(conn, table_name, col_name):
            print(f"  Column '{col_name}' already exists in {table_name}")
            continue
        
        try:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
            cursor.execute(alter_sql)
            conn.commit()
            print(f"  ✅ Added column '{col_name}' ({col_type})")
        except Exception as e:
            print(f"  ❌ Error adding column '{col_name}': {e}")
            raise

def create_funding_rounds_table(conn):
    """Create the funding_rounds table for individual funding rounds"""
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='funding_rounds'")
    if cursor.fetchone():
        print("  Table 'funding_rounds' already exists")
        return
    
    try:
        create_table_sql = """
        CREATE TABLE funding_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            startup_id INTEGER,
            deal_id INTEGER UNIQUE,
            cb_insights_org_id INTEGER,
            
            round_date DATETIME,
            round_date_str TEXT,
            round_name TEXT,
            round_category TEXT,
            simplified_round TEXT,
            
            amount_millions FLOAT,
            valuation_millions FLOAT,
            
            revenue_min FLOAT,
            revenue_max FLOAT,
            revenue_multiple_min FLOAT,
            revenue_multiple_max FLOAT,
            revenue_period TEXT,
            
            investors JSON,
            investor_count INTEGER,
            
            is_exit BOOLEAN DEFAULT 0,
            
            sources JSON,
            insights TEXT,
            
            data_source TEXT DEFAULT 'CB Insights API v2',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (startup_id) REFERENCES startups(id)
        )
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("  ✅ Created 'funding_rounds' table")
        
        # Create indexes for common queries
        indexes = [
            ("CREATE INDEX idx_funding_rounds_startup_id ON funding_rounds(startup_id)"),
            ("CREATE INDEX idx_funding_rounds_deal_id ON funding_rounds(deal_id)"),
            ("CREATE INDEX idx_funding_rounds_round_date ON funding_rounds(round_date)"),
            ("CREATE INDEX idx_funding_rounds_simplified_round ON funding_rounds(simplified_round)"),
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                conn.commit()
            except:
                pass  # Index might already exist
        
        print("  ✅ Created indexes for 'funding_rounds' table")
        
    except Exception as e:
        print(f"  ❌ Error creating 'funding_rounds' table: {e}")
        raise

def main():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return
    
    print(f"📊 Adding CB Insights funding data to database: {DB_PATH}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    try:
        # Add funding columns to startups table
        print("Processing 'startups' table...")
        add_columns_to_table(conn, 'startups', STARTUP_FUNDING_COLUMNS)
        print()
        
        # Create funding_rounds table
        print("Creating 'funding_rounds' table...")
        create_funding_rounds_table(conn)
        print()
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        print()
        print("📝 Next steps:")
        print("   1. Use CB Insights API v2 to fetch firmographics data")
        print("   2. Use /v2/financialtransactions/fundings endpoint for funding rounds")
        print("   3. Populate funding_rounds table with detailed round information")
        print("   4. Update startups table with aggregated metrics from Firmographics endpoint")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
