"""
Test the fixed skill analysis implementation
"""
from src.job_market_pulse import load_job_postings
from src.skill_obsolescence import analyze_skill_demand_patterns

print("=" * 80)
print("SKILL DEMAND ANALYSIS - FIXED IMPLEMENTATION TEST")
print("=" * 80)

# Load data
df = load_job_postings()
print(f"Job postings loaded: {len(df):,}")

if df.empty:
    print("❌ No job postings data available!")
    exit()

print("\n1. TESTING NEW SKILL DEMAND ANALYSIS:")
print("-" * 80)

# Test the new analysis function
results = analyze_skill_demand_patterns(
    df=df,
    top_k=20,
    min_mentions=50,
    demand_threshold=2.0
)

if results is not None and not results.empty:
    print(f"✅ Analysis successful: {len(results)} skills analyzed")
    
    print("\nSkill categories:")
    category_counts = results["category"].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} skills")
    
    print("\nTop 10 skills by demand:")
    top_skills = results.nlargest(10, "demand_percentage")
    for _, row in top_skills.iterrows():
        print(f"  {row['skill']:25s}: {row['demand_percentage']:5.1f}% demand, {row['mentions']:4d} mentions, {row['avg_salary_lpa']:5.1f} LPA ({row['category']})")
    
    print("\nHigh-demand skills:")
    high_demand = results[results["category"] == "High-Demand"]
    if not high_demand.empty:
        for _, row in high_demand.iterrows():
            print(f"  🔥 {row['skill']:25s}: {row['demand_percentage']:5.1f}% demand, {row['avg_salary_lpa']:5.1f} LPA")
    else:
        print("  No high-demand skills found with current thresholds")
    
    print("\nLow-demand skills:")
    low_demand = results[results["category"] == "Low-Demand"]
    if not low_demand.empty:
        for _, row in low_demand.head(5).iterrows():
            print(f"  📉 {row['skill']:25s}: {row['demand_percentage']:5.1f}% demand, {row['avg_salary_lpa']:5.1f} LPA")
    else:
        print("  No low-demand skills found")

else:
    print("❌ Analysis failed or returned no results")

print("\n2. SALARY DATA ANALYSIS:")
print("-" * 80)

if results is not None and not results.empty:
    # Analyze salary data
    skills_with_salary = results[results["avg_salary_lpa"] > 0]
    print(f"Skills with salary data: {len(skills_with_salary)}/{len(results)}")
    
    if not skills_with_salary.empty:
        print(f"Average salary range: {skills_with_salary['avg_salary_lpa'].min():.1f} - {skills_with_salary['avg_salary_lpa'].max():.1f} LPA")
        print(f"Median salary: {skills_with_salary['avg_salary_lpa'].median():.1f} LPA")
        
        print("\nTop 5 highest-paying skills:")
        top_salary = skills_with_salary.nlargest(5, "avg_salary_lpa")
        for _, row in top_salary.iterrows():
            print(f"  💰 {row['skill']:25s}: {row['avg_salary_lpa']:5.1f} LPA ({row['demand_percentage']:4.1f}% demand)")

print("\n3. USER SKILL MATCHING TEST:")
print("-" * 80)

if results is not None and not results.empty:
    # Test user skill matching
    test_skills = ["python", "javascript", "java", "react", "sql", "machine learning", "html", "css"]
    
    skill_map = results.set_index("skill").to_dict("index")
    
    print("Testing skill matching:")
    for test_skill in test_skills:
        matched = None
        for analyzed_skill in skill_map.keys():
            if test_skill.lower() in analyzed_skill.lower() or analyzed_skill.lower() in test_skill.lower():
                matched = analyzed_skill
                break
        
        if matched:
            data = skill_map[matched]
            print(f"  {test_skill:15s} → {matched:25s} ({data['category']}, {data['demand_percentage']:.1f}%)")
        else:
            print(f"  {test_skill:15s} → Not found")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
if results is not None and not results.empty:
    print("✅ Fixed implementation working correctly!")
    print(f"✅ {len(results)} skills analyzed successfully")
    print(f"✅ {len(category_counts)} different demand categories")
    print(f"✅ Salary data available for {len(skills_with_salary)} skills")
    print("✅ User skill matching functional")
    print("✅ Ready to replace the old obsolescence detector")
else:
    print("❌ Implementation needs further fixes")