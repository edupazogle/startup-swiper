#!/usr/bin/env python3
"""Test modal positioning on mobile and desktop."""

import asyncio
from playwright.async_api import async_playwright

async def test_modal_positioning():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        print("Testing Modal Positioning on Mobile and Desktop")
        print("="*60)
        
        # Test Mobile
        print("\n📱 MOBILE (375x812)")
        viewport_mobile = {'width': 375, 'height': 812}
        context_mobile = await browser.new_context(viewport=viewport_mobile)
        page_mobile = await context_mobile.new_page()
        
        await test_on_viewport(page_mobile, "mobile")
        await context_mobile.close()
        
        # Test Desktop
        print("\n💻 DESKTOP (1920x1080)")
        viewport_desktop = {'width': 1920, 'height': 1080}
        context_desktop = await browser.new_context(viewport=viewport_desktop)
        page_desktop = await context_desktop.new_page()
        
        await test_on_viewport(page_desktop, "desktop")
        await context_desktop.close()
        
        await browser.close()
        
        print("\n" + "="*60)
        print("✅ Testing complete!")

async def test_on_viewport(page, viewport_type):
    try:
        await page.goto('http://localhost:5000', wait_until='networkidle')
        await page.wait_for_timeout(1500)
        
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
        meeting_buttons = await page.query_selector_all('button')
        for button in meeting_buttons:
            text = await button.text_content()
            if text and 'Meeting AI' in text:
                await button.click()
                await page.wait_for_timeout(1500)
                break
        
        # Get modal position
        content = await page.query_selector('[data-slot="dialog-content"]')
        if content:
            position_info = await page.evaluate("""() => {
                const el = document.querySelector('[data-slot="dialog-content"]');
                const r = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                
                // Calculate center position
                const viewport_width = window.innerWidth;
                const viewport_height = window.innerHeight;
                const modal_center_x = r.left + r.width / 2;
                const modal_center_y = r.top + r.height / 2;
                const viewport_center_x = viewport_width / 2;
                const viewport_center_y = viewport_height / 2;
                
                const is_centered_x = Math.abs(modal_center_x - viewport_center_x) < 100;
                const is_centered_y = Math.abs(modal_center_y - viewport_center_y) < 100;
                
                return {
                    modal_top: Math.round(r.top),
                    modal_left: Math.round(r.left),
                    modal_width: Math.round(r.width),
                    modal_height: Math.round(r.height),
                    viewport_width: viewport_width,
                    viewport_height: viewport_height,
                    modal_center_x: Math.round(modal_center_x),
                    modal_center_y: Math.round(modal_center_y),
                    viewport_center_x: Math.round(viewport_center_x),
                    viewport_center_y: Math.round(viewport_center_y),
                    is_centered_x: is_centered_x,
                    is_centered_y: is_centered_y,
                    position: style.position
                };
            }""")
            
            print(f"  Modal Position: ({position_info['modal_left']}, {position_info['modal_top']})")
            print(f"  Modal Size: {position_info['modal_width']}x{position_info['modal_height']}")
            print(f"  Viewport Size: {position_info['viewport_width']}x{position_info['viewport_height']}")
            print(f"  CSS Position: {position_info['position']}")
            print(f"  Modal Center: ({position_info['modal_center_x']}, {position_info['modal_center_y']})")
            print(f"  Viewport Center: ({position_info['viewport_center_x']}, {position_info['viewport_center_y']})")
            
            if position_info['is_centered_x'] and position_info['is_centered_y']:
                print(f"  ✓ Modal is CENTERED")
            elif position_info['modal_top'] == 0 and position_info['modal_left'] == 0 and position_info['modal_width'] == position_info['viewport_width']:
                print(f"  ✓ Modal is FULL SCREEN (mobile layout)")
            elif position_info['modal_left'] < 50 and position_info['modal_top'] < 50:
                print(f"  ✗ Modal positioned in TOP-LEFT corner")
            else:
                print(f"  ⚠ Modal positioning unclear")
            
            # Take screenshot
            filename = f'/tmp/modal-{viewport_type}.png'
            await page.screenshot(path=filename)
            print(f"  Screenshot: {filename}")
        
        # Close modal
        await page.press('body', 'Escape')
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_modal_positioning())
