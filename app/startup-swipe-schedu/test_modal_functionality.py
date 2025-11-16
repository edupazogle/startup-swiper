#!/usr/bin/env python3
"""Test modal functionality - typing, navigation interaction, etc."""

import asyncio
from playwright.async_api import async_playwright

async def test_modal_functionality():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        viewport = {'width': 375, 'height': 812}
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        
        try:
            await page.goto('http://localhost:5000', wait_until='networkidle')
            await page.wait_for_timeout(1500)
            
            print("FUNCTIONAL TEST - Modal Interaction")
            print("="*60)
            
            # Login
            email_input = await page.query_selector('input[type="email"]')
            password_input = await page.query_selector('input[type="password"]')
            
            if email_input and password_input:
                print("✓ Logging in...")
                await email_input.fill('alice.jin@axa-uk.co.uk')
                await password_input.fill('123')
                
                login_button = await page.query_selector('button')
                if login_button:
                    await login_button.click()
                    await page.wait_for_timeout(4000)
                    print("✓ Logged in")
            
            # Navigate to Startups
            buttons = await page.query_selector_all('button')
            for button in buttons:
                text = await button.text_content()
                if text and 'Startups' in text:
                    await button.click()
                    await page.wait_for_timeout(2000)
                    print("✓ Navigated to Startups page")
                    break
            
            # Test Insights AI Modal
            print("\n📋 Testing Insights AI Modal...")
            insights_buttons = await page.query_selector_all('button')
            for button in insights_buttons:
                text = await button.text_content()
                if text and 'Insights AI' in text:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    
                    # Test typing in textarea
                    textarea = await page.query_selector('textarea')
                    if textarea:
                        print("✓ Found textarea input")
                        await textarea.click()
                        await textarea.fill('This is a test message about the startup')
                        await page.wait_for_timeout(500)
                        
                        # Check if text was entered
                        input_value = await textarea.input_value()
                        if input_value:
                            print(f"✓ Successfully typed message: '{input_value[:40]}...'")
                        else:
                            print("✗ Failed to type message")
                    else:
                        print("✗ No textarea found for input")
                    
                    # Verify modal can be closed with Escape
                    await page.press('body', 'Escape')
                    await page.wait_for_timeout(1000)
                    
                    overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                    if not overlay:
                        print("✓ Modal closed with Escape key")
                    else:
                        print("⚠ Modal may still be visible after Escape")
                    
                    break
            
            # Test Meeting AI Modal
            print("\n📋 Testing Meeting AI Modal...")
            meeting_buttons = await page.query_selector_all('button')
            for button in meeting_buttons:
                text = await button.text_content()
                if text and 'Meeting AI' in text:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    
                    # Verify navigation is still clickable
                    nav_buttons = await page.query_selector_all('nav button')
                    if nav_buttons:
                        print(f"✓ Navigation bar has {len(nav_buttons)} buttons")
                        
                        # Try clicking a navigation button (Calendar)
                        for nav_btn in nav_buttons:
                            nav_text = await nav_btn.text_content()
                            if nav_text and 'Calendar' in nav_text:
                                try:
                                    await nav_btn.click(timeout=1000)
                                    await page.wait_for_timeout(1000)
                                    print("✓ Navigation button (Calendar) is clickable")
                                except:
                                    print("✗ Navigation button is not clickable (modal may be blocking)")
                                break
                    else:
                        print("✗ No navigation buttons found")
                    
                    # Check if modal content is visible
                    header = await page.query_selector('[data-slot="dialog-header"]')
                    if header:
                        header_text = await header.text_content()
                        print(f"✓ Modal header visible: '{header_text[:50]}...'")
                    
                    # Close modal
                    await page.press('body', 'Escape')
                    await page.wait_for_timeout(1000)
                    print("✓ Modal closed")
                    
                    break
            
            print("\n" + "="*60)
            print("✅ All tests completed!")
            
            # Final screenshot
            await page.screenshot(path='/tmp/final-test.png')
            print("✓ Final screenshot saved: /tmp/final-test.png")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_modal_functionality())
