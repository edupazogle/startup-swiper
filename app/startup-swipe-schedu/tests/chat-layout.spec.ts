import { test, expect } from '@playwright/test';

test.describe('Chat Input Layout Stability', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('AI Concierge chat input stays fixed at bottom after sending message', async ({ page }) => {
    // Navigate to AI Concierge
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/01-homepage.png', fullPage: true });
    
    await page.click('button:has-text("AI Concierge")');
    
    // Wait for modal to open
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'test-results/02-modal-opened.png', fullPage: true });
    
    // Find the chat input
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await expect(chatInput).toBeVisible();
    
    // Get initial position of input area
    const inputArea = page.locator('div.flex-shrink-0:has(textarea)').first();
    const initialBox = await inputArea.boundingBox();
    expect(initialBox).not.toBeNull();
    console.log('Initial input position:', initialBox);
    
    // Type a message
    await chatInput.fill('Test message to check layout stability');
    await page.waitForTimeout(300);
    await page.screenshot({ path: 'test-results/03-after-typing.png', fullPage: true });
    
    // Get position after typing
    const afterTypingBox = await inputArea.boundingBox();
    expect(afterTypingBox).not.toBeNull();
    console.log('After typing position:', afterTypingBox);
    
    // Input should not move while typing
    expect(Math.abs(afterTypingBox!.y - initialBox!.y)).toBeLessThan(5);
    
    // Send the message - try multiple selectors
    const sendButton = page.locator('button[type="button"]').filter({ hasText: /send|arrow|➤/i }).or(
      page.locator('button svg').locator('..').filter({ has: page.locator('svg') })
    ).first();
    await sendButton.click();
    
    // Wait a bit for any layout shifts
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'test-results/04-after-sending.png', fullPage: true });
    
    // Get position after sending
    const afterSendingBox = await inputArea.boundingBox();
    expect(afterSendingBox).not.toBeNull();
    console.log('After sending position:', afterSendingBox);
    
    // Calculate position difference
    const yDiff = Math.abs(afterSendingBox!.y - initialBox!.y);
    console.log('Y position difference:', yDiff);
    
    // Input should stay at the same position (within 5px tolerance)
    expect(yDiff).toBeLessThan(5);
    expect(Math.abs(afterSendingBox!.height - initialBox!.height)).toBeLessThan(5);
    
    await page.screenshot({ path: 'test-results/05-final-state.png', fullPage: true });
  });

  test('Insights modal chat input stays fixed after sending message', async ({ page }) => {
    // Login first if needed
    const loginButton = page.locator('button:has-text("Login")');
    if (await loginButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await page.fill('input[type="email"]', 'test@example.com');
      await page.fill('input[type="password"]', 'password123');
      await page.click('button:has-text("Login")');
      await page.waitForLoadState('networkidle');
    }
    
    // Navigate to startups view
    await page.click('button:has-text("Swipe")').catch(() => {});
    await page.waitForTimeout(1000);
    
    // Click on Insights AI button (may need to adjust selector)
    const insightsButton = page.locator('button:has-text("Insights AI")').first();
    if (await insightsButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await insightsButton.click();
      
      // Wait for modal to open
      await page.waitForSelector('[role="dialog"]', { state: 'visible' });
      
      // Find the chat input
      const chatInput = page.locator('textarea[placeholder*="insights"]').first();
      await expect(chatInput).toBeVisible();
      
      // Get initial position
      const inputArea = page.locator('div.flex-shrink-0:has(textarea)').first();
      const initialBox = await inputArea.boundingBox();
      expect(initialBox).not.toBeNull();
      
      // Type and send message
      await chatInput.fill('Test insight message');
      await page.waitForTimeout(200);
      
      const beforeSendBox = await inputArea.boundingBox();
      
      // Send message
      await page.click('button[class*="gradient"]:has-text("")');
      await page.waitForTimeout(500);
      
      // Check position stability
      const afterSendBox = await inputArea.boundingBox();
      expect(afterSendBox).not.toBeNull();
      expect(Math.abs(afterSendBox!.y - beforeSendBox!.y)).toBeLessThan(5);
    }
  });

  test('Auroral background does not interfere with input interactions', async ({ page }) => {
    // Open AI Concierge
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    // Check that auroral background has pointer-events-none
    const auroralBg = page.locator('.auroral-layer').first();
    await expect(auroralBg).toHaveClass(/pointer-events-none/);
    
    // Verify input is still interactive
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.click();
    await chatInput.fill('Testing pointer events');
    
    const value = await chatInput.inputValue();
    expect(value).toBe('Testing pointer events');
  });

  test('Chat messages container scrolls properly without affecting input', async ({ page }) => {
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    const inputArea = page.locator('div.flex-shrink-0:has(textarea)').first();
    const initialBox = await inputArea.boundingBox();
    
    // Send multiple messages to create scroll
    for (let i = 0; i < 5; i++) {
      await chatInput.fill(`Test message ${i + 1}`);
      await page.click('button[type="button"]:has-text("")');
      await page.waitForTimeout(300);
    }
    
    // Input should still be at the same position
    const finalBox = await inputArea.boundingBox();
    expect(Math.abs(finalBox!.y - initialBox!.y)).toBeLessThan(5);
    
    // Messages container should be scrollable
    const messagesContainer = page.locator('div.flex-1.overflow-y-auto').first();
    await expect(messagesContainer).toBeVisible();
  });

  test('Modal is full screen on mobile viewport', async ({ page, browserName }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    // On mobile, modal should be full screen
    const modal = page.locator('[role="dialog"]').first();
    const modalBox = await modal.boundingBox();
    
    expect(modalBox).not.toBeNull();
    expect(modalBox!.width).toBeGreaterThan(350); // Almost full width
    expect(modalBox!.height).toBeGreaterThan(600); // Almost full height
  });

  test('Textarea auto-resizes without breaking layout', async ({ page }) => {
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    const inputArea = page.locator('div.flex-shrink-0:has(textarea)').first();
    
    const initialInputAreaBox = await inputArea.boundingBox();
    const initialTextareaBox = await chatInput.boundingBox();
    
    // Type multiple lines
    await chatInput.fill('Line 1\nLine 2\nLine 3\nLine 4\nLine 5');
    await page.waitForTimeout(200);
    
    const afterTextareaBox = await chatInput.boundingBox();
    const afterInputAreaBox = await inputArea.boundingBox();
    
    // Textarea should grow
    expect(afterTextareaBox!.height).toBeGreaterThan(initialTextareaBox!.height);
    
    // Input area should stay at bottom (y position should be similar)
    expect(Math.abs(afterInputAreaBox!.y - initialInputAreaBox!.y)).toBeLessThan(10);
  });

  test('Close button works and cleans up properly', async ({ page }) => {
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    // Send a message
    const chatInput = page.locator('textarea[placeholder*="message"]').first();
    await chatInput.fill('Test before closing');
    await page.click('button[type="button"]:has-text("")');
    await page.waitForTimeout(300);
    
    // Close modal
    await page.click('button[aria-label="Close"]').catch(() => 
      page.keyboard.press('Escape')
    );
    
    // Modal should be closed
    await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    
    // Reopen and verify it's in a clean state
    await page.click('button:has-text("AI Concierge")');
    await page.waitForSelector('[role="dialog"]', { state: 'visible' });
    
    const reopenedInput = page.locator('textarea[placeholder*="message"]').first();
    const value = await reopenedInput.inputValue();
    expect(value).toBe('');
  });
});
