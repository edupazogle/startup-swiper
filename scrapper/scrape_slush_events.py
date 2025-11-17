#!/usr/bin/env python3
"""
Slush Events Scraper - Scrapes activities/events from Slush platform
Extracts event details from browse page and individual event pages
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


class SlushEventsScraperRemote:
    """Scrapes all events/activities from Slush platform using remote Selenium"""
    
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
        self.screenshots_dir = Path("slush_events_screenshots")
        self.wait_timeout = 10
        self.logged_in = False
        self.event_links = []
        self.events_data = []
        
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
            logger.warning("⚠️  No Slush credentials found in .env file")
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
                    
                    # Submit the form
                    from selenium.webdriver.common.keys import Keys
                    password_input.send_keys(Keys.RETURN)
                    logger.info("✅ Submitted login form")
                    
                    # Wait for redirect
                    time.sleep(8)
                    self.take_screenshot("03_after_login")
                    
                    current_url = self.driver.current_url
                    logger.info(f"Current URL after login: {current_url}")
                    
                    if "activities" in current_url or "browse" in current_url or "slush25" in current_url:
                        logger.info("✅ Login successful!")
                        self.logged_in = True
                        return True
                    elif "login" not in current_url and "sign" not in current_url:
                        logger.info("✅ Login appears successful")
                        self.logged_in = True
                        return True
                    else:
                        logger.warning(f"⚠️  Login may have failed - URL: {current_url}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Failed to login: {e}")
            self.take_screenshot("error_login")
            return False
    
    def scrape_events_browse_page(self) -> List[str]:
        """Scrape all event links from activities browse page"""
        logger.info("="*70)
        logger.info("SCRAPING EVENTS BROWSE PAGE FOR EVENT LINKS")
        logger.info("="*70)
        
        if not self.logged_in:
            if not self.login():
                logger.error("❌ Cannot scrape without login")
                return []
        
        try:
            browse_url = "https://platform.slush.org/slush25/activities/browse"
            logger.info(f"Loading events browse page: {browse_url}")
            self.driver.get(browse_url)
            time.sleep(5)
            self.take_screenshot("events_browse_page_loaded")
            
            event_links = set()
            scroll_attempts = 0
            max_scrolls = 50
            
            last_count = 0
            no_change_count = 0
            
            logger.info("Starting to scroll and collect event links...")
            
            while scroll_attempts < max_scrolls:
                # Find all links that match event pattern
                links = self.driver.find_elements(By.TAG_NAME, "a")
                
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        # Match pattern: /slush25/activities/{uuid}
                        if href and "/slush25/activities/" in href and len(href.split('/')[-1]) > 20:
                            event_links.add(href)
                    except StaleElementReferenceException:
                        continue
                
                current_count = len(event_links)
                
                if current_count > last_count:
                    logger.info(f"Found {current_count} event links so far...")
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
                
                # Try scrolling main content area
                try:
                    main_content = self.driver.find_element(By.CSS_SELECTOR, "main, [role='main'], .content, div[class*='scroll']")
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", main_content)
                except:
                    pass
                
                scroll_attempts += 1
                
                if scroll_attempts % 10 == 0:
                    self.take_screenshot(f"events_browse_scroll_{scroll_attempts}")
            
            self.event_links = sorted(list(event_links))
            
            logger.info("="*70)
            logger.info(f"✅ Found {len(self.event_links)} unique event links")
            logger.info("="*70)
            
            if self.event_links:
                logger.info("Sample links:")
                for link in self.event_links[:5]:
                    logger.info(f"  - {link}")
            
            return self.event_links
            
        except Exception as e:
            logger.error(f"❌ Error scraping events browse page: {e}")
            self.take_screenshot("error_events_browse")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_event_details(self, event_url: str) -> Optional[Dict[str, Any]]:
        """Scrape details from a single event page"""
        try:
            logger.info(f"Scraping event: {event_url}")
            self.driver.get(event_url)
            time.sleep(3)
            
            event_data = {
                "url": event_url,
                "event_id": event_url.split('/')[-1],
                "scraped_at": datetime.now().isoformat()
            }
            
            # Extract event title
            try:
                title_selectors = [
                    "h1",
                    "[class*='title']",
                    "[class*='heading']",
                    "[class*='event-name']"
                ]
                for selector in title_selectors:
                    try:
                        title = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if title and title.text.strip():
                            event_data["title"] = title.text.strip()
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Could not find title: {e}")
            
            # Extract event description
            try:
                desc_selectors = [
                    "[class*='description']",
                    "[class*='about']",
                    "[class*='details']",
                    "p"
                ]
                for selector in desc_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        descriptions = []
                        for elem in elements[:3]:  # Get first 3 paragraphs
                            text = elem.text.strip()
                            if text and len(text) > 20:
                                descriptions.append(text)
                        if descriptions:
                            event_data["description"] = "\n".join(descriptions)
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Could not find description: {e}")
            
            # Extract date/time
            try:
                time_selectors = [
                    "[class*='time']",
                    "[class*='date']",
                    "[class*='when']",
                    "[class*='schedule']"
                ]
                for selector in time_selectors:
                    try:
                        time_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if time_elem and time_elem.text.strip():
                            event_data["datetime"] = time_elem.text.strip()
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Could not find datetime: {e}")
            
            # Extract location/venue
            try:
                location_selectors = [
                    "[class*='location']",
                    "[class*='venue']",
                    "[class*='place']",
                    "[class*='where']"
                ]
                for selector in location_selectors:
                    try:
                        location = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if location and location.text.strip():
                            event_data["location"] = location.text.strip()
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Could not find location: {e}")
            
            # Extract event type/category
            try:
                category_selectors = [
                    "[class*='category']",
                    "[class*='type']",
                    "[class*='tag']",
                    "span[class*='badge']"
                ]
                categories = []
                for selector in category_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) < 50:
                                categories.append(text)
                    except:
                        continue
                if categories:
                    event_data["categories"] = categories
            except Exception as e:
                logger.debug(f"Could not find categories: {e}")
            
            # Extract speakers/hosts
            try:
                speaker_selectors = [
                    "[class*='speaker']",
                    "[class*='host']",
                    "[class*='organizer']",
                    "[class*='presenter']"
                ]
                speakers = []
                for selector in speaker_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 2:
                                speakers.append(text)
                    except:
                        continue
                if speakers:
                    event_data["speakers"] = speakers
            except Exception as e:
                logger.debug(f"Could not find speakers: {e}")
            
            # Extract capacity/attendees info
            try:
                capacity_selectors = [
                    "[class*='capacity']",
                    "[class*='attendee']",
                    "[class*='participant']",
                    "[class*='spots']"
                ]
                for selector in capacity_selectors:
                    try:
                        capacity = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if capacity and capacity.text.strip():
                            event_data["capacity_info"] = capacity.text.strip()
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Could not find capacity: {e}")
            
            # Get all text content as fallback
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                event_data["full_text"] = page_text[:5000]  # First 5000 chars
            except:
                pass
            
            logger.info(f"✅ Scraped event: {event_data.get('title', 'Unknown')}")
            return event_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping event {event_url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scrape_all_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape details for all events"""
        logger.info("="*70)
        logger.info("SCRAPING ALL EVENT DETAILS")
        logger.info("="*70)
        
        if not self.event_links:
            logger.error("No event links to scrape. Run scrape_events_browse_page() first.")
            return []
        
        events_to_scrape = self.event_links[:limit] if limit else self.event_links
        
        logger.info(f"Scraping {len(events_to_scrape)} events...")
        
        for idx, event_url in enumerate(events_to_scrape, 1):
            logger.info(f"\n[{idx}/{len(events_to_scrape)}] Processing event...")
            
            event_data = self.scrape_event_details(event_url)
            if event_data:
                self.events_data.append(event_data)
            
            # Be nice to the server
            time.sleep(2)
        
        logger.info("="*70)
        logger.info(f"✅ Scraped {len(self.events_data)} events successfully")
        logger.info("="*70)
        
        return self.events_data
    
    def save_to_json(self, filename: str = "slush_events.json"):
        """Save events data to JSON file"""
        output_data = {
            "scraped_at": datetime.now().isoformat(),
            "total_events": len(self.events_data),
            "events": self.events_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Events data saved to: {filename}")
    
    def save_to_database(self, db_path: str = "slush_events.db"):
        """Save events data to SQLite database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    url TEXT,
                    title TEXT,
                    description TEXT,
                    datetime TEXT,
                    location TEXT,
                    categories TEXT,
                    speakers TEXT,
                    capacity_info TEXT,
                    full_text TEXT,
                    scraped_at TEXT
                )
            ''')
            
            # Insert events
            for event in self.events_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO events 
                    (event_id, url, title, description, datetime, location, categories, speakers, capacity_info, full_text, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.get('event_id'),
                    event.get('url'),
                    event.get('title'),
                    event.get('description'),
                    event.get('datetime'),
                    event.get('location'),
                    json.dumps(event.get('categories', [])),
                    json.dumps(event.get('speakers', [])),
                    event.get('capacity_info'),
                    event.get('full_text'),
                    event.get('scraped_at')
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Events data saved to database: {db_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {e}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Slush events/activities with Remote Selenium')
    parser.add_argument('--selenium-url', default='http://localhost:4444', help='Selenium Grid URL')
    parser.add_argument('--browser', default='chrome', choices=['chrome', 'firefox'], help='Browser to use')
    parser.add_argument('--screenshots', action='store_true', help='Save screenshots')
    parser.add_argument('--limit', type=int, help='Limit number of events to scrape')
    parser.add_argument('--json-output', default='slush_events.json', help='JSON output file')
    parser.add_argument('--db-output', default='slush_events.db', help='SQLite database output file')
    
    args = parser.parse_args()
    
    # Check for environment variable
    selenium_url = os.getenv('SELENIUM_HUB', args.selenium_url)
    
    logger.info("="*70)
    logger.info(f"SLUSH EVENTS SCRAPER (REMOTE {args.browser.upper()})")
    logger.info("="*70)
    logger.info(f"Selenium Grid: {selenium_url}")
    
    scraper = SlushEventsScraperRemote(
        selenium_url=selenium_url,
        browser=args.browser,
        screenshots=args.screenshots
    )
    
    try:
        scraper.setup_driver()
        
        if not scraper.login():
            logger.error("❌ Login failed - cannot proceed")
            return 1
        
        # Step 1: Scrape browse page for event links
        event_links = scraper.scrape_events_browse_page()
        
        if not event_links:
            logger.warning("⚠️  No event links found")
            return 1
        
        # Step 2: Scrape details for each event
        events = scraper.scrape_all_events(limit=args.limit)
        
        if not events:
            logger.warning("⚠️  No event data scraped")
            return 1
        
        # Step 3: Save to JSON
        scraper.save_to_json(args.json_output)
        
        # Step 4: Save to database
        scraper.save_to_database(args.db_output)
        
        logger.info("\n" + "="*70)
        logger.info("✅ SCRAPING COMPLETE")
        logger.info("="*70)
        logger.info(f"Total events scraped: {len(events)}")
        logger.info(f"JSON output: {args.json_output}")
        logger.info(f"Database output: {args.db_output}")
        
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
