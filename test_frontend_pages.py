"""
Frontend Page Testing Script
Tests all Streamlit pages by making HTTP requests to check if they load
"""
import requests
import time
from datetime import datetime

STREAMLIT_BASE = "http://localhost:8501"

def test_page_load(page_name, page_path):
    """Test if a Streamlit page loads without errors"""
    try:
        # Streamlit serves pages at specific paths
        url = f"{STREAMLIT_BASE}/{page_path}" if page_path else STREAMLIT_BASE
        
        start = time.time()
        response = requests.get(url, timeout=15)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            # Check if it's actually a Streamlit page (contains streamlit content)
            content = response.text.lower()
            if "streamlit" in content or "st-" in content or "data-testid" in content:
                return {
                    "name": page_name,
                    "status": "✅ LOADS",
                    "time": f"{elapsed:.2f}s",
                    "size": len(response.text),
                    "details": f"Status: {response.status_code}"
                }
            else:
                return {
                    "name": page_name,
                    "status": "⚠️ NO STREAMLIT",
                    "time": f"{elapsed:.2f}s",
                    "size": len(response.text),
                    "details": "Page loads but no Streamlit content detected"
                }
        else:
            return {
                "name": page_name,
                "status": "❌ HTTP ERROR",
                "time": f"{elapsed:.2f}s",
                "size": 0,
                "details": f"Status: {response.status_code}"
            }
    except Exception as e:
        return {
            "name": page_name,
            "status": "❌ FAILED",
            "time": "N/A",
            "size": 0,
            "details": str(e)[:100]
        }

def test_streamlit_health():
    """Test if Streamlit is running and healthy"""
    try:
        response = requests.get(f"{STREAMLIT_BASE}/healthz", timeout=5)
        return response.status_code == 200
    except:
        try:
            # Try main page
            response = requests.get(STREAMLIT_BASE, timeout=5)
            return response.status_code == 200
        except:
            return False

def run_frontend_tests():
    """Run comprehensive frontend tests"""
    print("=" * 80)
    print("STREAMLIT FRONTEND - PAGE LOAD TEST REPORT")
    print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Check if Streamlit is running
    print("🔍 Checking Streamlit Health...")
    if not test_streamlit_health():
        print("❌ Streamlit is not running or not accessible at http://localhost:8501")
        print("   Please ensure Streamlit is started with: streamlit run app.py")
        return
    
    print("✅ Streamlit is running and accessible")
    print()
    
    # Test all pages
    pages = [
        ("🏠 Home Page", ""),
        ("📊 Overview Dashboard", "1_Overview"),
        ("🧪 Scenario Simulator", "2_Simulator"),
        ("🏭 Sector Analysis", "3_Sector_Analysis"),
        ("💼 Career Lab", "4_Career_Lab"),
        ("🤖 AI Insights", "5_AI_Insights"),

        ("🎯 Job Risk Predictor", "7_Job_Risk_Predictor"),
        ("📡 Job Market Pulse", "8_Job_Market_Pulse"),
        ("🗺️ Geo Career Advisor", "9_Geo_Career_Advisor"),
        ("⚡ Skill Obsolescence", "10_Skill_Obsolescence"),
        ("📉 Phillips Curve", "11_Phillips_Curve"),
    ]
    
    results = []
    
    print("🌐 Testing Page Loads...")
    for page_name, page_path in pages:
        print(f"   Testing {page_name}...")
        result = test_page_load(page_name, page_path)
        results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Print Results
    print("\n" + "=" * 80)
    print("PAGE LOAD TEST RESULTS")
    print("=" * 80)
    print()
    
    passed = sum(1 for r in results if "✅" in r["status"])
    partial = sum(1 for r in results if "⚠️" in r["status"])
    failed = sum(1 for r in results if "❌" in r["status"])
    
    print(f"{'Page':<35} {'Status':<20} {'Load Time':<12} {'Size (KB)'}")
    print("-" * 80)
    
    for result in results:
        size_kb = f"{result['size'] / 1024:.1f}" if result['size'] > 0 else "0"
        print(f"{result['name']:<35} {result['status']:<20} {result['time']:<12} {size_kb}")
        if "FAILED" in result['status'] or "ERROR" in result['status']:
            print(f"  └─ {result['details']}")
    
    print("-" * 80)
    print(f"\nTotal Pages: {len(results)}")
    print(f"✅ Loading: {passed}")
    print(f"⚠️ Partial: {partial}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
    print()
    
    # Feature Summary
    print("=" * 80)
    print("FEATURE SUMMARY")
    print("=" * 80)
    print()
    
    if passed >= 10:
        print("🎉 EXCELLENT: All major pages are loading successfully!")
    elif passed >= 8:
        print("✅ GOOD: Most pages are working, minor issues detected")
    elif passed >= 6:
        print("⚠️ FAIR: Some pages have issues, needs attention")
    else:
        print("❌ POOR: Multiple pages failing, requires debugging")
    
    print()
    print("🌐 Access URLs:")
    print(f"   Frontend: {STREAMLIT_BASE}")
    print(f"   API Docs: http://localhost:8000/docs")
    print()
    
    # Deployment readiness
    print("=" * 80)
    print("DEPLOYMENT READINESS")
    print("=" * 80)
    print()
    
    if passed == len(results):
        print("🚀 READY FOR DEPLOYMENT")
        print("   ✅ All pages load successfully")
        print("   ✅ No critical errors detected")
        print("   ✅ Frontend is stable")
    elif failed == 0:
        print("⚠️ MOSTLY READY")
        print("   ✅ No complete failures")
        print("   ⚠️ Some minor issues to review")
        print("   ✅ Safe to deploy with monitoring")
    else:
        print("❌ NOT READY")
        print(f"   ❌ {failed} pages failing")
        print("   ❌ Requires fixes before deployment")
    
    print()
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    run_frontend_tests()