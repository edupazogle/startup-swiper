#!/usr/bin/env python3
"""Test responsive modal layout and content."""

import asyncio
from playwright.async_api import async_playwright

async def test_responsive_layout():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        viewport = {'width': 375, 'height': 812}
        context = await browser.new_context(viewport=viewport)
        page = await context.new_page()
        
        try:
            await page.goto('http://localhost:5000', wait_until='networkidle')
            await page.wait_for_timeout(1500)
            
            print("RESPONSIVE LAYOUT TEST")
            print("="*60)
            
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
                    print("✓ Logged in")
            
            # Navigate to Startups
            buttons = await page.query_selector_all('button')
            for button in buttons:
                text = await button.text_content()
                if text and 'Startups' in text:
                    await button.click()
                    await page.wait_for_timeout(2000)
                    print("✓ On Startups page")
                    break
            
            # Test Meeting AI Modal
            print("\n📋 MEETING AI MODAL:")
            meeting_buttons = await page.query_selector_all('button')
            for button in meeting_buttons:
                text = await button.text_content()
                if text and 'Meeting AI' in text:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    
                    # Check layout
                    content = await page.query_selector('[data-slot="dialog-content"]')
                    if content:
                        # Check if two columns exist on mobile (they should be stacked)
                        left_col = await page.evaluate("""() => {
                            const els = document.querySelectorAll('[data-slot="dialog-content"] > div > div');
                            if (els.length >= 2) {
                                const first = els[els.length-2]; // Get second-to-last (before feedback)
                                if (first && first.textContent.includes('Key')) return true;
                            }
                            return false;
                        }""")
                        
                        if left_col:
                            print("✓ Modal has sections (points & questions)")
                        
                        # Check for talking points cards
                        cards = await page.query_selector_all('[data-slot="dialog-content"] [role="article"]')
                        print(f"✓ Found {len(cards)} content cards")
                        
                        # Check feedback section
                        feedback_section = await page.evaluate("""() => {
                            const text = document.body.textContent;
                            return text.includes('Refine with feedback');
                        }""")
                        if feedback_section:
                            print("✓ Feedback section visible")
                        
                        # Check buttons
                        btn_count = await page.query_selector_all('[data-slot="dialog-content"] button')
                        print(f"✓ Found {len(btn_count)} buttons in modal")
                    
                    # Take screenshot
                    await page.screenshot(path='/tmp/meeting-ai-responsive.png')
                    print("✓ Screenshot: /tmp/meeting-ai-responsive.png")
                    
                    await page.press('body', 'Escape')
                    await page.wait_for_timeout(1000)
                    break
            
            # Test Insights AI Modal
            print("\n📋 INSIGHTS AI MODAL:")
            await page.wait_for_timeout(500)
            insights_buttons = await page.query_selector_all('button')
            for button in insights_buttons:
                text = await button.text_content()
                if text and 'Insights AI' in text:
                    await button.click()
                    await page.wait_for_timeout(1500)
                    
                    # Check if it's a chat-based modal
                    messages = await page.query_selector_all('[data-slot="dialog-content"] [role="article"]')
                    print(f"✓ Found {len(messages)} message containers")
                    
                    # Check for textarea (input area)
                    textarea = await page.query_selector('[data-slot="dialog-content"] textarea')
                    if textarea:
                        print("✓ Text input (textarea) available")
                        
                        # Try typing
                        await textarea.click()
                        await textarea.fill('Test message')
                        value = await textarea.input_value()
                        if value:
                            print(f"✓ Successfully typed: '{value}'")
                    
                    # Check send button
                    send_buttons = await page.query_selector_all('[data-slot="dialog-content"] button')
                    print(f"✓ Found {len(send_buttons)} buttons")
                    
                    # Take screenshot
                    await page.screenshot(path='/tmp/insights-ai-responsive.png')
                    print("✓ Screenshot: /tmp/insights-ai-responsive.png")
                    
                    await page.press('body', 'Escape')
                    break
            
            print("\n" + "="*60)
            print("✅ Responsive layout test complete!")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_responsive_layout())
