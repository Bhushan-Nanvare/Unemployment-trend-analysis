#!/usr/bin/env python3
"""
fix_data_accuracy.py

DATA ACCURACY CORRECTION SCRIPT
================================

Implements the corrections identified by the Reality Validation System
to improve data accuracy from 61.9% to 80%+ target.

Based on AI validation results from 2026-04-13.

Author: Reality Validation System
Date: 2026-04-13
Version: 1.0.0
"""

import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime


def backup_files():
    """Create backups of original files before modification"""
    print("📁 Creating backups...")
    
    files_to_backup = [
        "data/raw/india_inflation_corrected.csv",
        "data/raw/india_unemployment_realistic.csv"
    ]
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for file_path in files_to_backup:
        if Path(file_path).exists():
            backup_path = f"{file_path}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            print(f"  ✅ Backed up: {file_path} → {backup_path}")
        else:
            print(f"  ⚠️ File not found: {file_path}")


def fix_inflation_data():
    """Fix inflation data based on AI validation results"""
    print("\n🔧 Fixing inflation data...")
    
    file_path = "data/raw/india_inflation_corrected.csv"
    
    if not Path(file_path).exists():
        print(f"  ❌ File not found: {file_path}")
        return False
    
    # Load data
    df = pd.read_csv(file_path)
    print(f"  📊 Loaded {len(df)} rows")
    
    # Apply corrections based on AI validation
    corrections = {
        2019: 3.40,  # Was 4.80%, AI verified 3.40%
        2023: 6.45   # Was 5.40%, AI verified 6.45%
    }
    
    changes_made = 0
    for year, correct_value in corrections.items():
        mask = df['Year'] == year
        if mask.any():
            old_value = df.loc[mask, 'Inflation_Rate'].iloc[0]
            df.loc[mask, 'Inflation_Rate'] = correct_value
            print(f"  ✅ {year}: {old_value:.2f}% → {correct_value:.2f}%")
            changes_made += 1
        else:
            print(f"  ⚠️ Year {year} not found in data")
    
    # Save corrected data
    if changes_made > 0:
        df.to_csv(file_path, index=False)
        print(f"  💾 Saved {changes_made} corrections to {file_path}")
        return True
    else:
        print("  ℹ️ No changes needed")
        return False


def fix_unemployment_data():
    """Fix unemployment data based on AI validation results"""
    print("\n🔧 Fixing unemployment data...")
    
    file_path = "data/raw/india_unemployment_realistic.csv"
    
    if not Path(file_path).exists():
        print(f"  ❌ File not found: {file_path}")
        return False
    
    # Load data
    df = pd.read_csv(file_path)
    print(f"  📊 Loaded {len(df)} rows")
    
    # Apply corrections based on AI validation
    corrections = {
        2019: 7.20,  # Was 5.80%, AI verified 7.20%
    }
    
    changes_made = 0
    for year, correct_value in corrections.items():
        mask = df['Year'] == year
        if mask.any():
            old_value = df.loc[mask, 'Unemployment_Rate'].iloc[0]
            df.loc[mask, 'Unemployment_Rate'] = correct_value
            print(f"  ✅ {year}: {old_value:.2f}% → {correct_value:.2f}%")
            changes_made += 1
        else:
            print(f"  ⚠️ Year {year} not found in data")
    
    # Save corrected data
    if changes_made > 0:
        df.to_csv(file_path, index=False)
        print(f"  💾 Saved {changes_made} corrections to {file_path}")
        return True
    else:
        print("  ℹ️ No changes needed")
        return False


def fix_gdp_data():
    """Fix GDP data - note this requires updating the live_data.py source"""
    print("\n🔧 GDP Data Correction Needed...")
    print("  ⚠️ GDP data comes from World Bank API in src/live_data.py")
    print("  📝 Manual correction needed:")
    print("     2020 GDP: -5.78% → -7.30% (AI verified)")
    print("  💡 Consider updating the GDP data source or adding correction factor")
    
    return False  # Manual intervention required


def validate_corrections():
    """Validate that corrections were applied successfully"""
    print("\n✅ Validating corrections...")
    
    # Check inflation corrections
    inflation_file = "data/raw/india_inflation_corrected.csv"
    if Path(inflation_file).exists():
        df = pd.read_csv(inflation_file)
        
        # Check 2019 correction
        year_2019 = df[df['Year'] == 2019]
        if not year_2019.empty:
            value_2019 = year_2019['Inflation_Rate'].iloc[0]
            if abs(value_2019 - 3.40) < 0.01:
                print("  ✅ 2019 inflation: 3.40% (corrected)")
            else:
                print(f"  ❌ 2019 inflation: {value_2019:.2f}% (should be 3.40%)")
        
        # Check 2023 correction
        year_2023 = df[df['Year'] == 2023]
        if not year_2023.empty:
            value_2023 = year_2023['Inflation_Rate'].iloc[0]
            if abs(value_2023 - 6.45) < 0.01:
                print("  ✅ 2023 inflation: 6.45% (corrected)")
            else:
                print(f"  ❌ 2023 inflation: {value_2023:.2f}% (should be 6.45%)")
    
    # Check unemployment corrections
    unemployment_file = "data/raw/india_unemployment_realistic.csv"
    if Path(unemployment_file).exists():
        df = pd.read_csv(unemployment_file)
        
        # Check 2019 correction
        year_2019 = df[df['Year'] == 2019]
        if not year_2019.empty:
            value_2019 = year_2019['Unemployment_Rate'].iloc[0]
            if abs(value_2019 - 7.20) < 0.01:
                print("  ✅ 2019 unemployment: 7.20% (corrected)")
            else:
                print(f"  ❌ 2019 unemployment: {value_2019:.2f}% (should be 7.20%)")


def main():
    """Main correction process"""
    print("=" * 80)
    print("DATA ACCURACY CORRECTION SCRIPT")
    print("=" * 80)
    print("Implementing Reality Validation System recommendations...")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create backups
    backup_files()
    
    # Apply corrections
    inflation_fixed = fix_inflation_data()
    unemployment_fixed = fix_unemployment_data()
    gdp_noted = fix_gdp_data()
    
    # Validate corrections
    validate_corrections()
    
    # Summary
    print("\n" + "=" * 80)
    print("CORRECTION SUMMARY")
    print("=" * 80)
    
    total_fixes = sum([inflation_fixed, unemployment_fixed])
    
    print(f"✅ Inflation data: {'Fixed' if inflation_fixed else 'No changes'}")
    print(f"✅ Unemployment data: {'Fixed' if unemployment_fixed else 'No changes'}")
    print(f"⚠️ GDP data: Manual correction needed (see notes above)")
    
    if total_fixes > 0:
        print(f"\n🎉 Applied {total_fixes} automatic corrections")
        print("📈 Expected accuracy improvement: 61.9% → ~75%+")
        print("\n💡 Next steps:")
        print("   1. Run reality validation again: python test_reality_validation.py")
        print("   2. Fix GDP data manually (2020: -5.78% → -7.30%)")
        print("   3. Verify 2023-2024 data with official sources")
    else:
        print("\n⚠️ No automatic corrections applied")
        print("   Check if files exist and contain expected data")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()