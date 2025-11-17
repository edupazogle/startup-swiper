# 🚀 Quick Implementation Checklist
**Startup Swiper Mobile Optimization**

---

## ⚡ P0 - CRITICAL (Do This Week)

### Virtual Scrolling
- [ ] Install: `npm install @tanstack/react-virtual`
- [ ] Implement in `DashboardView.tsx` (line ~200-400)
- [ ] Replace `.map()` with `useVirtualizer` hook
- [ ] Test with all 3664 startups loaded
- [ ] Verify 60fps scrolling

### iOS Safe Areas
- [ ] Update `index.html` viewport meta:
  ```html
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  ```
- [ ] Add to `index.css`:
  ```css
  .safe-top { padding-top: env(safe-area-inset-top); }
  .safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
  ```
- [ ] Apply to: bottom nav, modals, fixed headers

### Input Fixes
- [ ] Set all input/textarea `font-size: 16px` minimum
- [ ] Add auto-grow to chat textareas (max 4 lines)
- [ ] Test keyboard behavior on iOS Safari

### Touch Targets
- [ ] Audit all buttons: `min-h-11 min-w-11` (44px)
- [ ] Fix header close buttons
- [ ] Increase filter chip padding

---

## 🎨 P1 - HIGH PRIORITY (Next Week)

### Micro-Interactions
- [ ] Add button press state: `active:scale-95`
- [ ] Card entrance: stagger animation with framer-motion
- [ ] Loading states: skeleton screens

### Page Transitions
- [ ] Wrap views in `<AnimatePresence>`
- [ ] Add fade+slide transitions (200ms)
- [ ] Preserve scroll position

### Code Splitting
- [ ] Lazy load modals:
  ```typescript
  const InsightsModal = lazy(() => import('./ImprovedInsightsModalNew'))
  ```
- [ ] Split by route
- [ ] Dynamic import heavy libs

---

## 📱 P2 - MEDIUM (Sprint After)

### Gesture Improvements
- [ ] Reduce swipe friction: `dragElastic: 0.2`
- [ ] Add haptic feedback: `navigator.vibrate(10)`
- [ ] Swipe indicators (gradient overlays)

### Scroll Animations
- [ ] Install: `npm install react-intersection-observer`
- [ ] Add reveal on scroll for cards
- [ ] Parallax on auroral background

### Advanced Caching
- [ ] Implement in-memory API cache
- [ ] Service Worker for offline
- [ ] Background sync for votes

---

## 🔧 Quick Wins (< 1 Hour Each)

### CSS Fixes
```css
/* Add to index.css */
body {
  overscroll-behavior-y: contain;
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  touch-action: manipulation;
}

button, a {
  touch-action: manipulation;
}
```

### Debounce Search
```typescript
import { useDebouncedValue } from 'usehooks-ts'

const debouncedSearch = useDebouncedValue(searchQuery, 300)
```

### Memoize Expensive Calculations
```typescript
const filteredStartups = useMemo(
  () => startups.filter(/* logic */),
  [startups, filters]
)
```

---

## 📊 Testing Commands

```bash
# Build and analyze bundle
npm run build
npx vite-bundle-visualizer

# Run Lighthouse
npx lighthouse http://localhost:5173 --view

# Test mobile viewport
# Open Chrome DevTools > Device Toolbar
# Test: iPhone 14 Pro, iPad Air, Pixel 7
```

---

## ✅ Definition of Done

- [ ] Virtual scrolling: Dashboard scrolls at 60fps with 3000+ items
- [ ] iOS: No UI cutoff on iPhone with notch
- [ ] Inputs: No auto-zoom on iOS when focusing
- [ ] Touch: All buttons are ≥ 44x44px
- [ ] Performance: Lighthouse score > 85
- [ ] Bundle: < 350KB gzipped
- [ ] Tested on: iPhone, Android, Desktop

---

## 🆘 Common Issues & Fixes

### Issue: Dashboard laggy with many items
**Fix:** Implement virtual scrolling (P0 task)

### Issue: iOS keyboard covers input
**Fix:** Add `scrollIntoView()` on input focus

### Issue: Modal doesn't fill iPhone screen
**Fix:** Add safe area padding and `h-screen`

### Issue: Large bundle size
**Fix:** Code splitting and tree-shaking

### Issue: Animations janky
**Fix:** Use only `transform` and `opacity`

---

**Start Here:** Pick any P0 item and complete it today! 🚀
