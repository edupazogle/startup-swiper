#!/usr/bin/env python3
"""
Test Slush login and profile scraping
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scrape_slush_profiles import SlushProfileScraper

def main():
    print("="*70)
    print("TESTING SLUSH LOGIN AND SCRAPING")
    print("="*70)
    
    # Initialize scraper with screenshots enabled
    scraper = SlushProfileScraper(headless=False, screenshots=True)
    
    try:
        # Setup driver
        scraper.setup_driver()
        print("✅ Driver initialized")
        
        # Test login
        print("\n" + "="*70)
        print("TESTING LOGIN")
        print("="*70)
        
        if scraper.login():
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            return 1
        
        # Test scraping a profile
        print("\n" + "="*70)
        print("TESTING PROFILE SCRAPING")
        print("="*70)
        
        test_url = "https://platform.slush.org/slush25/meeting-tool/browse/companies/58a0f564-1954-4d97-831c-c4a1ed032217"
        print(f"\nScraping: {test_url}")
        
        data = scraper.scrape_profile(test_url)
        
        print("\n" + "="*70)
        print("SCRAPED DATA")
        print("="*70)
        
        import json
        print(json.dumps(data, indent=2))
        
        # Keep browser open for inspection
        print("\n" + "="*70)
        print("Browser will stay open for 30 seconds for inspection...")
        print("="*70)
        
        import time
        time.sleep(30)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        scraper.close()
        print("\n✅ Test complete!")

if __name__ == '__main__':
    sys.exit(main())
