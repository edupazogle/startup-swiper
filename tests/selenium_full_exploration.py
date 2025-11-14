#!/usr/bin/env python3
"""
Selenium Web Automation Script with Login for Startup Swiper
Includes authentication and comprehensive navigation testing
"""

import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class StartupSwiperWithLogin:
    def __init__(self, base_url="http://localhost:5173", api_url="http://localhost:8000", headless=False):
        self.base_url = base_url
        self.api_url = api_url
        self.headless = headless
        self.driver = None
        self.screenshots_dir = "selenium_screenshots"
        self.log_file = f"selenium_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.test_user = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        self.log("Setting up Chrome WebDriver...")
        
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
        
        # Enable logging
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        self.log("Chrome WebDriver initialized successfully")
    
    def take_screenshot(self, name):
        """Take a screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshots_dir}/{timestamp}_{name}.png"
        self.driver.save_screenshot(filename)
        self.log(f"Screenshot saved: {filename}")
        return filename
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.log(f"Timeout waiting for element: {by}={value}")
            return None
    
    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except TimeoutException:
            self.log(f"Timeout waiting for clickable element: {by}={value}")
            return None
    
    def login(self):
        """Attempt to login to the application"""
        self.log("\n" + "="*80)
        self.log("ATTEMPTING LOGIN")
        self.log("="*80)
        
        try:
            # Look for login form or button
            login_elements = [
                ("input[type='email']", By.CSS_SELECTOR),
                ("input[name='email']", By.CSS_SELECTOR),
                ("//input[@placeholder='Email' or @placeholder='email']", By.XPATH),
                ("//button[contains(., 'Login') or contains(., 'Sign in')]", By.XPATH)
            ]
            
            login_found = False
            for selector, by_type in login_elements:
                try:
                    element = self.driver.find_element(by_type, selector)
                    if element:
                        login_found = True
                        self.log(f"✓ Found login element: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if login_found:
                # Try to fill in login form
                email_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']", timeout=5)
                if email_input:
                    email_input.clear()
                    email_input.send_keys(self.test_user["email"])
                    self.log(f"✓ Entered email: {self.test_user['email']}")
                    
                password_input = self.wait_for_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']", timeout=5)
                if password_input:
                    password_input.clear()
                    password_input.send_keys(self.test_user["password"])
                    self.log("✓ Entered password")
                    
                    # Click submit
                    submit_button = self.wait_for_clickable(By.XPATH, "//button[contains(., 'Login') or contains(., 'Sign in') or @type='submit']")
                    if submit_button:
                        submit_button.click()
                        time.sleep(3)
                        self.take_screenshot("01_after_login")
                        self.log("✓ Login attempted")
                    else:
                        # Try pressing Enter
                        password_input.send_keys(Keys.RETURN)
                        time.sleep(3)
                        self.take_screenshot("01_after_login_enter")
                        self.log("✓ Login attempted via Enter key")
            else:
                self.log("⚠ No login form found - app may not require authentication")
                self.take_screenshot("01_no_login_required")
                
        except Exception as e:
            self.log(f"⚠ Login process error: {str(e)}")
            self.take_screenshot("error_login")
    
    def navigate_to_home(self):
        """Navigate to the application home page"""
        self.log(f"\nNavigating to {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(3)
        self.take_screenshot("00_initial_load")
        self.log("✓ Home page loaded")
    
    def explore_side_menu(self):
        """Explore all side menu elements"""
        self.log("\n" + "="*80)
        self.log("EXPLORING: Side Menu Elements")
        self.log("="*80)
        
        try:
            # Look for sidebar or navigation menu
            menu_selectors = [
                "aside", "nav", "[role='navigation']",
                ".sidebar", ".side-menu", ".navigation"
            ]
            
            menu_found = False
            for selector in menu_selectors:
                try:
                    menu = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if menu and menu.is_displayed():
                        self.log(f"✓ Found menu: {selector}")
                        menu_found = True
                        
                        # Find all links in menu
                        links = menu.find_elements(By.TAG_NAME, "a")
                        buttons = menu.find_elements(By.TAG_NAME, "button")
                        
                        self.log(f"  - Found {len(links)} links")
                        self.log(f"  - Found {len(buttons)} buttons")
                        
                        # Click each menu item
                        all_items = links + buttons
                        for i, item in enumerate(all_items):
                            try:
                                if item.is_displayed() and item.is_enabled():
                                    item_text = item.text or item.get_attribute("aria-label") or f"Item {i+1}"
                                    self.log(f"\n  Clicking menu item: {item_text}")
                                    item.click()
                                    time.sleep(2)
                                    self.take_screenshot(f"menu_item_{i+1}_{item_text.replace(' ', '_')[:20]}")
                            except Exception as e:
                                self.log(f"  ⚠ Could not click item {i+1}: {str(e)}")
                        
                        break
                except NoSuchElementException:
                    continue
            
            if not menu_found:
                self.log("⚠ No traditional side menu found - checking for tab navigation")
                
        except Exception as e:
            self.log(f"✗ Error exploring side menu: {str(e)}")
    
    def explore_all_navigation_tabs(self):
        """Navigate through all tabs in the main navigation"""
        self.log("\n" + "="*80)
        self.log("EXPLORING: All Navigation Tabs")
        self.log("="*80)
        
        # Define all expected tabs based on App.tsx
        tabs = [
            ("swipe", "Swipe", "🎴"),
            ("dashboard", "Dashboard", "🚀"),
            ("insights", "Insights", "💡"),
            ("calendar", "Calendar", "📅"),
            ("ai", "AI Assistant", "🤖")
        ]
        
        for value, name, icon in tabs:
            try:
                self.log(f"\n{icon} Exploring {name} Tab...")
                
                # Try multiple ways to find the tab
                tab = None
                selectors = [
                    (By.XPATH, f"//button[@value='{value}']"),
                    (By.XPATH, f"//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{name.lower()}')]"),
                    (By.CSS_SELECTOR, f"button[value='{value}']"),
                ]
                
                for by, selector in selectors:
                    try:
                        tab = self.wait_for_clickable(by, selector, timeout=3)
                        if tab:
                            break
                    except:
                        continue
                
                if tab:
                    tab.click()
                    time.sleep(2)
                    self.take_screenshot(f"tab_{value}")
                    self.log(f"  ✓ {name} tab loaded")
                    
                    # Explore content in this tab
                    self.explore_current_view_content(name)
                else:
                    self.log(f"  ⚠ {name} tab not found")
                    
            except Exception as e:
                self.log(f"  ✗ Error accessing {name} tab: {str(e)}")
                self.take_screenshot(f"error_tab_{value}")
    
    def explore_current_view_content(self, view_name):
        """Explore content in the current view"""
        try:
            # Find interactive elements
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            cards = self.driver.find_elements(By.CSS_SELECTOR, "[class*='card'], .card")
            
            visible_buttons = [b for b in buttons if b.is_displayed()]
            visible_inputs = [i for i in inputs if i.is_displayed()]
            
            self.log(f"  Content: {len(visible_buttons)} buttons, {len(visible_inputs)} inputs, {len(cards)} cards")
            
            # Try to interact with first few visible buttons (excluding nav)
            interacted = 0
            for button in visible_buttons[:3]:
                try:
                    text = button.text or button.get_attribute("aria-label")
                    if text and "tab" not in text.lower() and interacted < 2:
                        self.log(f"    Clicking: {text[:30]}")
                        button.click()
                        time.sleep(1)
                        self.take_screenshot(f"interaction_{view_name}_{interacted}")
                        interacted += 1
                        # Go back if modal opened
                        try:
                            close_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Close') or contains(., '×')]")
                            if close_buttons and close_buttons[0].is_displayed():
                                close_buttons[0].click()
                                time.sleep(1)
                        except:
                            pass
                except:
                    pass
                    
        except Exception as e:
            self.log(f"    ⚠ Error exploring view content: {str(e)}")
    
    def explore_header_elements(self):
        """Explore all header elements"""
        self.log("\n" + "="*80)
        self.log("EXPLORING: Header Elements")
        self.log("="*80)
        
        try:
            header = self.driver.find_element(By.TAG_NAME, "header")
            if header:
                self.log("✓ Header found")
                
                # Find all interactive elements in header
                buttons = header.find_elements(By.TAG_NAME, "button")
                links = header.find_elements(By.TAG_NAME, "a")
                
                self.log(f"  Header contains {len(buttons)} buttons and {len(links)} links")
                
                for i, button in enumerate(buttons):
                    try:
                        if button.is_displayed():
                            text = button.text or button.get_attribute("aria-label") or f"Button {i+1}"
                            self.log(f"  Found button: {text}")
                    except:
                        pass
                
                self.take_screenshot("header_elements")
                
        except NoSuchElementException:
            self.log("⚠ No header element found")
    
    def run_full_exploration(self):
        """Run complete exploration of the application"""
        self.log("="*80)
        self.log("STARTING FULL NAVIGATION EXPLORATION - Startup Swiper")
        self.log("="*80)
        
        try:
            self.setup_driver()
            self.navigate_to_home()
            
            # Try login
            self.login()
            
            # Wait for app to fully load
            time.sleep(3)
            
            # Explore all sections
            self.explore_header_elements()
            self.explore_side_menu()
            self.explore_all_navigation_tabs()
            
            # Final state
            self.take_screenshot("final_state")
            
            # Print summary
            self.log("\n" + "="*80)
            self.log("EXPLORATION COMPLETED SUCCESSFULLY")
            self.log("="*80)
            self.log(f"Screenshots saved in: {self.screenshots_dir}/")
            self.log(f"Log file: {self.log_file}")
            
        except Exception as e:
            self.log(f"\n✗ CRITICAL ERROR: {str(e)}")
            self.take_screenshot("critical_error")
            import traceback
            self.log(traceback.format_exc())
            
        finally:
            if self.driver:
                self.log("\nClosing browser...")
                time.sleep(2)
                self.driver.quit()
                self.log("Browser closed")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Selenium automation with login for Startup Swiper")
    parser.add_argument("--url", default="http://localhost:5173", help="Base URL of the application")
    parser.add_argument("--api", default="http://localhost:8000", help="API URL")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--email", default="test@example.com", help="Login email")
    parser.add_argument("--password", default="testpassword123", help="Login password")
    
    args = parser.parse_args()
    
    automation = StartupSwiperWithLogin(
        base_url=args.url,
        api_url=args.api,
        headless=args.headless
    )
    
    if args.email:
        automation.test_user["email"] = args.email
    if args.password:
        automation.test_user["password"] = args.password
    
    automation.run_full_exploration()

if __name__ == "__main__":
    main()
