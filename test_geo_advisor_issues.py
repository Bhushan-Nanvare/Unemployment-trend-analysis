"""
Test to identify issues with Geo Career Advisor graphs and data accuracy
"""
import pandas as pd
import numpy as np
from src.geo_career_advisor import (
    aggregate_city_labour_market, 
    postings_with_city_key,
    load_city_reference
)
from src.job_market_pulse import load_job_postings

print("=" * 80)
print("GEO CAREER ADVISOR - ISSUE IDENTIFICATION")
print("=" * 80)

# Load data
df_jobs = load_job_postings()
print(f"Total job postings loaded: {len(df_jobs)}")

if df_jobs.empty:
    print("❌ No job postings data available!")
    exit()

# Check salary data quality
print("\n1. SALARY DATA QUALITY CHECK:")
print("-" * 80)

salary_cols = ["salary_min_lpa", "salary_max_lpa"]
for col in salary_cols:
    if col in df_jobs.columns:
        valid_salaries = pd.to_numeric(df_jobs[col], errors="coerce").dropna()
        print(f"{col}:")
        print(f"  Total rows: {len(df_jobs)}")
        print(f"  Valid salaries: {len(valid_salaries)} ({100*len(valid_salaries)/len(df_jobs):.1f}%)")
        print(f"  Range: {valid_salaries.min():.1f} - {valid_salaries.max():.1f} LPA")
        print(f"  Median: {valid_salaries.median():.1f} LPA")
        print(f"  Mean: {valid_salaries.mean():.1f} LPA")
    else:
        print(f"❌ Column '{col}' not found!")

# Check location data
print("\n2. LOCATION DATA ANALYSIS:")
print("-" * 80)

if "location" in df_jobs.columns:
    locations = df_jobs["location"].value_counts()
    print(f"Unique locations: {len(locations)}")
    print(f"Top 10 locations:")
    for loc, count in locations.head(10).items():
        print(f"  {loc}: {count} jobs ({100*count/len(df_jobs):.1f}%)")
else:
    print("❌ Location column not found!")

# Test city aggregation
print("\n3. CITY AGGREGATION TEST:")
print("-" * 80)

agg = aggregate_city_labour_market(df_jobs)
print(f"Cities after aggregation: {len(agg)}")

if not agg.empty:
    print("\nTop 10 cities by job postings:")
    for _, row in agg.head(10).iterrows():
        city = row.get("display_name", row["city_key"])
        postings = row["postings"]
        median_lpa = row.get("median_lpa", "N/A")
        if pd.notna(median_lpa):
            median_str = f"{median_lpa:.1f} LPA"
        else:
            median_str = "No salary data"
        print(f"  {city}: {postings} jobs, Median: {median_str}")

# Check city reference data
print("\n4. CITY REFERENCE DATA:")
print("-" * 80)

ref = load_city_reference()
if not ref.empty:
    print(f"Cities in reference: {len(ref)}")
    print(f"Columns: {list(ref.columns)}")
    
    # Check coordinate data
    if "lat" in ref.columns and "lon" in ref.columns:
        valid_coords = ref.dropna(subset=["lat", "lon"])
        print(f"Cities with coordinates: {len(valid_coords)} ({100*len(valid_coords)/len(ref):.1f}%)")
    
    # Check salary data in aggregation vs reference
    agg_with_coords = agg.dropna(subset=["lat", "lon"])
    print(f"Aggregated cities with coordinates: {len(agg_with_coords)}")
else:
    print("❌ City reference data not found!")

# Test specific issues
print("\n5. POTENTIAL ISSUES IDENTIFIED:")
print("-" * 80)

issues = []

# Issue 1: Missing salary data
salary_coverage = 0
if "salary_min_lpa" in df_jobs.columns and "salary_max_lpa" in df_jobs.columns:
    smin = pd.to_numeric(df_jobs["salary_min_lpa"], errors="coerce")
    smax = pd.to_numeric(df_jobs["salary_max_lpa"], errors="coerce")
    valid_salary_rows = (~smin.isna()) & (~smax.isna())
    salary_coverage = valid_salary_rows.sum() / len(df_jobs) * 100

if salary_coverage < 50:
    issues.append(f"Low salary data coverage: {salary_coverage:.1f}% (should be >80%)")

# Issue 2: Coordinate coverage
coord_coverage = 0
if not agg.empty and "lat" in agg.columns and "lon" in agg.columns:
    valid_coords = agg.dropna(subset=["lat", "lon"])
    coord_coverage = len(valid_coords) / len(agg) * 100

if coord_coverage < 80:
    issues.append(f"Low coordinate coverage: {coord_coverage:.1f}% (should be >90%)")

# Issue 3: Median salary calculation accuracy
if not agg.empty and "median_lpa" in agg.columns:
    cities_with_salary = agg.dropna(subset=["median_lpa"])
    if len(cities_with_salary) < len(agg) * 0.5:
        issues.append(f"Many cities missing median salary: {len(cities_with_salary)}/{len(agg)} cities have salary data")

# Issue 4: City key normalization
dkey = postings_with_city_key(df_jobs)
if not dkey.empty:
    original_cities = df_jobs["location"].nunique()
    normalized_cities = dkey["city_key"].nunique()
    if normalized_cities < original_cities * 0.8:
        issues.append(f"City normalization may be too aggressive: {original_cities} → {normalized_cities} cities")

# Issue 5: Graph data points accuracy
print("\nTesting graph data accuracy:")
if not agg.empty:
    # Check if median salary calculation is correct
    test_city = agg.iloc[0]["city_key"]
    city_jobs = dkey[dkey["city_key"] == test_city]
    
    if not city_jobs.empty and "salary_min_lpa" in city_jobs.columns:
        smin = pd.to_numeric(city_jobs["salary_min_lpa"], errors="coerce")
        smax = pd.to_numeric(city_jobs["salary_max_lpa"], errors="coerce")
        manual_median = ((smin + smax) / 2.0).median()
        agg_median = agg.iloc[0]["median_lpa"]
        
        print(f"Test city: {test_city}")
        print(f"Manual median calculation: {manual_median:.2f}")
        print(f"Aggregation median: {agg_median:.2f}")
        
        if abs(manual_median - agg_median) > 0.1:
            issues.append(f"Median salary calculation mismatch for {test_city}: {manual_median:.2f} vs {agg_median:.2f}")

if issues:
    print("\n❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
else:
    print("\n✅ No major issues detected in data processing")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print("1. Check salary data quality in source CSV")
print("2. Verify city reference coordinates are accurate") 
print("3. Test median salary calculations manually")
print("4. Ensure graph data points match aggregated data")
print("5. Validate location normalization logic")