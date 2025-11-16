#!/usr/bin/env python3
"""
Slush Platform Profile Scraper
Extracts detailed information from Slush startup detail pages using Selenium
Enriches database with data not available in the CSV export
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


class SlushProfileScraper:
    """Scrapes startup profiles from Slush platform"""
    
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
            
            # Look for login button or form
            try:
                # Try to find email input
                email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']", timeout=5)
                if not email_input:
                    email_input = self.wait_for_element(By.CSS_SELECTOR, "input[placeholder*='mail' i]", timeout=3)
                
                if email_input:
                    email_input.clear()
                    email_input.send_keys(self.email)
                    logger.info(f"✅ Entered email: {self.email}")
                    time.sleep(1)
                    
                    # Find password input
                    password_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']", timeout=5)
                    if password_input:
                        password_input.clear()
                        password_input.send_keys(self.password)
                        logger.info("✅ Entered password")
                        time.sleep(1)
                        
                        self.take_screenshot("02_credentials_entered")
                        
                        # Find and click submit button
                        submit_selectors = [
                            "button[type='submit']",
                            "button:contains('Log in')",
                            "button:contains('Sign in')",
                            "input[type='submit']",
                            "button[class*='login']",
                            "button[class*='submit']"
                        ]
                        
                        for selector in submit_selectors:
                            try:
                                submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if submit_button and submit_button.is_displayed():
                                    submit_button.click()
                                    logger.info("✅ Clicked login button")
                                    break
                            except:
                                continue
                        
                        # Wait for redirect after login
                        time.sleep(5)
                        self.take_screenshot("03_after_login")
                        
                        # Check if login was successful
                        current_url = self.driver.current_url
                        page_text = self.driver.page_source.lower()
                        
                        if "meeting-tool" in current_url or "browse" in current_url:
                            logger.info("✅ Login successful!")
                            self.logged_in = True
                            return True
                        elif "login" not in current_url and "sign" not in current_url:
                            logger.info("✅ Login appears successful (redirected from login page)")
                            self.logged_in = True
                            return True
                        else:
                            logger.warning("⚠️  Login may have failed - still on login page")
                            return False
                else:
                    logger.warning("⚠️  Could not find email input field")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error during login process: {e}")
                self.take_screenshot("error_login")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to access login page: {e}")
            return False
    
    def take_screenshot(self, name: str):
        """Take screenshot for debugging"""
        if self.screenshots and self.driver:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshots_dir / f"{timestamp}_{name}.png"
            self.driver.save_screenshot(str(filename))
            logger.debug(f"Screenshot saved: {filename}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = None) -> Optional[Any]:
        """Wait for element to be present"""
        timeout = timeout or self.wait_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.debug(f"Timeout waiting for element: {by}={value}")
            return None
    
    def safe_get_text(self, element, default: str = "") -> str:
        """Safely extract text from element"""
        try:
            text = element.text.strip() if element else default
            return text if text else default
        except (StaleElementReferenceException, Exception):
            return default
    
    def safe_get_attribute(self, element, attr: str, default: str = "") -> str:
        """Safely extract attribute from element"""
        try:
            value = element.get_attribute(attr) if element else default
            return value if value else default
        except (StaleElementReferenceException, Exception):
            return default
    
    def scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Scrape a single Slush startup profile page
        
        Args:
            profile_url: Full URL to the startup profile
            
        Returns:
            Dictionary with scraped data
        """
        logger.info(f"Scraping: {profile_url}")
        
        try:
            # Ensure we're logged in before scraping
            if not self.logged_in:
                logger.info("Not logged in yet, attempting login...")
                if not self.login():
                    logger.warning("⚠️  Proceeding without login - data may be limited")
            
            self.driver.get(profile_url)
            time.sleep(3)  # Wait for page load
            self.take_screenshot("profile_loaded")
            
            # Initialize data dictionary
            data = {
                'profile_url': profile_url,
                'scraped_at': datetime.now().isoformat(),
                'success': False
            }
            
            # Extract company name
            try:
                name_selectors = [
                    "h1",
                    "[class*='company-name']",
                    "[class*='startup-name']",
                    "[data-testid='company-name']"
                ]
                for selector in name_selectors:
                    try:
                        name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if name_elem:
                            data['company_name'] = self.safe_get_text(name_elem)
                            break
                    except NoSuchElementException:
                        continue
            except Exception as e:
                logger.debug(f"Error extracting company name: {e}")
            
            # Extract description/pitch
            try:
                desc_selectors = [
                    "[class*='description']",
                    "[class*='pitch']",
                    "[class*='about']",
                    "p[class*='text']",
                ]
                descriptions = []
                for selector in desc_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements[:3]:  # Get first 3 paragraphs
                            text = self.safe_get_text(elem)
                            if text and len(text) > 20:
                                descriptions.append(text)
                    except NoSuchElementException:
                        continue
                
                if descriptions:
                    data['full_description'] = "\n\n".join(descriptions)
            except Exception as e:
                logger.debug(f"Error extracting description: {e}")
            
            # Extract team members
            try:
                team_members = []
                team_selectors = [
                    "[class*='team-member']",
                    "[class*='founder']",
                    "[class*='person']",
                ]
                for selector in team_selectors:
                    try:
                        members = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for member in members:
                            member_data = {
                                'name': '',
                                'role': '',
                                'linkedin': ''
                            }
                            
                            # Try to extract name
                            try:
                                name_elem = member.find_element(By.CSS_SELECTOR, "[class*='name'], h2, h3, strong")
                                member_data['name'] = self.safe_get_text(name_elem)
                            except:
                                pass
                            
                            # Try to extract role
                            try:
                                role_elem = member.find_element(By.CSS_SELECTOR, "[class*='role'], [class*='title'], span, p")
                                member_data['role'] = self.safe_get_text(role_elem)
                            except:
                                pass
                            
                            # Try to extract LinkedIn
                            try:
                                linkedin_elem = member.find_element(By.CSS_SELECTOR, "a[href*='linkedin.com']")
                                member_data['linkedin'] = self.safe_get_attribute(linkedin_elem, 'href')
                            except:
                                pass
                            
                            if member_data['name']:
                                team_members.append(member_data)
                        
                        if team_members:
                            break
                    except NoSuchElementException:
                        continue
                
                if team_members:
                    data['team_members'] = team_members
            except Exception as e:
                logger.debug(f"Error extracting team: {e}")
            
            # Extract social media links
            try:
                social_links = {}
                link_elements = self.driver.find_elements(By.TAG_NAME, "a")
                
                for link in link_elements:
                    href = self.safe_get_attribute(link, 'href')
                    if not href:
                        continue
                    
                    if 'linkedin.com/company' in href and 'linkedin' not in social_links:
                        social_links['linkedin'] = href
                    elif 'twitter.com' in href or 'x.com' in href:
                        social_links['twitter'] = href
                    elif 'facebook.com' in href:
                        social_links['facebook'] = href
                    elif 'instagram.com' in href:
                        social_links['instagram'] = href
                    elif 'github.com' in href:
                        social_links['github'] = href
                
                if social_links:
                    data['social_links'] = social_links
            except Exception as e:
                logger.debug(f"Error extracting social links: {e}")
            
            # Extract tags/industries
            try:
                tags = []
                tag_selectors = [
                    "[class*='tag']",
                    "[class*='badge']",
                    "[class*='label']",
                    "[class*='category']",
                    "[class*='industry']",
                ]
                for selector in tag_selectors:
                    try:
                        tag_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for tag in tag_elements:
                            tag_text = self.safe_get_text(tag)
                            if tag_text and len(tag_text) < 50 and tag_text not in tags:
                                tags.append(tag_text)
                    except NoSuchElementException:
                        continue
                
                if tags:
                    data['additional_tags'] = tags
            except Exception as e:
                logger.debug(f"Error extracting tags: {e}")
            
            # Extract funding information if visible
            try:
                funding_keywords = ['funding', 'raised', 'investment', 'round', 'valuation']
                text_elements = self.driver.find_elements(By.CSS_SELECTOR, "p, div, span")
                
                for elem in text_elements:
                    text = self.safe_get_text(elem).lower()
                    if any(keyword in text for keyword in funding_keywords):
                        if 'funding_info' not in data:
                            data['funding_info'] = []
                        data['funding_info'].append(self.safe_get_text(elem))
            except Exception as e:
                logger.debug(f"Error extracting funding info: {e}")
            
            # Extract contact/website info
            try:
                website_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "a[href^='http']:not([href*='slush.org']):not([href*='linkedin']):not([href*='twitter']):not([href*='facebook'])"
                )
                websites = []
                for elem in website_elements[:3]:
                    href = self.safe_get_attribute(elem, 'href')
                    if href and href not in websites:
                        websites.append(href)
                
                if websites:
                    data['additional_websites'] = websites
            except Exception as e:
                logger.debug(f"Error extracting websites: {e}")
            
            # Mark as successful if we got at least some data
            data['success'] = bool(data.get('company_name') or data.get('full_description'))
            
            if data['success']:
                logger.info(f"✅ Successfully scraped: {data.get('company_name', 'Unknown')}")
            else:
                logger.warning(f"⚠️  Limited data extracted from {profile_url}")
            
            self.take_screenshot("profile_scraped")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error scraping {profile_url}: {e}")
            self.take_screenshot("error")
            return {
                'profile_url': profile_url,
                'scraped_at': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def get_profiles_from_db(db_path: str = "startup_swiper.db", limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get startup profiles from database that have Slush profile links
    
    Args:
        db_path: Path to SQLite database
        limit: Maximum number of profiles to fetch
        
    Returns:
        List of dictionaries with id, company_name, and profile_link
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT id, company_name, website, profile_link
        FROM startups
        WHERE profile_link IS NOT NULL 
        AND profile_link LIKE '%platform.slush.org%'
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    profiles = []
    for row in rows:
        profiles.append({
            'id': row[0],
            'company_name': row[1],
            'website': row[2],
            'profile_link': row[3]
        })
    
    return profiles


def update_database(db_path: str, startup_id: int, scraped_data: Dict[str, Any]):
    """
    Update database with scraped data
    
    Args:
        db_path: Path to SQLite database
        startup_id: Startup ID to update
        scraped_data: Dictionary with scraped data
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Prepare update fields
    updates = {}
    
    # Update description if we got a fuller one
    if scraped_data.get('full_description'):
        updates['scraped_description'] = scraped_data['full_description']
    
    # Store team members as JSON
    if scraped_data.get('team_members'):
        updates['team_members_json'] = json.dumps(scraped_data['team_members'])
    
    # Store social links as JSON
    if scraped_data.get('social_links'):
        updates['social_links_json'] = json.dumps(scraped_data['social_links'])
    
    # Store additional tags
    if scraped_data.get('additional_tags'):
        updates['additional_tags_json'] = json.dumps(scraped_data['additional_tags'])
    
    # Store funding info
    if scraped_data.get('funding_info'):
        updates['funding_info_json'] = json.dumps(scraped_data['funding_info'])
    
    # Mark as scraped
    updates['last_scraped_at'] = scraped_data['scraped_at']
    updates['scrape_success'] = 1 if scraped_data['success'] else 0
    
    if updates:
        # Add columns if they don't exist (for first run)
        for column in updates.keys():
            try:
                cursor.execute(f"ALTER TABLE startups ADD COLUMN {column} TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
        
        # Build UPDATE query
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [startup_id]
        
        cursor.execute(
            f"UPDATE startups SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()
    
    conn.close()


def scrape_slush_profiles(
    db_path: str = "startup_swiper.db",
    limit: Optional[int] = None,
    headless: bool = True,
    screenshots: bool = False,
    delay: float = 2.0
) -> Dict[str, Any]:
    """
    Scrape Slush profiles and update database
    
    Args:
        db_path: Path to SQLite database
        limit: Maximum number of profiles to scrape
        headless: Run browser in headless mode
        screenshots: Save screenshots for debugging
        delay: Delay between requests in seconds
        
    Returns:
        Summary dictionary
    """
    logger.info("="*70)
    logger.info("SLUSH PROFILE SCRAPER")
    logger.info("="*70)
    
    # Get profiles from database
    profiles = get_profiles_from_db(db_path, limit)
    logger.info(f"Found {len(profiles)} profiles to scrape")
    
    if not profiles:
        logger.warning("No profiles found with Slush profile links")
        return {'total': 0, 'success': 0, 'failed': 0}
    
    # Initialize scraper
    scraper = SlushProfileScraper(headless=headless, screenshots=screenshots)
    scraper.setup_driver()
    
    # Scrape profiles
    results = {
        'total': len(profiles),
        'success': 0,
        'failed': 0,
        'scraped_data': []
    }
    
    try:
        for i, profile in enumerate(profiles, 1):
            logger.info(f"\n[{i}/{len(profiles)}] Processing: {profile['company_name']}")
            
            # Scrape profile
            scraped_data = scraper.scrape_profile(profile['profile_link'])
            
            # Update database
            try:
                update_database(db_path, profile['id'], scraped_data)
                logger.info(f"✅ Database updated for ID {profile['id']}")
            except Exception as e:
                logger.error(f"❌ Failed to update database: {e}")
            
            # Track results
            if scraped_data['success']:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['scraped_data'].append({
                'id': profile['id'],
                'company_name': profile['company_name'],
                'success': scraped_data['success'],
                'fields_extracted': len([k for k in scraped_data.keys() if k not in ['profile_url', 'scraped_at', 'success', 'error']])
            })
            
            # Rate limiting
            if i < len(profiles):
                time.sleep(delay)
    
    finally:
        scraper.close()
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("SCRAPING SUMMARY")
    logger.info("="*70)
    logger.info(f"Total profiles: {results['total']}")
    logger.info(f"Successfully scraped: {results['success']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Success rate: {100*results['success']/results['total']:.1f}%")
    
    return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Scrape Slush startup profiles and enrich database'
    )
    parser.add_argument(
        '--db',
        default='startup_swiper.db',
        help='Path to SQLite database'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of profiles to scrape'
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
        '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: scrape only 1 profile with screenshots'
    )
    
    args = parser.parse_args()
    
    # Test mode
    if args.test:
        args.limit = 1
        args.screenshots = True
        args.visible = True
        logger.info("🧪 Running in TEST mode")
    
    # Run scraper
    results = scrape_slush_profiles(
        db_path=args.db,
        limit=args.limit,
        headless=not args.visible,
        screenshots=args.screenshots,
        delay=args.delay
    )
    
    # Save results
    output_file = f"slush_scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\n✅ Results saved to: {output_file}")
    
    return 0 if results['success'] > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
