#!/bin/bash

echo ""
echo "================================================================================"
echo "FINAL VERIFICATION TEST"
echo "================================================================================"

echo ""
echo "1. ✓ Checking source files..."
echo ""

echo "   StartupChat.tsx:"
grep -q "fixed md:relative inset-0" src/components/StartupChat.tsx && echo "      ✓ Mobile/Desktop positioning classes found" || echo "      ✗ Classes not found"
grep -q "bottom-20 md:bottom-auto" src/components/StartupChat.tsx && echo "      ✓ Bottom menu offset found" || echo "      ✗ Not found"

echo ""
echo "   FeedbackChatModal.tsx:"
grep -q "fixed md:relative" src/components/FeedbackChatModal.tsx && echo "      ✓ Position responsive classes found" || echo "      ✗ Not found"
grep -q "h-\[calc" src/components/FeedbackChatModal.tsx && echo "      ✓ Dynamic height calc found" || echo "      ✗ Not found"

echo ""
echo "   MeetingAIModal.tsx:"
grep -q "fixed md:relative" src/components/MeetingAIModal.tsx && echo "      ✓ Position responsive classes found" || echo "      ✗ Not found"
grep -q "z-50 md:z-auto" src/components/MeetingAIModal.tsx && echo "      ✓ Z-index responsive found" || echo "      ✗ Not found"

echo ""
echo "2. ✓ Checking built output..."
echo ""

# Check if CSS file exists
if [ -f "dist/assets/index-DAvV9LLY.css" ]; then
    echo "   ✓ CSS file found: dist/assets/index-DAvV9LLY.css"
    wc -c < dist/assets/index-DAvV9LLY.css | xargs -I {} echo "     Size: {} bytes"
else
    echo "   ✗ CSS file not found in dist"
fi

# Check if JS file exists
if [ -f "dist/assets/index-B3gouIZv.js" ]; then
    echo "   ✓ JS file found: dist/assets/index-B3gouIZv.js"
    wc -c < dist/assets/index-B3gouIZv.js | xargs -I {} echo "     Size: {} bytes"
else
    echo "   ✗ JS file not found in dist"
fi

echo ""
echo "3. ✓ Build validation..."
echo ""

if npm run build > /tmp/build_output.log 2>&1; then
    build_time=$(grep "built in" /tmp/build_output.log | tail -1)
    echo "   ✓ Build successful: $build_time"
    
    # Check for errors
    if grep -q "error" /tmp/build_output.log; then
        echo "   ✗ Errors found in build"
    else
        echo "   ✓ No build errors"
    fi
else
    echo "   ✗ Build failed"
fi

echo ""
echo "================================================================================"
echo "VERIFICATION COMPLETE"
echo "================================================================================"
echo ""

