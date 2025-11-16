#!/usr/bin/env python3
"""Detailed check of modal and nav click areas."""

import asyncio
from playwright.async_api import async_playwright

async def test_click_areas():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        viewport = {'width': 375, 'height': 812}
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        
        try:
            await page.goto('http://localhost:5000', wait_until='networkidle')
            await page.wait_for_timeout(1500)
            
            print("DETAILED CLICK AREA ANALYSIS")
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
            
            # Open Meeting AI modal
            meeting_buttons = await page.query_selector_all('button')
            for button in meeting_buttons:
                text = await button.text_content()
                if text and 'Meeting AI' in text:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    break
            
            # Get detailed info about modal and nav
            modal_content = await page.query_selector('[data-slot="dialog-content"]')
            nav = await page.query_selector('nav')
            
            if modal_content:
                modal_info = await page.evaluate("""() => {
                    const el = document.querySelector('[data-slot="dialog-content"]');
                    const r = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return {
                        top: r.top,
                        bottom: r.bottom,
                        left: r.left,
                        right: r.right,
                        pointerEvents: style.pointerEvents,
                        zIndex: style.zIndex
                    };
                }""")
                print("Modal Content:")
                print(f"  Y Range: {modal_info['top']} to {modal_info['bottom']}")
                print(f"  Pointer Events: {modal_info['pointerEvents']}")
                print(f"  Z-Index: {modal_info['zIndex']}")
            
            if nav:
                nav_info = await page.evaluate("""() => {
                    const el = document.querySelector('nav');
                    const r = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return {
                        top: r.top,
                        bottom: r.bottom,
                        left: r.left,
                        right: r.right,
                        pointerEvents: style.pointerEvents,
                        zIndex: style.zIndex
                    };
                }""")
                print("\nNavigation:")
                print(f"  Y Range: {nav_info['top']} to {nav_info['bottom']}")
                print(f"  Pointer Events: {nav_info['pointerEvents']}")
                print(f"  Z-Index: {nav_info['zIndex']}")
            
            # Try to find the actual clickable Calendar button
            nav_buttons = await page.query_selector_all('nav button')
            print(f"\nNavigation Buttons Found: {len(nav_buttons)}")
            
            for i, btn in enumerate(nav_buttons):
                btn_text = await btn.text_content()
                btn_info = await page.evaluate(f"""() => {{
                    const btns = document.querySelectorAll('nav button');
                    const el = btns[{i}];
                    if (!el) return null;
                    const r = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    return {{
                        text: el.textContent.trim().substring(0, 20),
                        top: r.top,
                        bottom: r.bottom,
                        pointerEvents: style.pointerEvents,
                        zIndex: style.zIndex
                    }};
                }}""")
                
                if btn_info:
                    print(f"  [{i}] {btn_info['text']}")
                    print(f"      Y: {btn_info['top']}-{btn_info['bottom']}, "
                          f"Pointer: {btn_info['pointerEvents']}, Z: {btn_info['zIndex']}")
            
            # Test clicking nav button
            print("\nTesting nav button click...")
            calendar_btn = await page.locator('nav button:has-text("Calendar")').first
            try:
                await calendar_btn.click(force=True)
                print("✓ Navigation button clicked with force=True")
            except Exception as e:
                print(f"✗ Failed to click: {e}")
                
                # Try clicking at specific coordinates
                try:
                    nav_buttons = await page.query_selector_all('nav button')
                    if len(nav_buttons) > 3:
                        await page.click('nav button:nth-child(4)', force=True)
                        print("✓ Clicked nav button via selector with force=True")
                except Exception as e2:
                    print(f"✗ Also failed with selector: {e2}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_click_areas())
