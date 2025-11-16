#!/usr/bin/env python3
"""
Import CB Insights funding data for startups with cb_insights_id.
Updates: total_funding, total_equity_funding, last_funding_date, valuation, revenue data.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def load_cb_insights_data():
    """Load CB Insights enrichment data."""
    cb_path = Path('api/cb_insights_enrichment_results.json')
    with open(cb_path, 'r') as f:
        data = json.load(f)
    # Create lookup by cb_insights_id
    return {str(c['cb_insights_id']): c for c in data['firmographics'].values()}


def load_db_startups_with_cb_id():
    """Load startups from DB that have cb_insights_id."""
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company_name, cb_insights_id 
        FROM startups 
        WHERE cb_insights_id IS NOT NULL
    """)
    startups = {str(cb_id): (id_, name) for id_, name, cb_id in cursor.fetchall()}
    conn.close()
    return startups


def extract_funding_data(cb_company):
    """Extract funding-related fields from CB Insights company."""
    return {
        'total_funding': cb_company.get('total_funding'),
        'total_equity_funding': cb_company.get('total_equity_funding'),
        'last_funding_date': cb_company.get('last_funding_date'),
        'valuation': cb_company.get('valuation'),
        'latest_revenue_min': cb_company.get('latest_revenue_min'),
        'latest_revenue_max': cb_company.get('latest_revenue_max'),
        'revenue_date': cb_company.get('revenue_date'),
    }


def update_startup_funding(conn, startup_id, funding_data):
    """Update startup with CB Insights funding data."""
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE startups
        SET 
            total_funding = COALESCE(?, total_funding),
            total_equity_funding = COALESCE(?, total_equity_funding),
            last_funding_date = COALESCE(?, last_funding_date),
            valuation = COALESCE(?, valuation),
            latest_revenue_min = COALESCE(?, latest_revenue_min),
            latest_revenue_max = COALESCE(?, latest_revenue_max),
            revenue_date = COALESCE(?, revenue_date),
            last_enriched_date = ?
        WHERE id = ?
    """, (
        funding_data['total_funding'],
        funding_data['total_equity_funding'],
        funding_data['last_funding_date'],
        funding_data['valuation'],
        funding_data['latest_revenue_min'],
        funding_data['latest_revenue_max'],
        funding_data['revenue_date'],
        datetime.now().isoformat(),
        startup_id
    ))
    conn.commit()


def main():
    print("=" * 70)
    print("CB INSIGHTS FUNDING IMPORT")
    print("=" * 70)
    
    # Load data
    print("\n[1/4] Loading CB Insights data...")
    cb_data = load_cb_insights_data()
    print(f"  Loaded {len(cb_data):,} companies from CB Insights")
    
    print("\n[2/4] Loading DB startups with CB ID...")
    db_startups = load_db_startups_with_cb_id()
    print(f"  Found {len(db_startups)} startups with cb_insights_id")
    
    print("\n[3/4] Importing CB Insights funding data...")
    conn = sqlite3.connect('startup_swiper.db')
    
    updated_count = 0
    found_in_cb = 0
    funding_stats = {
        'total_funding_updated': 0,
        'equity_funding_updated': 0,
        'last_funding_date_updated': 0,
        'valuation_updated': 0,
        'revenue_min_updated': 0,
        'revenue_max_updated': 0,
    }
    
    for cb_id_str, (startup_id, startup_name) in db_startups.items():
        if cb_id_str in cb_data:
            found_in_cb += 1
            cb_company = cb_data[cb_id_str]
            funding_data = extract_funding_data(cb_company)
            
            # Count what we're updating
            if funding_data['total_funding'] is not None:
                funding_stats['total_funding_updated'] += 1
            if funding_data['total_equity_funding'] is not None:
                funding_stats['equity_funding_updated'] += 1
            if funding_data['last_funding_date'] is not None:
                funding_stats['last_funding_date_updated'] += 1
            if funding_data['valuation'] is not None:
                funding_stats['valuation_updated'] += 1
            if funding_data['latest_revenue_min'] is not None:
                funding_stats['revenue_min_updated'] += 1
            if funding_data['latest_revenue_max'] is not None:
                funding_stats['revenue_max_updated'] += 1
            
            update_startup_funding(conn, startup_id, funding_data)
            updated_count += 1
    
    conn.close()
    
    print(f"  Matched {found_in_cb}/{len(db_startups)} startups to CB Insights")
    print(f"  Updated {updated_count} startups with CB Insights funding data:")
    print(f"    - total_funding: {funding_stats['total_funding_updated']} records")
    print(f"    - total_equity_funding: {funding_stats['equity_funding_updated']} records")
    print(f"    - last_funding_date: {funding_stats['last_funding_date_updated']} records")
    print(f"    - valuation: {funding_stats['valuation_updated']} records")
    print(f"    - revenue_min: {funding_stats['revenue_min_updated']} records")
    print(f"    - revenue_max: {funding_stats['revenue_max_updated']} records")
    
    print("\n[4/4] Verification...")
    conn = sqlite3.connect('startup_swiper.db')
    cursor = conn.cursor()
    
    # Check how many startups now have funding data
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN total_funding IS NOT NULL THEN 1 END) as with_funding,
            COUNT(CASE WHEN total_equity_funding IS NOT NULL THEN 1 END) as with_equity,
            COUNT(CASE WHEN last_funding_date IS NOT NULL THEN 1 END) as with_funding_date,
            COUNT(CASE WHEN valuation IS NOT NULL THEN 1 END) as with_valuation,
            COUNT(CASE WHEN latest_revenue_min IS NOT NULL OR latest_revenue_max IS NOT NULL THEN 1 END) as with_revenue
        FROM startups
    """)
    counts = cursor.fetchone()
    print(f"  Total startups with total_funding: {counts[0]:,}")
    print(f"  Total startups with equity_funding: {counts[1]:,}")
    print(f"  Total startups with funding_date: {counts[2]:,}")
    print(f"  Total startups with valuation: {counts[3]:,}")
    print(f"  Total startups with revenue data: {counts[4]:,}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print(f"✓ Import complete - {updated_count} startups enriched from CB Insights")
    print("=" * 70)


if __name__ == '__main__':
    main()
