import { test, expect } from '@playwright/test';

test('debug swiper layout', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:5000');
  
  // Wait for the page to load
  await page.waitForTimeout(2000);
  
  // Take a screenshot of the full page
  await page.screenshot({ path: 'layout-full.png', fullPage: true });
  
  // Get viewport size
  const viewport = page.viewportSize();
  console.log('Viewport:', viewport);
  
  // Check for the main container
  const mainContainer = page.locator('.flex-1.flex.flex-col.lg\\:flex-row').first();
  const mainBox = await mainContainer.boundingBox();
  console.log('Main container:', mainBox);
  
  // Check for left sidebar
  const leftSidebar = page.locator('.w-\\[320px\\]').first();
  const sidebarBox = await leftSidebar.boundingBox();
  console.log('Left sidebar:', sidebarBox);
  
  // Check for swiper card area
  const swiperArea = page.locator('.max-w-\\[1400px\\]').first();
  const swiperBox = await swiperArea.boundingBox();
  console.log('Swiper area:', swiperBox);
  
  // Check if elements are visible
  const sidebarVisible = await leftSidebar.isVisible();
  const swiperVisible = await swiperArea.isVisible();
  console.log('Sidebar visible:', sidebarVisible);
  console.log('Swiper visible:', swiperVisible);
  
  // Get computed styles
  const containerStyles = await mainContainer.evaluate((el) => {
    const computed = window.getComputedStyle(el);
    return {
      maxWidth: computed.maxWidth,
      display: computed.display,
      justifyContent: computed.justifyContent,
      gap: computed.gap,
      padding: computed.padding
    };
  });
  console.log('Container styles:', containerStyles);
  
  // Take a focused screenshot of the swiper area
  if (swiperBox) {
    await page.screenshot({ 
      path: 'layout-swiper.png',
      clip: {
        x: Math.max(0, swiperBox.x - 50),
        y: Math.max(0, swiperBox.y - 50),
        width: Math.min(swiperBox.width + 100, viewport!.width),
        height: Math.min(swiperBox.height + 100, viewport!.height)
      }
    });
  }
});
