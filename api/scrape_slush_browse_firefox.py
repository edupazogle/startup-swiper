#!/usr/bin/env python3
"""
Slush Browse Page Scraper - Firefox Version
Uses Firefox instead of Chrome for better compatibility
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
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException
)
from webdriver_manager.firefox import GeckoDriverManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlushBrowseScraperFirefox:
    """Scrapes all startups from Slush browse page using Firefox"""
    
    def __init__(self, headless: bool = True, screenshots: bool = False):
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
        """Initialize Firefox WebDriver"""
        logger.info("Setting up Firefox WebDriver...")
        
        firefox_options = Options()
        
        if self.headless:
            firefox_options.add_argument("--headless")
        
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        
        # Set preferences to avoid detection
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference('useAutomationExtension', False)
        firefox_options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
        
        try:
            logger.info("Using webdriver-manager to setup GeckoDriver...")
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            logger.info("✅ Firefox WebDriver initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firefox: {e}")
            raise
        
        self.driver.implicitly_wait(5)
    
    def take_screenshot(self, name: str):
        """Take screenshot for debugging"""
        if self.screenshots and self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"{timestamp}_{name}.png"
            self.driver.save_screenshot(str(filename))
            logger.debug(f"Screenshot saved: {filename}")
    
    def login(self) -> bool:
        """Login to Slush platform"""
        if not self.email or not self.password:
            logger.warning("⚠️  No Slush credentials found")
            return False
        
        try:
            logger.info("Attempting to login to Slush platform...")
            
            self.driver.get("https://platform.slush.org/")
            time.sleep(3)
            self.take_screenshot("01_login_page")
            
            # Find email input
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
                    
                    # Wait for redirect
                    time.sleep(5)
                    self.take_screenshot("03_after_login")
                    
                    current_url = self.driver.current_url
                    
                    if "meeting-tool" in current_url or "browse" in current_url:
                        logger.info("✅ Login successful!")
                        self.logged_in = True
                        return True
                    elif "login" not in current_url:
                        logger.info("✅ Login appears successful")
                        self.logged_in = True
                        return True
                    else:
                        logger.warning("⚠️  Login may have failed")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Failed to login: {e}")
            self.take_screenshot("error_login")
            return False
    
    def scrape_browse_page(self) -> List[str]:
        """Scrape all profile links from browse page"""
        logger.info("="*70)
        logger.info("SCRAPING BROWSE PAGE FOR PROFILE LINKS")
        logger.info("="*70)
        
        if not self.logged_in:
            if not self.login():
                logger.error("❌ Cannot scrape without login")
                return []
        
        try:
            browse_url = "https://platform.slush.org/slush25/meeting-tool/browse"
            logger.info(f"Loading browse page: {browse_url}")
            self.driver.get(browse_url)
            time.sleep(5)
            self.take_screenshot("browse_page_loaded")
            
            profile_links = set()
            scroll_attempts = 0
            max_scrolls = 50
            
            last_count = 0
            no_change_count = 0
            
            logger.info("Starting to scroll and collect profile links...")
            
            while scroll_attempts < max_scrolls:
                # Find all links
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
                
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Try scrolling main content
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, "main, [role='main'], .content")
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_content)
                except:
                    pass
                
                scroll_attempts += 1
                
                if scroll_attempts % 10 == 0:
                    self.take_screenshot(f"browse_scroll_{scroll_attempts}")
            
            self.profile_links = sorted(list(profile_links))
            
            logger.info("="*70)
            logger.info(f"✅ Found {len(self.profile_links)} unique profile links")
            logger.info("="*70)
            
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
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Slush browse page with Firefox')
    parser.add_argument('--visible', action='store_true', help='Run browser in visible mode')
    parser.add_argument('--screenshots', action='store_true', help='Save screenshots')
    parser.add_argument('--output', default='slush_profile_links.json', help='Output file')
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("SLUSH BROWSE PAGE SCRAPER (FIREFOX)")
    logger.info("="*70)
    
    scraper = SlushBrowseScraperFirefox(
        headless=not args.visible,
        screenshots=args.screenshots
    )
    
    try:
        scraper.setup_driver()
        
        if not scraper.login():
            logger.error("❌ Login failed")
            return 1
        
        links = scraper.scrape_browse_page()
        
        if not links:
            logger.warning("⚠️  No profile links found")
            return 1
        
        scraper.save_links_to_file(args.output)
        
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
