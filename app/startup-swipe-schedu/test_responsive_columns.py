#!/usr/bin/env python3
"""Test responsive layout of columns on mobile."""

import asyncio
from playwright.async_api import async_playwright

async def test_responsive_columns():
    async with async_playwright() as p:
        # Test on mobile
        browser = await p.chromium.launch(headless=True)
        viewport = {'width': 375, 'height': 812}
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        
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
                    await page.wait_for_timeout(2500)
                    break
            
            # Get column positions
            layout_info = await page.evaluate("""() => {
                const container = document.querySelector('[data-slot="dialog-content"]');
                if (!container) return null;
                
                // Find the flex container with the two columns
                const flexContainer = Array.from(container.querySelectorAll('div')).find(div => {
                    const classes = div.className;
                    return classes && classes.includes('flex-col') && classes.includes('md:flex-row');
                });
                
                if (!flexContainer) return null;
                
                const rect = flexContainer.getBoundingClientRect();
                const children = flexContainer.children;
                
                return {
                    container: {
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        display: window.getComputedStyle(flexContainer).display,
                        flexDirection: window.getComputedStyle(flexContainer).flexDirection
                    },
                    columns: Array.from(children).map((child, i) => {
                        const childRect = child.getBoundingClientRect();
                        const heading = child.querySelector('h3');
                        return {
                            index: i,
                            name: heading ? heading.textContent.trim() : 'Unknown',
                            width: Math.round(childRect.width),
                            height: Math.round(childRect.height),
                            x: Math.round(childRect.left - rect.left)
                        };
                    })
                };
            }""")
            
            print("=" * 60)
            print("MOBILE (375x812) - RESPONSIVE LAYOUT TEST")
            print("=" * 60)
            
            if layout_info:
                print(f"\nFlexbox Container:")
                print(f"  Display: {layout_info['container']['display']}")
                print(f"  Flex Direction: {layout_info['container']['flexDirection']}")
                print(f"  Container Size: {layout_info['container']['width']}x{layout_info['container']['height']}")
                
                print(f"\nColumns ({len(layout_info['columns'])}):")
                for col in layout_info['columns']:
                    print(f"  Column {col['index'] + 1}: {col['name']}")
                    print(f"    Size: {col['width']}x{col['height']}")
                    print(f"    Position X: {col['x']}")
                    
                    # Check if columns are stacking (each should be ~full width on mobile)
                    if layout_info['columns'][0]['width'] > 300:
                        print(f"    ✓ Column is FULL WIDTH (stacking vertically)")
                    else:
                        print(f"    ✗ Column is NARROW (side-by-side layout)")
            else:
                print("Could not find flex container")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_responsive_columns())
