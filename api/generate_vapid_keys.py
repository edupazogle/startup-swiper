#!/usr/bin/env python3
"""
VAPID Key Generator for Web Push Notifications

This script generates VAPID (Voluntary Application Server Identification) keys
required for sending web push notifications.

Usage:
    python generate_vapid_keys.py

The keys will be displayed and should be added to your .env file:
    VAPID_PUBLIC_KEY=your_public_key_here
    VAPID_PRIVATE_KEY=your_private_key_here
"""

try:
    from py_vapid import Vapid
except ImportError:
    print("Error: py-vapid not installed")
    print("Install it with: pip install py-vapid")
    exit(1)

def generate_vapid_keys():
    """Generate VAPID key pair"""
    print("Generating VAPID keys for web push notifications...\n")
    
    # Generate new VAPID key pair
    vapid = Vapid()
    vapid.generate_keys()
    
    # Get keys
    public_key = vapid.public_key.export_public_pem().decode('utf-8')
    private_key = vapid.private_key.export_private_pem().decode('utf-8')
    
    # URL-safe base64 versions (what you actually need)
    public_key_base64 = vapid.public_key.public_key_bytes
    private_key_base64 = vapid.raw_private_key
    
    print("=" * 70)
    print("VAPID KEYS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Add these to your .env file:")
    print("-" * 70)
    print()
    print(f"VAPID_PUBLIC_KEY={public_key_base64.decode('utf-8')}")
    print(f"VAPID_PRIVATE_KEY={private_key_base64.decode('utf-8')}")
    print()
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT:")
    print("  - Keep the PRIVATE key secret!")
    print("  - Never commit the PRIVATE key to git")
    print("  - The PUBLIC key is safe to share with clients")
    print("  - Add both keys to api/.env file")
    print()
    print("✅ You can now enable push notifications in your app!")
    print()
    
    # Save to file for convenience
    try:
        with open('.env.vapid', 'w') as f:
            f.write(f"VAPID_PUBLIC_KEY={public_key_base64.decode('utf-8')}\n")
            f.write(f"VAPID_PRIVATE_KEY={private_key_base64.decode('utf-8')}\n")
        print("💾 Keys also saved to .env.vapid file")
        print("   Copy these to your main .env file")
    except Exception as e:
        print(f"Could not save to file: {e}")
    
    print()

if __name__ == "__main__":
    generate_vapid_keys()
