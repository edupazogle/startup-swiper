#!/usr/bin/env python3
"""
Slush Events Scraper V2 - Works with actual Slush page structure
Parses DOM elements directly instead of looking for direct URLs
"""

import os
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SlushEventsScraperV2:
    """Scrapes event data from Slush platform activities page"""
    
    def __init__(
        self,
        selenium_grid_url: str = "http://localhost:4444",
        screenshots: bool = False,
        output_dir: str = "slush_events_data"
    ):
        self.selenium_grid_url = selenium_grid_url
        self.screenshots = screenshots
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if screenshots:
            self.screenshots_dir = Path("slush_events_screenshots")
            self.screenshots_dir.mkdir(exist_ok=True)
        
        self.email = os.getenv("SLUSH_EMAIL")
        self.password = os.getenv("SLUSH_PASSWORD")
        
        self.driver = None
        self.events_data = []
    
    def setup_driver(self):
        """Initialize remote Selenium WebDriver"""
        try:
            logger.info(f"Connecting to Selenium Grid at {self.selenium_grid_url}...")
            
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Remote(
                command_executor=self.selenium_grid_url,
                options=options
            )
            
            self.driver.implicitly_wait(5)
            logger.info("✅ Connected to Selenium Grid")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Selenium Grid: {e}")
            raise
    
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
            email_input.clear()
            email_input.send_keys(self.email)
            logger.info(f"✅ Entered email")
            time.sleep(1)
            
            # Find password input
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
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
            time.sleep(5)
            self.take_screenshot("03_after_login")
            
            current_url = self.driver.current_url
            logger.info(f"Current URL after login: {current_url}")
            
            if "slush25" in current_url:
                logger.info("✅ Login successful!")
                return True
            else:
                logger.warning("⚠️  Login may have failed - unexpected URL")
                return False
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            self.take_screenshot("error_login")
            return False
    
    def scrape_events_from_browse_page(self, max_scrolls: int = 20) -> List[Dict]:
        """
        Scrape event data directly from browse page DOM elements
        """
        try:
            logger.info("="*70)
            logger.info("Navigating to activities browse page...")
            logger.info("="*70)
            
            self.driver.get("https://platform.slush.org/slush25/activities/browse")
            time.sleep(5)
            self.take_screenshot("04_browse_page_loaded")
            
            logger.info(f"Current URL: {self.driver.current_url}")
            logger.info(f"Page title: {self.driver.title}")
            
            # Wait for content to load
            logger.info("Waiting for event content to load...")
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Organized by')]"))
                )
                logger.info("✅ Event content detected on page")
            except TimeoutException:
                logger.error("❌ Timeout waiting for event content")
                return []
            
            # Activate day filters to see all events
            logger.info("Activating day filters...")
            try:
                # Click on "Advanced Filters" if not expanded
                try:
                    advanced_filters_btn = self.driver.find_element(
                        By.XPATH,
                        "//span[contains(@class, 'sc-jHSbPC') and text()='Advanced Filters']"
                    )
                    advanced_filters_btn.click()
                    time.sleep(1)
                    logger.info("✅ Opened Advanced Filters")
                except:
                    logger.info("Advanced Filters already open or not found")
                
                # Click "Day" accordion to expand it
                try:
                    day_accordion = self.driver.find_element(
                        By.XPATH,
                        "//button[.//span[text()='Day ']]"
                    )
                    # Check if it's closed (data-state="closed")
                    parent = day_accordion.find_element(By.XPATH, "..")
                    if parent.get_attribute("data-state") == "closed":
                        day_accordion.click()
                        time.sleep(1)
                        logger.info("✅ Expanded Day filter")
                except Exception as e:
                    logger.warning(f"Could not expand Day accordion: {e}")
                
                # Find and click day checkboxes
                day_checkboxes = self.driver.find_elements(
                    By.XPATH,
                    "//label[contains(@class, 'sc-jMsorb')]//input[@type='checkbox']"
                )
                
                checked_count = 0
                for idx, checkbox in enumerate(day_checkboxes):
                    try:
                        # Check if already checked
                        if not checkbox.is_selected():
                            # Click the parent label instead of the checkbox directly
                            parent_label = checkbox.find_element(By.XPATH, "../..")
                            self.driver.execute_script("arguments[0].click();", parent_label)
                            checked_count += 1
                            time.sleep(0.5)
                    except Exception as e:
                        logger.debug(f"Could not click checkbox {idx}: {e}")
                        continue
                
                if checked_count > 0:
                    logger.info(f"✅ Activated {checked_count} day filters")
                    time.sleep(2)  # Wait for content to reload
                else:
                    logger.info("Day filters already active or not found")
                
            except Exception as e:
                logger.warning(f"⚠️  Could not activate day filters: {e}")
                logger.info("Continuing with default filters...")
            
            # Click "view all" buttons to expand all event categories
            logger.info("Expanding all event categories...")
            try:
                # Find all "view all" buttons
                view_all_buttons = self.driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'gPjmmR')]//div[contains(@class, 'fkMFSM')]"
                )
                
                logger.info(f"Found {len(view_all_buttons)} 'view all' buttons")
                
                for idx, button in enumerate(view_all_buttons):
                    try:
                        # Scroll button into view
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # Click it
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(1)
                        logger.info(f"✅ Clicked 'view all' button {idx + 1}")
                    except Exception as e:
                        logger.debug(f"Could not click button {idx}: {e}")
                        continue
                
                # Wait for content to expand
                time.sleep(3)
                self.take_screenshot("05_categories_expanded")
                
            except Exception as e:
                logger.warning(f"⚠️  Could not expand categories: {e}")
            
            events_data = []
            seen_events = set()
            last_count = 0
            no_change_scrolls = 0
            
            logger.info("="*70)
            logger.info("Starting to collect event data...")
            logger.info("="*70)
            
            for scroll_num in range(max_scrolls):
                try:
                    # Find all event card containers - look for the specific clickable container with event details
                    # Pattern: div with class "fxipBD" that contains the organizer and title
                    event_containers = self.driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'fxipBD') and .//span[contains(@class, 'sc-gDGPri') and contains(text(), 'Organized by')]]"
                    )
                    
                    logger.info(f"\n[Scroll {scroll_num + 1}/{max_scrolls}] Found {len(event_containers)} event containers on page")
                    
                    for idx, container in enumerate(event_containers):
                        try:
                            # Extract organizer
                            organizer_elem = container.find_element(
                                By.XPATH,
                                ".//span[contains(@class, 'sc-gDGPri') and contains(text(), 'Organized by')]"
                            )
                            organizer = organizer_elem.text.replace("Organized by ", "").strip()
                            
                            # Extract title
                            title_elem = container.find_element(
                                By.XPATH,
                                ".//span[contains(@class, 'sc-gUYXyr')]"
                            )
                            title = title_elem.text.strip()
                            
                            # Create unique key
                            event_key = f"{title}|||{organizer}"
                            
                            # Skip if we've seen this event
                            if event_key in seen_events:
                                continue
                            
                            seen_events.add(event_key)
                            
                            # Extract datetime (first jxiMIY span)
                            datetime_str = ""
                            try:
                                datetime_elem = container.find_element(
                                    By.XPATH,
                                    ".//div[contains(@class, 'dtaHQV')]//span[contains(@class, 'jxiMIY')]"
                                )
                                datetime_str = datetime_elem.text.strip()
                            except:
                                pass
                            
                            # Extract location (second jxiMIY span)
                            location = ""
                            try:
                                location_elems = container.find_elements(
                                    By.XPATH,
                                    ".//div[contains(@class, 'dtaHQV')]//span[contains(@class, 'jxiMIY')]"
                                )
                                if len(location_elems) > 1:
                                    location = location_elems[1].text.strip()
                            except:
                                pass
                            
                            # Extract categories/tags - only from this specific event container
                            categories = []
                            try:
                                tag_container = container.find_element(
                                    By.XPATH,
                                    ".//div[contains(@class, 'jpeGDW')]"
                                )
                                tag_elems = tag_container.find_elements(
                                    By.XPATH,
                                    ".//span[contains(@class, 'gEnNDj')]"
                                )
                                categories = [tag.text.strip() for tag in tag_elems if tag.text.strip()]
                            except:
                                pass
                            
                            # Extract status badges - look in sibling container
                            status = []
                            try:
                                # Navigate to parent container to find status
                                card_parent = container.find_element(By.XPATH, "../..")
                                status_container = card_parent.find_element(
                                    By.XPATH,
                                    ".//div[contains(@class, 'sdiOz')]//div[contains(@class, 'dSaUeQ')]"
                                )
                                status_elems = status_container.find_elements(
                                    By.XPATH,
                                    ".//span[contains(@class, 'flPfqf')]"
                                )
                                status = [s.text.strip() for s in status_elems if s.text.strip()]
                            except:
                                pass
                            
                            # Create event data
                            event_data = {
                                "title": title,
                                "organizer": organizer,
                                "datetime": datetime_str,
                                "location": location,
                                "categories": categories,
                                "status": status,
                                "scraped_at": datetime.now().isoformat()
                            }
                            
                            events_data.append(event_data)
                            logger.info(f"  ✅ [{len(events_data)}] {title[:60]}... by {organizer[:30]}")
                            
                        except StaleElementReferenceException:
                            continue
                        except Exception as e:
                            logger.debug(f"  ⚠️  Error parsing container {idx}: {e}")
                            continue
                    
                    # Check progress
                    current_count = len(events_data)
                    if current_count == last_count:
                        no_change_scrolls += 1
                        if no_change_scrolls >= 5:
                            logger.info("\n⏹️  No new events found after 5 scrolls - stopping")
                            break
                    else:
                        no_change_scrolls = 0
                        last_count = current_count
                    
                    # Scroll down
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # Try scrolling specific content container
                    try:
                        scroll_container = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "div[class*='eDePCo'], div[id='view-container']"
                        )
                        self.driver.execute_script(
                            "arguments[0].scrollTop = arguments[0].scrollHeight",
                            scroll_container
                        )
                    except:
                        pass
                    
                except Exception as e:
                    logger.error(f"Error during scroll {scroll_num + 1}: {e}")
                    continue
            
            self.events_data = events_data
            
            logger.info("="*70)
            logger.info(f"✅ Collected {len(events_data)} unique events")
            logger.info("="*70)
            
            return events_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping browse page: {e}")
            self.take_screenshot("error_scraping")
            return []
    
    def save_events_json(self, filename: str = None):
        """Save events data to JSON file"""
        if not self.events_data:
            logger.warning("No events data to save")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"slush_events_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.events_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Saved {len(self.events_data)} events to {filepath}")
            
            # Print sample
            if self.events_data:
                logger.info("\nSample event:")
                logger.info(json.dumps(self.events_data[0], indent=2))
            
        except Exception as e:
            logger.error(f"❌ Error saving JSON: {e}")
    
    def cleanup(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape Slush events (V2 - works with actual page structure)")
    parser.add_argument("--grid-url", default="http://localhost:4444", help="Selenium Grid URL")
    parser.add_argument("--screenshots", action="store_true", help="Take screenshots during scraping")
    parser.add_argument("--max-scrolls", type=int, default=30, help="Maximum number of scrolls")
    parser.add_argument("--output", help="Output JSON filename")
    
    args = parser.parse_args()
    
    scraper = SlushEventsScraperV2(
        selenium_grid_url=args.grid_url,
        screenshots=args.screenshots
    )
    
    try:
        # Setup
        scraper.setup_driver()
        
        # Login
        if not scraper.login():
            logger.error("Failed to login - exiting")
            return
        
        # Scrape events
        events = scraper.scrape_events_from_browse_page(max_scrolls=args.max_scrolls)
        
        if events:
            scraper.save_events_json(args.output)
            logger.info(f"\n{'='*70}")
            logger.info(f"✅ Successfully scraped {len(events)} events!")
            logger.info(f"{'='*70}")
        else:
            logger.warning("No events were scraped")
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()
