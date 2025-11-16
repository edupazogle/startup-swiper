"""
CB Insights API v2 Enrichment Module
Fetches firmographics and funding data from CB Insights API and populates the database
"""

import os
import json
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path
import logging

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try multiple .env locations
    env_paths = [
        Path(__file__).parent.parent / '.env',  # Root .env
        Path(__file__).parent.parent / 'app' / 'startup-swipe-schedu' / '.env',  # App .env
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    # dotenv not required if environment vars are already set
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CBInsightsEnricher:
    """Enriches startup data using CB Insights API v2"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize CB Insights API client
        
        Args:
            client_id: CB Insights client ID (defaults to CBI_CLIENT_ID or CBINSIGHTS_CLIENT_ID env var)
            client_secret: CB Insights client secret (defaults to CBI_CLIENT_SECRET or CBINSIGHTS_CLIENT_SECRET env var)
        """
        self.client_id = client_id or os.getenv('CBI_CLIENT_ID') or os.getenv('CBINSIGHTS_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CBI_CLIENT_SECRET') or os.getenv('CBINSIGHTS_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "CB Insights credentials not provided. "
                "Set CBI_CLIENT_ID and CBI_CLIENT_SECRET environment variables "
                "or pass them to the constructor."
            )
        
        self.base_url = "https://api.cbinsights.com"
        self.token = None
        self.token_expiry = None
        
    def authorize(self) -> bool:
        """Get authorization token from CB Insights"""
        try:
            url = f"{self.base_url}/v2/authorize"
            payload = {
                "clientId": self.client_id,
                "clientSecret": self.client_secret
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('token')  # CB Insights returns 'token', not 'accessToken'
            
            if self.token:
                logger.info("✅ Successfully authorized with CB Insights API")
                return True
            else:
                logger.error("❌ Failed to get access token from CB Insights")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authorization failed: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization"""
        if not self.token:
            raise ValueError("Not authorized. Call authorize() first.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_firmographics_by_name(
        self,
        company_name: str,
        limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Get firmographics data for a company by name
        
        Args:
            company_name: Company name to search for
            limit: Maximum number of results
            
        Returns:
            Firmographics response data or None if not found
        """
        try:
            url = f"{self.base_url}/v2/firmographics"
            payload = {
                "namePartial": [company_name],
                "limit": limit
            }
            
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('orgs') and len(data['orgs']) > 0:
                logger.info(f"✅ Found {len(data['orgs'])} companies matching '{company_name}'")
                return data
            else:
                logger.warning(f"⚠️  No companies found matching '{company_name}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get firmographics for '{company_name}': {e}")
            return None
    
    def get_firmographics_by_org_ids(
        self,
        org_ids: List[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Get firmographics data for companies by CB Insights org IDs
        
        Args:
            org_ids: List of CB Insights organization IDs
            
        Returns:
            Firmographics response data or None if not found
        """
        try:
            url = f"{self.base_url}/v2/firmographics"
            payload = {
                "orgIds": org_ids
            }
            
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('orgs'):
                logger.info(f"✅ Retrieved firmographics for {len(data['orgs'])} organizations")
                return data
            else:
                logger.warning(f"⚠️  No firmographics found for provided org IDs")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get firmographics by org IDs: {e}")
            return None
    
    def get_funding_rounds(
        self,
        org_ids: List[int],
        page_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed funding rounds for organizations
        
        Args:
            org_ids: List of CB Insights organization IDs
            page_token: Pagination token for additional results
            
        Returns:
            Funding rounds data or None if not found
        """
        try:
            url = f"{self.base_url}/v2/financialtransactions/fundings"
            payload = {
                "orgIds": org_ids
            }
            
            if page_token:
                payload["pageToken"] = page_token
            
            headers = self._get_headers()
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('orgs'):
                total_fundings = sum(
                    len(org.get('fundings', [])) for org in data['orgs']
                )
                logger.info(f"✅ Retrieved {total_fundings} funding rounds for {len(data['orgs'])} organizations")
                return data
            else:
                logger.warning(f"⚠️  No funding data found for provided org IDs")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get funding rounds: {e}")
            return None
    
    def extract_funding_data(self, org: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract aggregated funding data from firmographics response
        
        Args:
            org: Organization data from firmographics response
            
        Returns:
            Dictionary with extracted funding fields
        """
        financials = org.get('financials', {})
        
        return {
            'total_funding': financials.get('totalFunding'),
            'total_equity_funding': financials.get('totalEquityFunding'),
            'last_funding_date': financials.get('lastFundingDate'),
            'valuation': financials.get('valuation'),
            'latest_revenue_min': financials.get('revenueMin'),
            'latest_revenue_max': financials.get('revenueMax'),
            'revenue_date': financials.get('revenueDate'),
        }
    
    def extract_company_data(self, org: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract company information from firmographics response
        
        Args:
            org: Organization data from firmographics response
            
        Returns:
            Dictionary with extracted company fields
        """
        summary = org.get('summary', {})
        headcount = org.get('headcount', {})
        taxonomy = org.get('taxonomy', {})
        address = summary.get('address', {}) if isinstance(summary.get('address'), dict) else {}
        
        return {
            'cb_insights_id': org.get('orgId'),
            'company_name': summary.get('name'),
            'company_description': summary.get('description') or summary.get('shortDescription'),
            'founding_year': summary.get('foundedYear'),  # API uses foundedYear, not foundingYear
            'website': summary.get('url') or summary.get('website'),
            'company_city': address.get('city'),
            'company_country': address.get('country'),  # API returns country as string directly
            'employees': headcount.get('currentHeadcount') if isinstance(headcount, dict) else None,
            'primary_industry': taxonomy.get('industry'),  # Could be string or dict
            'secondary_industry': taxonomy.get('subindustry'),  # API returns subindustry (singular) as string
        }
    
    def extract_funding_rounds(self, org_fundings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract individual funding rounds from financial transactions response
        
        Args:
            org_fundings: Organization funding data from financial transactions response
            
        Returns:
            List of dictionaries with individual funding round information
        """
        rounds = []
        
        for transaction in org_fundings.get('fundings', []):
            round_data = {
                'deal_id': transaction.get('dealId'),
                'cb_insights_org_id': org_fundings.get('orgId'),
                'round_date': transaction.get('date'),
                'round_date_str': transaction.get('date'),
                'round_name': transaction.get('round'),
                'round_category': transaction.get('roundCategory'),
                'simplified_round': transaction.get('simplifiedRound'),
                'amount_millions': transaction.get('amountInMillions'),
                'valuation_millions': transaction.get('valuationInMillions'),
                'revenue_min': transaction.get('revenueMin'),
                'revenue_max': transaction.get('revenueMax'),
                'revenue_multiple_min': transaction.get('revenueMultipleMin'),
                'revenue_multiple_max': transaction.get('revenueMultipleMax'),
                'revenue_period': transaction.get('revenueTimePeriod'),
                'investor_count': len(transaction.get('investors', [])),
                'investors': transaction.get('investors'),
                'is_exit': transaction.get('isExit', False),
                'sources': transaction.get('sources'),
                'insights': transaction.get('insights', {}).get('summaryOfInsights') 
                            if transaction.get('insights') else None,
            }
            
            rounds.append(round_data)
        
        return rounds


def example_usage():
    """Example usage of the CB Insights enricher"""
    
    # Initialize enricher
    enricher = CBInsightsEnricher()
    
    # Authorize
    if not enricher.authorize():
        print("Failed to authorize with CB Insights API")
        return
    
    # Example 1: Get firmographics by company name
    print("\n📊 Example 1: Fetch firmographics by company name")
    print("-" * 60)
    
    firmographics = enricher.get_firmographics_by_name("Stripe", limit=1)
    if firmographics and firmographics.get('orgs'):
        org = firmographics['orgs'][0]
        print(f"\nCompany: {org['summary']['name']}")
        print(f"Total Funding: ${org['financials'].get('totalFunding', 'N/A')}M")
        print(f"Valuation: ${org['financials'].get('valuation', 'N/A')}M")
        print(f"Employees: {org['headcount'].get('currentHeadcount', 'N/A')}")
        
        # Extract data
        funding_data = enricher.extract_funding_data(org)
        company_data = enricher.extract_company_data(org)
        
        print(f"\nExtracted Company Data:")
        for key, value in company_data.items():
            print(f"  {key}: {value}")
        
        print(f"\nExtracted Funding Data:")
        for key, value in funding_data.items():
            print(f"  {key}: {value}")
    
    # Example 2: Get funding rounds
    print("\n\n💰 Example 2: Fetch detailed funding rounds")
    print("-" * 60)
    
    if firmographics and firmographics.get('orgs'):
        org_id = firmographics['orgs'][0].get('orgId')
        
        funding_data = enricher.get_funding_rounds([org_id])
        if funding_data and funding_data.get('orgs'):
            org_fundings = funding_data['orgs'][0]
            rounds = enricher.extract_funding_rounds(org_fundings)
            
            print(f"\nFound {len(rounds)} funding rounds:")
            for i, round_info in enumerate(rounds[:3], 1):
                print(f"\n  Round {i}:")
                print(f"    Date: {round_info['round_date']}")
                print(f"    Type: {round_info['round_name']}")
                print(f"    Amount: ${round_info['amount_millions']}M")
                print(f"    Valuation: ${round_info['valuation_millions']}M")
                print(f"    Investors: {round_info['investor_count']}")


if __name__ == "__main__":
    print("CB Insights API v2 Enrichment Module")
    print("=" * 60)
    print("\nTo use this module:")
    print("1. Set CBI_CLIENT_ID and CBI_CLIENT_SECRET environment variables")
    print("2. Import CBInsightsEnricher class")
    print("3. Call enrich methods to fetch data")
    print("\nExample:")
    print("  enricher = CBInsightsEnricher()")
    print("  enricher.authorize()")
    print("  data = enricher.get_firmographics_by_name('Company Name')")
    print("\n" + "=" * 60)
    
    # Uncomment to run example (requires valid credentials)
    # example_usage()
