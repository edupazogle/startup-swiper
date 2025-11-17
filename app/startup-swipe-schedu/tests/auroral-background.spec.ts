import { test, expect } from '@playwright/test';

test.describe('Auroral Background Integration', () => {
  test('Platform review page has auroral-northern-dusk background', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Navigate to platform review/dashboard
    const dashboardButton = page.locator('button:has-text("Dashboard")').or(page.locator('a[href*="dashboard"]'));
    if (await dashboardButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await dashboardButton.click();
      await page.waitForLoadState('networkidle');
    }
    
    // Check for auroral background
    const auroralLayer = page.locator('.auroral-layer.auroral-northern-dusk');
    await expect(auroralLayer).toBeVisible();
    
    // Verify it's positioned correctly
    await expect(auroralLayer).toHaveClass(/fixed|absolute/);
    await expect(auroralLayer).toHaveClass(/inset-0/);
  });

  test('AI Concierge has auroral-northern-intense background', async ({ page }) => {
    await page.goto('/');
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    // Check for auroral background in modal
    const auroralLayer = page.locator('.auroral-layer.auroral-northern-intense');
    await expect(auroralLayer).toBeVisible();
    
    // Should be positioned absolutely within modal
    await expect(auroralLayer).toHaveClass(/absolute/);
    await expect(auroralLayer).toHaveClass(/inset-0/);
    
    // Should have pointer-events-none to not interfere
    await expect(auroralLayer).toHaveClass(/pointer-events-none/);
  });

  test('Insights modal has auroral-northern-intense background', async ({ page }) => {
    await page.goto('/');
    
    // Try to access insights modal
    const insightsButton = page.locator('button:has-text("Insights AI")').first();
    if (await insightsButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await insightsButton.click();
      await page.waitForSelector('[role="dialog"]', { state: 'visible' });
      
      const auroralLayer = page.locator('.auroral-layer.auroral-northern-intense');
      await expect(auroralLayer).toBeVisible();
      await expect(auroralLayer).toHaveClass(/pointer-events-none/);
    }
  });

  test('Auroral background animates smoothly', async ({ page }) => {
    await page.goto('/');
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const auroralLayer = page.locator('.auroral-layer').first();
    
    // Check for animation properties
    const animationName = await auroralLayer.evaluate(el => 
      window.getComputedStyle(el).animationName
    );
    expect(animationName).toContain('northern');
    
    const animationDuration = await auroralLayer.evaluate(el => 
      window.getComputedStyle(el).animationDuration
    );
    expect(animationDuration).not.toBe('0s');
  });

  test('Content is readable over auroral background', async ({ page }) => {
    await page.goto('/');
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    // Check that text is visible and has good contrast
    const headerText = page.locator('[role="dialog"] h2, [role="dialog"] [class*="DialogTitle"]').first();
    await expect(headerText).toBeVisible();
    
    // Text should have light color over dark background
    const color = await headerText.evaluate(el => 
      window.getComputedStyle(el).color
    );
    // Should be light (RGB values > 200)
    expect(color).toMatch(/rgb\((2[0-4][0-9]|25[0-5]),\s*(2[0-4][0-9]|25[0-5]),\s*(2[0-4][0-9]|25[0-5])\)/);
  });
});

test.describe('Mobile Performance and Responsiveness', () => {
  test('Chat modals are full screen on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
    await page.goto('/');
    
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const modal = page.locator('[role="dialog"]').first();
    await expect(modal).toHaveClass(/h-screen/);
    await expect(modal).toHaveClass(/rounded-none/);
  });

  test('Performance: Page loads within acceptable time on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Should load within 5 seconds on mobile
    expect(loadTime).toBeLessThan(5000);
  });

  test('Modal opens quickly without blocking UI', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const startTime = Date.now();
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    const openTime = Date.now() - startTime;
    
    // Modal should open within 1 second
    expect(openTime).toBeLessThan(1000);
  });

  test('Touch interactions work correctly', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    
    // Simulate touch interaction
    await chatInput.tap();
    await chatInput.fill('Touch test message');
    
    const value = await chatInput.inputValue();
    expect(value).toBe('Touch test message');
  });

  test('iOS Safari viewport handling', async ({ page, browserName }) => {
    // Simulate iOS Safari
    await page.setViewportSize({ width: 375, height: 812 }); // iPhone X
    await page.goto('/');
    
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    // Modal should handle iOS safe areas
    const modal = page.locator('[role="dialog"]').first();
    const modalBox = await modal.boundingBox();
    
    expect(modalBox).not.toBeNull();
    expect(modalBox!.height).toBeGreaterThan(700); // Accounts for notch
  });

  test('Keyboard appearance does not break layout on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const inputArea = page.locator('div.flex-shrink-0:has(textarea)').first();
    const beforeKeyboardBox = await inputArea.boundingBox();
    
    // Focus input (simulates keyboard appearing)
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.focus();
    await page.waitForTimeout(500);
    
    const afterKeyboardBox = await inputArea.boundingBox();
    
    // Input should still be visible and at reasonable position
    expect(afterKeyboardBox).not.toBeNull();
    expect(afterKeyboardBox!.y).toBeGreaterThan(0);
    expect(afterKeyboardBox!.y).toBeLessThan(beforeKeyboardBox!.y + 100); // Some shift is ok
  });
});

test.describe('Cross-browser Compatibility', () => {
  test('Works on different browsers', async ({ page, browserName }) => {
    await page.goto('/');
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const auroralLayer = page.locator('.auroral-layer').first();
    await expect(auroralLayer).toBeVisible();
    
    // Check animation works across browsers
    const hasAnimation = await auroralLayer.evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.animationName !== 'none';
    });
    
    expect(hasAnimation).toBe(true);
  });
});
