"""
Test to identify issues with Skill Obsolescence Detector
"""
import pandas as pd
from src.job_market_pulse import load_job_postings
from src.skill_obsolescence import detect_skill_obsolescence

print("=" * 80)
print("SKILL OBSOLESCENCE DETECTOR - ISSUE IDENTIFICATION")
print("=" * 80)

# Load data
df = load_job_postings()
print(f"Job postings loaded: {len(df):,}")

if df.empty:
    print("❌ No job postings data available!")
    exit()

print("\n1. DATA AVAILABILITY CHECK:")
print("-" * 80)

# Check required columns
required_cols = ["post_date", "_text", "description"]
for col in required_cols:
    if col in df.columns:
        if col == "post_date":
            valid_dates = df[col].dropna()
            print(f"✅ {col}: {len(valid_dates):,} valid dates ({100*len(valid_dates)/len(df):.1f}%)")
            if len(valid_dates) > 0:
                print(f"   Date range: {valid_dates.min()} to {valid_dates.max()}")
                date_span = (valid_dates.max() - valid_dates.min()).days
                print(f"   Span: {date_span} days ({date_span/30:.1f} months)")
        else:
            valid_text = df[col].dropna()
            print(f"✅ {col}: {len(valid_text):,} valid entries ({100*len(valid_text)/len(df):.1f}%)")
    else:
        print(f"❌ {col}: Missing!")

print("\n2. SKILL DETECTION TEST:")
print("-" * 80)

# Test skill detection
from src.job_market_pulse import skill_phrase_list, phrase_in_blob

skills = skill_phrase_list()
print(f"Available skill phrases: {len(skills)}")
print(f"Sample skills: {skills[:10]}")

# Test skill detection in sample jobs
sample_jobs = df.head(100)
skill_matches = {}
for _, row in sample_jobs.iterrows():
    text = row.get("_text", "")
    for skill in skills[:20]:  # Test first 20 skills
        if phrase_in_blob(skill, text):
            skill_matches[skill] = skill_matches.get(skill, 0) + 1

print(f"\nSkill matches in first 100 jobs:")
for skill, count in sorted(skill_matches.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {skill}: {count} matches")

print("\n3. TIME SERIES ANALYSIS:")
print("-" * 80)

# Check if we can do time series analysis
if "post_date" in df.columns:
    df_dated = df.dropna(subset=["post_date"])
    if len(df_dated) > 0:
        # Group by month
        df_dated["month"] = df_dated["post_date"].dt.to_period("M")
        monthly_counts = df_dated.groupby("month").size()
        print(f"Monthly job posting distribution:")
        for month, count in monthly_counts.items():
            print(f"  {month}: {count:,} jobs")
        
        unique_months = len(monthly_counts)
        print(f"\nUnique months: {unique_months}")
        
        if unique_months < 3:
            print("❌ PROBLEM: Need at least 3 months for trend analysis!")
        else:
            print("✅ Sufficient time periods for trend analysis")
    else:
        print("❌ No valid dates for time series analysis")

print("\n4. OBSOLESCENCE DETECTION TEST:")
print("-" * 80)

try:
    summary_df, pivot_df = detect_skill_obsolescence(
        df=df,
        freq="M",
        top_k=10,
        min_total_mentions=5,
        alpha=0.05,
        slope_threshold_log=0.02,
        category_min_change_ratio=1.8,
        fade_threshold_mentions=1,
    )
    
    print(f"Summary results: {len(summary_df)} skills analyzed")
    print(f"Pivot data shape: {pivot_df.shape}")
    
    if not summary_df.empty:
        print("\nSkill categories:")
        category_counts = summary_df["category"].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count} skills")
        
        print("\nTop 5 skills by total mentions:")
        top_skills = summary_df.nlargest(5, "total_mentions")
        for _, row in top_skills.iterrows():
            print(f"  {row['skill']}: {row['total_mentions']} mentions ({row['category']})")
    else:
        print("❌ No skills detected in obsolescence analysis!")
        
    if pivot_df.empty:
        print("❌ No pivot data generated!")
    else:
        print(f"✅ Pivot data: {pivot_df.shape[0]} time periods, {pivot_df.shape[1]} skills")

except Exception as e:
    print(f"❌ Error in obsolescence detection: {e}")

print("\n5. ISSUES IDENTIFIED:")
print("-" * 80)

issues = []

# Issue 1: Date range too narrow
if "post_date" in df.columns:
    valid_dates = df["post_date"].dropna()
    if len(valid_dates) > 0:
        date_span = (valid_dates.max() - valid_dates.min()).days
        if date_span < 60:  # Less than 2 months
            issues.append(f"Date range too narrow: {date_span} days (need 3+ months for trends)")

# Issue 2: CSV upload confusion
issues.append("UI asks for CSV upload when data should be automatically available")

# Issue 3: No clear purpose explanation
issues.append("Purpose unclear - should show declining/emerging skills from existing job data")

# Issue 4: Detection settings too complex
issues.append("Too many technical parameters exposed to users")

if issues:
    print("❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
else:
    print("✅ No major issues detected")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print("1. Remove CSV upload requirement - use existing job data")
print("2. Add synthetic time series data or use different approach")
print("3. Simplify UI - hide technical parameters")
print("4. Add clear explanation of what the tool does")
print("5. Show skill trends from job posting frequency")
print("6. Add skill demand analysis from current data")