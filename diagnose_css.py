#!/usr/bin/env python3
"""Check actual computed CSS and DOM structure"""
import asyncio
from playwright.async_api import async_playwright


async def diagnose_popup_css():
    """Diagnose popup CSS on mobile and desktop"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        print("\n" + "=" * 80)
        print("POPUP CSS DIAGNOSTIC")
        print("=" * 80)
        
        # Mobile
        print("\n📱 MOBILE (375x667)")
        mobile_ctx = await browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = await mobile_ctx.new_page()
        await mobile_page.goto("http://localhost:5173", wait_until="networkidle")
        await mobile_page.wait_for_timeout(1000)
        
        # Find all elements with "fixed" or "dialog" classes
        fixed_elements = await mobile_page.query_selector_all("[class*='fixed']")
        print(f"Elements with 'fixed' class: {len(fixed_elements)}")
        
        for elem in fixed_elements:
            classes = await elem.get_attribute("class")
            tag = await elem.evaluate("el => el.tagName")
            visible = await elem.evaluate("el => el.offsetHeight > 0")
            print(f"  {tag}: visible={visible}")
            print(f"    Classes: {classes[:100]}...")
        
        dialogs = await mobile_page.query_selector_all("[role='dialog']")
        print(f"\nDialog elements: {len(dialogs)}")
        
        for i, dialog in enumerate(dialogs):
            classes = await dialog.get_attribute("class")
            print(f"  Dialog {i+1}: {classes[:80]}...")
        
        await mobile_page.screenshot(path="/tmp/mobile_diagnostic.png")
        print("\n✓ Mobile screenshot: /tmp/mobile_diagnostic.png")
        await mobile_ctx.close()
        
        # Desktop
        print("\n💻 DESKTOP (1280x720)")
        desktop_ctx = await browser.new_context(viewport={"width": 1280, "height": 720})
        desktop_page = await desktop_ctx.new_page()
        await desktop_page.goto("http://localhost:5173", wait_until="networkidle")
        await desktop_page.wait_for_timeout(1000)
        
        # Find all elements with "fixed" or "dialog" classes
        fixed_elements = await desktop_page.query_selector_all("[class*='fixed']")
        print(f"Elements with 'fixed' class: {len(fixed_elements)}")
        
        for elem in fixed_elements:
            classes = await elem.get_attribute("class")
            tag = await elem.evaluate("el => el.tagName")
            visible = await elem.evaluate("el => el.offsetHeight > 0")
            print(f"  {tag}: visible={visible}")
            print(f"    Classes: {classes[:100]}...")
        
        dialogs = await desktop_page.query_selector_all("[role='dialog']")
        print(f"\nDialog elements: {len(dialogs)}")
        
        for i, dialog in enumerate(dialogs):
            classes = await dialog.get_attribute("class")
            box = await dialog.bounding_box()
            print(f"  Dialog {i+1}:")
            print(f"    Classes: {classes[:80]}...")
            if box:
                print(f"    Position: x={box['x']:.0f}, y={box['y']:.0f}, w={box['width']:.0f}, h={box['height']:.0f}")
        
        await desktop_page.screenshot(path="/tmp/desktop_diagnostic.png")
        print("\n✓ Desktop screenshot: /tmp/desktop_diagnostic.png")
        await desktop_ctx.close()
        
        await browser.close()
        
        print("\n" + "=" * 80)
        print("✓ Diagnostic complete. Check screenshots for visual verification.")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(diagnose_popup_css())
