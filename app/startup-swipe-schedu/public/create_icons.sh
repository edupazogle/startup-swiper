#!/bin/bash

# Simple script to create placeholder PWA icons
# These are just colored squares - replace with your actual logo/branding

echo "Creating placeholder PWA icons..."

cd "$(dirname "$0")"

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "❌ ImageMagick not found. Please install it:"
    echo "   Ubuntu/Debian: sudo apt-get install imagemagick"
    echo "   macOS: brew install imagemagick"
    echo ""
    echo "Or create icons manually and place them in public/ folder:"
    echo "   - icon-192.png (192x192) - Required"
    echo "   - icon-512.png (512x512) - Required"
    exit 1
fi

# Colors
PRIMARY_COLOR="#6366f1"  # Indigo
BADGE_COLOR="#f59e0b"    # Amber

# Create icons
echo "Creating icon-72.png..."
convert -size 72x72 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 40 -fill white -annotate +0+0 "S" \
    icon-72.png

echo "Creating icon-96.png..."
convert -size 96x96 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 50 -fill white -annotate +0+0 "S" \
    icon-96.png

echo "Creating icon-128.png..."
convert -size 128x128 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 64 -fill white -annotate +0+0 "S" \
    icon-128.png

echo "Creating icon-144.png..."
convert -size 144x144 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 72 -fill white -annotate +0+0 "S" \
    icon-144.png

echo "Creating icon-152.png..."
convert -size 152x152 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 76 -fill white -annotate +0+0 "S" \
    icon-152.png

echo "Creating icon-192.png..."
convert -size 192x192 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 96 -fill white -annotate +0+0 "S" \
    icon-192.png

echo "Creating icon-384.png..."
convert -size 384x384 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 192 -fill white -annotate +0+0 "S" \
    icon-384.png

echo "Creating icon-512.png..."
convert -size 512x512 xc:"$PRIMARY_COLOR" \
    -gravity center -pointsize 256 -fill white -annotate +0+0 "S" \
    icon-512.png

echo "Creating badge-72.png..."
convert -size 72x72 xc:"$BADGE_COLOR" \
    -gravity center -pointsize 40 -fill white -annotate +0+0 "🚀" \
    badge-72.png

echo "✅ Placeholder icons created successfully!"
echo ""
echo "📁 Files created:"
ls -lh icon-*.png badge-*.png
echo ""
echo "⚠️  These are temporary placeholders. Replace with your actual logo!"
