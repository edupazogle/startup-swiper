#!/usr/bin/env python3
"""
Slush Browse Page Scraper
Extracts all startup profile links from the browse page
Then scrapes individual profiles
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlushBrowseScraper:
    """Scrapes all startups from Slush browse page"""
    
    def __init__(self, headless: bool = True, screenshots: bool = False):
        """
        Initialize scraper
        
        Args:
            headless: Run browser in headless mode
            screenshots: Save screenshots for debugging
        """
        self.headless = headless
        self.screenshots = screenshots
        self.driver = None
        self.screenshots_dir = Path("slush_scraper_screenshots")
        self.wait_timeout = 10
        self.logged_in = False
        self.profile_links = []
        
        # Load credentials from environment
        self.email = os.getenv('SLUSH_EMAIL')
        self.password = os.getenv('SLUSH_PASSWORD')
        
        if screenshots:
            self.screenshots_dir.mkdir(exist_ok=True)
    
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to avoid bot detection
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        try:
            # Try to use webdriver-manager to auto-install ChromeDriver
            logger.info("Using webdriver-manager to setup ChromeDriver...")
            service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized with webdriver-manager")
        except Exception as e:
            logger.warning(f"webdriver-manager failed: {e}, trying default Chrome...")
            # Fallback to default Chrome
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized with default driver")
        
        self.driver.implicitly_wait(5)
    
    def take_screenshot(self, name: str):
        """Take screenshot for debugging"""
        if self.screenshots and self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"{timestamp}_{name}.png"
            self.driver.save_screenshot(str(filename))
            logger.debug(f"Screenshot saved: {filename}")
    
    def login(self) -> bool:
        """
        Login to Slush platform
        
        Returns:
            True if login successful, False otherwise
        """
        if not self.email or not self.password:
            logger.warning("⚠️  No Slush credentials found in environment variables")
            return False
        
        try:
            logger.info("Attempting to login to Slush platform...")
            
            # Go to login page
            self.driver.get("https://platform.slush.org/")
            time.sleep(3)
            self.take_screenshot("01_login_page")
            
            # Try to find email input
            email_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
            if email_input:
                email_input.clear()
                email_input.send_keys(self.email)
                logger.info(f"✅ Entered email: {self.email}")
                time.sleep(1)
                
                # Find password input
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
                if password_input:
                    password_input.clear()
                    password_input.send_keys(self.password)
                    logger.info("✅ Entered password")
                    time.sleep(1)
                    
                    self.take_screenshot("02_credentials_entered")
                    
                    # Find and click submit button
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    if submit_button:
                        submit_button.click()
                        logger.info("✅ Clicked login button")
                    
                    # Wait for redirect after login
                    time.sleep(5)
                    self.take_screenshot("03_after_login")
                    
                    # Check if login was successful
                    current_url = self.driver.current_url
                    
                    if "meeting-tool" in current_url or "browse" in current_url:
                        logger.info("✅ Login successful!")
                        self.logged_in = True
                        return True
                    elif "login" not in current_url:
                        logger.info("✅ Login appears successful (redirected from login page)")
                        self.logged_in = True
                        return True
                    else:
                        logger.warning("⚠️  Login may have failed - still on login page")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Failed to login: {e}")
            self.take_screenshot("error_login")
            return False
    
    def scrape_browse_page(self) -> List[str]:
        """
        Scrape all profile links from the browse page
        
        Returns:
            List of profile URLs
        """
        logger.info("="*70)
        logger.info("SCRAPING BROWSE PAGE FOR PROFILE LINKS")
        logger.info("="*70)
        
        # Ensure we're logged in
        if not self.logged_in:
            if not self.login():
                logger.error("❌ Cannot scrape without login")
                return []
        
        try:
            # Go to browse page
            browse_url = "https://platform.slush.org/slush25/meeting-tool/browse"
            logger.info(f"Loading browse page: {browse_url}")
            self.driver.get(browse_url)
            time.sleep(5)
            self.take_screenshot("browse_page_loaded")
            
            profile_links = set()
            scroll_attempts = 0
            max_scrolls = 50  # Limit scrolling attempts
            
            last_count = 0
            no_change_count = 0
            
            logger.info("Starting to scroll and collect profile links...")
            
            while scroll_attempts < max_scrolls:
                # Find all links on current page
                links = self.driver.find_elements(By.TAG_NAME, "a")
                
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if href and "/browse/companies/" in href:
                            profile_links.add(href)
                    except StaleElementReferenceException:
                        continue
                
                current_count = len(profile_links)
                
                if current_count > last_count:
                    logger.info(f"Found {current_count} profile links so far...")
                    last_count = current_count
                    no_change_count = 0
                else:
                    no_change_count += 1
                    if no_change_count >= 5:
                        logger.info("No new links found after 5 scrolls, stopping...")
                        break
                
                # Scroll down to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Also try scrolling the main content area if it exists
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, "main, [role='main'], .content")
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_content)
                except:
                    pass
                
                scroll_attempts += 1
                
                # Periodic screenshot
                if scroll_attempts % 10 == 0:
                    self.take_screenshot(f"browse_scroll_{scroll_attempts}")
            
            self.profile_links = sorted(list(profile_links))
            
            logger.info("="*70)
            logger.info(f"✅ Found {len(self.profile_links)} unique profile links")
            logger.info("="*70)
            
            # Show first few links
            if self.profile_links:
                logger.info("Sample links:")
                for link in self.profile_links[:5]:
                    logger.info(f"  - {link}")
            
            return self.profile_links
            
        except Exception as e:
            logger.error(f"❌ Error scraping browse page: {e}")
            self.take_screenshot("error_browse")
            import traceback
            traceback.print_exc()
            return []
    
    def save_links_to_file(self, filename: str = "slush_profile_links.json"):
        """Save profile links to JSON file"""
        data = {
            "scraped_at": datetime.now().isoformat(),
            "total_links": len(self.profile_links),
            "links": self.profile_links
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"✅ Profile links saved to: {filename}")
    
    def update_database_with_links(self, db_path: str = "startup_swiper.db"):
        """
        Update database with discovered profile links
        Creates or updates startups table with profile links
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if we need to create or update
            updates = 0
            inserts = 0
            
            for link in self.profile_links:
                # Extract company ID from URL
                company_id = link.split("/")[-1]
                
                # Check if this profile link already exists
                cursor.execute(
                    "SELECT id FROM startups WHERE profile_link = ?",
                    (link,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    updates += 1
                else:
                    # Insert new record with minimal info
                    cursor.execute(
                        """
                        INSERT INTO startups (profile_link, discovered_at, company_name)
                        VALUES (?, ?, ?)
                        """,
                        (link, datetime.now().isoformat(), f"Company_{company_id[:8]}")
                    )
                    inserts += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Database updated: {updates} existing, {inserts} new")
            
        except Exception as e:
            logger.error(f"❌ Failed to update database: {e}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape all profile links from Slush browse page'
    )
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Run browser in visible mode (not headless)'
    )
    parser.add_argument(
        '--screenshots',
        action='store_true',
        help='Save screenshots for debugging'
    )
    parser.add_argument(
        '--output',
        default='slush_profile_links.json',
        help='Output file for profile links'
    )
    parser.add_argument(
        '--db',
        default='startup_swiper.db',
        help='Database path to update'
    )
    parser.add_argument(
        '--no-db-update',
        action='store_true',
        help='Skip database update'
    )
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("SLUSH BROWSE PAGE SCRAPER")
    logger.info("="*70)
    
    scraper = SlushBrowseScraper(
        headless=not args.visible,
        screenshots=args.screenshots
    )
    
    try:
        # Setup driver
        scraper.setup_driver()
        
        # Login
        if not scraper.login():
            logger.error("❌ Login failed")
            return 1
        
        # Scrape browse page
        links = scraper.scrape_browse_page()
        
        if not links:
            logger.warning("⚠️  No profile links found")
            return 1
        
        # Save links to file
        scraper.save_links_to_file(args.output)
        
        # Update database
        if not args.no_db_update:
            scraper.update_database_with_links(args.db)
        
        logger.info("\n" + "="*70)
        logger.info("✅ SCRAPING COMPLETE")
        logger.info("="*70)
        logger.info(f"Total profile links: {len(links)}")
        logger.info(f"Output file: {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        scraper.close()


if __name__ == '__main__':
    sys.exit(main())
