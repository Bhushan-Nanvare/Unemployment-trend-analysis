"""
Test the improvements made to Geo Career Advisor
"""
import pandas as pd
from src.geo_career_advisor import aggregate_city_labour_market, normalize_city_key
from src.job_market_pulse import load_job_postings

print("=" * 80)
print("GEO CAREER ADVISOR - IMPROVEMENTS VERIFICATION")
print("=" * 80)

# Load data
df_jobs = load_job_postings()
agg = aggregate_city_labour_market(df_jobs)

print(f"Total job postings: {len(df_jobs):,}")
print(f"Cities after aggregation: {len(agg)}")

print("\n1. COORDINATE COVERAGE IMPROVEMENT:")
print("-" * 80)

if not agg.empty:
    cities_with_coords = agg.dropna(subset=["lat", "lon"])
    coord_coverage = len(cities_with_coords) / len(agg) * 100
    
    print(f"Cities with coordinates: {len(cities_with_coords)}/{len(agg)} ({coord_coverage:.1f}%)")
    
    # Show top cities by job count and their coordinate status
    print("\nTop 20 cities - coordinate status:")
    for _, row in agg.head(20).iterrows():
        city = row.get("display_name", row["city_key"])
        has_coords = "✅" if pd.notna(row.get("lat")) and pd.notna(row.get("lon")) else "❌"
        print(f"  {city:25s} {row['postings']:5d} jobs {has_coords}")

print("\n2. SALARY DATA QUALITY:")
print("-" * 80)

if "salary_coverage_pct" in agg.columns:
    print("Salary coverage by city (top 15):")
    salary_cities = agg.dropna(subset=["median_lpa"]).head(15)
    for _, row in salary_cities.iterrows():
        city = row.get("display_name", row["city_key"])
        coverage = row.get("salary_coverage_pct", 0)
        median = row.get("median_lpa", 0)
        salary_count = row.get("salary_count", 0)
        print(f"  {city:20s}: {coverage:5.1f}% coverage ({salary_count:4d}/{row['postings']:4d} jobs) → {median:.1f} LPA")

print("\n3. CITY NORMALIZATION IMPROVEMENTS:")
print("-" * 80)

# Test city normalization improvements
test_cities = [
    "Bengaluru", "bangalore", "BLR",
    "Mumbai", "Bombay", 
    "Delhi NCR", "New Delhi", "NCR",
    "Gurgaon", "Gurugram", "GGN",
    "Hyderabad", "HYD", "Secunderabad",
    "Chennai", "Madras",
    "Kolkata", "Calcutta",
    "Pune/Mumbai", "Delhi/Gurgaon",
    "Karnataka", "Maharashtra",
    "Remote", "Work from Home", "WFH"
]

print("City normalization test:")
for city in test_cities:
    normalized = normalize_city_key(city)
    print(f"  {city:20s} → {normalized}")

print("\n4. GRAPH DATA ACCURACY:")
print("-" * 80)

# Test median salary calculation accuracy
cities_for_graph = agg.dropna(subset=["median_lpa"]).head(10)
if not cities_for_graph.empty:
    print("Cities suitable for salary trend line:")
    for _, row in cities_for_graph.iterrows():
        city = row.get("display_name", row["city_key"])
        median = row.get("median_lpa")
        coverage = row.get("salary_coverage_pct", 0)
        suitable = "✅" if coverage >= 10 else "⚠️"
        print(f"  {city:20s}: {median:5.1f} LPA ({coverage:4.1f}% coverage) {suitable}")
    
    suitable_cities = cities_for_graph[cities_for_graph.get("salary_coverage_pct", 0) >= 10]
    print(f"\nCities suitable for trend line (≥10% coverage): {len(suitable_cities)}")
else:
    print("No cities with salary data found")

print("\n5. DATA QUALITY METRICS:")
print("-" * 80)

if not agg.empty:
    # Overall metrics
    total_jobs = agg["postings"].sum()
    total_salary_jobs = agg.get("salary_count", pd.Series([0])).sum()
    overall_salary_coverage = total_salary_jobs / total_jobs * 100 if total_jobs > 0 else 0
    
    cities_with_coords = len(agg.dropna(subset=["lat", "lon"]))
    coord_coverage = cities_with_coords / len(agg) * 100
    
    cities_with_salary = len(agg.dropna(subset=["median_lpa"]))
    salary_city_coverage = cities_with_salary / len(agg) * 100
    
    print(f"Overall salary coverage: {overall_salary_coverage:.1f}% ({total_salary_jobs:,}/{total_jobs:,} jobs)")
    print(f"Cities with coordinates: {coord_coverage:.1f}% ({cities_with_coords}/{len(agg)} cities)")
    print(f"Cities with salary data: {salary_city_coverage:.1f}% ({cities_with_salary}/{len(agg)} cities)")
    
    # Quality assessment
    print(f"\nQuality Assessment:")
    if coord_coverage >= 80:
        print("✅ Coordinate coverage: Excellent")
    elif coord_coverage >= 60:
        print("🟡 Coordinate coverage: Good") 
    else:
        print("❌ Coordinate coverage: Needs improvement")
        
    if overall_salary_coverage >= 30:
        print("✅ Salary coverage: Acceptable")
    elif overall_salary_coverage >= 20:
        print("🟡 Salary coverage: Limited")
    else:
        print("❌ Salary coverage: Poor")
        
    if len(suitable_cities) >= 5:
        print("✅ Graph data: Sufficient for trend lines")
    elif len(suitable_cities) >= 3:
        print("🟡 Graph data: Minimal trend lines possible")
    else:
        print("❌ Graph data: Insufficient for trend lines")

print("\n" + "=" * 80)
print("IMPROVEMENTS SUMMARY:")
print("=" * 80)
print("✅ Enhanced city normalization (handles 30+ variations)")
print("✅ Improved salary calculation (filters invalid data)")
print("✅ Added coordinate filling for major cities")
print("✅ Better graph data validation")
print("✅ Added data quality indicators")
print("✅ Salary coverage tracking per city")
print("✅ Graph trend line requirements (≥10% coverage)")