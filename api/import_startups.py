#!/usr/bin/env python3
"""
Import all startups from slush_full_list.json into slush2_extracted.json
Maps fields from slush_full_list to the schema defined in slush2_extracted.json
Enriches with data from slush2.json where available
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

def parse_date(year_str):
    """Convert founding year to ISO date format"""
    if not year_str or year_str == 'N/A':
        return None
    try:
        year = int(year_str)
        return f"{year}-01-01T00:00:00.000Z"
    except (ValueError, TypeError):
        return None

def map_startup_fields(startup_full, startup_slush2=None, next_id=50000):
    """
    Map fields from slush_full_list format to slush2_extracted format
    Enrich with slush2 data if available
    """
    
    # Base mapping from slush_full_list
    mapped = {
        "id": next_id,
        "dateCreated": datetime.utcnow().isoformat() + "Z",
        "name": startup_full.get("company_name", ""),
        "dateFounded": parse_date(startup_full.get("founding_year")),
        "employees": "Undisclosed",
        "legalEntity": None,
        "mainContactId": None,
        "website": startup_full.get("website", ""),
        "shortDescription": startup_full.get("company_description", "")[:200] if startup_full.get("company_description") else "",
        "description": startup_full.get("company_description", ""),
        "technologyReadiness": None,
        "currentInvestmentStage": "Undisclosed",
        "totalFunding": None,
        "originalTotalFunding": None,
        "originalTotalFundingCurrency": None,
        "lastFundingDate": None,
        "lastFunding": None,
        "originalLastFunding": None,
        "originalLastFundingCurrency": None,
        "pricingModel": None,
        "sfId": None,
        "billingCountry": startup_full.get("company_country", ""),
        "billingState": None,
        "billingStreet": None,
        "billingCity": startup_full.get("company_city", ""),
        "billingPostalCode": None,
        "fundingIsUndisclosed": False,
        "lastModifiedById": None,
        "parentCompanyId": None,
        "lastModifiedDate": None,
        "pitchbookId": None,
        "lastPitchbookSync": None,
        "isMissingValidation": False,
        "lastQualityCheckDate": None,
        "lastQualityCheckById": None,
        "isQualityChecked": None,
        "qualityChecks": [],
        "lastQualityCheckBy": None,
        "featuredLists": [
            {
                "id": 5,
                "name": "SLUSH 2025",
                "logo": "https://vclms-frontend-prod-dcs.s3.eu-central-1.amazonaws.com/Slush_Black.png"
            }
        ],
        "opportunities": [],
        "leadOpportunities": [],
        "files": [],
        "logoUrl": None,
        "topics": startup_full.get("curated_collections_tags", []) if startup_full.get("curated_collections_tags") else [],
        "tech": [],
        "maturity": startup_full.get("company_type", ""),
        "maturity_score": 0
    }
    
    # Add custom fields from slush_full_list
    if startup_full.get("company_linked_in"):
        mapped["linkedin"] = startup_full.get("company_linked_in")
    
    if startup_full.get("primary_industry"):
        mapped["primary_industry"] = startup_full.get("primary_industry")
    
    if startup_full.get("secondary_industry"):
        mapped["secondary_industry"] = startup_full.get("secondary_industry")
    
    if startup_full.get("focus_industries"):
        mapped["focus_industries"] = startup_full.get("focus_industries")
    
    if startup_full.get("business_types"):
        mapped["business_types"] = startup_full.get("business_types")
        
    if startup_full.get("prominent_investors"):
        mapped["prominent_investors"] = startup_full.get("prominent_investors")
    
    if startup_full.get("profile_link"):
        mapped["profile_link"] = startup_full.get("profile_link")
    
    # Enrich with slush2 data if available
    if startup_slush2:
        # Copy all fields from slush2 that are more complete
        enrich_fields = [
            "id", "dateCreated", "dateFounded", "employees", "legalEntity",
            "mainContactId", "technologyReadiness", "currentInvestmentStage",
            "totalFunding", "originalTotalFunding", "originalTotalFundingCurrency",
            "lastFundingDate", "lastFunding", "originalLastFunding",
            "originalLastFundingCurrency", "pricingModel", "sfId",
            "billingState", "billingStreet", "billingPostalCode",
            "fundingIsUndisclosed", "lastModifiedById", "parentCompanyId",
            "lastModifiedDate", "pitchbookId", "lastPitchbookSync",
            "isMissingValidation", "lastQualityCheckDate", "lastQualityCheckById",
            "isQualityChecked", "qualityChecks", "lastQualityCheckBy",
            "featuredLists", "opportunities", "leadOpportunities", "files",
            "logoUrl", "tech", "maturity_score"
        ]
        
        for field in enrich_fields:
            if field in startup_slush2 and startup_slush2[field] is not None:
                mapped[field] = startup_slush2[field]
        
        # Prefer slush2 description if longer/more detailed
        if startup_slush2.get("description") and len(startup_slush2.get("description", "")) > len(mapped.get("description", "")):
            mapped["description"] = startup_slush2["description"]
            mapped["shortDescription"] = startup_slush2.get("shortDescription", mapped["shortDescription"])
    
    return mapped

def main():
    # Define paths
    base_path = Path(__file__).parent.parent
    docs_path = base_path / "docs" / "architecture" / "ddbb"
    
    slush_full_path = docs_path / "slush_full_list.json"
    slush2_path = docs_path / "slush2.json"
    slush2_extracted_path = docs_path / "slush2_extracted.json"
    
    # Also update the app's copy
    app_extracted_path = base_path / "app" / "startup-swipe-schedu" / "startups" / "slush2_extracted.json"
    
    print("=" * 80)
    print("STARTUP DATA IMPORT")
    print("=" * 80)
    print()
    
    # Load all JSON files
    print("📂 Loading JSON files...")
    slush_full_list = load_json(slush_full_path)
    print(f"   ✓ slush_full_list.json: {len(slush_full_list)} startups")
    
    slush2 = load_json(slush2_path)
    print(f"   ✓ slush2.json: {len(slush2)} startups")
    
    slush2_extracted = load_json(slush2_extracted_path)
    print(f"   ✓ slush2_extracted.json: {len(slush2_extracted)} startups")
    print()
    
    # Create lookup dictionaries
    print("🔍 Creating lookup indexes...")
    
    # Index slush2 by name for enrichment
    slush2_by_name = {}
    for startup in slush2:
        name = startup.get("name", "").strip().lower()
        if name:
            slush2_by_name[name] = startup
    
    # Index existing extracted startups by name to avoid duplicates
    extracted_by_name = {}
    for startup in slush2_extracted:
        name = startup.get("name", "").strip().lower()
        if name:
            extracted_by_name[name] = startup
    
    print(f"   ✓ Indexed {len(slush2_by_name)} startups from slush2.json")
    print(f"   ✓ Indexed {len(extracted_by_name)} existing startups from slush2_extracted.json")
    print()
    
    # Find the highest ID in existing data
    max_id = max([s.get("id", 0) for s in slush2_extracted], default=50000)
    next_id = max_id + 1
    
    print(f"🔢 Starting new IDs from: {next_id}")
    print()
    
    # Process each startup from slush_full_list
    print("🔄 Processing startups...")
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for startup_full in slush_full_list:
        name = startup_full.get("company_name", "").strip()
        name_lower = name.lower()
        
        if not name:
            skipped_count += 1
            continue
        
        # Check if already exists
        if name_lower in extracted_by_name:
            # Startup already exists - could optionally update it
            skipped_count += 1
            continue
        
        # Get enrichment data from slush2 if available
        startup_slush2 = slush2_by_name.get(name_lower)
        
        # Map the startup
        mapped_startup = map_startup_fields(startup_full, startup_slush2, next_id)
        
        # Add to extracted list
        slush2_extracted.append(mapped_startup)
        extracted_by_name[name_lower] = mapped_startup
        
        added_count += 1
        next_id += 1
        
        if added_count % 100 == 0:
            print(f"   Processed {added_count} new startups...")
    
    print()
    print("=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"✅ Added: {added_count} new startups")
    print(f"⏭️  Skipped: {skipped_count} (already exist or invalid)")
    print(f"📊 Total startups in slush2_extracted.json: {len(slush2_extracted)}")
    print()
    
    # Save updated slush2_extracted.json
    print("💾 Saving updated files...")
    save_json(slush2_extracted_path, slush2_extracted)
    print(f"   ✓ Saved {slush2_extracted_path}")
    
    # Also update the app's copy
    if app_extracted_path.exists():
        save_json(app_extracted_path, slush2_extracted)
        print(f"   ✓ Saved {app_extracted_path}")
    
    print()
    print("✨ Import complete!")
    print()

if __name__ == "__main__":
    main()
