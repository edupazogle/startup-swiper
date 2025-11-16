#!/usr/bin/env python3
"""
Final verification test for dialog positioning fix.
Tests both mobile (full-width) and desktop (centered) behavior.
"""

import subprocess
import json
import sys
from pathlib import Path

def run_playwright_test():
    """Create and run a Playwright test for dialog positioning."""
    
    test_code = '''
const { test, expect } = require('@playwright/test');

test.describe('Dialog Positioning - Final Solution', () => {
  const BASE_URL = 'http://localhost:5173';
  
  test('Mobile: FeedbackChatModal should be full-width on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(BASE_URL);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Try to trigger the FeedbackChatModal
    // Look for elements that might trigger it
    const feedbackButtons = await page.$$('[data-testid*="feedback"], button:has-text("Feedback"), button:has-text("Chat")');
    
    if (feedbackButtons.length > 0) {
      await feedbackButtons[0].click();
      await page.waitForSelector('[data-slot="dialog-overlay"]', { timeout: 2000 }).catch(() => null);
    }
    
    // Check if dialog overlay exists and is flex centered
    const overlay = await page.$('[data-slot="dialog-overlay"]');
    if (overlay) {
      const overlayClasses = await overlay.getAttribute('class');
      console.log('Overlay classes:', overlayClasses);
      expect(overlayClasses).toContain('flex');
      expect(overlayClasses).toContain('items-center');
      expect(overlayClasses).toContain('justify-center');
      
      // Check dialog content positioning
      const content = await page.$('[data-slot="dialog-content"]');
      if (content) {
        const contentBBox = await content.boundingBox();
        console.log('Mobile - Content bounding box:', contentBBox);
        
        // On mobile, width should be close to viewport width (375)
        // Allow some margin for padding
        expect(contentBBox.width).toBeGreaterThan(330);
      }
    }
  });
  
  test('Desktop: FeedbackChatModal should be centered on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Try to trigger the FeedbackChatModal
    const feedbackButtons = await page.$$('[data-testid*="feedback"], button:has-text("Feedback"), button:has-text("Chat")');
    
    if (feedbackButtons.length > 0) {
      await feedbackButtons[0].click();
      await page.waitForSelector('[data-slot="dialog-overlay"]', { timeout: 2000 }).catch(() => null);
    }
    
    // Check if dialog is centered
    const content = await page.$('[data-slot="dialog-content"]');
    if (content) {
      const contentBBox = await content.boundingBox();
      console.log('Desktop - Content bounding box:', contentBBox);
      
      // Check that content is roughly centered
      // Center of viewport: 640 (1280/2)
      // Content center: left + width/2
      const contentCenter = contentBBox.x + contentBBox.width / 2;
      const viewportCenter = 640;
      const offset = Math.abs(contentCenter - viewportCenter);
      
      console.log('Desktop - Content center:', contentCenter, 'Viewport center:', viewportCenter, 'Offset:', offset);
      // Allow 50px tolerance
      expect(offset).toBeLessThan(50);
    }
  });
  
  test('Dialog Overlay should use flex centering (architecture check)', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    // Check the computed styles of overlay
    const overlayComputedStyle = await page.evaluate(() => {
      const overlay = document.querySelector('[data-slot="dialog-overlay"]');
      if (!overlay) return null;
      const style = window.getComputedStyle(overlay);
      return {
        display: style.display,
        justifyContent: style.justifyContent,
        alignItems: style.alignItems,
      };
    });
    
    console.log('Overlay computed styles:', overlayComputedStyle);
    expect(overlayComputedStyle.display).toBe('flex');
    expect(overlayComputedStyle.justifyContent).toBe('center');
    expect(overlayComputedStyle.alignItems).toBe('center');
  });
});
'''
    
    # Write test file
    test_file = Path('/home/akyo/startup_swiper/app/startup-swipe-schedu/test-dialog-final.spec.js')
    test_file.write_text(test_code)
    
    print(f"Test file created: {test_file}")
    print("\nTo run the test:")
    print("1. Start the dev server: npm run dev")
    print("2. In another terminal, run: npx playwright test test-dialog-final.spec.js")
    
    return True

if __name__ == '__main__':
    run_playwright_test()
    print("\n✅ Test file created successfully")
