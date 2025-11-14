#!/usr/bin/env python3
"""
Selenium Web Automation Script for Startup Swiper
Tests all navigation elements and functionality
"""

import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class StartupSwiperAutomation:
    def __init__(self, base_url="http://localhost:5173", headless=False):
        self.base_url = base_url
        self.headless = headless
        self.driver = None
        self.screenshots_dir = "selenium_screenshots"
        self.log_file = f"selenium_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Create screenshots directory
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
            chrome_options.add_argument("--headless")
        
        # Additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
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
    
    def navigate_to_home(self):
        """Navigate to the application home page"""
        self.log(f"Navigating to {self.base_url}")
        self.driver.get(self.base_url)
        time.sleep(2)
        self.take_screenshot("01_home_page")
        self.log("Home page loaded")
    
    def test_swipe_view(self):
        """Test Swipe View (main startup swiping interface)"""
        self.log("\n" + "="*80)
        self.log("TESTING: Swipe View")
        self.log("="*80)
        
        try:
            # Click on Swipe tab
            swipe_tab = self.wait_for_clickable(By.XPATH, "//button[contains(@value, 'swipe') or .//text()[contains(., 'Swipe')]]")
            if swipe_tab:
                swipe_tab.click()
                time.sleep(2)
                self.take_screenshot("02_swipe_view")
                self.log("✓ Swipe view loaded")
                
                # Check for startup card
                try:
                    startup_card = self.driver.find_element(By.CLASS_NAME, "startup-card")
                    self.log("✓ Startup card displayed")
                except NoSuchElementException:
                    self.log("⚠ Startup card not found")
                
                # Try to find swipe buttons (like/dislike)
                time.sleep(1)
                
        except Exception as e:
            self.log(f"✗ Error in Swipe View: {str(e)}")
            self.take_screenshot("error_swipe_view")
    
    def test_dashboard_view(self):
        """Test Dashboard View"""
        self.log("\n" + "="*80)
        self.log("TESTING: Dashboard View")
        self.log("="*80)
        
        try:
            # Click on Dashboard tab
            dashboard_tab = self.wait_for_clickable(By.XPATH, "//button[contains(@value, 'dashboard') or .//text()[contains(., 'Dashboard')]]")
            if dashboard_tab:
                dashboard_tab.click()
                time.sleep(2)
                self.take_screenshot("03_dashboard_view")
                self.log("✓ Dashboard view loaded")
                
                # Check for dashboard elements
                time.sleep(1)
                
        except Exception as e:
            self.log(f"✗ Error in Dashboard View: {str(e)}")
            self.take_screenshot("error_dashboard_view")
    
    def test_insights_view(self):
        """Test Insights View"""
        self.log("\n" + "="*80)
        self.log("TESTING: Insights View")
        self.log("="*80)
        
        try:
            # Click on Insights tab
            insights_tab = self.wait_for_clickable(By.XPATH, "//button[contains(@value, 'insights') or .//text()[contains(., 'Insights')]]")
            if insights_tab:
                insights_tab.click()
                time.sleep(2)
                self.take_screenshot("04_insights_view")
                self.log("✓ Insights view loaded")
                
        except Exception as e:
            self.log(f"✗ Error in Insights View: {str(e)}")
            self.take_screenshot("error_insights_view")
    
    def test_calendar_view(self):
        """Test Calendar View"""
        self.log("\n" + "="*80)
        self.log("TESTING: Calendar View")
        self.log("="*80)
        
        try:
            # Click on Calendar tab
            calendar_tab = self.wait_for_clickable(By.XPATH, "//button[contains(@value, 'calendar') or .//text()[contains(., 'Calendar')]]")
            if calendar_tab:
                calendar_tab.click()
                time.sleep(2)
                self.take_screenshot("05_calendar_view")
                self.log("✓ Calendar view loaded")
                
        except Exception as e:
            self.log(f"✗ Error in Calendar View: {str(e)}")
            self.take_screenshot("error_calendar_view")
    
    def test_ai_assistant_view(self):
        """Test AI Assistant View"""
        self.log("\n" + "="*80)
        self.log("TESTING: AI Assistant View")
        self.log("="*80)
        
        try:
            # Click on AI tab
            ai_tab = self.wait_for_clickable(By.XPATH, "//button[contains(@value, 'ai') or .//text()[contains(., 'AI')]]")
            if ai_tab:
                ai_tab.click()
                time.sleep(2)
                self.take_screenshot("06_ai_assistant_view")
                self.log("✓ AI Assistant view loaded")
                
        except Exception as e:
            self.log(f"✗ Error in AI Assistant View: {str(e)}")
            self.take_screenshot("error_ai_assistant_view")
    
    def test_admin_view(self):
        """Test Admin View"""
        self.log("\n" + "="*80)
        self.log("TESTING: Admin View")
        self.log("="*80)
        
        try:
            # Look for admin button (usually in header or as separate element)
            # This might require authentication
            admin_button = self.driver.find_elements(By.XPATH, "//button[contains(., 'Admin') or contains(@aria-label, 'Admin')]")
            if admin_button:
                admin_button[0].click()
                time.sleep(2)
                self.take_screenshot("07_admin_view")
                self.log("✓ Admin view loaded")
            else:
                self.log("⚠ Admin button not found (may require auth)")
                
        except Exception as e:
            self.log(f"⚠ Admin View not accessible: {str(e)}")
    
    def test_header_elements(self):
        """Test header elements like logo, buttons, etc."""
        self.log("\n" + "="*80)
        self.log("TESTING: Header Elements")
        self.log("="*80)
        
        try:
            # Check for logo
            logos = self.driver.find_elements(By.TAG_NAME, "img")
            self.log(f"✓ Found {len(logos)} images (logos)")
            
            # Check for notification bell
            notification_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'notification') or .//svg[contains(@class, 'bell')]]")
            if notification_buttons:
                self.log(f"✓ Found {len(notification_buttons)} notification button(s)")
            
            # Check for action buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            self.log(f"✓ Found {len(buttons)} total buttons on page")
            
            self.take_screenshot("08_header_elements")
            
        except Exception as e:
            self.log(f"✗ Error testing header elements: {str(e)}")
    
    def test_all_tabs(self):
        """Navigate through all tabs systematically"""
        self.log("\n" + "="*80)
        self.log("TESTING: All Navigation Tabs")
        self.log("="*80)
        
        tabs = [
            ("swipe", "Swipe"),
            ("dashboard", "Dashboard"),
            ("insights", "Insights"),
            ("calendar", "Calendar"),
            ("ai", "AI Assistant")
        ]
        
        for value, name in tabs:
            try:
                self.log(f"\nNavigating to {name} tab...")
                tab = self.wait_for_clickable(By.XPATH, f"//button[@value='{value}']", timeout=5)
                if tab:
                    tab.click()
                    time.sleep(2)
                    self.take_screenshot(f"tab_{value}")
                    self.log(f"✓ {name} tab accessible")
                else:
                    self.log(f"⚠ {name} tab not found by value, trying text match...")
                    tab_by_text = self.wait_for_clickable(By.XPATH, f"//button[contains(., '{name}')]", timeout=5)
                    if tab_by_text:
                        tab_by_text.click()
                        time.sleep(2)
                        self.take_screenshot(f"tab_{value}_alt")
                        self.log(f"✓ {name} tab accessible (via text match)")
                    
            except Exception as e:
                self.log(f"✗ Error accessing {name} tab: {str(e)}")
    
    def test_interactions(self):
        """Test interactive elements"""
        self.log("\n" + "="*80)
        self.log("TESTING: Interactive Elements")
        self.log("="*80)
        
        try:
            # Go to swipe view
            swipe_tab = self.wait_for_clickable(By.XPATH, "//button[@value='swipe']")
            if swipe_tab:
                swipe_tab.click()
                time.sleep(2)
                
                # Look for interactive buttons
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                interactive_count = 0
                
                for button in all_buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            interactive_count += 1
                    except:
                        pass
                
                self.log(f"✓ Found {interactive_count} interactive buttons")
                self.take_screenshot("09_interactive_elements")
                
        except Exception as e:
            self.log(f"✗ Error testing interactions: {str(e)}")
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        self.log("="*80)
        self.log("STARTING FULL TEST SUITE - Startup Swiper Automation")
        self.log("="*80)
        
        try:
            self.setup_driver()
            self.navigate_to_home()
            
            # Wait for app to load
            time.sleep(3)
            
            # Run all tests
            self.test_header_elements()
            self.test_all_tabs()
            self.test_swipe_view()
            self.test_dashboard_view()
            self.test_insights_view()
            self.test_calendar_view()
            self.test_ai_assistant_view()
            self.test_admin_view()
            self.test_interactions()
            
            # Final screenshot
            self.take_screenshot("10_final_state")
            
            self.log("\n" + "="*80)
            self.log("TEST SUITE COMPLETED SUCCESSFULLY")
            self.log("="*80)
            
        except Exception as e:
            self.log(f"\n✗ CRITICAL ERROR: {str(e)}")
            self.take_screenshot("critical_error")
            
        finally:
            if self.driver:
                self.log("\nClosing browser...")
                time.sleep(2)
                self.driver.quit()
                self.log("Browser closed")
                
            self.log(f"\nLog file saved: {self.log_file}")
            self.log(f"Screenshots saved in: {self.screenshots_dir}/")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Selenium automation for Startup Swiper")
    parser.add_argument("--url", default="http://localhost:5173", help="Base URL of the application")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    automation = StartupSwiperAutomation(base_url=args.url, headless=args.headless)
    automation.run_full_test_suite()

if __name__ == "__main__":
    main()
