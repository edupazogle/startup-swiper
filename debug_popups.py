#!/usr/bin/env python3
"""Playwright test to debug popup positioning on mobile and desktop"""
import asyncio
import json
from playwright.async_api import async_playwright


async def test_popup_positioning():
    """Test popup positioning on mobile and desktop viewports"""
    async with async_playwright() as p:
        # Use system Chromium
        browser = await p.chromium.launch(
            executable_path="/snap/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        results = {"mobile": {}, "desktop": {}}
        
        # ===== MOBILE TEST =====
        print("\n" + "=" * 80)
        print("MOBILE TEST (375x667)")
        print("=" * 80)
        
        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)"
        )
        mobile_page = await mobile_context.new_page()
        
        try:
            print("[Mobile] Loading page...")
            await mobile_page.goto("http://localhost:5173", wait_until="networkidle", timeout=30000)
            await mobile_page.wait_for_timeout(2000)
            
            viewport = mobile_page.viewport_size
            if not viewport:
                # Fallback to context viewport
                context_viewport = mobile_context.viewport
                viewport = {"width": context_viewport["width"], "height": context_viewport["height"]}
            print(f"[Mobile] Viewport: {viewport['width']}x{viewport['height']}")
            
            # Check StartupChat
            chat_container = await mobile_page.query_selector(".fixed.w-full")
            if chat_container:
                box = await chat_container.bounding_box()
                print(f"[Mobile] ✓ Found chat container")
                print(f"  Size: {box['width']:.0f}x{box['height']:.0f}")
                offset = viewport['height'] - (box['y'] + box['height'])
                print(f"  Space from bottom: {offset:.0f}px (target: 80px)")
                results["mobile"]["chat"] = {"found": True, "bottom_offset": offset}
            else:
                print("[Mobile] ✗ Chat container not found")
                results["mobile"]["chat"] = {"found": False}
            
            # Check dialogs
            dialogs = await mobile_page.query_selector_all("[role='dialog']")
            print(f"[Mobile] Found {len(dialogs)} dialog(s)")
            
            for i, dialog in enumerate(dialogs):
                box = await dialog.bounding_box()
                offset = viewport['height'] - (box['y'] + box['height'])
                is_correct = 70 <= offset <= 90
                print(f"[Mobile] Dialog {i+1}: {offset:.0f}px offset {'✓' if is_correct else '✗'}")
                results["mobile"][f"dialog_{i}"] = {"bottom_offset": offset, "correct": is_correct}
            
            await mobile_page.screenshot(path="/tmp/mobile_test.png")
            print("[Mobile] ✓ Screenshot: /tmp/mobile_test.png")
            
        except Exception as e:
            print(f"[Mobile] ✗ Error: {e}")
            results["mobile"]["error"] = str(e)
        finally:
            await mobile_context.close()
        
        # ===== DESKTOP TEST =====
        print("\n" + "=" * 80)
        print("DESKTOP TEST (1280x720)")
        print("=" * 80)
        
        desktop_context = await browser.new_context(viewport={"width": 1280, "height": 720})
        desktop_page = await desktop_context.new_page()
        
        try:
            print("[Desktop] Loading page...")
            await desktop_page.goto("http://localhost:5173", wait_until="networkidle", timeout=30000)
            await desktop_page.wait_for_timeout(2000)
            
            viewport = desktop_page.viewport_size
            if not viewport:
                viewport = {"width": 1280, "height": 720}
            print(f"[Desktop] Viewport: {viewport['width']}x{viewport['height']}")
            
            # Check dialogs
            dialogs = await desktop_page.query_selector_all("[role='dialog']")
            print(f"[Desktop] Found {len(dialogs)} dialog(s)")
            
            for i, dialog in enumerate(dialogs):
                box = await dialog.bounding_box()
                if box is None:
                    print(f"[Desktop] Dialog {i+1}: not visible")
                    continue
                
                center_x = box['x'] + box['width'] / 2
                center_y = box['y'] + box['height'] / 2
                viewport_center_x = viewport['width'] / 2
                viewport_center_y = viewport['height'] / 2
                offset_x = abs(center_x - viewport_center_x)
                offset_y = abs(center_y - viewport_center_y)
                is_centered = offset_x < 50 and offset_y < 50
                
                print(f"[Desktop] Dialog {i+1}: offset ({offset_x:.0f}, {offset_y:.0f}) {'✓ CENTERED' if is_centered else '✗ OFF'}")
                results["desktop"][f"dialog_{i}"] = {
                    "offset_x": offset_x,
                    "offset_y": offset_y,
                    "centered": is_centered
                }
            
            await desktop_page.screenshot(path="/tmp/desktop_test.png")
            print("[Desktop] ✓ Screenshot: /tmp/desktop_test.png")
            
        except Exception as e:
            print(f"[Desktop] ✗ Error: {e}")
            results["desktop"]["error"] = str(e)
        finally:
            await desktop_context.close()
        
        await browser.close()
        
        # ===== SUMMARY =====
        print("\n" + "=" * 80)
        print("VERDICT")
        print("=" * 80)
        
        with open("/tmp/popup_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print("\n✓ Results saved to: /tmp/popup_test_results.json")


if __name__ == "__main__":
    print("\n🎬 Starting test...\n")
    asyncio.run(test_popup_positioning())
    print("\n🎬 Done!\n")
