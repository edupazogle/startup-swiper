#!/usr/bin/env python3
"""
Generate CB Insights Scouting Report for Simplifai

This script uses the CB Insights API v2 to:
1. Get authorization token from client credentials
2. Search for Simplifai organization
3. Generate a detailed scouting report
4. Save the report in JSON and Markdown formats
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# CB Insights API credentials from .env
CBINSIGHTS_CLIENT_ID = "d13b9206-0ab1-451c-bd27-19454cbd67b1"
CBINSIGHTS_CLIENT_SECRET = "82fef28b517bd39ef977fe87415d69a45fbcdc376293ca3e3fd5ef0240901fb8"
CB_INSIGHTS_BASE_URL = "https://api.cbinsights.com"
COMPANY_NAME = "Simplifai"


class CBInsightsV2Client:
    """CB Insights API v2 client for authorization and data retrieval"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = CB_INSIGHTS_BASE_URL
        self.bearer_token: Optional[str] = None
        
    async def authorize(self) -> bool:
        """
        Get authorization bearer token from CB Insights API
        
        Returns:
            True if authorization successful, False otherwise
        """
        auth_url = f"{self.base_url}/v2/authorize"
        payload = {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(auth_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        # CB Insights v2 uses 'token', not 'access_token'
                        self.bearer_token = data.get("token") or data.get("access_token")
                        if self.bearer_token:
                            print(f"✅ Authorization successful")
                            print(f"   Token (first 50 chars): {self.bearer_token[:50]}...")
                            return True
                        else:
                            print(f"❌ No token in response: {data}")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ Authorization failed: {response.status}")
                        print(f"   Response: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Authorization error: {str(e)}")
            return False
    
    async def search_organizations(self, query: str) -> Dict[str, Any]:
        """
        Search for organizations by name
        
        Args:
            query: Organization name to search
            
        Returns:
            Search results
        """
        if not self.bearer_token:
            print("❌ Not authorized. Call authorize() first.")
            return {}
        
        search_url = f"{self.base_url}/v2/organizations"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "names": [query],
            "limit": 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(search_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Search successful")
                        return data
                    else:
                        error_text = await response.text()
                        print(f"❌ Search failed: {response.status}")
                        print(f"   Response: {error_text}")
                        return {}
        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return {}
    
    async def get_scouting_report(self, org_id: int) -> Dict[str, Any]:
        """
        Get scouting report for an organization
        
        Args:
            org_id: CB Insights organization ID
            
        Returns:
            Scouting report data
        """
        if not self.bearer_token:
            print("❌ Not authorized. Call authorize() first.")
            return {}
        
        report_url = f"{self.base_url}/v2/organizations/{org_id}/scoutingreport"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        try:
            print(f"\n🔄 Generating scouting report for organization ID {org_id}...")
            print("   (This may take a few minutes...)")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(report_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Scouting report generated successfully")
                        return data
                    else:
                        error_text = await response.text()
                        print(f"❌ Report generation failed: {response.status}")
                        print(f"   Response: {error_text}")
                        return {}
        except Exception as e:
            print(f"❌ Report generation error: {str(e)}")
            return {}


def extract_organization_id(search_results: Dict[str, Any], company_name: str) -> Optional[int]:
    """
    Extract organization ID from search results
    
    Args:
        search_results: Results from organization search
        company_name: Company name to match
        
    Returns:
        Organization ID if found, None otherwise
    """
    organizations = search_results.get("orgs", [])
    
    print(f"\n📋 Search Results ({len(organizations)} found):")
    
    for i, org in enumerate(organizations, 1):
        org_name = org.get("name", "Unknown")
        org_id = org.get("orgId", "N/A")
        description = org.get("description", "")[:80]
        
        # Try to match by name (case-insensitive)
        is_match = org_name.lower() == company_name.lower()
        marker = "✓" if is_match else "•"
        
        print(f"   {marker} {i}. {org_name} (ID: {org_id})")
        print(f"      {description}...")
        
        if is_match and i == 1:  # Prefer first exact match
            print(f"      ✅ MATCHED: {company_name}")
            return org_id
    
    # Return the first organization if it's a match
    if organizations and organizations[0].get("name", "").lower() == company_name.lower():
        org_id = organizations[0].get("orgId")
        print(f"\n✅ Using first result: {organizations[0].get('name')} (ID: {org_id})")
        return org_id
    
    return None


def save_report(company_name: str, report_data: Dict[str, Any]) -> tuple[str, str]:
    """
    Save scouting report to files in both docs/cbinsights and downloads/cbinsights
    
    Args:
        company_name: Company name for file naming
        report_data: Report data to save
        
    Returns:
        Tuple of (markdown_file_path, json_file_path)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = company_name.lower().replace(" ", "_").replace(".", "")
    
    # Save to both locations
    locations = [
        "/home/akyo/startup_swiper/docs/cbinsights",
        "/home/akyo/startup_swiper/downloads/cbinsights"
    ]
    
    markdown_files = []
    json_files = []
    
    for location in locations:
        # Ensure directory exists
        import os
        os.makedirs(location, exist_ok=True)
        
        # Prepare markdown file
        markdown_file = f"{location}/{safe_name}_scouting_report_{timestamp}.md"
        markdown_content = report_data.get("reportMarkdown", "")
        
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        markdown_files.append(markdown_file)
        
        # Prepare JSON file with full report data
        json_file = f"{location}/{safe_name}_scouting_report_{timestamp}.json"
        json_content = {
            "generated_at": datetime.now().isoformat(),
            "company_name": company_name,
            "orgInfo": report_data.get("orgInfo", {}),
            "reportJson": report_data.get("reportJson", ""),
            "reportMarkdown": report_data.get("reportMarkdown", "")
        }
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_content, f, indent=2, ensure_ascii=False)
        
        json_files.append(json_file)
    
    # Return the downloads/cbinsights paths (most useful)
    return markdown_files[1], json_files[1]


def print_report_summary(report_data: Dict[str, Any]) -> None:
    """Print a summary of the scouting report"""
    org_info = report_data.get("orgInfo", {})
    report_json = report_data.get("reportJson", "{}")
    
    print("\n" + "="*80)
    print("📊 SCOUTING REPORT SUMMARY")
    print("="*80)
    
    # Organization information
    print(f"\n🏢 Organization Information:")
    print(f"   Name: {org_info.get('name', 'N/A')}")
    print(f"   Type: {org_info.get('organizationType', 'N/A')}")
    
    # Proprietary scores
    scores = org_info.get("scores", {})
    if scores:
        print(f"\n📈 Proprietary Scores:")
        print(f"   Mosaic Score: {scores.get('mosaicScore', 'N/A')}")
        print(f"   Commercial Maturity: {scores.get('commercialMaturity', 'N/A')}")
        print(f"   Exit Probability: {scores.get('exitProbability', 'N/A')}")
    
    # Financial information
    print(f"\n💰 Financial Information:")
    financials = org_info.get("financials", {})
    if financials:
        print(f"   Total Funding: ${financials.get('totalFunding', 'N/A')}")
        print(f"   Valuation: ${financials.get('valuation', 'N/A')}")
        print(f"   Last Funding: {financials.get('lastFundingAmount', 'N/A')}")
    
    # Location
    location = org_info.get("location", {})
    if location:
        print(f"\n📍 Location:")
        print(f"   City: {location.get('city', 'N/A')}")
        print(f"   Country: {location.get('country', 'N/A')}")
    
    # Report content preview
    try:
        report_json_data = json.loads(report_json) if isinstance(report_json, str) else report_json
        print(f"\n📝 Report Sections Found:")
        for section in report_json_data.keys():
            print(f"   • {section}")
    except:
        pass
    
    print("\n" + "="*80)


async def main():
    """Main execution flow"""
    print("\n" + "="*80)
    print("CB INSIGHTS SCOUTING REPORT GENERATOR")
    print("="*80)
    print(f"\nCompany: {COMPANY_NAME}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize client
    print("\n1️⃣  AUTHENTICATION")
    print("-" * 80)
    client = CBInsightsV2Client(CBINSIGHTS_CLIENT_ID, CBINSIGHTS_CLIENT_SECRET)
    
    if not await client.authorize():
        print("❌ Failed to authorize with CB Insights API")
        sys.exit(1)
    
    # Search for organization
    print("\n2️⃣  SEARCHING FOR ORGANIZATION")
    print("-" * 80)
    search_results = await client.search_organizations(COMPANY_NAME)
    org_id = extract_organization_id(search_results, COMPANY_NAME)
    
    if not org_id:
        print(f"\n❌ Could not find organization ID for {COMPANY_NAME}")
        sys.exit(1)
    
    print(f"\n✅ Found organization: {COMPANY_NAME} (ID: {org_id})")
    
    # Generate scouting report
    print("\n3️⃣  GENERATING SCOUTING REPORT")
    print("-" * 80)
    report_data = await client.get_scouting_report(org_id)
    
    if not report_data:
        print(f"❌ Failed to generate scouting report")
        sys.exit(1)
    
    # Print summary
    print_report_summary(report_data)
    
    # Save report files
    print("\n4️⃣  SAVING REPORT FILES")
    print("-" * 80)
    markdown_file, json_file = save_report(COMPANY_NAME, report_data)
    print(f"✅ Markdown report saved: {markdown_file}")
    print(f"✅ JSON report saved: {json_file}")
    
    # Store in database
    print("\n5️⃣  STORING IN DATABASE")
    print("-" * 80)
    try:
        from database import get_db
        from scouting_report_parser import store_scouting_report
        
        db = next(get_db())
        
        markdown_content = report_data.get("reportMarkdown", "")
        json_content = report_data.get("reportJson", "")
        
        scouting_report = store_scouting_report(
            db=db,
            company_name=COMPANY_NAME,
            cb_insights_org_id=org_id,
            markdown_content=markdown_content,
            json_content=json_content,
            markdown_file_path=markdown_file,
            json_file_path=json_file,
            startup_id=None  # Can be linked to startup if company exists in DB
        )
        
        print(f"✅ Scouting report stored in database (ID: {scouting_report.id})")
        print(f"   Company: {scouting_report.company_name}")
        print(f"   Revenue: ${scouting_report.revenue_latest}M")
        print(f"   Employees: {scouting_report.employee_count}")
        print(f"   Commercial Maturity: {scouting_report.commercial_maturity}/5")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not store in database: {str(e)}")
        print("   Report files have been saved successfully")
    
    # Display markdown content
    print("\n6️⃣  REPORT PREVIEW (Markdown)")
    print("-" * 80)
    markdown_content = report_data.get("reportMarkdown", "")
    # Show first 2000 characters
    preview = markdown_content[:2000] + "..." if len(markdown_content) > 2000 else markdown_content
    print(preview)
    
    print("\n" + "="*80)
    print("✅ SCOUTING REPORT GENERATION COMPLETE")
    print("="*80)
    print(f"\n📂 Reports saved to:")
    print(f"   • docs/cbinsights/: {COMPANY_NAME.lower()}_scouting_report_*.md|.json")
    print(f"   • downloads/cbinsights/: {COMPANY_NAME.lower()}_scouting_report_*.md|.json")
    print(f"\n💾 Database: Scouting report data stored for querying")
    print(f"\n💡 Next steps:")
    print(f"   1. Review the reports in docs/cbinsights/ for documentation")
    print(f"   2. Query database for analysis and comparison")
    print(f"   3. Share downloads/cbinsights/ files with stakeholders")


if __name__ == "__main__":
    asyncio.run(main())
