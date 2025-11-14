#!/usr/bin/env python3
"""
Download/Export Startups - Filter and export startups based on criteria

This script allows you to export startups that match specific rules/filters:
- By country (e.g., only Finnish startups)
- By maturity stage (e.g., only scaleups)
- By funding level (e.g., funded startups only)
- By enrichment status (e.g., only enriched startups)
- By website availability
- By specific fields (e.g., has LinkedIn, has email)
- Custom combinations of filters

Usage:
    # Download all startups
    python3 api/download_startups.py --output all_startups.json
    
    # Download only enriched startups
    python3 api/download_startups.py --enriched-only --output enriched_startups.json
    
    # Download startups from specific countries
    python3 api/download_startups.py --countries FI,SE,NO --output nordic_startups.json
    
    # Download funded scaleups with websites
    python3 api/download_startups.py --has-funding --maturity scaleup --has-website --output funded_scaleups.json
    
    # Download startups with complete contact info
    python3 api/download_startups.py --has-email --has-linkedin --output contact_complete.json
    
    # Export to CSV
    python3 api/download_startups.py --output startups.csv --format csv
"""

import json
import csv
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class StartupFilter:
    """Filter startups based on various criteria"""
    
    def __init__(self):
        self.filters = []
    
    def add_filter(self, name: str, func):
        """Add a filter function"""
        self.filters.append((name, func))
    
    def apply(self, startups: List[Dict]) -> List[Dict]:
        """Apply all filters to startups"""
        filtered = startups
        for name, func in self.filters:
            before = len(filtered)
            filtered = [s for s in filtered if func(s)]
            after = len(filtered)
            logger.info(f"Filter '{name}': {before} → {after} startups ({before-after} removed)")
        return filtered


def load_startups(database_file: str) -> List[Dict]:
    """Load startups from database"""
    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            startups = json.load(f)
            logger.info(f"Loaded {len(startups)} startups from {database_file}")
            return startups
    except Exception as e:
        logger.error(f"Failed to load database: {e}")
        return []


def export_to_json(startups: List[Dict], output_file: str, pretty: bool = True):
    """Export startups to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(startups, f, indent=2, ensure_ascii=False)
            else:
                json.dump(startups, f, ensure_ascii=False)
        logger.info(f"Exported {len(startups)} startups to {output_file}")
    except Exception as e:
        logger.error(f"Failed to export to JSON: {e}")


def export_to_csv(startups: List[Dict], output_file: str, fields: Optional[List[str]] = None):
    """Export startups to CSV file"""
    if not startups:
        logger.warning("No startups to export")
        return
    
    # Default fields to export
    if fields is None:
        fields = [
            'id', 'name', 'website', 'shortDescription',
            'billingCountry', 'billingCity', 'maturity',
            'employees', 'totalFunding', 'currentInvestmentStage',
            'dateFounded', 'is_enriched'
        ]
    
    # Add enrichment fields if available
    sample = startups[0]
    if sample.get('enrichment'):
        fields.extend(['enrichment_emails', 'enrichment_linkedin', 'enrichment_phone'])
    
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for startup in startups:
                # Flatten enrichment data for CSV
                row = startup.copy()
                if startup.get('enrichment'):
                    enrich = startup['enrichment']
                    row['enrichment_emails'] = ','.join(enrich.get('emails', []))
                    row['enrichment_linkedin'] = enrich.get('social_media', {}).get('linkedin', '')
                    row['enrichment_phone'] = ','.join(enrich.get('phone_numbers', []))
                
                writer.writerow(row)
        
        logger.info(f"Exported {len(startups)} startups to {output_file}")
    except Exception as e:
        logger.error(f"Failed to export to CSV: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Download/Export startups with filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Input/Output
    parser.add_argument('--input', default='docs/architecture/ddbb/slush2_extracted.json',
                        help='Input database file (default: slush2_extracted.json)')
    parser.add_argument('--output', '-o', required=True,
                        help='Output file (JSON or CSV)')
    parser.add_argument('--format', choices=['json', 'csv'], default=None,
                        help='Output format (auto-detected from extension if not specified)')
    parser.add_argument('--pretty', action='store_true', default=True,
                        help='Pretty print JSON output (default: True)')
    
    # Filtering options
    filter_group = parser.add_argument_group('Filtering Options')
    filter_group.add_argument('--countries', type=str,
                              help='Filter by countries (comma-separated, e.g., FI,SE,NO)')
    filter_group.add_argument('--maturity', type=str,
                              help='Filter by maturity stage (e.g., scaleup, startup)')
    filter_group.add_argument('--min-funding', type=float,
                              help='Minimum total funding amount')
    filter_group.add_argument('--has-funding', action='store_true',
                              help='Only startups with funding > 0')
    filter_group.add_argument('--has-website', action='store_true',
                              help='Only startups with website')
    filter_group.add_argument('--has-email', action='store_true',
                              help='Only startups with email in enrichment data')
    filter_group.add_argument('--has-linkedin', action='store_true',
                              help='Only startups with LinkedIn in enrichment data')
    filter_group.add_argument('--enriched-only', action='store_true',
                              help='Only enriched startups')
    filter_group.add_argument('--min-employees', type=str,
                              help='Minimum employee count (e.g., 11-50)')
    filter_group.add_argument('--founded-after', type=int,
                              help='Founded after year (e.g., 2020)')
    filter_group.add_argument('--topics', type=str,
                              help='Filter by topics (comma-separated keywords)')
    
    # Statistics
    parser.add_argument('--stats', action='store_true',
                        help='Show statistics about filtered results')
    
    args = parser.parse_args()
    
    # Determine output format
    if args.format is None:
        if args.output.endswith('.csv'):
            args.format = 'csv'
        else:
            args.format = 'json'
    
    # Load startups
    base_path = Path(__file__).parent.parent
    input_file = base_path / args.input
    startups = load_startups(input_file)
    
    if not startups:
        logger.error("No startups loaded. Exiting.")
        return 1
    
    # Build filter chain
    filter_chain = StartupFilter()
    
    if args.countries:
        countries = [c.strip().upper() for c in args.countries.split(',')]
        filter_chain.add_filter(
            f"countries={','.join(countries)}",
            lambda s: (s.get('billingCountry') or '').upper() in countries
        )
    
    if args.maturity:
        maturity_lower = args.maturity.lower()
        filter_chain.add_filter(
            f"maturity={args.maturity}",
            lambda s: maturity_lower in s.get('maturity', '').lower()
        )
    
    if args.has_funding:
        def has_funding_filter(s):
            funding = s.get('totalFunding', 0)
            try:
                return funding and float(funding) > 0
            except (ValueError, TypeError):
                return False
        filter_chain.add_filter("has_funding", has_funding_filter)
    
    if args.min_funding:
        def min_funding_filter(s):
            funding = s.get('totalFunding', 0)
            try:
                return float(funding) >= args.min_funding
            except (ValueError, TypeError):
                return False
        filter_chain.add_filter(f"min_funding={args.min_funding}", min_funding_filter)
    
    if args.has_website:
        filter_chain.add_filter(
            "has_website",
            lambda s: s.get('website') and s['website'].strip()
        )
    
    if args.enriched_only:
        filter_chain.add_filter(
            "enriched_only",
            lambda s: s.get('is_enriched', False) or s.get('enrichment')
        )
    
    if args.has_email:
        filter_chain.add_filter(
            "has_email",
            lambda s: s.get('enrichment', {}).get('emails') and len(s['enrichment']['emails']) > 0
        )
    
    if args.has_linkedin:
        filter_chain.add_filter(
            "has_linkedin",
            lambda s: s.get('enrichment', {}).get('social_media', {}).get('linkedin')
        )
    
    if args.founded_after:
        filter_chain.add_filter(
            f"founded_after={args.founded_after}",
            lambda s: s.get('dateFounded') and args.founded_after <= int(s['dateFounded'][:4])
        )
    
    if args.topics:
        topics = [t.strip().lower() for t in args.topics.split(',')]
        filter_chain.add_filter(
            f"topics={','.join(topics)}",
            lambda s: any(
                any(topic in str(t).lower() for topic in topics)
                for t in s.get('topics', [])
            )
        )
    
    # Apply filters
    logger.info(f"Applying {len(filter_chain.filters)} filter(s)...")
    filtered_startups = filter_chain.apply(startups)
    
    logger.info(f"Final result: {len(filtered_startups)} startups")
    
    # Show statistics if requested
    if args.stats:
        print("\n" + "="*60)
        print("STATISTICS")
        print("="*60)
        
        # Country distribution
        countries = {}
        for s in filtered_startups:
            country = s.get('billingCountry', 'Unknown')
            countries[country] = countries.get(country, 0) + 1
        print(f"\nTop 10 Countries:")
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {country}: {count}")
        
        # Maturity distribution
        maturity = {}
        for s in filtered_startups:
            mat = s.get('maturity', 'Unknown')
            maturity[mat] = maturity.get(mat, 0) + 1
        print(f"\nMaturity Stages:")
        for stage, count in sorted(maturity.items(), key=lambda x: x[1], reverse=True):
            print(f"  {stage}: {count}")
        
        # Enrichment stats
        enriched = sum(1 for s in filtered_startups if s.get('is_enriched') or s.get('enrichment'))
        with_website = sum(1 for s in filtered_startups if s.get('website'))
        with_funding = sum(1 for s in filtered_startups if s.get('totalFunding') and 
                          (isinstance(s['totalFunding'], (int, float)) and s['totalFunding'] > 0))
        
        total = len(filtered_startups)
        if total > 0:
            print(f"\nData Completeness:")
            print(f"  Enriched: {enriched} ({100*enriched/total:.1f}%)")
            print(f"  Has Website: {with_website} ({100*with_website/total:.1f}%)")
            print(f"  Has Funding: {with_funding} ({100*with_funding/total:.1f}%)")
        else:
            print(f"\nData Completeness: No startups matched filters")
        print("="*60 + "\n")
    
    # Export results
    output_path = base_path / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.format == 'csv':
        export_to_csv(filtered_startups, output_path)
    else:
        export_to_json(filtered_startups, output_path, args.pretty)
    
    logger.info(f"✓ Successfully exported {len(filtered_startups)} startups to {args.output}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
