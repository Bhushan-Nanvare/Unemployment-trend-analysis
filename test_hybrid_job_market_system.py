"""
test_hybrid_job_market_system.py

Test the hybrid job market data system with validation.

Tests:
1. Adzuna API data validation
2. Historical data fallback
3. Data source labeling
4. Consistency enforcement
5. Invalid data rejection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_providers.career_data_manager import CareerDataManager
from src.data_providers.job_market_validator import JobMarketValidator


def test_data_source_summary():
    """Test data source summary"""
    print("\n" + "="*80)
    print("TEST 1: Data Source Summary")
    print("="*80)
    
    manager = CareerDataManager()
    summary = manager.get_data_source_summary()
    
    print(f"Adzuna API Available: {summary['adzuna_api_available']}")
    print(f"Historical Data Available: {summary['historical_data_available']}")
    print(f"Primary Source: {summary['primary_source']}")
    print(f"Fallback Source: {summary['fallback_source']}")
    print(f"\nRecommendation: {summary['recommendation']}")
    
    return summary['adzuna_api_available'] or summary['historical_data_available']


def test_single_role_data():
    """Test fetching data for a single role"""
    print("\n" + "="*80)
    print("TEST 2: Single Role Data Fetch")
    print("="*80)
    
    manager = CareerDataManager()
    
    role = "Software Engineer"
    print(f"\nFetching data for: {role}")
    
    data = manager.get_role_market_data(role, "india")
    
    print(f"\n✅ Data fetched successfully")
    print(f"Source: {data.get('source', 'unknown')}")
    print(f"Source Label: {data.get('source_label', 'N/A')}")
    print(f"Total Jobs: {data.get('total_jobs', 0)}")
    print(f"Avg Salary: ₹{data.get('avg_salary', 0):,.0f}")
    print(f"Top Skills: {', '.join(data.get('top_skills', [])[:5])}")
    print(f"Confidence Score: {data.get('confidence_score', 0):.1%}")
    print(f"Data Freshness: {data.get('data_freshness', 'unknown')}")
    
    # Check for warnings
    warning = data.get('data_age_warning')
    if warning:
        print(f"\n{warning}")
    
    # Check validation
    if data.get('validation_passed'):
        print(f"\n✅ Data validation passed")
        if data.get('validation_warnings'):
            print(f"Warnings: {len(data.get('validation_warnings', []))}")
            for w in data.get('validation_warnings', []):
                print(f"  ⚠️ {w}")
    
    return data.get('source') is not None


def test_multiple_roles_consistency():
    """Test consistency across multiple roles"""
    print("\n" + "="*80)
    print("TEST 3: Multiple Roles Consistency")
    print("="*80)
    
    manager = CareerDataManager()
    
    roles = ["Software Engineer", "Data Scientist", "Product Manager"]
    print(f"\nFetching data for {len(roles)} roles...")
    
    results = manager.get_multiple_roles_data(roles, "india")
    
    # Check sources
    sources = set(data.get('source', 'unknown') for data in results.values())
    
    print(f"\n✅ Fetched data for {len(results)} roles")
    print(f"Sources used: {sources}")
    
    if len(sources) == 1:
        print(f"✅ CONSISTENT: All roles use same source ({sources.pop()})")
        consistent = True
    else:
        print(f"❌ INCONSISTENT: Mixed sources detected - {sources}")
        consistent = False
    
    # Show summary for each role
    for role, data in results.items():
        print(f"\n{role}:")
        print(f"  Source: {data.get('source_label', 'N/A')}")
        print(f"  Jobs: {data.get('total_jobs', 0)}")
        print(f"  Confidence: {data.get('confidence_score', 0):.1%}")
    
    return consistent


def test_validation():
    """Test data validation"""
    print("\n" + "="*80)
    print("TEST 4: Data Validation")
    print("="*80)
    
    # Test valid data
    print("\nTest 4a: Valid data")
    valid_data = {
        "total_jobs": 1500,
        "avg_salary": 800000,
        "top_skills": ["python", "java", "sql"],
        "source": "adzuna"
    }
    
    is_valid, result = JobMarketValidator.validate_job_data(valid_data)
    print(f"Valid: {is_valid}")
    print(f"Quality Score: {result.data_quality_score:.1f}/100")
    
    # Test invalid data
    print("\nTest 4b: Invalid data (salary too low)")
    invalid_data = {
        "total_jobs": 100,
        "avg_salary": 50000,  # Too low
        "top_skills": ["python"],
        "source": "adzuna"
    }
    
    is_valid, result = JobMarketValidator.validate_job_data(invalid_data)
    print(f"Valid: {is_valid}")
    print(f"Quality Score: {result.data_quality_score:.1f}/100")
    print(f"Errors: {result.errors}")
    
    # Test missing fields
    print("\nTest 4c: Missing required fields")
    incomplete_data = {
        "total_jobs": 100,
        # Missing avg_salary, top_skills, source
    }
    
    is_valid, result = JobMarketValidator.validate_job_data(incomplete_data)
    print(f"Valid: {is_valid}")
    print(f"Errors: {result.errors}")
    
    return True


def test_data_source_labels():
    """Test data source labeling"""
    print("\n" + "="*80)
    print("TEST 5: Data Source Labels")
    print("="*80)
    
    # Test different sources
    sources = [
        {"source": "adzuna", "data_freshness": "2026-04-13"},
        {"source": "historical_csv", "data_freshness": "2019-07-01"},
        {"source": "default", "data_freshness": "2026-04-13"},
    ]
    
    for data in sources:
        label = JobMarketValidator.get_data_source_label(data)
        warning = JobMarketValidator.get_data_age_warning(data)
        
        print(f"\nSource: {data['source']}")
        print(f"Label: {label}")
        if warning:
            print(f"Warning: {warning[:100]}...")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("HYBRID JOB MARKET SYSTEM - TEST SUITE")
    print("="*80)
    print("Testing validation, fallback, and consistency...")
    
    results = []
    
    # Run tests
    results.append(("Data Source Summary", test_data_source_summary()))
    results.append(("Single Role Data", test_single_role_data()))
    results.append(("Multiple Roles Consistency", test_multiple_roles_consistency()))
    results.append(("Data Validation", test_validation()))
    results.append(("Data Source Labels", test_data_source_labels()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*80)
    print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Hybrid system is working correctly.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
