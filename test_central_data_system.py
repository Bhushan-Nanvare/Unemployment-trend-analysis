"""
test_central_data_system.py

Test script for the new central data system and validation engine.

This script verifies:
1. Central data loader works correctly
2. Validation engine detects issues
3. Data quality reports are generated
4. All data sources are accessible
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from central_data import (
    load_unemployment,
    load_inflation,
    get_data_quality_report,
    print_data_quality_report
)

from validation_engine import (
    validate_time_series,
    print_validation_report,
    UNEMPLOYMENT_CONFIG,
    INFLATION_CONFIG
)


def test_central_data_system():
    """Test the central data system."""
    print("\n" + "="*80)
    print("TESTING CENTRAL DATA SYSTEM")
    print("="*80 + "\n")
    
    # Test 1: Load unemployment data
    print("TEST 1: Loading Unemployment Data")
    print("-" * 80)
    unemployment_df = load_unemployment()
    print(f"✅ Loaded {len(unemployment_df)} rows of unemployment data")
    print(f"   Year range: {unemployment_df['Year'].min()} - {unemployment_df['Year'].max()}")
    print(f"   Value range: {unemployment_df['Unemployment_Rate'].min():.2f}% - {unemployment_df['Unemployment_Rate'].max():.2f}%")
    print()
    
    # Test 2: Load inflation data
    print("TEST 2: Loading Inflation Data")
    print("-" * 80)
    inflation_df = load_inflation()
    print(f"✅ Loaded {len(inflation_df)} rows of inflation data")
    if not inflation_df.empty:
        print(f"   Year range: {inflation_df['Year'].min()} - {inflation_df['Year'].max()}")
        print(f"   Value range: {inflation_df['Inflation_Rate'].min():.2f}% - {inflation_df['Inflation_Rate'].max():.2f}%")
    print()
    
    # Test 3: Data quality report
    print("TEST 3: Data Quality Report")
    print("-" * 80)
    print_data_quality_report()
    
    # Test 4: Detailed validation
    print("TEST 4: Detailed Validation - Unemployment")
    print("-" * 80)
    unemployment_corrected, unemployment_report = validate_time_series(
        unemployment_df,
        "Unemployment_Rate",
        "Year",
        UNEMPLOYMENT_CONFIG,
        auto_correct=True
    )
    print_validation_report(unemployment_report, "Unemployment Data")
    
    # Test 5: Detailed validation - Inflation
    if not inflation_df.empty:
        print("TEST 5: Detailed Validation - Inflation")
        print("-" * 80)
        inflation_corrected, inflation_report = validate_time_series(
            inflation_df,
            "Inflation_Rate",
            "Year",
            INFLATION_CONFIG,
            auto_correct=True
        )
        print_validation_report(inflation_report, "Inflation Data")
    
    # Test 6: Summary
    print("TEST 6: System Health Summary")
    print("-" * 80)
    report = get_data_quality_report()
    
    print(f"System Health: {report['overall_system_health']}")
    print(f"Unemployment Quality: {report['unemployment']['data_quality_score']:.1f}/100")
    print(f"Inflation Quality: {report['inflation']['data_quality_score']:.1f}/100")
    print()
    
    if report['overall_system_health'] == "HEALTHY":
        print("✅ ALL TESTS PASSED - System is healthy")
    elif report['overall_system_health'] == "DEGRADED":
        print("⚠️  TESTS PASSED WITH WARNINGS - System is degraded but functional")
    else:
        print("❌ TESTS FAILED - System has critical issues")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_central_data_system()
