#!/usr/bin/env python3
"""Debug modals on Startups page - check for Insights AI and Meeting AI buttons."""

import asyncio
from playwright.async_api import async_playwright

async def debug_startups_modals():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Mobile only for faster debugging
        viewport = {'width': 375, 'height': 812}
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        
        try:
            await page.goto('http://localhost:5000', wait_until='networkidle')
            await page.wait_for_timeout(1500)
            
            print("MOBILE VIEW (375x812)")
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
                    print("✓ Logged in, waiting for page to load...")
            
            # Find and click the Startups button
            all_buttons = await page.query_selector_all('button')
            startups_button = None
            
            for button in all_buttons:
                text = await button.text_content()
                if text and 'Startups' in text:
                    startups_button = button
                    print(f"\n✓ Found Startups button, clicking it...")
                    break
            
            if startups_button:
                await startups_button.click()
                await page.wait_for_timeout(2000)
                print("✓ Clicked Startups, waiting for page to load...")
            else:
                print("✗ Could not find Startups button")
            
            # Now look for Insights AI and Meeting AI buttons
            all_buttons = await page.query_selector_all('button')
            print(f"\n✓ Found {len(all_buttons)} buttons on Startups page:")
            
            insights_ai_button = None
            meeting_ai_button = None
            
            for i, button in enumerate(all_buttons):
                text = await button.text_content()
                aria_label = await button.get_attribute('aria-label')
                test_id = await button.get_attribute('data-testid')
                
                text_display = (text or '').strip()[:50]
                print(f"  [{i}] Text: '{text_display}', aria: {aria_label}, test: {test_id}")
                
                if text and 'Insights AI' in text:
                    insights_ai_button = button
                    print(f"       ^^^ FOUND INSIGHTS AI BUTTON ^^^")
                
                if text and 'Meeting AI' in text:
                    meeting_ai_button = button
                    print(f"       ^^^ FOUND MEETING AI BUTTON ^^^")
            
            # Try clicking Insights AI if found
            if insights_ai_button:
                print(f"\n✓ Clicking Insights AI button...")
                await insights_ai_button.click()
                await page.wait_for_timeout(1000)
                
                overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                print(f"✓ Dialog overlay after clicking Insights AI: {bool(overlay)}")
                
                if overlay:
                    # Take screenshot
                    await page.screenshot(path='/tmp/insights-ai-modal.png')
                    print("✓ Screenshot saved: /tmp/insights-ai-modal.png")
            else:
                print("\n✗ Could not find Insights AI button")
            
            # Try clicking Meeting AI if found
            if meeting_ai_button:
                # Close previous modal if open
                overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                if overlay:
                    await page.press('body', 'Escape')
                    await page.wait_for_timeout(500)
                
                print(f"\n✓ Clicking Meeting AI button...")
                await meeting_ai_button.click()
                await page.wait_for_timeout(1000)
                
                overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                print(f"✓ Dialog overlay after clicking Meeting AI: {bool(overlay)}")
                
                if overlay:
                    # Take screenshot
                    await page.screenshot(path='/tmp/meeting-ai-modal.png')
                    print("✓ Screenshot saved: /tmp/meeting-ai-modal.png")
            else:
                print("\n✗ Could not find Meeting AI button")
            
            print("\n" + "="*60)
            print("Debug complete!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_startups_modals())
