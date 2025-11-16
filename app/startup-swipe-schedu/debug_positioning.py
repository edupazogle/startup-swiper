#!/usr/bin/env python3
"""Debug overlay and content positioning."""

import asyncio
from playwright.async_api import async_playwright

async def debug_positioning():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        viewport = {'width': 1920, 'height': 1080}
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
                    await page.wait_for_timeout(1500)
                    break
            
            # Debug overlay and content
            debug_info = await page.evaluate("""() => {
                const overlay = document.querySelector('[data-slot="dialog-overlay"]');
                const content = document.querySelector('[data-slot="dialog-content"]');
                
                const overlay_style = overlay ? window.getComputedStyle(overlay) : null;
                const content_style = content ? window.getComputedStyle(content) : null;
                
                const overlay_rect = overlay ? overlay.getBoundingClientRect() : null;
                const content_rect = content ? content.getBoundingClientRect() : null;
                const parent_rect = content ? content.parentElement.getBoundingClientRect() : null;
                
                return {
                    overlay: overlay ? {
                        display: overlay_style.display,
                        position: overlay_style.position,
                        zIndex: overlay_style.zIndex,
                        width: Math.round(overlay_rect.width),
                        height: Math.round(overlay_rect.height),
                        flexDirection: overlay_style.flexDirection,
                        justifyContent: overlay_style.justifyContent,
                        alignItems: overlay_style.alignItems
                    } : null,
                    content: content ? {
                        display: content_style.display,
                        position: content_style.position,
                        zIndex: content_style.zIndex,
                        width: Math.round(content_rect.width),
                        height: Math.round(content_rect.height),
                        top: Math.round(content_rect.top),
                        left: Math.round(content_rect.left)
                    } : null,
                    parent: parent_rect ? {
                        width: Math.round(parent_rect.width),
                        height: Math.round(parent_rect.height)
                    } : null
                };
            }""")
            
            print("OVERLAY STYLING:")
            if debug_info['overlay']:
                for key, value in debug_info['overlay'].items():
                    print(f"  {key}: {value}")
            
            print("\nCONTENT STYLING:")
            if debug_info['content']:
                for key, value in debug_info['content'].items():
                    print(f"  {key}: {value}")
            
            print("\nPARENT STYLING:")
            if debug_info['parent']:
                for key, value in debug_info['parent'].items():
                    print(f"  {key}: {value}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_positioning())
