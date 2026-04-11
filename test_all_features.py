"""
Comprehensive Feature Testing Script
Tests all API endpoints and generates a detailed report
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

def test_endpoint(name, method, url, payload=None, expected_keys=None):
    """Test a single endpoint and return results"""
    try:
        start = time.time()
        if method == "GET":
            response = requests.get(url, timeout=30)
        else:
            response = requests.post(url, json=payload, timeout=30)
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            status = "✅ PASS"
            
            # Check for expected keys
            if expected_keys:
                missing = [k for k in expected_keys if k not in data]
                if missing:
                    status = f"⚠️ PARTIAL (missing: {missing})"
            
            return {
                "name": name,
                "status": status,
                "time": f"{elapsed:.2f}s",
                "response_size": len(json.dumps(data)),
                "details": f"Status: {response.status_code}"
            }
        else:
            return {
                "name": name,
                "status": "❌ FAIL",
                "time": f"{elapsed:.2f}s",
                "response_size": 0,
                "details": f"Status: {response.status_code}, Error: {response.text[:100]}"
            }
    except Exception as e:
        return {
            "name": name,
            "status": "❌ ERROR",
            "time": "N/A",
            "response_size": 0,
            "details": str(e)[:100]
        }

def run_all_tests():
    """Run comprehensive tests on all features"""
    print("=" * 80)
    print("UNEMPLOYMENT INTELLIGENCE PLATFORM - FEATURE TEST REPORT")
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    results = []
    
    # 1. Data Status Check
    print("📊 Testing Core Data Services...")
    results.append(test_endpoint(
        "Data Status Check",
        "GET",
        f"{API_BASE}/data-status",
        expected_keys=["source", "country"]
    ))
    
    # 2. Baseline Simulation
    print("🧪 Testing Simulation Engine...")
    results.append(test_endpoint(
        "Baseline Simulation",
        "POST",
        f"{API_BASE}/simulate",
        payload={
            "shock_intensity": 0.0,
            "shock_duration": 0,
            "recovery_rate": 0.0,
            "forecast_horizon": 6
        },
        expected_keys=["baseline", "shocked", "indices"]
    ))
    
    # 3. Shock Scenario
    results.append(test_endpoint(
        "Shock Scenario (Moderate)",
        "POST",
        f"{API_BASE}/simulate",
        payload={
            "shock_intensity": 3.0,
            "shock_duration": 2,
            "recovery_rate": 0.3,
            "forecast_horizon": 6
        },
        expected_keys=["baseline", "shocked", "indices"]
    ))
    
    # 4. Backtesting
    print("🔬 Testing Model Validation...")
    results.append(test_endpoint(
        "Backtesting Model",
        "POST",
        f"{API_BASE}/backtest",
        payload={"test_years": 3},
        expected_keys=["historical", "backtest", "mae", "mape"]
    ))
    
    # 5. Model Validation
    results.append(test_endpoint(
        "Model Validation Report",
        "GET",
        f"{API_BASE}/validate",
        expected_keys=["r2_score", "mae"]
    ))
    
    # 6. Sensitivity Analysis
    print("📈 Testing Sensitivity Analysis...")
    results.append(test_endpoint(
        "Sensitivity Analysis",
        "POST",
        f"{API_BASE}/sensitivity_analysis",
        payload={
            "base_shock_intensity": 0.3,
            "base_shock_duration": 2,
            "base_recovery_rate": 0.3,
            "forecast_horizon": 6
        },
        expected_keys=["tornado_data", "heatmap_data"]
    ))
    
    # 7. Historical Events
    print("📚 Testing Historical Events...")
    results.append(test_endpoint(
        "Historical Events",
        "GET",
        f"{API_BASE}/events",
        expected_keys=["events"]
    ))
    
    # Print Results
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for r in results if "✅" in r["status"])
    partial = sum(1 for r in results if "⚠️" in r["status"])
    failed = sum(1 for r in results if "❌" in r["status"])
    
    print(f"{'Feature':<40} {'Status':<15} {'Time':<10} {'Size (bytes)'}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['name']:<40} {result['status']:<15} {result['time']:<10} {result['response_size']}")
        if "FAIL" in result['status'] or "ERROR" in result['status']:
            print(f"  └─ {result['details']}")
    
    print("-" * 80)
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️ Partial: {partial}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
    print()
    
    # Feature Coverage
    print("=" * 80)
    print("FEATURE COVERAGE BY PAGE")
    print("=" * 80)
    print()
    
    features = {
        "📊 Overview Dashboard": ["Data Status Check", "Baseline Simulation", "Historical Events"],
        "🧪 Scenario Simulator": ["Shock Scenario (Moderate)", "Sensitivity Analysis"],
        "🔬 Model Validation": ["Backtesting Model", "Model Validation Report"],
    }
    
    for page, tests in features.items():
        page_results = [r for r in results if r["name"] in tests]
        page_passed = sum(1 for r in page_results if "✅" in r["status"])
        status_icon = "✅" if page_passed == len(page_results) else "⚠️" if page_passed > 0 else "❌"
        print(f"{status_icon} {page}: {page_passed}/{len(page_results)} tests passed")
    
    print()
    print("=" * 80)
    print("🌐 BROWSER ACCESS")
    print("=" * 80)
    print()
    print("Frontend: http://localhost:8501")
    print("Backend API Docs: http://localhost:8000/docs")
    print()
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    run_all_tests()
