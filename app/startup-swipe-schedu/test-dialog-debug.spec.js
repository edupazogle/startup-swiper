import { test, expect } from '@playwright/test';

test.describe('Dialog Positioning Debug - Visual Test', () => {
  const BASE_URL = 'http://localhost:5000';
  
  test('Mobile view - Check dialog overlay structure and positioning', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(BASE_URL);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Check if dialog overlay exists in DOM
    const overlayExists = await page.$('[data-slot="dialog-overlay"]');
    console.log('\n=== MOBILE VIEW ===');
    console.log('Overlay exists in DOM:', !!overlayExists);
    
    // Get dialog overlay computed styles
    const overlayStyles = await page.evaluate(() => {
      const overlay = document.querySelector('[data-slot="dialog-overlay"]');
      if (!overlay) return null;
      
      const styles = window.getComputedStyle(overlay);
      return {
        display: styles.display,
        position: styles.position,
        justifyContent: styles.justifyContent,
        alignItems: styles.alignItems,
        zIndex: styles.zIndex,
        backgroundColor: styles.backgroundColor,
        inset: `top: ${styles.top}, right: ${styles.right}, bottom: ${styles.bottom}, left: ${styles.left}`,
      };
    });
    
    console.log('Overlay computed styles:', overlayStyles);
    
    // Get dialog content styles
    const contentStyles = await page.evaluate(() => {
      const content = document.querySelector('[data-slot="dialog-content"]');
      if (!content) return null;
      
      const styles = window.getComputedStyle(content);
      const bbox = content.getBoundingClientRect();
      
      return {
        display: styles.display,
        position: styles.position,
        width: `${bbox.width}px`,
        height: `${bbox.height}px`,
        top: `${bbox.top}px`,
        left: `${bbox.left}px`,
        maxWidth: styles.maxWidth,
        padding: styles.padding,
        border: styles.border,
      };
    });
    
    console.log('Dialog content styles:', contentStyles);
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/mobile-dialog-view.png', fullPage: false });
    console.log('Screenshot saved: /tmp/mobile-dialog-view.png');
  });
  
  test('Desktop view - Check dialog overlay structure and positioning', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto(BASE_URL);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    console.log('\n=== DESKTOP VIEW ===');
    
    // Check if dialog overlay exists in DOM
    const overlayExists = await page.$('[data-slot="dialog-overlay"]');
    console.log('Overlay exists in DOM:', !!overlayExists);
    
    // Get dialog overlay computed styles
    const overlayStyles = await page.evaluate(() => {
      const overlay = document.querySelector('[data-slot="dialog-overlay"]');
      if (!overlay) return null;
      
      const styles = window.getComputedStyle(overlay);
      return {
        display: styles.display,
        position: styles.position,
        justifyContent: styles.justifyContent,
        alignItems: styles.alignItems,
        zIndex: styles.zIndex,
        backgroundColor: styles.backgroundColor,
        inset: `top: ${styles.top}, right: ${styles.right}, bottom: ${styles.bottom}, left: ${styles.left}`,
      };
    });
    
    console.log('Overlay computed styles:', overlayStyles);
    
    // Get dialog content styles
    const contentStyles = await page.evaluate(() => {
      const content = document.querySelector('[data-slot="dialog-content"]');
      if (!content) return null;
      
      const styles = window.getComputedStyle(content);
      const bbox = content.getBoundingClientRect();
      
      return {
        display: styles.display,
        position: styles.position,
        width: `${bbox.width}px`,
        height: `${bbox.height}px`,
        top: `${bbox.top}px`,
        left: `${bbox.left}px`,
        maxWidth: styles.maxWidth,
        padding: styles.padding,
        border: styles.border,
      };
    });
    
    console.log('Dialog content styles:', contentStyles);
    
    // Take screenshot
    await page.screenshot({ path: '/tmp/desktop-dialog-view.png', fullPage: false });
    console.log('Screenshot saved: /tmp/desktop-dialog-view.png');
  });

  test('Check HTML structure of dialog components', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    
    console.log('\n=== HTML STRUCTURE ===');
    
    // Get the dialog HTML structure
    const dialogHTML = await page.evaluate(() => {
      const dialog = document.querySelector('[data-slot="dialog-overlay"]');
      if (!dialog) return 'Dialog overlay not found in DOM';
      
      // Get parent structure
      return {
        overlayTag: dialog.tagName,
        overlayClasses: dialog.className,
        contentTag: dialog.querySelector('[data-slot="dialog-content"]')?.tagName,
        contentClasses: dialog.querySelector('[data-slot="dialog-content"]')?.className,
      };
    });
    
    console.log('Dialog HTML structure:', dialogHTML);
  });
});
