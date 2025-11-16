#!/usr/bin/env python3
"""
Slush Profile Detail Scraper
Scrapes individual startup profiles using authenticated Selenium session
"""

import os
import sys
import time
import json
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException
)
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlushProfileDetailScraper:
    """Scrapes detailed information from Slush startup profiles"""
    
    def __init__(self, selenium_url: str = "http://localhost:4444", browser: str = "chrome", limit: int = 10):
        self.selenium_url = selenium_url
        self.browser = browser.lower()
        self.driver = None
        self.limit = limit
        self.screenshots_dir = Path("slush_scraper_screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)
        self.email = os.getenv('SLUSH_EMAIL')
        self.password = os.getenv('SLUSH_PASSWORD')
        self.logged_in = False
    
    def setup_driver(self):
        """Initialize Remote WebDriver"""
        logger.info(f"Setting up {self.browser} via Selenium Grid...")
        
        if self.browser == "firefox":
            options = FirefoxOptions()
        else:
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        
        options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Remote(
                command_executor=self.selenium_url,
                options=options
            )
            logger.info(f"✅ Remote {self.browser} WebDriver initialized")
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            raise
        
        self.driver.implicitly_wait(5)
    
    def take_screenshot(self, name: str):
        """Take screenshot"""
        if self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"{timestamp}_{name}.png"
            self.driver.save_screenshot(str(filename))
            logger.debug(f"Screenshot: {filename}")
    
    def get_profiles_from_db(self) -> List[tuple]:
        """Get startup profiles from database"""
        conn = sqlite3.connect('startup_swiper.db')
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT id, company_name, profile_link 
            FROM startups 
            WHERE profile_link IS NOT NULL 
            AND profile_link LIKE '%platform.slush.org%'
            AND scraped_description IS NULL
            LIMIT {self.limit}
        """)
        
        profiles = cursor.fetchall()
        conn.close()
        
        logger.info(f"Found {len(profiles)} profiles to scrape")
        return profiles
    
    def scrape_profile(self, startup_id: int, company_name: str, profile_url: str) -> Dict[str, Any]:
        """Scrape a single profile"""
        logger.info(f"\n{'='*70}")
        logger.info(f"Scraping: [{startup_id}] {company_name}")
        logger.info(f"URL: {profile_url}")
        logger.info(f"{'='*70}")
        
        try:
            self.driver.get(profile_url)
            time.sleep(3)  # Wait for page load
            
            self.take_screenshot(f"profile_{startup_id}_{company_name[:20]}")
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract text content
            body = soup.find('body')
            if body:
                text_content = body.get_text(separator='\n', strip=True)
            else:
                text_content = soup.get_text(separator='\n', strip=True)
            
            # Look for specific content
            data = {
                'id': startup_id,
                'company_name': company_name,
                'profile_url': profile_url,
                'scraped_at': datetime.now().isoformat(),
                'page_title': soup.title.string if soup.title else None,
                'text_content': text_content[:2000],  # First 2000 chars
                'success': True
            }
            
            # Try to extract more specific fields
            try:
                # Look for description in common places
                description_divs = soup.find_all('div', class_=lambda x: x and 'description' in x.lower())
                if description_divs:
                    data['description'] = ' '.join([div.get_text() for div in description_divs[:3]])
            except:
                pass
            
            try:
                # Look for team/people section
                team_section = soup.find(lambda tag: tag.name and 'team' in tag.get_text().lower())
                if team_section:
                    data['team_section'] = team_section.get_text()[:500]
            except:
                pass
            
            try:
                # Look for social links
                links = soup.find_all('a')
                social_links = {}
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text()
                    
                    if 'linkedin' in href.lower():
                        social_links['linkedin'] = href
                    elif 'twitter' in href.lower() or 'x.com' in href.lower():
                        social_links['twitter'] = href
                    elif 'github' in href.lower():
                        social_links['github'] = href
                    elif 'facebook' in href.lower():
                        social_links['facebook'] = href
                
                if social_links:
                    data['social_links'] = social_links
            except:
                pass
            
            logger.info(f"✅ Successfully scraped {len(text_content)} characters of content")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error scraping profile: {e}")
            data = {
                'id': startup_id,
                'company_name': company_name,
                'profile_url': profile_url,
                'scraped_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
            return data
    
    def save_to_database(self, data: Dict[str, Any]):
        """Save scraped data to database"""
        conn = sqlite3.connect('startup_swiper.db')
        cursor = conn.cursor()
        
        try:
            # Update startup record
            cursor.execute("""
                UPDATE startups 
                SET scraped_description = ?,
                    last_scraped_at = ?,
                    scrape_success = ?,
                    social_links_json = ?
                WHERE id = ?
            """, (
                data.get('text_content'),
                data.get('scraped_at'),
                1 if data.get('success') else 0,
                json.dumps(data.get('social_links', {})),
                data['id']
            ))
            
            conn.commit()
            logger.info(f"✅ Saved to database")
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
        finally:
            conn.close()
    
    def run(self):
        """Main scraping loop"""
        logger.info("="*70)
        logger.info("SLUSH PROFILE DETAIL SCRAPER")
        logger.info("="*70)
        logger.info(f"Selenium URL: {self.selenium_url}")
        logger.info(f"Limit: {self.limit} profiles")
        
        try:
            self.setup_driver()
            
            # Get profiles to scrape
            profiles = self.get_profiles_from_db()
            
            if not profiles:
                logger.info("No profiles to scrape")
                return
            
            # Scrape each profile
            successful = 0
            failed = 0
            
            for startup_id, company_name, profile_url in profiles:
                data = self.scrape_profile(startup_id, company_name, profile_url)
                self.save_to_database(data)
                
                if data.get('success'):
                    successful += 1
                else:
                    failed += 1
                
                time.sleep(2)  # Rate limiting
            
            # Summary
            logger.info("\n" + "="*70)
            logger.info("SCRAPING SUMMARY")
            logger.info("="*70)
            logger.info(f"✅ Successful: {successful}")
            logger.info(f"❌ Failed: {failed}")
            logger.info(f"Total: {successful + failed}")
            
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Slush profile details')
    parser.add_argument('--selenium-url', default='http://localhost:4444', help='Selenium Grid URL')
    parser.add_argument('--browser', default='chrome', choices=['chrome', 'firefox'], help='Browser')
    parser.add_argument('--limit', type=int, default=10, help='Number of profiles to scrape')
    
    args = parser.parse_args()
    
    scraper = SlushProfileDetailScraper(
        selenium_url=args.selenium_url,
        browser=args.browser,
        limit=args.limit
    )
    
    try:
        scraper.run()
        return 0
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
