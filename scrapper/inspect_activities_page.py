#!/usr/bin/env python3
"""
Quick script to check what's on the Slush events page
"""

import os
import sys
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions

load_dotenv()

def main():
    # Setup Chrome
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    selenium_url = "http://localhost:4444"
    driver = webdriver.Remote(command_executor=selenium_url, options=options)
    
    try:
        # Login
        print("Logging in...")
        driver.get("https://platform.slush.org/")
        time.sleep(3)
        
        email_input = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
        email_input.send_keys(os.getenv('SLUSH_EMAIL'))
        
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password_input.send_keys(os.getenv('SLUSH_PASSWORD'))
        
        from selenium.webdriver.common.keys import Keys
        password_input.send_keys(Keys.RETURN)
        time.sleep(8)
        
        print(f"Logged in, current URL: {driver.current_url}")
        
        # Navigate to activities page
        print("\nNavigating to activities page...")
        driver.get("https://platform.slush.org/slush25/activities/browse")
        time.sleep(5)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Save page source
        with open("activities_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n✅ Page source saved to: activities_page_source.html")
        
        # Check all links
        print("\n=== All Links on Page ===")
        links = driver.find_elements(By.TAG_NAME, "a")
        activity_links = []
        for link in links:
            href = link.get_attribute("href")
            if href and "activities" in href:
                activity_links.append(href)
                print(f"  {href}")
        
        print(f"\n✅ Found {len(activity_links)} activity-related links")
        
        # Check for specific patterns
        print("\n=== Checking for different URL patterns ===")
        all_hrefs = [link.get_attribute("href") for link in links if link.get_attribute("href")]
        
        patterns = [
            "/activities/",
            "/events/",
            "/schedule/",
            "/agenda/",
            "slush25"
        ]
        
        for pattern in patterns:
            matches = [h for h in all_hrefs if h and pattern in h]
            print(f"{pattern}: {len(matches)} links")
            if matches:
                for m in matches[:3]:
                    print(f"  - {m}")
        
        # Get all text content
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"\n=== Page Text Sample (first 500 chars) ===")
        print(body_text[:500])
        
        # Save full text
        with open("activities_page_text.txt", "w", encoding="utf-8") as f:
            f.write(body_text)
        print("\n✅ Full page text saved to: activities_page_text.txt")
        
        # Take screenshot
        driver.save_screenshot("activities_page_full.png")
        print("✅ Screenshot saved to: activities_page_full.png")
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    main()
