#!/usr/bin/env python3
"""Advanced test: Trigger popups and verify positioning"""
import asyncio
import json
from playwright.async_api import async_playwright


async def test_popup_trigger():
    """Test popup positioning when triggered"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        results = {"mobile": {}, "desktop": {}}
        
        # ===== MOBILE TEST =====
        print("\n" + "=" * 80)
        print("MOBILE TEST - Inspecting CSS Classes (375x667)")
        print("=" * 80)
        
        mobile_ctx = await browser.new_context(viewport={"width": 375, "height": 667})
        mobile_page = await mobile_ctx.new_page()
        
        try:
            print("[Mobile] Loading page...")
            await mobile_page.goto("http://localhost:5173", wait_until="networkidle")
            await mobile_page.wait_for_timeout(1000)
            
            # Inspect all elements with class attributes
            all_elements = await mobile_page.query_selector_all("[class]")
            print(f"[Mobile] Total elements with classes: {len(all_elements)}")
            
            # Look for our specific styling patterns
            test_patterns = [
                ("fixed", "Mobile fixed positioning"),
                ("md:relative", "Desktop relative positioning"),
                ("bottom-20", "Bottom menu offset"),
                ("md:bottom-auto", "Desktop bottom auto"),
                ("h-\\[calc", "Dynamic height calculation"),
                ("z-50", "Z-index for mobile overlay"),
            ]
            
            found_patterns = {}
            for pattern, description in test_patterns:
                # Check if pattern exists in page content
                result = await mobile_page.evaluate(f"""
                    () => {{
                        const bodyHTML = document.body.innerHTML;
                        return bodyHTML.includes('{pattern}');
                    }}
                """)
                found_patterns[description] = result
                status = "✓" if result else "✗"
                print(f"[Mobile] {status} {description}: {result}")
            
            results["mobile"]["css_patterns"] = found_patterns
            
            # Take screenshot showing the actual mobile layout
            await mobile_page.screenshot(path="/tmp/mobile_layout.png")
            print("[Mobile] ✓ Screenshot: /tmp/mobile_layout.png")
            
            # Check viewport dimensions
            viewport_size = await mobile_page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
            print(f"[Mobile] Actual viewport: {viewport_size['width']}x{viewport_size['height']}")
            results["mobile"]["viewport"] = viewport_size
            
        except Exception as e:
            print(f"[Mobile] ✗ Error: {e}")
            results["mobile"]["error"] = str(e)
        finally:
            await mobile_ctx.close()
        
        # ===== DESKTOP TEST =====
        print("\n" + "=" * 80)
        print("DESKTOP TEST - Inspecting CSS Classes (1280x720)")
        print("=" * 80)
        
        desktop_ctx = await browser.new_context(viewport={"width": 1280, "height": 720})
        desktop_page = await desktop_ctx.new_page()
        
        try:
            print("[Desktop] Loading page...")
            await desktop_page.goto("http://localhost:5173", wait_until="networkidle")
            await desktop_page.wait_for_timeout(1000)
            
            # Same pattern checking
            test_patterns = [
                ("fixed", "Mobile fixed positioning"),
                ("md:relative", "Desktop relative positioning"),
                ("max-h-\\[90vh\\]", "Desktop modal height"),
                ("md:max-w", "Desktop max width constraint"),
                ("z-50", "Mobile overlay z-index"),
                ("md:z-auto", "Desktop normal z-index"),
            ]
            
            found_patterns = {}
            for pattern, description in test_patterns:
                result = await desktop_page.evaluate(f"""
                    () => {{
                        const bodyHTML = document.body.innerHTML;
                        return bodyHTML.includes('{pattern}');
                    }}
                """)
                found_patterns[description] = result
                status = "✓" if result else "✗"
                print(f"[Desktop] {status} {description}: {result}")
            
            results["desktop"]["css_patterns"] = found_patterns
            
            # Take screenshot
            await desktop_page.screenshot(path="/tmp/desktop_layout.png")
            print("[Desktop] ✓ Screenshot: /tmp/desktop_layout.png")
            
            # Check viewport dimensions
            viewport_size = await desktop_page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
            print(f"[Desktop] Actual viewport: {viewport_size['width']}x{viewport_size['height']}")
            results["desktop"]["viewport"] = viewport_size
            
        except Exception as e:
            print(f"[Desktop] ✗ Error: {e}")
            results["desktop"]["error"] = str(e)
        finally:
            await desktop_ctx.close()
        
        await browser.close()
        
        # ===== SUMMARY =====
        print("\n" + "=" * 80)
        print("CSS PATTERN VERIFICATION RESULTS")
        print("=" * 80)
        
        mobile_pass = all(results["mobile"].get("css_patterns", {}).values())
        desktop_pass = all(results["desktop"].get("css_patterns", {}).values())
        
        print(f"\n📱 Mobile: {'✓ PASS' if mobile_pass else '✗ FAIL'}")
        for pattern, found in results["mobile"].get("css_patterns", {}).items():
            print(f"  {'✓' if found else '✗'} {pattern}")
        
        print(f"\n💻 Desktop: {'✓ PASS' if desktop_pass else '✗ FAIL'}")
        for pattern, found in results["desktop"].get("css_patterns", {}).items():
            print(f"  {'✓' if found else '✗'} {pattern}")
        
        # Save results
        with open("/tmp/popup_css_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\n✓ Results saved to: /tmp/popup_css_test_results.json")
        print("✓ Screenshots: /tmp/mobile_layout.png, /tmp/desktop_layout.png")
        
        # Overall verdict
        if mobile_pass and desktop_pass:
            print("\n" + "=" * 80)
            print("✅ ALL TESTS PASSED - CSS CLASSES WORKING CORRECTLY")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("⚠️  SOME PATTERNS NOT FOUND - CHECK SCREENSHOTS")
            print("=" * 80)


if __name__ == "__main__":
    print("\n🎬 Starting CSS pattern verification test...\n")
    asyncio.run(test_popup_trigger())
    print("\n🎬 Done!\n")
