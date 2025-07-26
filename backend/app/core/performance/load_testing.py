import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics
import logging

logger = logging.getLogger(__name__)

class LoadTester:
    """Load testing service for performance validation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def single_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", data: dict = None) -> Dict:
        """Execute single HTTP request and measure performance"""
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    status = response.status
                    response_time = time.time() - start_time
                    content_length = len(await response.text())
            else:
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    status = response.status
                    response_time = time.time() - start_time
                    content_length = len(await response.text())
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status": status,
                "response_time": response_time,
                "content_length": content_length,
                "success": 200 <= status < 400
            }
        
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status": 0,
                "response_time": time.time() - start_time,
                "content_length": 0,
                "success": False,
                "error": str(e)
            }
    
    async def concurrent_load_test(self, endpoint: str, concurrent_users: int = 10, requests_per_user: int = 10) -> Dict:
        """Run concurrent load test on endpoint"""
        
        async def user_session(user_id: int):
            """Simulate single user session"""
            user_results = []
            
            async with aiohttp.ClientSession() as session:
                for request_num in range(requests_per_user):
                    result = await self.single_request(session, endpoint)
                    result["user_id"] = user_id
                    result["request_num"] = request_num
                    user_results.append(result)
                    
                    # Small delay between requests
                    await asyncio.sleep(0.1)
            
            return user_results
        
        # Run concurrent user sessions
        start_time = time.time()
        tasks = [user_session(user_id) for user_id in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Flatten results
        flat_results = [result for user_results in all_results for result in user_results]
        
        # Calculate statistics
        response_times = [r["response_time"] for r in flat_results if r["success"]]
        success_count = sum(1 for r in flat_results if r["success"])
        total_requests = len(flat_results)
        
        return {
            "endpoint": endpoint,
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": total_requests,
            "successful_requests": success_count,
            "failed_requests": total_requests - success_count,
            "success_rate": (success_count / total_requests) * 100 if total_requests > 0 else 0,
            "total_test_time": total_time,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "response_time_stats": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0
            }
        }
    
    async def stress_test_suite(self) -> Dict:
        """Run comprehensive stress test suite"""
        
        test_endpoints = [
            "/api/integration/financial-summary/1",
            "/api/accounts-payable/vendors",
            "/api/accounts-receivable/customers",
            "/api/cash-management/cash-position",
            "/api/budget/budgets"
        ]
        
        test_scenarios = [
            {"users": 5, "requests": 10, "name": "light_load"},
            {"users": 10, "requests": 20, "name": "medium_load"},
            {"users": 20, "requests": 30, "name": "heavy_load"}
        ]
        
        suite_results = {
            "test_start_time": time.time(),
            "endpoint_results": {},
            "scenario_results": {}
        }
        
        for endpoint in test_endpoints:
            endpoint_results = []
            
            for scenario in test_scenarios:
                logger.info(f"Testing {endpoint} with {scenario['users']} users, {scenario['requests']} requests each")
                
                result = await self.concurrent_load_test(
                    endpoint, 
                    concurrent_users=scenario["users"], 
                    requests_per_user=scenario["requests"]
                )
                
                result["scenario"] = scenario["name"]
                endpoint_results.append(result)
                
                # Brief pause between scenarios
                await asyncio.sleep(2)
            
            suite_results["endpoint_results"][endpoint] = endpoint_results
        
        # Calculate overall statistics
        suite_results["test_end_time"] = time.time()
        suite_results["total_test_duration"] = suite_results["test_end_time"] - suite_results["test_start_time"]
        
        # Aggregate results by scenario
        for scenario in test_scenarios:
            scenario_stats = {
                "total_requests": 0,
                "successful_requests": 0,
                "average_response_time": 0,
                "average_rps": 0
            }
            
            scenario_results = []
            for endpoint_results in suite_results["endpoint_results"].values():
                scenario_result = next((r for r in endpoint_results if r["scenario"] == scenario["name"]), None)
                if scenario_result:
                    scenario_results.append(scenario_result)
            
            if scenario_results:
                scenario_stats["total_requests"] = sum(r["total_requests"] for r in scenario_results)
                scenario_stats["successful_requests"] = sum(r["successful_requests"] for r in scenario_results)
                scenario_stats["average_response_time"] = statistics.mean([r["response_time_stats"]["mean"] for r in scenario_results])
                scenario_stats["average_rps"] = statistics.mean([r["requests_per_second"] for r in scenario_results])
            
            suite_results["scenario_results"][scenario["name"]] = scenario_stats
        
        return suite_results
    
    def generate_performance_report(self, results: Dict) -> str:
        """Generate human-readable performance report"""
        
        report = f"""
LOAD TEST PERFORMANCE REPORT
============================

Test Duration: {results['total_test_duration']:.2f} seconds
Test Start: {time.ctime(results['test_start_time'])}

SCENARIO SUMMARY:
"""
        
        for scenario_name, stats in results["scenario_results"].items():
            success_rate = (stats["successful_requests"] / stats["total_requests"]) * 100 if stats["total_requests"] > 0 else 0
            
            report += f"""
{scenario_name.upper()}:
  Total Requests: {stats['total_requests']}
  Successful: {stats['successful_requests']} ({success_rate:.1f}%)
  Avg Response Time: {stats['average_response_time']:.3f}s
  Avg RPS: {stats['average_rps']:.1f}
"""
        
        report += "\nENDPOINT DETAILS:\n"
        
        for endpoint, endpoint_results in results["endpoint_results"].items():
            report += f"\n{endpoint}:\n"
            
            for result in endpoint_results:
                report += f"  {result['scenario']}: {result['success_rate']:.1f}% success, "
                report += f"{result['response_time_stats']['mean']:.3f}s avg, "
                report += f"{result['requests_per_second']:.1f} RPS\n"
        
        return report

# Usage example
async def run_load_tests():
    """Run load tests and generate report"""
    tester = LoadTester()
    results = await tester.stress_test_suite()
    report = tester.generate_performance_report(results)
    
    print(report)
    
    # Save results to file
    with open("load_test_results.json", "w") as f:
        import json
        json.dump(results, f, indent=2, default=str)
    
    return results