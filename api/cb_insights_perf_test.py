"""
CB Insights API Performance Testing and Optimization
Tests different strategies for efficiently enriching startup data from CB Insights
"""

import os
import csv
import json
import time
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Track performance metrics for API calls"""
    strategy_name: str
    total_orgs: int
    api_calls: int
    success_count: int
    failure_count: int
    total_time_seconds: float
    data_retrieved_mb: float
    orgs_per_second: float
    cost_per_org: float  # Estimated based on API calls
    
    def __str__(self) -> str:
        return f"""
{self.strategy_name}:
  Total Orgs: {self.total_orgs}
  API Calls: {self.api_calls}
  Success: {self.success_count}, Failures: {self.failure_count}
  Time: {self.total_time_seconds:.2f}s
  Data Retrieved: {self.data_retrieved_mb:.2f}MB
  Throughput: {self.orgs_per_second:.2f} orgs/sec
  Cost/Org: {self.cost_per_org:.2f} API credits (est.)
        """


class CBInsightsAPITester:
    """Test CB Insights API performance with different strategies"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or os.getenv('CBI_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('CBI_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "CB Insights credentials not provided. "
                "Set CBI_CLIENT_ID and CBI_CLIENT_SECRET environment variables"
            )
        
        self.base_url = "https://api.cbinsights.com"
        self.token = None
        self.metrics_log = []
    
    def authorize(self) -> bool:
        """Get authorization token"""
        try:
            url = f"{self.base_url}/v2/authorize"
            payload = {
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.token = data.get('accessToken')
            
            if self.token:
                logger.info("✅ Successfully authorized with CB Insights API")
                return True
            else:
                logger.error("❌ Failed to get access token")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authorization failed: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        if not self.token:
            raise ValueError("Not authorized. Call authorize() first.")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def load_org_ids(self, csv_path: str) -> List[int]:
        """Load org IDs from CSV file"""
        org_ids = []
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    org_id = row.get('cb_insights_id')
                    if org_id:
                        try:
                            org_ids.append(int(org_id))
                        except ValueError:
                            logger.warning(f"Invalid org ID: {org_id}")
            
            logger.info(f"✅ Loaded {len(org_ids)} org IDs from {csv_path}")
            return org_ids
            
        except Exception as e:
            logger.error(f"❌ Failed to load CSV: {e}")
            return []
    
    # ========================================
    # Strategy 1: Sequential Individual Calls
    # ========================================
    
    def test_sequential_individual(self, org_ids: List[int], limit: int = 10) -> PerformanceMetrics:
        """Test: One API call per org (baseline)"""
        logger.info("\n" + "="*70)
        logger.info("Strategy 1: Sequential Individual Calls (1 org/call)")
        logger.info("="*70)
        
        org_ids_sample = org_ids[:limit]
        start_time = time.time()
        
        success_count = 0
        total_data_bytes = 0
        
        for i, org_id in enumerate(org_ids_sample, 1):
            try:
                url = f"{self.base_url}/v2/firmographics"
                payload = {"orgIds": [org_id]}
                headers = self._get_headers()
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                total_data_bytes += len(json.dumps(data))
                
                if data.get('orgs'):
                    success_count += 1
                    logger.info(f"  [{i}/{limit}] ✅ Org ID {org_id}: {len(data.get('orgs', []))} results")
                else:
                    logger.warning(f"  [{i}/{limit}] ⚠️  Org ID {org_id}: No data")
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"  [{i}/{limit}] ❌ Org ID {org_id}: {e}")
        
        elapsed = time.time() - start_time
        
        metrics = PerformanceMetrics(
            strategy_name="Sequential Individual (1 org/call)",
            total_orgs=len(org_ids_sample),
            api_calls=len(org_ids_sample),
            success_count=success_count,
            failure_count=len(org_ids_sample) - success_count,
            total_time_seconds=elapsed,
            data_retrieved_mb=total_data_bytes / (1024 * 1024),
            orgs_per_second=len(org_ids_sample) / elapsed if elapsed > 0 else 0,
            cost_per_org=1.0  # Each org = 1 API call
        )
        
        logger.info(metrics)
        return metrics
    
    # ========================================
    # Strategy 2: Batched Calls (10 orgs/call)
    # ========================================
    
    def test_batched_calls(self, org_ids: List[int], batch_size: int = 10, limit: int = 100) -> PerformanceMetrics:
        """Test: Batch multiple orgs per API call"""
        logger.info("\n" + "="*70)
        logger.info(f"Strategy 2: Batched Calls ({batch_size} orgs/call)")
        logger.info("="*70)
        
        org_ids_sample = org_ids[:limit]
        start_time = time.time()
        
        success_count = 0
        total_data_bytes = 0
        api_calls = 0
        
        # Split into batches
        batches = [org_ids_sample[i:i + batch_size] for i in range(0, len(org_ids_sample), batch_size)]
        
        for batch_num, batch in enumerate(batches, 1):
            try:
                url = f"{self.base_url}/v2/firmographics"
                payload = {"orgIds": batch}
                headers = self._get_headers()
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                total_data_bytes += len(json.dumps(data))
                api_calls += 1
                
                num_results = len(data.get('orgs', []))
                success_count += num_results
                logger.info(f"  [Batch {batch_num}] ✅ {len(batch)} orgs: {num_results} results")
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"  [Batch {batch_num}] ❌ {e}")
        
        elapsed = time.time() - start_time
        
        metrics = PerformanceMetrics(
            strategy_name=f"Batched Calls ({batch_size} orgs/call)",
            total_orgs=len(org_ids_sample),
            api_calls=api_calls,
            success_count=success_count,
            failure_count=len(org_ids_sample) - success_count,
            total_time_seconds=elapsed,
            data_retrieved_mb=total_data_bytes / (1024 * 1024),
            orgs_per_second=len(org_ids_sample) / elapsed if elapsed > 0 else 0,
            cost_per_org=api_calls / len(org_ids_sample) if org_ids_sample else 0
        )
        
        logger.info(metrics)
        return metrics
    
    # ========================================
    # Strategy 3: Parallel Batched Calls
    # ========================================
    
    def test_parallel_batched(self, org_ids: List[int], batch_size: int = 20, 
                             max_workers: int = 5, limit: int = 100) -> PerformanceMetrics:
        """Test: Parallel batch requests with thread pool"""
        logger.info("\n" + "="*70)
        logger.info(f"Strategy 3: Parallel Batched ({batch_size} orgs/call, {max_workers} workers)")
        logger.info("="*70)
        
        org_ids_sample = org_ids[:limit]
        start_time = time.time()
        
        success_count = 0
        total_data_bytes = 0
        api_calls = 0
        
        # Split into batches
        batches = [org_ids_sample[i:i + batch_size] for i in range(0, len(org_ids_sample), batch_size)]
        
        def fetch_batch(batch_num: int, batch: List[int]) -> Tuple[int, int, int]:
            """Fetch a batch of org data"""
            try:
                url = f"{self.base_url}/v2/firmographics"
                payload = {"orgIds": batch}
                headers = self._get_headers()
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                num_results = len(data.get('orgs', []))
                data_bytes = len(json.dumps(data))
                
                logger.info(f"  [Batch {batch_num}] ✅ {len(batch)} orgs: {num_results} results")
                return num_results, data_bytes, 1
                
            except Exception as e:
                logger.error(f"  [Batch {batch_num}] ❌ {e}")
                return 0, 0, 1
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_batch, i, batch): i 
                for i, batch in enumerate(batches, 1)
            }
            
            for future in as_completed(futures):
                results, data_bytes, calls = future.result()
                success_count += results
                total_data_bytes += data_bytes
                api_calls += calls
        
        elapsed = time.time() - start_time
        
        metrics = PerformanceMetrics(
            strategy_name=f"Parallel Batched ({batch_size} orgs/call, {max_workers} workers)",
            total_orgs=len(org_ids_sample),
            api_calls=api_calls,
            success_count=success_count,
            failure_count=len(org_ids_sample) - success_count,
            total_time_seconds=elapsed,
            data_retrieved_mb=total_data_bytes / (1024 * 1024),
            orgs_per_second=len(org_ids_sample) / elapsed if elapsed > 0 else 0,
            cost_per_org=api_calls / len(org_ids_sample) if org_ids_sample else 0
        )
        
        logger.info(metrics)
        return metrics
    
    # ========================================
    # Strategy 4: Funding Rounds Focused
    # ========================================
    
    def test_funding_rounds_strategy(self, org_ids: List[int], batch_size: int = 5, limit: int = 50) -> PerformanceMetrics:
        """Test: Dual-endpoint strategy for both firmographics AND funding rounds"""
        logger.info("\n" + "="*70)
        logger.info(f"Strategy 4: Funding Rounds Focus (Firmographics + Fundings)")
        logger.info("="*70)
        
        org_ids_sample = org_ids[:limit]
        start_time = time.time()
        
        success_count = 0
        total_data_bytes = 0
        api_calls = 0
        
        # Step 1: Get firmographics in batches
        batches = [org_ids_sample[i:i + batch_size] for i in range(0, len(org_ids_sample), batch_size)]
        
        logger.info("\n📊 Phase 1: Fetching Firmographics...")
        for batch_num, batch in enumerate(batches, 1):
            try:
                url = f"{self.base_url}/v2/firmographics"
                payload = {"orgIds": batch}
                headers = self._get_headers()
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                num_results = len(data.get('orgs', []))
                total_data_bytes += len(json.dumps(data))
                api_calls += 1
                success_count += num_results
                
                logger.info(f"  [Batch {batch_num}] ✅ Firmographics: {num_results} orgs")
                
                time.sleep(0.05)
                
            except Exception as e:
                logger.error(f"  [Batch {batch_num}] ❌ Firmographics: {e}")
        
        # Step 2: Get funding rounds for same orgs
        logger.info("\n💰 Phase 2: Fetching Funding Rounds...")
        for batch_num, batch in enumerate(batches, 1):
            try:
                url = f"{self.base_url}/v2/financialtransactions/fundings"
                payload = {"orgIds": batch}
                headers = self._get_headers()
                
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                num_results = sum(len(org.get('fundings', [])) for org in data.get('orgs', []))
                total_data_bytes += len(json.dumps(data))
                api_calls += 1
                
                logger.info(f"  [Batch {batch_num}] ✅ Fundings: {num_results} rounds")
                
                time.sleep(0.05)
                
            except Exception as e:
                logger.error(f"  [Batch {batch_num}] ❌ Fundings: {e}")
        
        elapsed = time.time() - start_time
        
        metrics = PerformanceMetrics(
            strategy_name="Dual Endpoints (Firmographics + Fundings)",
            total_orgs=len(org_ids_sample),
            api_calls=api_calls,
            success_count=success_count,
            failure_count=len(org_ids_sample) - success_count,
            total_time_seconds=elapsed,
            data_retrieved_mb=total_data_bytes / (1024 * 1024),
            orgs_per_second=len(org_ids_sample) / elapsed if elapsed > 0 else 0,
            cost_per_org=api_calls / len(org_ids_sample) if org_ids_sample else 0
        )
        
        logger.info(metrics)
        return metrics
    
    def print_comparison(self, metrics_list: List[PerformanceMetrics]):
        """Print comparison of all strategies"""
        logger.info("\n" + "="*70)
        logger.info("PERFORMANCE COMPARISON SUMMARY")
        logger.info("="*70)
        
        print("\n┌─────────────────────────────────────────────────────────────┐")
        print("│ Strategy                          │ Time   │ Orgs/sec │ Cost │")
        print("├─────────────────────────────────────────────────────────────┤")
        
        for metrics in metrics_list:
            strategy = metrics.strategy_name[:30].ljust(30)
            time_str = f"{metrics.total_time_seconds:6.2f}s".ljust(8)
            throughput = f"{metrics.orgs_per_second:7.2f}".ljust(9)
            cost = f"{metrics.cost_per_org:5.2f}".ljust(6)
            print(f"│ {strategy} │ {time_str} │ {throughput} │ {cost} │")
        
        print("└─────────────────────────────────────────────────────────────┘")
        
        # Find winner
        best_time = min(metrics_list, key=lambda m: m.total_time_seconds)
        best_cost = min(metrics_list, key=lambda m: m.cost_per_org)
        best_throughput = max(metrics_list, key=lambda m: m.orgs_per_second)
        
        logger.info(f"\n🏆 Fastest: {best_time.strategy_name} ({best_time.total_time_seconds:.2f}s)")
        logger.info(f"💰 Cheapest: {best_cost.strategy_name} ({best_cost.cost_per_org:.2f} credits/org)")
        logger.info(f"⚡ Best Throughput: {best_throughput.strategy_name} ({best_throughput.orgs_per_second:.2f} orgs/sec)")


def main():
    """Run all performance tests"""
    
    # Load CSV
    csv_path = "/home/akyo/startup_swiper/downloads/startup_resolution_resolved_20251116_023054.csv"
    
    # Check if credentials are set
    if not os.getenv('CBI_CLIENT_ID') or not os.getenv('CBI_CLIENT_SECRET'):
        logger.error("❌ CB Insights credentials not set")
        logger.error("   Set CBI_CLIENT_ID and CBI_CLIENT_SECRET environment variables")
        return
    
    try:
        # Initialize tester
        tester = CBInsightsAPITester()
        
        # Authorize
        if not tester.authorize():
            return
        
        # Load org IDs from CSV
        org_ids = tester.load_org_ids(csv_path)
        if not org_ids:
            return
        
        # Run tests
        metrics_list = []
        
        # Strategy 1: Sequential individual (small sample)
        print("\n\n🧪 Testing Strategy 1: Sequential Individual Calls")
        m1 = tester.test_sequential_individual(org_ids, limit=5)
        metrics_list.append(m1)
        
        # Strategy 2: Batched calls
        print("\n\n🧪 Testing Strategy 2: Batched Calls")
        m2 = tester.test_batched_calls(org_ids, batch_size=10, limit=50)
        metrics_list.append(m2)
        
        # Strategy 3: Parallel batched
        print("\n\n🧪 Testing Strategy 3: Parallel Batched Calls")
        m3 = tester.test_parallel_batched(org_ids, batch_size=15, max_workers=3, limit=50)
        metrics_list.append(m3)
        
        # Strategy 4: Funding rounds focused
        print("\n\n🧪 Testing Strategy 4: Dual Endpoints (Firmographics + Fundings)")
        m4 = tester.test_funding_rounds_strategy(org_ids, batch_size=5, limit=30)
        metrics_list.append(m4)
        
        # Print comparison
        tester.print_comparison(metrics_list)
        
        # Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "org_count": len(org_ids),
            "strategies": [
                {
                    "name": m.strategy_name,
                    "total_orgs": m.total_orgs,
                    "api_calls": m.api_calls,
                    "success_count": m.success_count,
                    "total_time_seconds": m.total_time_seconds,
                    "data_mb": m.data_retrieved_mb,
                    "orgs_per_second": m.orgs_per_second,
                    "cost_per_org": m.cost_per_org,
                }
                for m in metrics_list
            ]
        }
        
        results_file = "/home/akyo/startup_swiper/api/cb_insights_perf_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n✅ Results saved to {results_file}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
