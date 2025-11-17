# Playwright Test Suite

## Overview
Comprehensive test suite to verify chat layout stability, auroral background integration, and mobile performance.

## Test Files

### 1. `chat-layout.spec.ts`
Tests for chat input stability and layout integrity:
- ✅ Input stays fixed at bottom after sending messages
- ✅ Auroral background doesn't interfere with input
- ✅ Messages container scrolls properly
- ✅ Full-screen on mobile
- ✅ Textarea auto-resize without breaking layout
- ✅ Close and reopen functionality

### 2. `auroral-background.spec.ts`
Tests for auroral background and performance:
- ✅ Background appears on correct pages
- ✅ Proper positioning and pointer-events
- ✅ Animation runs smoothly
- ✅ Content readable over background
- ✅ Mobile performance benchmarks
- ✅ iOS Safari compatibility
- ✅ Cross-browser support

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests with UI
```bash
npm run test:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:headed
```

### Debug tests
```bash
npm run test:debug
```

### View test report
```bash
npm run test:report
```

### Run specific test file
```bash
npx playwright test tests/chat-layout.spec.ts
```

### Run specific test
```bash
npx playwright test -g "chat input stays fixed"
```

## Test Configuration

- **Browsers**: Chromium, Mobile Chrome (Pixel 5), Mobile Safari (iPhone 12)
- **Retries**: 2 in CI, 0 locally
- **Timeout**: 30s per test
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry

## CI/CD Integration

Tests are configured to run automatically in CI with:
- `fullyParallel: true` for faster execution
- `retries: 2` for flaky test handling
- `workers: 1` for consistent CI results

## Manual Testing Checklist

While automated tests cover core functionality, also manually verify:

1. **Chat Input Stability**
   - [ ] Send multiple messages rapidly
   - [ ] Type long messages with line breaks
   - [ ] Test on actual iOS device
   - [ ] Test with virtual keyboard appearing/disappearing

2. **Auroral Background**
   - [ ] Verify smooth animation on low-end devices
   - [ ] Check color contrast in different lighting
   - [ ] Ensure no performance degradation

3. **Mobile Experience**
   - [ ] Test on various screen sizes
   - [ ] Verify touch targets are large enough
   - [ ] Check scrolling is smooth
   - [ ] Test in landscape orientation

## Troubleshooting

### Tests fail locally
```bash
# Rebuild the app first
npm run build

# Install Playwright browsers if needed
npx playwright install
```

### Tests timeout
- Increase timeout in `playwright.config.ts`
- Check if dev server is running properly
- Verify network connectivity

### Flaky tests
- Check for animation timing issues
- Add explicit waits where needed
- Verify selectors are stable

## Coverage

Current test coverage:
- **Chat Layout**: 7 tests
- **Auroral Background**: 8 tests
- **Mobile Performance**: 5 tests
- **Cross-browser**: 1 test

**Total**: 21 automated tests across 3 browsers = 63 test runs
