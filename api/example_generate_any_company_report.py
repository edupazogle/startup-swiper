#!/usr/bin/env python3
"""
Example: Generate CB Insights Scouting Report for Any Company

This script shows how to generate scouting reports for different companies.
"""

import asyncio
import sys
sys.path.insert(0, '/home/akyo/startup_swiper/api')

# Import the client class
from generate_simplifai_scouting_report import CBInsightsV2Client

CBINSIGHTS_CLIENT_ID = "d13b9206-0ab1-451c-bd27-19454cbd67b1"
CBINSIGHTS_CLIENT_SECRET = "82fef28b517bd39ef977fe87415d69a45fbcdc376293ca3e3fd5ef0240901fb8"


async def generate_report_for_company(company_name: str):
    """Generate scouting report for any company"""
    
    print(f"\n{'='*80}")
    print(f"Generating report for: {company_name}")
    print(f"{'='*80}\n")
    
    # Initialize client
    client = CBInsightsV2Client(CBINSIGHTS_CLIENT_ID, CBINSIGHTS_CLIENT_SECRET)
    
    # Authenticate
    if not await client.authorize():
        print("❌ Failed to authorize")
        return
    
    # Search for organization
    search_results = await client.search_organizations(company_name)
    orgs = search_results.get("orgs", [])
    
    if not orgs:
        print(f"❌ No organizations found for '{company_name}'")
        return
    
    print(f"✅ Found {len(orgs)} organization(s):")
    for i, org in enumerate(orgs[:5], 1):  # Show top 5
        org_id = org.get("orgId")
        org_name = org.get("name")
        description = org.get("description", "")[:100]
        print(f"   {i}. {org_name} (ID: {org_id})")
        print(f"      {description}...")
    
    # Get the first matching organization
    target_org = orgs[0]
    org_id = target_org.get("orgId")
    org_name = target_org.get("name")
    
    print(f"\n➡️  Generating report for: {org_name} (ID: {org_id})")
    
    # Generate report
    report_data = await client.get_scouting_report(org_id)
    
    if not report_data:
        print("❌ Failed to generate report")
        return
    
    # Extract key information
    org_info = report_data.get("orgInfo", {})
    report_json = report_data.get("reportJson", "{}")
    report_markdown = report_data.get("reportMarkdown", "")
    
    print(f"\n✅ Report generated successfully!")
    print(f"\n📊 Key Sections:")
    
    import json
    try:
        report_data_parsed = json.loads(report_json) if isinstance(report_json, str) else report_json
        for section in list(report_data_parsed.keys())[:5]:
            print(f"   • {section}")
    except:
        pass
    
    # Show preview
    print(f"\n📝 Report Preview (first 500 chars):")
    print("-" * 80)
    print(report_markdown[:500] + "..." if len(report_markdown) > 500 else report_markdown)
    print("-" * 80)
    
    print(f"\n✅ Full reports saved!")
    print(f"   Markdown: ./downloads/{org_name.lower().replace(' ', '_')}_scouting_report_*.md")
    print(f"   JSON: ./downloads/{org_name.lower().replace(' ', '_')}_scouting_report_*.json")


async def main():
    """Example usage with different companies"""
    
    companies_to_search = [
        "Simplifai",        # Already completed
        "Stripe",           # Example: Payment processing
        "OpenAI",           # Example: AI research
        "Figma",            # Example: Design tools
    ]
    
    # For demonstration, just show how to use it
    print("\n" + "="*80)
    print("CB INSIGHTS SCOUTING REPORT GENERATOR - USAGE EXAMPLES")
    print("="*80)
    
    print("\n📚 EXAMPLES - How to generate reports for other companies:")
    print("-" * 80)
    
    for i, company in enumerate(companies_to_search, 1):
        print(f"\n{i}. {company}")
        print(f"   >>> await generate_report_for_company('{company}')")
    
    # Uncomment below to actually generate reports (will take several minutes per company)
    # 
    # for company in companies_to_search[:1]:  # Just first one to save time
    #     await generate_report_for_company(company)


if __name__ == "__main__":
    asyncio.run(main())
