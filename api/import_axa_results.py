#!/usr/bin/env python3
"""
Import AXA Evaluation Results to Database

Reads axa_full_3665_results.json and imports all evaluation data
with every parameter into the database.

Usage:
    python3 api/import_axa_results.py
    python3 api/import_axa_results.py --dry-run
    python3 api/import_axa_results.py --verbose
"""

import json
import sys
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

DB_PATH = "startup_swiper.db"
RESULTS_PATH = "downloads/axa_full_3665_results.json"


def load_results(results_path: str) -> List[Dict[str, Any]]:
    """Load the AXA results JSON file"""
    path = Path(results_path)
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")
    
    print(f"📖 Loading AXA results from {results_path}...")
    with open(path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        results = data
    elif isinstance(data, dict) and 'results' in data:
        results = data['results']
    else:
        raise ValueError("Unexpected JSON structure - expected list or dict with 'results' key")
    
    print(f"✓ Loaded {len(results)} evaluation records")
    return results


def create_connection(db_path: str):
    """Create database connection"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"✗ Connection failed: {e}")
        return None


def validate_database(conn):
    """Verify database connection"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM startups")
        count = cursor.fetchone()[0]
        print(f"✓ Database connected - {count:,} total startups")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


def ensure_columns_exist(conn):
    """Ensure all required AXA columns exist in database"""
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(startups)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Required columns mapping
    required_columns = {
        'axa_evaluation_date': 'DATETIME',
        'axa_overall_score': 'REAL',
        'axa_priority_tier': 'TEXT',
        'axa_categories_matched': 'JSON',
        'axa_fit_summary': 'TEXT',
        'axa_can_use_as_provider': 'BOOLEAN',
        'axa_business_leverage': 'TEXT',
        'axa_matched_rules': 'JSON',
        'axa_rule_scores': 'JSON',
    }
    
    # Add missing columns
    added_count = 0
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            print(f"  Adding column: {col_name}")
            try:
                cursor.execute(f"ALTER TABLE startups ADD COLUMN {col_name} {col_type}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"    Warning: {e}")
    
    if added_count > 0:
        print(f"✓ Added {added_count} missing columns")
        conn.commit()
    else:
        print(f"✓ All required columns exist")


def import_results(conn, results: List[Dict[str, Any]], dry_run: bool = False, verbose: bool = False):
    """Import evaluation results into database"""
    
    total_count = len(results)
    imported_count = 0
    skipped_count = 0
    error_count = 0
    errors = []
    
    cursor = conn.cursor()
    
    print(f"\n📊 Processing {total_count:,} evaluation records...")
    
    for idx, result in enumerate(results, 1):
        startup_id = result.get('startup_id')
        startup_name = result.get('startup_name', 'Unknown')
        
        try:
            # Check if startup exists
            cursor.execute("SELECT id FROM startups WHERE id = ?", (startup_id,))
            if not cursor.fetchone():
                skipped_count += 1
                if verbose:
                    print(f"  ⚠ [{idx:4d}/{total_count}] ID {startup_id} not found in database")
                continue
            
            # Parse evaluation date
            eval_date = result.get('evaluation_date')
            if isinstance(eval_date, str):
                try:
                    eval_date = datetime.fromisoformat(eval_date.replace('Z', '+00:00')).isoformat()
                except:
                    eval_date = None
            
            # Execute update with all parameters
            cursor.execute("""
                UPDATE startups SET
                    axa_evaluation_date = ?,
                    axa_overall_score = ?,
                    axa_priority_tier = ?,
                    axa_categories_matched = ?,
                    axa_fit_summary = ?,
                    axa_can_use_as_provider = ?,
                    axa_business_leverage = ?,
                    axa_matched_rules = ?,
                    axa_rule_scores = ?
                WHERE id = ?
            """, (
                eval_date,
                result.get('overall_score'),
                result.get('priority_tier'),
                json.dumps(result.get('categories_matched', [])),
                result.get('axa_fit_summary'),
                1 if result.get('can_use_as_provider') else 0,
                result.get('business_leverage'),
                json.dumps(result.get('matched_rules', [])),
                json.dumps(result.get('rule_scores', {})),
                startup_id
            ))
            
            imported_count += 1
            
            if verbose:
                score = result.get('overall_score', 0)
                tier = result.get('priority_tier', 'Unknown')
                print(f"  ✓ [{idx:4d}/{total_count}] {startup_name} (ID {startup_id}) - Score: {score:.1f}% - {tier}")
            elif idx % 100 == 0:
                print(f"  [{idx:4d}/{total_count}] Processing... ({imported_count} imported, {skipped_count} skipped)")
        
        except Exception as e:
            error_count += 1
            error_msg = f"ID {startup_id} ({startup_name}): {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"  ✗ [{idx:4d}/{total_count}] Error - {error_msg}")
    
    # Commit if not dry-run
    if not dry_run:
        print(f"\n💾 Committing changes...")
        try:
            conn.commit()
            print(f"✓ Database committed successfully")
        except Exception as e:
            conn.rollback()
            print(f"✗ Commit failed: {e}")
            error_count += 1
    else:
        print(f"\n(DRY RUN - no changes made)")
    
    # Print summary
    print(f"\n📈 Import Summary:")
    print(f"  ✓ Imported: {imported_count:,}")
    print(f"  ⚠ Skipped: {skipped_count:,}")
    print(f"  ✗ Errors: {error_count:,}")
    print(f"  {'(DRY RUN)' if dry_run else '✓ COMMITTED'}")
    
    if errors and len(errors) <= 10:
        print(f"\n📋 Errors:")
        for error in errors:
            print(f"  - {error}")
    elif errors:
        print(f"\n📋 First 10 errors (of {len(errors)} total):")
        for error in errors[:10]:
            print(f"  - {error}")
    
    return imported_count, skipped_count, error_count


def print_sample_records(conn, count: int = 5):
    """Print sample of imported records"""
    print(f"\n📋 Sample of imported records (top {count} by score):")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company_name, axa_overall_score, axa_priority_tier, 
               axa_can_use_as_provider, axa_matched_rules, axa_fit_summary
        FROM startups
        WHERE axa_overall_score IS NOT NULL
        ORDER BY axa_overall_score DESC
        LIMIT ?
    """, (count,))
    
    records = cursor.fetchall()
    
    for idx, row in enumerate(records, 1):
        rules = json.loads(row['axa_matched_rules']) if row['axa_matched_rules'] else []
        print(f"\n  [{idx}] {row['company_name']} (ID {row['id']})")
        print(f"      Score: {row['axa_overall_score']:.1f}%")
        print(f"      Tier: {row['axa_priority_tier']}")
        print(f"      Provider: {'✓ Yes' if row['axa_can_use_as_provider'] else '✗ No'}")
        print(f"      Rules: {rules}")
        summary = row['axa_fit_summary']
        if summary:
            print(f"      Summary: {summary[:100]}...")


def print_statistics(conn):
    """Print comprehensive statistics about imported data"""
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute("""
        SELECT 
            COUNT(*) as total_startups,
            COUNT(CASE WHEN axa_overall_score IS NOT NULL THEN 1 END) as with_axa,
            ROUND(AVG(axa_overall_score), 2) as avg_score,
            MIN(axa_overall_score) as min_score,
            MAX(axa_overall_score) as max_score
        FROM startups
    """)
    stats = cursor.fetchone()
    
    print(f"\n📊 AXA EVALUATION STATISTICS")
    print(f"  Total Startups: {stats['total_startups']:,}")
    print(f"  With AXA Evaluation: {stats['with_axa']:,} ({(stats['with_axa']/stats['total_startups']*100):.1f}%)")
    print(f"  Average Score: {stats['avg_score']:.1f}%")
    print(f"  Score Range: {stats['min_score']:.1f}% - {stats['max_score']:.1f}%")
    
    # Tier distribution
    cursor.execute("""
        SELECT axa_priority_tier, COUNT(*) as count
        FROM startups
        WHERE axa_priority_tier IS NOT NULL
        GROUP BY axa_priority_tier
        ORDER BY 
            CASE 
                WHEN axa_priority_tier LIKE 'Tier 1%' THEN 1
                WHEN axa_priority_tier LIKE 'Tier 2%' THEN 2
                WHEN axa_priority_tier LIKE 'Tier 3%' THEN 3
                WHEN axa_priority_tier LIKE 'Tier 4%' THEN 4
            END
    """)
    
    print(f"\n🎯 TIER DISTRIBUTION")
    for tier, count in cursor.fetchall():
        pct = (count / stats['with_axa'] * 100) if stats['with_axa'] > 0 else 0
        print(f"  {tier:.<35} {count:>4} ({pct:>5.1f}%)")
    
    # Provider distribution
    cursor.execute("""
        SELECT axa_can_use_as_provider, COUNT(*) as count
        FROM startups
        WHERE axa_can_use_as_provider IS NOT NULL
        GROUP BY axa_can_use_as_provider
        ORDER BY count DESC
    """)
    
    print(f"\n👥 PROVIDER SUITABILITY")
    for can_use, count in cursor.fetchall():
        status = "✓ Can Use as Provider" if can_use else "✗ Not Suitable"
        pct = (count / stats['with_axa'] * 100) if stats['with_axa'] > 0 else 0
        print(f"  {status:.<35} {count:>4} ({pct:>5.1f}%)")


def main():
    parser = argparse.ArgumentParser(
        description='Import AXA Evaluation Results to Database'
    )
    parser.add_argument('--dry-run', action='store_true', 
                        help='Preview import without updating database')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed progress for each record')
    parser.add_argument('--no-sample', action='store_true',
                        help='Skip printing sample records')
    
    args = parser.parse_args()
    
    try:
        # Load results
        results = load_results(RESULTS_PATH)
        
        # Create database connection
        conn = create_connection(DB_PATH)
        if not conn:
            return 1
        
        # Validate database
        if not validate_database(conn):
            print("✗ Database validation failed")
            return 1
        
        # Ensure all columns exist
        ensure_columns_exist(conn)
        
        # Import results
        imported, skipped, errors = import_results(
            conn, 
            results,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        # Print sample records and statistics
        if imported > 0 and not args.no_sample:
            print_sample_records(conn, count=3)
        
        print_statistics(conn)
        
        conn.close()
        
        print(f"\n✓ Import complete")
        return 0 if errors == 0 else 1
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
