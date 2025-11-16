#!/usr/bin/env python3
"""Debug modal positioning and dimensions on mobile."""

import asyncio
from playwright.async_api import async_playwright

async def debug_modal_positioning():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
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
            
            # Click Insights AI button (first one found)
            insights_buttons = await page.query_selector_all('button')
            for button in insights_buttons:
                text = await button.text_content()
                if text and 'Insights AI' in text:
                    print("\n✓ Clicking Insights AI button...")
                    await button.click()
                    await page.wait_for_timeout(1500)
                    
                    # Get modal dimensions
                    overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                    content = await page.query_selector('[data-slot="dialog-content"]')
                    
                    if overlay:
                        overlay_info = await page.evaluate("""() => {
                            const el = document.querySelector('[data-slot="dialog-overlay"]');
                            const r = el.getBoundingClientRect();
                            const s = window.getComputedStyle(el);
                            return {
                                x: Math.round(r.x),
                                y: Math.round(r.y),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                zIndex: s.zIndex,
                                display: s.display
                            };
                        }""")
                        print(f"\n📍 INSIGHTS AI MODAL - Overlay:")
                        print(f"   Position: ({overlay_info['x']}, {overlay_info['y']})")
                        print(f"   Size: {overlay_info['width']}x{overlay_info['height']}")
                        print(f"   Z-Index: {overlay_info['zIndex']}")
                    
                    if content:
                        content_info = await page.evaluate("""() => {
                            const el = document.querySelector('[data-slot="dialog-content"]');
                            const r = el.getBoundingClientRect();
                            const s = window.getComputedStyle(el);
                            return {
                                x: Math.round(r.x),
                                y: Math.round(r.y),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                top: s.top,
                                left: s.left,
                                zIndex: s.zIndex,
                                position: s.position
                            };
                        }""")
                        print(f"\n   Content:")
                        print(f"   Position: ({content_info['x']}, {content_info['y']})")
                        print(f"   Size: {content_info['width']}x{content_info['height']}")
                        print(f"   CSS Position: {content_info['position']}")
                        print(f"   Z-Index: {content_info['zIndex']}")
                    
                    # Check navigation bar
                    nav = await page.query_selector('nav')
                    if nav:
                        nav_info = await page.evaluate("""() => {
                            const nav = document.querySelector('nav');
                            if (!nav) return null;
                            const r = nav.getBoundingClientRect();
                            const s = window.getComputedStyle(nav);
                            return {
                                x: Math.round(r.x),
                                y: Math.round(r.y),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                zIndex: s.zIndex,
                                visibility: s.visibility
                            };
                        }""")
                        print(f"\n   Navigation Bar:")
                        print(f"   Position: ({nav_info['x']}, {nav_info['y']})")
                        print(f"   Size: {nav_info['width']}x{nav_info['height']}")
                        print(f"   Z-Index: {nav_info['zIndex']}")
                    
                    await page.screenshot(path='/tmp/insights-ai-debug.png')
                    print(f"\n✓ Screenshot saved: /tmp/insights-ai-debug.png")
                    break
            
            # Close modal with Escape
            await page.press('body', 'Escape')
            await page.wait_for_timeout(1000)
            
            # Now test Meeting AI
            meeting_buttons = await page.query_selector_all('button')
            for button in meeting_buttons:
                text = await button.text_content()
                if text and 'Meeting AI' in text:
                    print("\n✓ Clicking Meeting AI button...")
                    await button.click()
                    await page.wait_for_timeout(1500)
                    
                    # Get modal dimensions
                    overlay = await page.query_selector('[data-slot="dialog-overlay"]')
                    content = await page.query_selector('[data-slot="dialog-content"]')
                    
                    if overlay:
                        overlay_info = await page.evaluate("""() => {
                            const el = document.querySelector('[data-slot="dialog-overlay"]');
                            const r = el.getBoundingClientRect();
                            const s = window.getComputedStyle(el);
                            return {
                                x: Math.round(r.x),
                                y: Math.round(r.y),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                zIndex: s.zIndex
                            };
                        }""")
                        print(f"\n📍 MEETING AI MODAL - Overlay:")
                        print(f"   Position: ({overlay_info['x']}, {overlay_info['y']})")
                        print(f"   Size: {overlay_info['width']}x{overlay_info['height']}")
                        print(f"   Z-Index: {overlay_info['zIndex']}")
                    
                    if content:
                        content_info = await page.evaluate("""() => {
                            const el = document.querySelector('[data-slot="dialog-content"]');
                            const r = el.getBoundingClientRect();
                            const s = window.getComputedStyle(el);
                            return {
                                x: Math.round(r.x),
                                y: Math.round(r.y),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                zIndex: s.zIndex,
                                position: s.position,
                                top: r.top,
                                bottom: r.bottom
                            };
                        }""")
                        print(f"\n   Content:")
                        print(f"   Position: ({content_info['x']}, {content_info['y']})")
                        print(f"   Size: {content_info['width']}x{content_info['height']}")
                        print(f"   Top: {content_info['top']}, Bottom: {content_info['bottom']}")
                        print(f"   Z-Index: {content_info['zIndex']}")
                    
                    # Check navigation bar
                    nav = await page.query_selector('nav')
                    if nav:
                        nav_info = await page.evaluate("""() => {
                            const nav = document.querySelector('nav');
                            if (!nav) return null;
                            const r = nav.getBoundingClientRect();
                            const s = window.getComputedStyle(nav);
                            return {
                                x: Math.round(r.x),
                                y: Math.round(r.y),
                                width: Math.round(r.width),
                                height: Math.round(r.height),
                                zIndex: s.zIndex,
                                visible: r.height > 0
                            };
                        }""")
                        print(f"\n   Navigation Bar:")
                        print(f"   Position: ({nav_info['x']}, {nav_info['y']})")
                        print(f"   Size: {nav_info['width']}x{nav_info['height']}")
                        print(f"   Z-Index: {nav_info['zIndex']}")
                        print(f"   Visible: {nav_info['visible']}")
                    
                    await page.screenshot(path='/tmp/meeting-ai-debug.png')
                    print(f"\n✓ Screenshot saved: /tmp/meeting-ai-debug.png")
                    break
            
            print("\n" + "="*60)
            print("Debug complete!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_modal_positioning())
