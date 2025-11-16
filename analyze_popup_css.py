#!/usr/bin/env python3
"""
Simple script to check CSS classes and styling on the popup components
"""

import re
import os

def check_file_styling(filepath, component_name):
    """Check CSS classes in component files"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    print(f"\n{'=' * 80}")
    print(f"{component_name}")
    print(f"{'=' * 80}")
    
    # Find DialogContent or main container className
    if 'DialogContent' in content:
        match = re.search(r'<DialogContent\s+className="([^"]*)"', content)
        if match:
            classes = match.group(1)
            print(f"DialogContent className:\n{classes}\n")
            
            # Parse classes
            print("Parsed classes:")
            mobile_classes = []
            desktop_classes = []
            
            for cls in classes.split():
                if 'md:' in cls:
                    desktop_classes.append(cls)
                else:
                    mobile_classes.append(cls)
            
            print(f"\n✓ Mobile (< md breakpoint):")
            for cls in sorted(mobile_classes):
                print(f"  - {cls}")
            
            print(f"\n✓ Desktop (md+ breakpoint):")
            for cls in sorted(desktop_classes):
                print(f"  - {cls}")
    
    elif 'div className' in content:
        match = re.search(r'<div\s+className="([^"]*)">\s*<ConciergeChatHeader', content)
        if match:
            classes = match.group(1)
            print(f"Main container className:\n{classes}\n")
            
            print("Parsed classes:")
            mobile_classes = []
            desktop_classes = []
            
            for cls in classes.split():
                if 'md:' in cls:
                    desktop_classes.append(cls)
                else:
                    mobile_classes.append(cls)
            
            print(f"\n✓ Mobile (< md breakpoint):")
            for cls in sorted(mobile_classes):
                print(f"  - {cls}")
            
            print(f"\n✓ Desktop (md+ breakpoint):")
            for cls in sorted(desktop_classes):
                print(f"  - {cls}")

# Check all three components
check_file_styling(
    "/home/akyo/startup_swiper/app/startup-swipe-schedu/src/components/StartupChat.tsx",
    "StartupChat.tsx"
)

check_file_styling(
    "/home/akyo/startup_swiper/app/startup-swipe-schedu/src/components/FeedbackChatModal.tsx",
    "FeedbackChatModal.tsx"
)

check_file_styling(
    "/home/akyo/startup_swiper/app/startup-swipe-schedu/src/components/MeetingAIModal.tsx",
    "MeetingAIModal.tsx"
)

print(f"\n{'=' * 80}")
print("Summary: CSS Classes Analysis")
print(f"{'=' * 80}")
print("""
Key takeaways:
- Mobile: Uses fixed positioning with inset-0, bottom-20 offset for menu
- Desktop: Should revert to normal modal behavior with md: prefixed classes
- z-50/z-auto: Ensures proper layering on mobile vs desktop

If popups appear off-center on desktop, the issue is likely:
1. Dialog's centering being broken by fixed positioning on desktop
2. z-index conflicts with other overlays
3. Width constraints not being properly applied

To test interactively:
1. Open browser DevTools (F12)
2. Toggle device toolbar for mobile view
3. Inspect the Dialog or popup element
4. Check computed CSS for position, inset, width, height values
""")
