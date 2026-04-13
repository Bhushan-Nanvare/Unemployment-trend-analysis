"""
test_reality_validation.py

COMPREHENSIVE REALITY VALIDATION TEST
======================================

Tests model predictions and stored data against real-world facts using AI.

Validates:
1. Historical inflation rates (2019-2024)
2. Historical GDP growth rates (2019-2024)
3. Historical unemployment rates (2019-2024)
4. COVID-19 impact (2020)
5. Model predictions accuracy

Requires: GROQ_API_KEY or GEMINI_API_KEY in .env
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.validation.reality_checker import RealityChecker, format_reality_check_report
from src.central_data import load_unemployment, load_inflation
from src.live_data import fetch_gdp_growth
import pandas as pd


def test_inflation_rates():
    """Test inflation rates against AI verification"""
    print("\n" + "="*80)
    print("TEST 1: Inflation Rates Validation")
    print("="*80)
    
    checker = RealityChecker()
    
    # Load inflation data
    inflation_df = load_inflation()
    
    # Test recent years (2019-2024)
    test_years = [2019, 2020, 2021, 2022, 2023, 2024]
    results = []
    
    for year in test_years:
        year_data = inflation_df[inflation_df['Year'] == year]
        
        if not year_data.empty:
            model_value = float(year_data['Inflation_Rate'].iloc[0])
            
            print(f"\nChecking {year}...")
            print(f"Model Value: {model_value:.2f}%")
            
            result = checker.check_inflation_rate(year, model_value)
            results.append(result)
            
            if result.ai_verified_value is not None:
                print(f"AI Verified: {result.ai_verified_value:.2f}%")
                print(f"Deviation: {result.deviation:.2f}pp")
                print(f"Status: {'✅ ACCURATE' if result.is_accurate else '❌ INACCURATE'}")
            else:
                print("⚠️ AI verification not available")
            
            # Add delay to avoid rate limits
            time.sleep(2)
    
    return results


def test_gdp_growth_rates():
    """Test GDP growth rates against AI verification"""
    print("\n" + "="*80)
    print("TEST 2: GDP Growth Rates Validation")
    print("="*80)
    
    checker = RealityChecker()
    
    # Load GDP data
    gdp_df = fetch_gdp_growth("India")
    
    # Test recent years
    test_years = [2019, 2020, 2021, 2022, 2023]
    results = []
    
    for year in test_years:
        year_data = gdp_df[gdp_df['Year'] == year]
        
        if not year_data.empty:
            model_value = float(year_data['Value'].iloc[0])
            
            print(f"\nChecking {year}...")
            print(f"Model Value: {model_value:.2f}%")
            
            result = checker.check_gdp_growth(year, model_value)
            results.append(result)
            
            if result.ai_verified_value is not None:
                print(f"AI Verified: {result.ai_verified_value:.2f}%")
                print(f"Deviation: {result.deviation:.2f}pp")
                print(f"Status: {'✅ ACCURATE' if result.is_accurate else '❌ INACCURATE'}")
            else:
                print("⚠️ AI verification not available")
            
            # Add delay to avoid rate limits
            time.sleep(2)
    
    return results


def test_unemployment_rates():
    """Test unemployment rates against AI verification"""
    print("\n" + "="*80)
    print("TEST 3: Unemployment Rates Validation")
    print("="*80)
    
    checker = RealityChecker()
    
    # Load unemployment data
    unemployment_df = load_unemployment()
    
    # Test recent years
    test_years = [2019, 2020, 2021, 2022, 2023, 2024]
    results = []
    
    for year in test_years:
        year_data = unemployment_df[unemployment_df['Year'] == year]
        
        if not year_data.empty:
            model_value = float(year_data['Unemployment_Rate'].iloc[0])
            
            print(f"\nChecking {year}...")
            print(f"Model Value: {model_value:.2f}%")
            
            result = checker.check_unemployment_rate(year, model_value)
            results.append(result)
            
            if result.ai_verified_value is not None:
                print(f"AI Verified: {result.ai_verified_value:.2f}%")
                print(f"Deviation: {result.deviation:.2f}pp")
                print(f"Status: {'✅ ACCURATE' if result.is_accurate else '❌ INACCURATE'}")
            else:
                print("⚠️ AI verification not available")
            
            # Add delay to avoid rate limits
            time.sleep(2)
    
    return results


def test_covid_impact():
    """Test COVID-19 impact validation"""
    print("\n" + "="*80)
    print("TEST 4: COVID-19 Impact Validation")
    print("="*80)
    
    checker = RealityChecker()
    
    # Load data for 2020
    unemployment_df = load_unemployment()
    year_2020 = unemployment_df[unemployment_df['Year'] == 2020]
    
    if not year_2020.empty:
        unemployment_2020 = float(year_2020['Unemployment_Rate'].iloc[0])
        
        print(f"\n2020 Unemployment Rate: {unemployment_2020:.2f}%")
        
        # Check if this reflects COVID impact
        result = checker.check_economic_event(
            2020,
            f"COVID-19 pandemic caused unemployment spike to around {unemployment_2020:.1f}%"
        )
        
        print(f"\nAI Verification:")
        print(result.ai_response[:300])
        
        return [result]
    
    return []


def test_specific_values():
    """Test specific known values"""
    print("\n" + "="*80)
    print("TEST 5: Specific Known Values")
    print("="*80)
    
    checker = RealityChecker()
    results = []
    
    # Test cases with known values
    test_cases = [
        {
            "metric": "inflation",
            "year": 2020,
            "model_value": 6.2,
            "description": "India inflation during COVID"
        },
        {
            "metric": "gdp",
            "year": 2020,
            "model_value": -7.3,
            "description": "India GDP contraction during COVID"
        },
        {
            "metric": "unemployment",
            "year": 2020,
            "model_value": 7.1,
            "description": "India unemployment during COVID (annual average)"
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['description']}")
        print(f"Model Value: {test['model_value']}%")
        
        if test['metric'] == 'inflation':
            result = checker.check_inflation_rate(test['year'], test['model_value'])
        elif test['metric'] == 'gdp':
            result = checker.check_gdp_growth(test['year'], test['model_value'])
        else:
            result = checker.check_unemployment_rate(test['year'], test['model_value'])
        
        results.append(result)
        
        if result.ai_verified_value is not None:
            print(f"AI Verified: {result.ai_verified_value}%")
            print(f"Deviation: {result.deviation:.2f}pp")
            print(f"Status: {'✅ ACCURATE' if result.is_accurate else '❌ INACCURATE'}")
        else:
            print("⚠️ AI verification not available")
        
        # Add delay to avoid rate limits
        time.sleep(2)
    
    return results


def run_all_tests():
    """Run all reality validation tests"""
    print("\n" + "="*80)
    print("REALITY VALIDATION TEST SUITE")
    print("="*80)
    print("Validating model data against real-world facts using AI...")
    
    # Check if AI is available
    checker = RealityChecker()
    if not checker.groq_api_key and not checker.gemini_api_key:
        print("\n⚠️ WARNING: No AI API keys found!")
        print("Set GROQ_API_KEY or GEMINI_API_KEY in .env file to enable validation")
        print("\nTo get API keys:")
        print("- Groq (free): https://console.groq.com")
        print("- Gemini (free): https://aistudio.google.com/app/apikey")
        return False
    
    print("\n✅ AI API available for validation\n")
    
    all_results = []
    
    # Run tests
    print("\nRunning validation tests...")
    
    try:
        results = test_inflation_rates()
        all_results.extend(results)
    except Exception as e:
        print(f"❌ Inflation test failed: {e}")
    
    try:
        results = test_gdp_growth_rates()
        all_results.extend(results)
    except Exception as e:
        print(f"❌ GDP test failed: {e}")
    
    try:
        results = test_unemployment_rates()
        all_results.extend(results)
    except Exception as e:
        print(f"❌ Unemployment test failed: {e}")
    
    try:
        results = test_covid_impact()
        all_results.extend(results)
    except Exception as e:
        print(f"❌ COVID test failed: {e}")
    
    try:
        results = test_specific_values()
        all_results.extend(results)
    except Exception as e:
        print(f"❌ Specific values test failed: {e}")
    
    # Generate report
    if all_results:
        report = format_reality_check_report(all_results)
        print(report)
        
        # Save report
        try:
            with open("reality_validation_report.txt", "w", encoding='utf-8') as f:
                f.write(report)
            print("📄 Report saved to: reality_validation_report.txt")
        except UnicodeEncodeError:
            # Fallback: save with ASCII encoding, replacing problematic characters
            with open("reality_validation_report.txt", "w", encoding='ascii', errors='replace') as f:
                f.write(report)
            print("📄 Report saved to: reality_validation_report.txt (ASCII encoding)")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
            print("Report content printed above instead.")
        
        # Summary
        accurate_count = sum(1 for r in all_results if r.is_accurate)
        total_count = len(all_results)
        accuracy_pct = (accurate_count / total_count * 100) if total_count > 0 else 0
        
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        print(f"Total Checks: {total_count}")
        print(f"Accurate: {accurate_count}")
        print(f"Inaccurate: {total_count - accurate_count}")
        print(f"Accuracy Rate: {accuracy_pct:.1f}%")
        print("="*80)
        
        return accuracy_pct >= 80.0  # Pass if 80%+ accurate
    else:
        print("\n⚠️ No results to report")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
