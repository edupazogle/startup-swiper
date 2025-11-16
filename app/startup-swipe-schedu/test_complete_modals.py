#!/usr/bin/env python3
"""Comprehensive test of modal functionality and responsiveness."""

import asyncio
from playwright.async_api import async_playwright

async def test_complete_modals():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        print("=" * 70)
        print("COMPREHENSIVE MODAL FUNCTIONALITY TEST")
        print("=" * 70)
        
        for viewport_name, viewport in [("MOBILE", {'width': 375, 'height': 812}), ("DESKTOP", {'width': 1920, 'height': 1080})]:
            print(f"\n\n{'='*70}")
            print(f"{viewport_name} ({viewport['width']}x{viewport['height']})")
            print(f"{'='*70}\n")
            
            context = await browser.new_context(viewport=viewport)
            page = await context.new_page()
            
            try:
                # Navigate
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
                
                # Test Meeting AI Modal
                print("1. MEETING AI MODAL")
                print("-" * 70)
                meeting_buttons = await page.query_selector_all('button')
                for button in meeting_buttons:
                    text = await button.text_content()
                    if text and 'Meeting AI' in text:
                        await button.click()
                        await page.wait_for_timeout(2500)
                        break
                
                modal_info = await page.evaluate("""() => {
                    const content = document.querySelector('[data-slot="dialog-content"]');
                    const overlay = document.querySelector('[data-slot="dialog-overlay"]');
                    
                    if (!content || !overlay) return null;
                    
                    const content_rect = content.getBoundingClientRect();
                    const overlay_rect = overlay.getBoundingClientRect();
                    
                    const flexContainer = Array.from(content.querySelectorAll('div')).find(div => {
                        const classes = div.className;
                        return classes && classes.includes('flex-col') && classes.includes('md:flex-row');
                    });
                    
                    return {
                        modal_visible: content_rect.width > 0,
                        modal_size: {
                            width: Math.round(content_rect.width),
                            height: Math.round(content_rect.height)
                        },
                        modal_position: {
                            x: Math.round(content_rect.x),
                            y: Math.round(content_rect.y)
                        },
                        modal_center: {
                            x: Math.round(content_rect.x + content_rect.width / 2),
                            y: Math.round(content_rect.y + content_rect.height / 2)
                        },
                        viewport_center: {
                            x: Math.round(overlay_rect.width / 2),
                            y: Math.round(overlay_rect.height / 2)
                        },
                        overlay_visible: overlay_rect.width > 0,
                        columns_stacking: flexContainer ? window.getComputedStyle(flexContainer).flexDirection === 'column' : null,
                        overlay_opacity: window.getComputedStyle(overlay).opacity
                    };
                }""")
                
                if modal_info:
                    print(f"✓ Modal Visible: {modal_info['modal_visible']}")
                    print(f"✓ Modal Size: {modal_info['modal_size']['width']}x{modal_info['modal_size']['height']}")
                    print(f"✓ Modal Position: ({modal_info['modal_position']['x']}, {modal_info['modal_position']['y']})")
                    
                    center_match = (abs(modal_info['modal_center']['x'] - modal_info['viewport_center']['x']) < 10 and 
                                   abs(modal_info['modal_center']['y'] - modal_info['viewport_center']['y']) < 10)
                    print(f"{'✓' if center_match else '✗'} Modal Centered: {center_match}")
                    
                    print(f"✓ Overlay Visible: {modal_info['overlay_visible']}")
                    print(f"✓ Columns Stacking: {modal_info['columns_stacking']}")
                else:
                    print("✗ Could not get modal info")
                
                # Test closing
                print("\n2. MODAL CLOSING TEST")
                print("-" * 70)
                await page.keyboard.press('Escape')
                await page.wait_for_timeout(500)
                
                closed = await page.evaluate("""() => {
                    const content = document.querySelector('[data-slot="dialog-content"]');
                    if (!content) return true;
                    const rect = content.getBoundingClientRect();
                    return rect.width === 0 || window.getComputedStyle(content).display === 'none';
                }""")
                
                print(f"{'✓' if closed else '✗'} Modal closed with Escape: {closed}")
                
                # Test overlay visibility after close
                overlay_stuck = await page.evaluate("""() => {
                    const overlay = document.querySelector('[data-slot="dialog-overlay"]');
                    if (!overlay) return false;
                    const rect = overlay.getBoundingClientRect();
                    const visible = rect.width > 0 && window.getComputedStyle(overlay).opacity !== '0';
                    return visible;
                }""")
                
                print(f"{'✓' if not overlay_stuck else '✗'} No overlay stuck: {not overlay_stuck}")
                
                # Test Insights AI Modal
                print("\n3. INSIGHTS AI MODAL")
                print("-" * 70)
                insights_buttons = await page.query_selector_all('button')
                for button in insights_buttons:
                    text = await button.text_content()
                    if text and 'Insights AI' in text:
                        await button.click()
                        await page.wait_for_timeout(2500)
                        break
                
                insights_info = await page.evaluate("""() => {
                    const content = document.querySelector('[data-slot="dialog-content"]');
                    if (!content) return null;
                    
                    const rect = content.getBoundingClientRect();
                    return {
                        visible: rect.width > 0,
                        size: {
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        },
                        has_input: document.querySelector('textarea') !== null
                    };
                }""")
                
                if insights_info:
                    print(f"✓ Modal Visible: {insights_info['visible']}")
                    print(f"✓ Modal Size: {insights_info['size']['width']}x{insights_info['size']['height']}")
                    print(f"✓ Has Input Field: {insights_info['has_input']}")
                else:
                    print("✗ Could not open Insights AI modal")
                
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                await context.close()
        
        await browser.close()
        
        print("\n" + "=" * 70)
        print("✅ TESTING COMPLETE")
        print("=" * 70)

if __name__ == '__main__':
    asyncio.run(test_complete_modals())
