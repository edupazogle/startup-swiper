#!/usr/bin/env python3
"""
Deploy enriched startup data to slush2_extracted.json
Merges enrichment fields from slush2_enriched.json into slush2_extracted.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def merge_enrichment(startup, enrichment):
    """
    Merge enrichment data into startup record
    Preserves existing fields and adds new enrichment fields
    """
    # Add enrichment data as a top-level field
    startup["enrichment"] = {
        "enrichment_date": enrichment.get("enrichment_date"),
        "enrichment_success": enrichment.get("enrichment_success"),
        "sources_checked": enrichment.get("sources_checked", []),
        "website_url": enrichment.get("website_url"),
        "page_title": enrichment.get("page_title"),
        "emails": enrichment.get("emails", []),
        "phone_numbers": enrichment.get("phone_numbers", []),
        "social_media": enrichment.get("social_media", {}),
        "tech_stack": enrichment.get("tech_stack", []),
        "key_pages": enrichment.get("key_pages", {}),
        "team_members": enrichment.get("team_members", [])
    }

    # Mark as enriched
    startup["is_enriched"] = True
    startup["last_enriched_date"] = enrichment.get("enrichment_date")

    return startup

def main():
    # Define paths
    base_path = Path(__file__).parent.parent
    docs_path = base_path / "docs" / "architecture" / "ddbb"

    enriched_path = docs_path / "slush2_enriched.json"
    extracted_path = docs_path / "slush2_extracted.json"

    # Also update the app's copy
    app_extracted_path = base_path / "app" / "startup-swipe-schedu" / "startups" / "slush2_extracted.json"

    print("=" * 80)
    print("ENRICHED DATA DEPLOYMENT")
    print("=" * 80)
    print()

    # Load JSON files
    print("📂 Loading JSON files...")

    if not enriched_path.exists():
        print(f"❌ Error: {enriched_path} not found")
        print("   Please run the enrichment script first")
        sys.exit(1)

    enriched_data = load_json(enriched_path)
    print(f"   ✓ slush2_enriched.json: {len(enriched_data)} startups")

    extracted_data = load_json(extracted_path)
    print(f"   ✓ slush2_extracted.json: {len(extracted_data)} startups")
    print()

    # Create lookup dictionaries
    print("🔍 Creating lookup indexes...")

    # Index enriched data by name
    enriched_by_name = {}
    for startup in enriched_data:
        name = startup.get("name", "").strip().lower()
        if name and startup.get("enrichment"):
            enriched_by_name[name] = startup

    print(f"   ✓ Indexed {len(enriched_by_name)} enriched startups")
    print()

    # Merge enrichment data
    print("🔄 Merging enrichment data...")
    merged_count = 0
    skipped_count = 0
    updated_count = 0

    for startup in extracted_data:
        name = startup.get("name", "").strip().lower()

        if not name:
            skipped_count += 1
            continue

        # Check if enrichment data exists
        if name in enriched_by_name:
            enriched_startup = enriched_by_name[name]
            enrichment = enriched_startup.get("enrichment")

            if enrichment and enrichment.get("enrichment_success"):
                # Check if already has enrichment data
                if startup.get("enrichment"):
                    updated_count += 1
                else:
                    merged_count += 1

                # Merge enrichment
                startup = merge_enrichment(startup, enrichment)

                # Update in the list (in place)
                idx = extracted_data.index(startup)
                extracted_data[idx] = startup
        else:
            skipped_count += 1

    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"✅ New enrichments added: {merged_count}")
    print(f"🔄 Existing enrichments updated: {updated_count}")
    print(f"⏭️  Skipped (no enrichment data): {skipped_count}")
    print(f"📊 Total enriched startups: {merged_count + updated_count}")
    print()

    # Save updated slush2_extracted.json
    print("💾 Saving updated files...")

    # Backup original file
    backup_path = extracted_path.with_suffix('.json.backup')
    save_json(backup_path, load_json(extracted_path))
    print(f"   ✓ Backup saved to {backup_path}")

    # Save updated file
    save_json(extracted_path, extracted_data)
    print(f"   ✓ Saved {extracted_path}")

    # Also update the app's copy
    if app_extracted_path.exists():
        save_json(app_extracted_path, extracted_data)
        print(f"   ✓ Saved {app_extracted_path}")
    else:
        print(f"   ⚠️  App copy not found: {app_extracted_path}")

    print()
    print("✨ Deployment complete!")
    print()

    # Show sample enriched startup
    enriched_sample = next((s for s in extracted_data if s.get("enrichment")), None)
    if enriched_sample:
        print("📋 Sample enriched startup:")
        print(f"   Name: {enriched_sample['name']}")
        enrichment = enriched_sample.get("enrichment", {})
        print(f"   Emails: {len(enrichment.get('emails', []))}")
        print(f"   Phone numbers: {len(enrichment.get('phone_numbers', []))}")
        print(f"   Social media: {len(enrichment.get('social_media', {}))}")
        print(f"   Tech stack: {len(enrichment.get('tech_stack', []))}")
        print(f"   Key pages: {len(enrichment.get('key_pages', {}))}")
        print(f"   Team members: {len(enrichment.get('team_members', []))}")
        print()

if __name__ == "__main__":
    main()
