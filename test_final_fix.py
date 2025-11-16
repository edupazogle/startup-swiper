#!/usr/bin/env python3
"""Final test to verify mobile popup is now full-width and centered"""
import asyncio
from playwright.async_api import async_playwright


async def test_final():
    """Verify the fixed popup positioning"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        print("\n" + "=" * 80)
        print("FINAL POPUP POSITIONING VERIFICATION")
        print("=" * 80)
        
        # Mobile test
        print("\n📱 Mobile (375x667)")
        mobile_ctx = await browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = await mobile_ctx.new_page()
        
        await mobile_page.goto("http://localhost:5173", wait_until="networkidle")
        await mobile_page.wait_for_timeout(2000)
        
        # Check computed styles of DialogContent
        styles = await mobile_page.evaluate("""
            () => {
                const content = document.querySelector('[data-slot="dialog-content"]');
                if (!content) {
                    const allElems = document.querySelectorAll('[class*="fixed"]');
                    return {found: false, element_count: allElems.length, total_elements: document.querySelectorAll('*').length};
                }
                const cs = window.getComputedStyle(content);
                const rect = content.getBoundingClientRect();
                return {
                    found: true,
                    position: cs.position,
                    width: cs.width,
                    height: cs.height,
                    top: cs.top,
                    left: cs.left,
                    right: cs.right,
                    bottom: cs.bottom,
                    bbox: {x: rect.x, y: rect.y, width: rect.width, height: rect.height}
                };
            }
        """)
        
        print(f"DialogContent found: {styles.get('found', False)}")
        if styles.get('found'):
            print(f"  Position: {styles['position']}")
            print(f"  Width: {styles['width']}")
            print(f"  Height: {styles['height']}")
            bbox = styles.get('bbox', {})
            print(f"  BBox: x={bbox.get('x'):.0f}, y={bbox.get('y'):.0f}, w={bbox.get('width'):.0f}, h={bbox.get('height'):.0f}")
            
            # Check if full width
            is_full_width = bbox.get('width', 0) >= 370
            is_full_height = bbox.get('height', 0) >= 580
            print(f"  ✓ Full width (370+px): {is_full_width}")
            print(f"  ✓ Full height (580+px): {is_full_height}")
            print(f"  Overall: {'✅ PASS' if (is_full_width and is_full_height) else '❌ FAIL'}")
        
        await mobile_page.screenshot(path="/tmp/final_mobile_test.png")
        print(f"  Screenshot: /tmp/final_mobile_test.png")
        await mobile_ctx.close()
        
        # Desktop test
        print("\n💻 Desktop (1280x720)")
        desktop_ctx = await browser.new_context(viewport={"width": 1280, "height": 720})
        desktop_page = await desktop_ctx.new_page()
        
        await desktop_page.goto("http://localhost:5173", wait_until="networkidle")
        await desktop_page.wait_for_timeout(2000)
        
        # Check computed styles
        styles = await desktop_page.evaluate("""
            () => {
                const content = document.querySelector('[data-slot="dialog-content"]');
                if (!content) return {found: false};
                const cs = window.getComputedStyle(content);
                const rect = content.getBoundingClientRect();
                return {
                    found: true,
                    position: cs.position,
                    width: cs.width,
                    bbox: {x: rect.x, y: rect.y, width: rect.width, height: rect.height}
                };
            }
        """)
        
        print(f"DialogContent found: {styles.get('found', False)}")
        if styles.get('found'):
            print(f"  Position: {styles['position']}")
            print(f"  Width: {styles['width']}")
            bbox = styles.get('bbox', {})
            center_x = bbox.get('x', 0) + bbox.get('width', 0) / 2
            expected_center = 640
            offset = abs(center_x - expected_center)
            is_centered = offset < 50
            print(f"  BBox center: {center_x:.0f}px (viewport center: {expected_center}px, offset: {offset:.0f}px)")
            print(f"  ✓ Centered: {is_centered}")
            print(f"  Overall: {'✅ PASS' if is_centered else '❌ FAIL'}")
        
        await desktop_page.screenshot(path="/tmp/final_desktop_test.png")
        print(f"  Screenshot: /tmp/final_desktop_test.png")
        await desktop_ctx.close()
        
        await browser.close()
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_final())
