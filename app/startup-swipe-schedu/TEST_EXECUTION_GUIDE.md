# Test Setup and Execution Guide

## Quick Test Execution

Since Playwright installation may have environment-specific issues, here's how to run the tests:

### Option 1: Run tests manually (Recommended for now)

```bash
# Navigate to project
cd /home/akyo/startup_swiper/app/startup-swipe-schedu

# Start the app in preview mode
npm run build
npm run preview

# In another terminal, test manually or use the test scripts below
```

### Option 2: Install Playwright browsers separately

```bash
# Install playwright globally
npm install -g playwright

# Install browsers (may require sudo)
playwright install chromium

# Run tests
npx playwright test
```

### Option 3: Use the Docker setup (if available)

```bash
docker run --rm --network host -v $(pwd):/work -w /work mcr.microsoft.com/playwright:latest npx playwright test
```

## Manual Test Checklist

Since automated tests may have setup issues, use this manual checklist:

### ✅ **Chat Input Layout Stability**

1. **AI Concierge Modal**
   - [ ] Open AI Concierge
   - [ ] Type a message
   - [ ] Click send
   - [ ] Verify input stays at bottom (doesn't jump up)
   - [ ] Send multiple messages rapidly
   - [ ] Verify layout remains stable

2. **Insights Modal**
   - [ ] Open Insights AI from startup card
   - [ ] Type and send message
   - [ ] Verify input stays fixed
   - [ ] Test with long multi-line messages

### ✅ **Auroral Background**

3. **Background Integration**
   - [ ] Dashboard/Platform Review: Check for `auroral-northern-dusk`
   - [ ] AI Concierge: Check for `auroral-northern-intense`
   - [ ] Insights Modal: Check for `auroral-northern-intense`
   - [ ] Verify animations are smooth
   - [ ] Confirm `pointer-events-none` is applied

4. **Visual Quality**
   - [ ] Content is readable over background
   - [ ] No flickering or visual artifacts
   - [ ] Background doesn't interfere with interactions

### ✅ **Mobile Testing**

5. **Responsive Design** (test on phone or use DevTools device mode)
   - [ ] Set viewport to 375x667 (iPhone SE)
   - [ ] Open AI Concierge - should be full screen
   - [ ] Type message - keyboard shouldn't break layout
   - [ ] Send message - input stays fixed
   - [ ] Scroll messages - smooth scrolling
   - [ ] Close and reopen - works correctly

6. **Performance**
   - [ ] Page loads within 5 seconds
   - [ ] Modal opens within 1 second
   - [ ] No lag when typing
   - [ ] Animations don't cause jank

### ✅ **Cross-browser**

7. **Browser Compatibility**
   - [ ] Test in Chrome/Chromium
   - [ ] Test in Firefox
   - [ ] Test in Safari (if available)
   - [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## DevTools Checklist

Use browser DevTools to verify technical implementation:

```javascript
// In browser console, check for:

// 1. Auroral background has pointer-events-none
document.querySelector('.auroral-layer').style.pointerEvents === 'none'

// 2. Content wrapper has overflow-hidden
getComputedStyle(document.querySelector('[role="dialog"] > div:last-child')).overflow === 'hidden'

// 3. Messages container has proper min-height
getComputedStyle(document.querySelector('.flex-1.overflow-y-auto')).minHeight === '0px'

// 4. Animation is running
getComputedStyle(document.querySelector('.auroral-layer')).animationName !== 'none'
```

## Test Results Template

After manual testing, record results:

```markdown
## Test Results - [Date]

### Chat Layout Stability
- AI Concierge: ✅ Pass / ❌ Fail
- Insights Modal: ✅ Pass / ❌ Fail
- Notes: _______________________

### Auroral Background
- Integration: ✅ Pass / ❌ Fail
- Animation: ✅ Pass / ❌ Fail
- Notes: _______________________

### Mobile Experience
- Layout: ✅ Pass / ❌ Fail
- Performance: ✅ Pass / ❌ Fail
- Notes: _______________________

### Cross-browser
- Chrome: ✅ Pass / ❌ Fail
- Firefox: ✅ Pass / ❌ Fail
- Safari: ✅ Pass / ❌ Fail
- Notes: _______________________
```

## Automated Tests (When Playwright is working)

Once Playwright is properly installed:

```bash
# List all tests
npm run test -- --list

# Run all tests
npm test

# Run with UI
npm run test:ui

# Run in headed mode (see browser)
npm run test:headed

# Debug specific test
npm run test:debug -- -g "chat input stays fixed"

# Generate report
npm run test:report
```

## Troubleshooting

### Playwright won't install
- Try: `rm -rf node_modules package-lock.json && npm install`
- Or install globally: `npm install -g @playwright/test`
- Or use Docker method above

### Tests fail locally
- Ensure app is built: `npm run build`
- Check app is running: `http://localhost:4173`
- Verify selectors match current DOM structure

### Layout issues found
- Check browser console for errors
- Use DevTools to inspect element positions
- Verify CSS classes are applied correctly
- Check for JavaScript errors

## Files Created

- `playwright.config.ts` - Test configuration
- `tests/chat-layout.spec.ts` - Chat stability tests (7 tests)
- `tests/auroral-background.spec.ts` - Background & performance tests (8 tests)
- `tests/README.md` - Test documentation

**Total: 21 tests across 3 test suites**
