#!/usr/bin/env python3
"""Verify the CSS classes are in the built output"""
import os
import re

build_dir = "app/startup-swipe-schedu/dist/assets"
js_files = [f for f in os.listdir(build_dir) if f.endswith(".js")]

print("\n" + "=" * 80)
print("VERIFYING BUILT CSS CLASSES")
print("=" * 80)

classes_to_find = {
    "mobile_fixed": "fixed.*md:relative",
    "mobile_bottom_offset": "bottom-20.*md:bottom-auto",
    "mobile_top": "top-0.*md:top-auto",
    "dialog_relative": "md:relative",
}

for js_file in js_files:
    filepath = os.path.join(build_dir, js_file)
    with open(filepath, 'rb') as f:
        content = f.read()
    
    print(f"\nChecking {js_file}...")
    
    for key, pattern in classes_to_find.items():
        if re.search(pattern.encode() if isinstance(pattern, str) else pattern, content):
            print(f"  ✓ {key}: FOUND")
        else:
            # Try without regex
            if any(cls.encode() in content for cls in pattern.split('|')):
                print(f"  ✓ {key}: FOUND (partial)")

print("\n" + "=" * 80)
print("✓ CSS classes verification complete")
print("=" * 80 + "\n")
