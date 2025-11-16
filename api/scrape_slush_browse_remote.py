#!/usr/bin/env python3
"""
Slush Browse Page Scraper - Docker/Remote Selenium Version
Connects to Selenium Grid (standalone or hub)
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

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SlushBrowseScraperRemote:
    """Scrapes all startups from Slush browse page using remote Selenium"""
    
    def __init__(self, selenium_url: str, browser: str = "chrome", screenshots: bool = False):
        """
        Initialize scraper
        
        Args:
            selenium_url: URL to Selenium Grid (e.g., http://localhost:4444)
            browser: Browser to use ("chrome" or "firefox")
            screenshots: Save screenshots for debugging
        """
        self.selenium_url = selenium_url
        self.browser = browser.lower()
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
        """Initialize Remote WebDriver"""
        logger.info(f"Setting up {self.browser} via Selenium Grid at {self.selenium_url}...")
        
        if self.browser == "firefox":
            options = FirefoxOptions()
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("general.useragent.override", 
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
        else:
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        
        options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Remote(
                command_executor=self.selenium_url,
                options=options
            )
            logger.info(f"✅ Remote {self.browser} WebDriver initialized")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Selenium Grid: {e}")
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
                    
                    # Find and click submit button - try multiple selectors
                    submit_selectors = [
                        "button[type='submit']",
                        "button:contains('Log in')",
                        "button:contains('Sign in')",
                        "input[type='submit']",
                        "button[class*='login']",
                        "button[class*='submit']",
                        "button",  # Last resort - find any button
                    ]
                    
                    submit_clicked = False
                    for selector in submit_selectors:
                        try:
                            if selector == "button":
                                # For generic button, find all and click first visible
                                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                                for btn in buttons:
                                    if btn.is_displayed() and btn.is_enabled():
                                        btn.click()
                                        logger.info(f"✅ Clicked button: {btn.text[:50]}")
                                        submit_clicked = True
                                        break
                            else:
                                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if submit_button and submit_button.is_displayed():
                                    submit_button.click()
                                    logger.info(f"✅ Clicked login button using: {selector}")
                                    submit_clicked = True
                                    break
                        except:
                            continue
                    
                    if not submit_clicked:
                        # Try pressing Enter on password field
                        from selenium.webdriver.common.keys import Keys
                        password_input.send_keys(Keys.RETURN)
                        logger.info("✅ Pressed Enter on password field")
                    
                    # Wait for redirect
                    time.sleep(8)  # Increased wait time
                    self.take_screenshot("03_after_login")
                    
                    current_url = self.driver.current_url
                    logger.info(f"Current URL after login attempt: {current_url}")
                    
                    if "meeting-tool" in current_url or "browse" in current_url:
                        logger.info("✅ Login successful!")
                        self.logged_in = True
                        return True
                    elif "login" not in current_url and "sign" not in current_url and "auth" not in current_url:
                        logger.info("✅ Login appears successful")
                        self.logged_in = True
                        return True
                    else:
                        logger.warning(f"⚠️  Login may have failed - current URL: {current_url}")
                        # Save page source for debugging
                        with open("login_page_source.html", "w") as f:
                            f.write(self.driver.page_source)
                        logger.info("📄 Page source saved to login_page_source.html")
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
    
    parser = argparse.ArgumentParser(description='Scrape Slush browse page with Remote Selenium')
    parser.add_argument('--selenium-url', default='http://localhost:4444', help='Selenium Grid URL')
    parser.add_argument('--browser', default='chrome', choices=['chrome', 'firefox'], help='Browser to use')
    parser.add_argument('--screenshots', action='store_true', help='Save screenshots')
    parser.add_argument('--output', default='slush_profile_links.json', help='Output file')
    
    args = parser.parse_args()
    
    # Check for environment variable
    selenium_url = os.getenv('SELENIUM_HUB', args.selenium_url)
    
    logger.info("="*70)
    logger.info(f"SLUSH BROWSE PAGE SCRAPER (REMOTE {args.browser.upper()})")
    logger.info("="*70)
    logger.info(f"Selenium Grid: {selenium_url}")
    
    scraper = SlushBrowseScraperRemote(
        selenium_url=selenium_url,
        browser=args.browser,
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
