#!/usr/bin/env python3
"""Debug dialog positioning by logging in and finding modal triggers."""

import asyncio
from playwright.async_api import async_playwright

async def debug_dialog():
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
            
            # Get all buttons and their text
            buttons_info = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('button')).map((btn, idx) => ({
                    index: idx,
                    text: btn.textContent.trim().substring(0, 50),
                    ariaLabel: btn.getAttribute('aria-label'),
                    dataTestId: btn.getAttribute('data-testid')
                }));
            }""")
            
            print(f"\n✓ Found {len(buttons_info)} buttons:")
            for btn in buttons_info:
                print(f"  [{btn['index']}] Text: {btn['text']}, aria: {btn['ariaLabel']}, test: {btn['dataTestId']}")
            
            # Try clicking each button to see if any opens a modal
            print("\n✓ Trying to trigger modals by clicking buttons...")
            for i, btn_info in enumerate(buttons_info):
                try:
                    button = (await page.query_selector_all('button'))[i]
                    await button.click()
                    await page.wait_for_timeout(500)
                    
                    # Check if overlay appeared
                    overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                    if overlay:
                        print(f"✓ Button {i} opened a modal!")
                        break
                    else:
                        # Click might have navigated, so try going back
                        await page.wait_for_timeout(500)
                except:
                    pass
            
            # Check if overlay exists
            overlay = await page.query_selector('[data-slot="dialog-overlay"]')
            print(f"\n✓ Dialog overlay exists: {bool(overlay)}")
            
            if overlay:
                overlay_info = await page.evaluate("""() => {
                    const el = document.querySelector('[data-slot="dialog-overlay"]');
                    const s = window.getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return {
                        display: s.display,
                        justifyContent: s.justifyContent,
                        alignItems: s.alignItems,
                        width: Math.round(r.width),
                        height: Math.round(r.height)
                    };
                }""")
                
                content_info = await page.evaluate("""() => {
                    const el = document.querySelector('[data-slot="dialog-content"]');
                    if (!el) return null;
                    const s = window.getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return {
                        width: Math.round(r.width),
                        height: Math.round(r.height),
                        top: Math.round(r.top),
                        left: Math.round(r.left)
                    };
                }""")
                
                print("\nOverlay:", overlay_info)
                print("Content:", content_info)
                
                if content_info:
                    width_ok = content_info['width'] >= 330
                    print(f"\n{'✓' if width_ok else '✗'} Full-width: {content_info['width']}px >= 330px")
            
            # Take screenshot
            await page.screenshot(path='/tmp/mobile-modal-test.png')
            print("\n✓ Screenshot: /tmp/mobile-modal-test.png")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await context.close()
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_dialog())
