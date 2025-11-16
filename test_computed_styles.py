#!/usr/bin/env python3
"""Test computed CSS styles directly - ignores minification"""
import asyncio
from playwright.async_api import async_playwright


async def test_computed_styles():
    """Test actual computed CSS styles on elements"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        print("\n" + "=" * 80)
        print("COMPUTED CSS STYLES TEST")
        print("=" * 80)
        
        # ===== MOBILE TEST =====
        print("\n📱 MOBILE (375x667)")
        mobile_ctx = await browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = await mobile_ctx.new_page()
        
        await mobile_page.goto("http://localhost:5173", wait_until="networkidle")
        await mobile_page.wait_for_timeout(2000)
        
        # Check what CSS got applied to the body/main container
        computed = await mobile_page.evaluate("""
            () => {
                const root = document.querySelector('#root') || document.body;
                const style = window.getComputedStyle(root);
                return {
                    width: style.width,
                    height: style.height,
                    position: style.position,
                    display: style.display
                };
            }
        """)
        
        print(f"Root element computed styles:")
        print(f"  Width: {computed['width']}")
        print(f"  Height: {computed['height']}")
        print(f"  Position: {computed['position']}")
        print(f"  Display: {computed['display']}")
        
        # Check CSS file is loaded
        css_loaded = await mobile_page.evaluate("""
            () => {
                const links = document.querySelectorAll('link[rel="stylesheet"]');
                return {
                    css_files: links.length,
                    stylesheets: document.styleSheets.length
                };
            }
        """)
        print(f"\nCSS loaded: {css_loaded['css_files']} link tags, {css_loaded['stylesheets']} stylesheets")
        
        await mobile_page.screenshot(path="/tmp/mobile_computed_styles.png")
        print(f"✓ Screenshot: /tmp/mobile_computed_styles.png")
        await mobile_ctx.close()
        
        # ===== DESKTOP TEST =====
        print("\n💻 DESKTOP (1280x720)")
        desktop_ctx = await browser.new_context(viewport={"width": 1280, "height": 720})
        desktop_page = await desktop_ctx.new_page()
        
        await desktop_page.goto("http://localhost:5173", wait_until="networkidle")
        await desktop_page.wait_for_timeout(2000)
        
        # Check computed styles
        computed = await desktop_page.evaluate("""
            () => {
                const root = document.querySelector('#root') || document.body;
                const style = window.getComputedStyle(root);
                return {
                    width: style.width,
                    height: style.height,
                    position: style.position,
                    display: style.display
                };
            }
        """)
        
        print(f"Root element computed styles:")
        print(f"  Width: {computed['width']}")
        print(f"  Height: {computed['height']}")
        print(f"  Position: {computed['position']}")
        print(f"  Display: {computed['display']}")
        
        # Check CSS file is loaded
        css_loaded = await desktop_page.evaluate("""
            () => {
                const links = document.querySelectorAll('link[rel="stylesheet"]');
                return {
                    css_files: links.length,
                    stylesheets: document.styleSheets.length
                };
            }
        """)
        print(f"\nCSS loaded: {css_loaded['css_files']} link tags, {css_loaded['stylesheets']} stylesheets")
        
        await desktop_page.screenshot(path="/tmp/desktop_computed_styles.png")
        print(f"✓ Screenshot: /tmp/desktop_computed_styles.png")
        await desktop_ctx.close()
        
        await browser.close()
        
        print("\n" + "=" * 80)
        print("✅ COMPUTED STYLES TEST COMPLETE")
        print("=" * 80)
        print("\nScreenshots show actual rendered layout with CSS applied.")
        print("Visual inspection will confirm correct responsive behavior.")


if __name__ == "__main__":
    print("\n🎬 Testing computed CSS styles...\n")
    asyncio.run(test_computed_styles())
    print("\n🎬 Done!\n")
