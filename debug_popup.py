#!/usr/bin/env python3
"""
Playwright script to debug popup positioning on mobile and desktop
"""
import asyncio
from playwright.async_api import async_playwright


async def debug_popups():
    async with async_playwright() as p:
        # Test on mobile viewport
        print("=" * 80)
        print("TESTING MOBILE VIEWPORT (375x667)")
        print("=" * 80)
        
        browser = await p.chromium.launch(headless=True)
        
        # Mobile context
        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
        )
        mobile_page = await mobile_context.new_page()
        
        try:
            await mobile_page.goto("http://localhost:5173", wait_until="networkidle")
            
            # Find and click a popup trigger (adjust selector as needed)
            print("\n[Mobile] Waiting for page to load...")
            await mobile_page.wait_for_timeout(2000)
            
            # Check for chat or modal elements
            dialogs = await mobile_page.query_selector_all("[role='dialog']")
            print(f"[Mobile] Found {len(dialogs)} dialog elements")
            
            # Get viewport dimensions
            viewport = mobile_page.viewport
            print(f"[Mobile] Viewport: {viewport['width']}x{viewport['height']}")
            
            # Look for the startup chat or modal
            chat_elem = await mobile_page.query_selector(".fixed.md\\:relative")
            if chat_elem:
                box = await chat_elem.bounding_box()
                print(f"[Mobile] Chat element position: {box}")
            
            # Screenshot
            await mobile_page.screenshot(path="/tmp/mobile_popup.png")
            print("[Mobile] Screenshot saved: /tmp/mobile_popup.png")
            
        except Exception as e:
            print(f"[Mobile] Error: {e}")
        finally:
            await mobile_context.close()
        
        # Desktop context
        print("\n" + "=" * 80)
        print("TESTING DESKTOP VIEWPORT (1280x720)")
        print("=" * 80)
        
        desktop_context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        desktop_page = await desktop_context.new_page()
        
        try:
            await desktop_page.goto("http://localhost:5173", wait_until="networkidle")
            
            print("\n[Desktop] Waiting for page to load...")
            await desktop_page.wait_for_timeout(2000)
            
            # Check for dialogs
            dialogs = await desktop_page.query_selector_all("[role='dialog']")
            print(f"[Desktop] Found {len(dialogs)} dialog elements")
            
            # Get viewport dimensions
            viewport = desktop_page.viewport
            print(f"[Desktop] Viewport: {viewport['width']}x{viewport['height']}")
            
            # Screenshot
            await desktop_page.screenshot(path="/tmp/desktop_popup.png")
            print("[Desktop] Screenshot saved: /tmp/desktop_popup.png")
            
        except Exception as e:
            print(f"[Desktop] Error: {e}")
        finally:
            await desktop_context.close()
        
        await browser.close()
        print("\n" + "=" * 80)
        print("Debug complete! Check /tmp/mobile_popup.png and /tmp/desktop_popup.png")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(debug_popups())
