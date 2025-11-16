#!/usr/bin/env python3
"""
Test CB Insights API to determine maximum safe concurrency level

This script:
1. Starts with low concurrency (1)
2. Gradually increases concurrency
3. Monitors for rate limits, timeouts, and errors
4. Identifies the maximum safe concurrency level
5. Provides recommendations for optimal settings
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CB Insights API credentials
CBINSIGHTS_CLIENT_ID = "d13b9206-0ab1-451c-bd27-19454cbd67b1"
CBINSIGHTS_CLIENT_SECRET = "82fef28b517bd39ef977fe87415d69a45fbcdc376293ca3e3fd5ef0240901fb8"
CB_INSIGHTS_BASE_URL = "https://api.cbinsights.com"
REQUEST_TIMEOUT = 180  # 3 minutes


class ConcurrencyTester:
    """Test API concurrency limits"""
    
    def __init__(self):
        self.bearer_token: str = None
        self.results: Dict[int, Dict[str, Any]] = {}
        
    async def authorize(self, session: aiohttp.ClientSession) -> bool:
        """Get authorization token"""
        auth_url = f"{CB_INSIGHTS_BASE_URL}/v2/authorize"
        payload = {
            "clientId": CBINSIGHTS_CLIENT_ID,
            "clientSecret": CBINSIGHTS_CLIENT_SECRET
        }
        
        try:
            async with session.post(auth_url, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    self.bearer_token = data.get("token") or data.get("access_token")
                    return bool(self.bearer_token)
                return False
        except Exception as e:
            print(f"❌ Authorization failed: {e}")
            return False
    
    async def make_request(self, org_id: int, company_name: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Make a single scouting report request"""
        if not self.bearer_token:
            return {"success": False, "error": "Not authorized"}
        
        report_url = f"{CB_INSIGHTS_BASE_URL}/v2/organizations/{org_id}/scoutingreport"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        start_time = time.time()
        try:
            async with session.post(report_url, headers=headers, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                elapsed = time.time() - start_time
                
                if response.status == 200:
                    await response.json()  # Consume response
                    return {
                        "success": True,
                        "status": 200,
                        "elapsed": elapsed,
                        "company": company_name
                    }
                elif response.status == 429:  # Rate limit
                    return {
                        "success": False,
                        "error": "RATE_LIMIT",
                        "status": 429,
                        "elapsed": elapsed,
                        "company": company_name
                    }
                elif response.status == 503:  # Service unavailable
                    return {
                        "success": False,
                        "error": "SERVICE_UNAVAILABLE",
                        "status": 503,
                        "elapsed": elapsed,
                        "company": company_name
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP_{response.status}",
                        "status": response.status,
                        "elapsed": elapsed,
                        "company": company_name
                    }
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": "TIMEOUT",
                "elapsed": elapsed,
                "company": company_name
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "elapsed": elapsed,
                "company": company_name
            }
    
    async def test_concurrency_level(self, concurrency: int, test_companies: List[tuple]) -> Dict[str, Any]:
        """Test a specific concurrency level"""
        print(f"\n{'='*80}")
        print(f"Testing Concurrency Level: {concurrency}")
        print(f"{'='*80}")
        print(f"Making {len(test_companies)} simultaneous requests...")
        
        async with aiohttp.ClientSession() as session:
            # Authorize
            if not await self.authorize(session):
                print("❌ Authorization failed")
                return {"success": False, "concurrency": concurrency, "error": "Authorization failed"}
            
            print("✅ Authorized")
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(concurrency)
            
            async def limited_request(org_id: int, company_name: str):
                async with semaphore:
                    return await self.make_request(org_id, company_name, session)
            
            # Run requests
            start_time = time.time()
            tasks = [
                limited_request(org_id, company_name)
                for org_id, company_name in test_companies
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Analyze results
            successes = sum(1 for r in responses if isinstance(r, dict) and r.get("success"))
            failures = len(responses) - successes
            rate_limits = sum(1 for r in responses if isinstance(r, dict) and r.get("error") == "RATE_LIMIT")
            timeouts = sum(1 for r in responses if isinstance(r, dict) and r.get("error") == "TIMEOUT")
            avg_time = sum(r.get("elapsed", 0) for r in responses if isinstance(r, dict)) / len(responses) if responses else 0
            
            result = {
                "success": True,
                "concurrency": concurrency,
                "total_requests": len(test_companies),
                "successes": successes,
                "failures": failures,
                "rate_limits": rate_limits,
                "timeouts": timeouts,
                "total_time": total_time,
                "avg_time_per_request": avg_time,
                "requests_per_second": len(test_companies) / total_time if total_time > 0 else 0,
                "success_rate": successes / len(responses) * 100 if responses else 0
            }
            
            self.results[concurrency] = result
            
            # Print results
            print(f"\n📊 Results for Concurrency {concurrency}:")
            print(f"  ✅ Successes: {successes}/{len(test_companies)}")
            print(f"  ❌ Failures: {failures}")
            if rate_limits > 0:
                print(f"  🚫 Rate limits: {rate_limits}")
            if timeouts > 0:
                print(f"  ⏱️  Timeouts: {timeouts}")
            print(f"  ⏱️  Total time: {total_time:.1f}s")
            print(f"  ⏱️  Avg per request: {avg_time:.1f}s")
            print(f"  📈 Success rate: {result['success_rate']:.1f}%")
            
            return result


async def main():
    """Main test execution"""
    # Use the same companies we'll actually process (top ones from database)
    test_companies = [
        (815158, "Simplifai"),
        (6318413, "DefendSphere"),
        (1352007, "Granter"),
        (1032611, "OASYS NOW"),
        (2500795, "Kiku"),
        (175299, "PromoRepublic"),
        (1224573, "Earthian AI"),
        (1191723, "Jido"),
        (707222, "Powerful Medical"),
        (1204229, "Straion"),
    ]
    
    tester = ConcurrencyTester()
    
    print("=" * 80)
    print("CB INSIGHTS API - CONCURRENCY LIMIT TEST")
    print("=" * 80)
    print(f"Test companies: {len(test_companies)}")
    print(f"Test IDs: {[c[1] for c in test_companies]}")
    print(f"Timeout per request: {REQUEST_TIMEOUT}s")
    
    # Test with increasing concurrency levels
    test_levels = [1, 2, 3, 4, 5]
    
    for level in test_levels:
        result = await tester.test_concurrency_level(level, test_companies)
        
        if not result.get("success"):
            print(f"\n⚠️  Stopping tests - concurrency {level} had errors")
            break
        
        # Stop if we hit rate limits
        if result.get("rate_limits", 0) > 0:
            print(f"\n⚠️  Rate limits detected at concurrency {level}")
            print("   Recommend using lower concurrency")
            break
        
        # Stop if success rate drops below 80%
        if result.get("success_rate", 0) < 80:
            print(f"\n⚠️  Success rate dropped below 80% at concurrency {level}")
            break
        
        # Brief pause between test levels
        await asyncio.sleep(5)
    
    # Print final recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    
    if tester.results:
        # Find best concurrency
        valid_results = {k: v for k, v in tester.results.items() if v.get("success_rate", 0) >= 80 and v.get("rate_limits", 0) == 0}
        
        if valid_results:
            best_concurrency = max(valid_results.items(), key=lambda x: x[1].get("success_rate", 0))[0]
            best_result = valid_results[best_concurrency]
            
            print(f"✅ SAFE MAXIMUM CONCURRENCY: {best_concurrency}")
            print(f"\n   At this level:")
            print(f"   - Success rate: {best_result['success_rate']:.1f}%")
            print(f"   - Avg time per report: {best_result['avg_time_per_request']:.1f}s")
            print(f"   - Total time for 775 reports: ~{(775 / best_concurrency * best_result['avg_time_per_request']) / 3600:.1f} hours")
            print(f"   - Rate: {best_result['requests_per_second']:.2f} requests/second")
            
            if best_concurrency == 1:
                print(f"\n💡 Recommendation: Use concurrency={best_concurrency} (sequential processing)")
                print(f"   The API appears to throttle concurrent requests")
            else:
                print(f"\n💡 Recommendation: Use concurrency={best_concurrency} (parallel processing)")
                print(f"   This provides good speed without hitting rate limits")
        else:
            print("⚠️  No safe concurrency levels found")
            print("   Recommend: concurrency=1 (sequential processing)")
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
