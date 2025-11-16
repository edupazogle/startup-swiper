#!/usr/bin/env python3
"""Test if modals stay open when clicking inside."""

import asyncio
from playwright.async_api import async_playwright

async def test_modal_persistence():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        viewport = {'width': 375, 'height': 812}
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        
        try:
            await page.goto('http://localhost:5000', wait_until='networkidle')
            await page.wait_for_timeout(1500)
            
            print("Testing Modal Persistence")
            print("="*60)
            
            # Login
            email_input = await page.query_selector('input[type="email"]')
            password_input = await page.query_selector('input[type="password"]')
            if email_input and password_input:
                await email_input.fill('alice.jin@axa-uk.co.uk')
                await password_input.fill('123')
                login_button = await page.query_selector('button')
                if login_button:
                    await login_button.click()
                    await page.wait_for_timeout(4000)
            
            # Navigate to Startups
            buttons = await page.query_selector_all('button')
            for button in buttons:
                text = await button.text_content()
                if text and 'Startups' in text:
                    await button.click()
                    await page.wait_for_timeout(2000)
                    break
            
            # Open Meeting AI
            print("\n1️⃣  Opening Meeting AI modal...")
            meeting_buttons = await page.query_selector_all('button')
            for button in meeting_buttons:
                text = await button.text_content()
                if text and 'Meeting AI' in text:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    break
            
            # Check if modal is visible
            overlay = await page.query_selector('[data-slot="dialog-overlay"]')
            content = await page.query_selector('[data-slot="dialog-content"]')
            
            if overlay and content:
                print("✓ Modal opened successfully")
            else:
                print("✗ Modal not found after opening")
                return
            
            # Click inside the modal (on a card)
            print("\n2️⃣  Clicking on modal content...")
            cards = await page.query_selector_all('[data-slot="dialog-content"] div[class*="Card"]')
            if cards:
                await cards[0].click()
                await page.wait_for_timeout(500)
                print("✓ Clicked on card in modal")
            
            # Check if modal is still visible
            overlay_after = await page.query_selector('[data-slot="dialog-overlay"]')
            content_after = await page.query_selector('[data-slot="dialog-content"]')
            
            if overlay_after and content_after:
                print("✓ Modal still visible after click")
            else:
                print("✗ Modal closed after clicking inside!")
                return
            
            # Try clicking on text inside modal
            print("\n3️⃣  Clicking on modal text...")
            try:
                await page.locator('[data-slot="dialog-content"]').click(position={'x': 50, 'y': 100})
                await page.wait_for_timeout(500)
                print("✓ Clicked on modal text area")
            except:
                print("⚠ Could not click on text area")
            
            # Check again
            overlay_final = await page.query_selector('[data-slot="dialog-overlay"]')
            content_final = await page.query_selector('[data-slot="dialog-content"]')
            
            if overlay_final and content_final:
                print("✓ Modal still visible after text click")
            else:
                print("✗ Modal closed after clicking text!")
            
            # Try pressing a button in the modal
            print("\n4️⃣  Checking modal buttons...")
            modal_buttons = await page.query_selector_all('[data-slot="dialog-content"] button')
            print(f"Found {len(modal_buttons)} buttons in modal")
            
            # Close with Escape
            print("\n5️⃣  Closing with Escape...")
            await page.press('body', 'Escape')
            await page.wait_for_timeout(1000)
            
            overlay_closed = await page.query_selector('[data-slot="dialog-overlay"]')
            if not overlay_closed:
                print("✓ Modal closed with Escape")
            else:
                print("✗ Modal still visible after Escape")
            
            print("\n" + "="*60)
            await page.screenshot(path='/tmp/modal-persistence-test.png')
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_modal_persistence())
