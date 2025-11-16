"""
Database migration to create scouting_reports table

Run this script to add the scouting_reports table to the database.
"""

import sys
sys.path.insert(0, '/home/akyo/startup_swiper/api')

from database import engine
from models_startup import ScoutingReport

# Create the table
try:
    ScoutingReport.metadata.create_all(bind=engine)
    print("✅ Created scouting_reports table successfully!")
    print("\nTable structure:")
    print("  - id (primary key)")
    print("  - startup_id (optional FK to startups)")
    print("  - company_name")
    print("  - cb_insights_org_id")
    print("  - Financial metrics (revenue, income, funding)")
    print("  - Team info (employees, CEO, founders)")
    print("  - Market position (commercial_maturity, competitors)")
    print("  - Strategic data (opportunities, threats, partnerships)")
    print("  - Report content (markdown, JSON)")
    print("  - File paths (markdown_file_path, json_file_path)")
    print("\nYou can now store scouting reports in the database!")
except Exception as e:
    print(f"❌ Error creating table: {str(e)}")
    sys.exit(1)
