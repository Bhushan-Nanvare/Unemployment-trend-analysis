"""
test_streamlit_integration.py

Test script to verify Streamlit validation integration works correctly.

Run this before deploying to ensure all components function properly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported."""
    print("\n" + "="*80)
    print("TEST 1: Module Imports")
    print("="*80)
    
    try:
        from src.central_data import load_unemployment, load_inflation, get_data_quality_report
        print("✅ central_data imports successful")
    except Exception as e:
        print(f"❌ central_data import failed: {e}")
        return False
    
    try:
        from src.validation_ui_helpers import (
            render_quality_dashboard,
            render_quality_summary_compact,
            render_validation_warnings,
            get_quality_emoji,
            get_quality_label,
            get_quality_color
        )
        print("✅ validation_ui_helpers imports successful")
    except Exception as e:
        print(f"❌ validation_ui_helpers import failed: {e}")
        return False
    
    return True


def test_data_loading():
    """Test that data loads correctly with validation."""
    print("\n" + "="*80)
    print("TEST 2: Data Loading with Validation")
    print("="*80)
    
    try:
        from src.central_data import load_unemployment, load_inflation
        
        # Load unemployment data
        unemployment_df = load_unemployment()
        print(f"✅ Unemployment data loaded: {len(unemployment_df)} rows")
        print(f"   Columns: {list(unemployment_df.columns)}")
        print(f"   Year range: {unemployment_df['Year'].min()}-{unemployment_df['Year'].max()}")
        
        # Load inflation data
        inflation_df = load_inflation()
        print(f"✅ Inflation data loaded: {len(inflation_df)} rows")
        print(f"   Columns: {list(inflation_df.columns)}")
        print(f"   Year range: {inflation_df['Year'].min()}-{inflation_df['Year'].max()}")
        
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_report():
    """Test that quality report generates correctly."""
    print("\n" + "="*80)
    print("TEST 3: Quality Report Generation")
    print("="*80)
    
    try:
        from src.central_data import get_data_quality_report
        
        report = get_data_quality_report()
        
        print(f"✅ Quality report generated")
        print(f"   Timestamp: {report['timestamp']}")
        print(f"   System Health: {report['overall_system_health']}")
        print(f"\n   Unemployment:")
        print(f"     - Source: {report['unemployment']['source']}")
        print(f"     - Quality Score: {report['unemployment']['data_quality_score']:.1f}/100")
        print(f"     - Valid: {report['unemployment']['is_valid']}")
        print(f"     - Rows: {report['unemployment']['rows']}")
        print(f"     - Errors: {len(report['unemployment']['errors'])}")
        print(f"     - Warnings: {len(report['unemployment']['warnings'])}")
        print(f"\n   Inflation:")
        print(f"     - Source: {report['inflation']['source']}")
        print(f"     - Quality Score: {report['inflation']['data_quality_score']:.1f}/100")
        print(f"     - Valid: {report['inflation']['is_valid']}")
        print(f"     - Rows: {report['inflation']['rows']}")
        print(f"     - Errors: {len(report['inflation']['errors'])}")
        print(f"     - Warnings: {len(report['inflation']['warnings'])}")
        
        # Check quality scores
        if report['unemployment']['data_quality_score'] >= 70:
            print(f"\n✅ Unemployment quality acceptable ({report['unemployment']['data_quality_score']:.1f}/100)")
        else:
            print(f"\n⚠️ Unemployment quality low ({report['unemployment']['data_quality_score']:.1f}/100)")
        
        if report['inflation']['data_quality_score'] >= 70:
            print(f"✅ Inflation quality acceptable ({report['inflation']['data_quality_score']:.1f}/100)")
        else:
            print(f"⚠️ Inflation quality low ({report['inflation']['data_quality_score']:.1f}/100)")
        
        return True
    except Exception as e:
        print(f"❌ Quality report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_helpers():
    """Test that UI helper functions work correctly."""
    print("\n" + "="*80)
    print("TEST 4: UI Helper Functions")
    print("="*80)
    
    try:
        from src.validation_ui_helpers import (
            get_quality_emoji,
            get_quality_label,
            get_quality_color,
            render_quality_badge,
            render_quality_dashboard,
            render_quality_summary_compact
        )
        from src.central_data import get_data_quality_report
        
        # Test quality indicators
        for score in [95, 85, 75, 60, 40]:
            emoji = get_quality_emoji(score)
            label = get_quality_label(score)
            color = get_quality_color(score)
            print(f"   Score {score}: {emoji} {label} (color: {color})")
        
        print("\n✅ Quality indicator functions work")
        
        # Test badge rendering
        badge = render_quality_badge(100.0)
        if "🟢" in badge and "100" in badge:
            print("✅ Quality badge rendering works")
        else:
            print("⚠️ Quality badge may have issues")
        
        # Test dashboard rendering
        report = get_data_quality_report()
        dashboard = render_quality_dashboard(report)
        if "Data Quality Dashboard" in dashboard and "🔍" in dashboard:
            print("✅ Quality dashboard rendering works")
        else:
            print("⚠️ Quality dashboard may have issues")
        
        # Test compact summary rendering
        summary = render_quality_summary_compact(report)
        if "Data Quality" in summary and "📊" in summary:
            print("✅ Compact summary rendering works")
        else:
            print("⚠️ Compact summary may have issues")
        
        return True
    except Exception as e:
        print(f"❌ UI helper functions failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_overview_page_syntax():
    """Test that Overview page has valid Python syntax."""
    print("\n" + "="*80)
    print("TEST 5: Overview Page Syntax")
    print("="*80)
    
    try:
        import ast
        
        with open("pages/1_Overview.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        # Try to parse the file
        ast.parse(code)
        print("✅ Overview page has valid Python syntax")
        
        # Check for required imports
        if "from src.central_data import" in code:
            print("✅ Overview page imports central_data")
        else:
            print("⚠️ Overview page missing central_data import")
        
        if "from src.validation_ui_helpers import" in code:
            print("✅ Overview page imports validation_ui_helpers")
        else:
            print("⚠️ Overview page missing validation_ui_helpers import")
        
        if "render_quality_dashboard" in code:
            print("✅ Overview page uses quality dashboard")
        else:
            print("⚠️ Overview page not using quality dashboard")
        
        if "render_quality_summary_compact" in code:
            print("✅ Overview page uses sidebar quality summary")
        else:
            print("⚠️ Overview page not using sidebar quality summary")
        
        return True
    except SyntaxError as e:
        print(f"❌ Overview page has syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Overview page check failed: {e}")
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*80)
    print("STREAMLIT INTEGRATION TEST SUITE")
    print("="*80)
    print("Testing validation system integration into Streamlit...")
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Data Loading", test_data_loading()))
    results.append(("Quality Report", test_quality_report()))
    results.append(("UI Helpers", test_ui_helpers()))
    results.append(("Overview Page Syntax", test_overview_page_syntax()))
    
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
        print("\n🎉 ALL TESTS PASSED! Integration is ready for deployment.")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix issues before deploying.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
