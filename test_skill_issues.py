"""
Test skill demand scoring issues
"""
from src.job_risk_model import predict_job_risk, compute_skill_demand_score, parse_skills

print("=" * 80)
print("SKILL DEMAND ANALYSIS")
print("=" * 80)

# Test different skills
skills_to_test = [
    "python",
    "html", 
    "css",
    "javascript", 
    "excel",
    "data entry",
    "machine learning",
    "communication",
    "jquery",
    "manual testing"
]

print("\n1. SKILL DEMAND SCORES:")
print("-" * 80)
for skill in skills_to_test:
    parsed = parse_skills(skill)
    score, matched = compute_skill_demand_score(parsed)
    print(f"{skill:20s} → Score: {score:.3f} | Matched: {matched}")

print("\n2. RISK PREDICTIONS (5 years exp, Bachelor's, Tech, Metro):")
print("-" * 80)
for skill in skills_to_test:
    result = predict_job_risk(
        skill, "Bachelor's degree", 5,
        "Metro / Tier-1 city", "Technology / software"
    )
    print(f"{skill:20s} → Risk: {result.high_risk_probability_pct:5.1f}% ({result.risk_level})")

print("\n3. TESTING UNRECOGNIZED SKILLS:")
print("-" * 80)
unrecognized_skills = ["html", "css", "photoshop", "microsoft word", "typing"]
for skill in unrecognized_skills:
    parsed = parse_skills(skill)
    score, matched = compute_skill_demand_score(parsed)
    result = predict_job_risk(
        skill, "Bachelor's degree", 5,
        "Metro / Tier-1 city", "Technology / software"
    )
    print(f"{skill:20s} → Score: {score:.3f} | Risk: {result.high_risk_probability_pct:5.1f}%")

print("\n4. RISK LEVEL THRESHOLDS:")
print("-" * 80)
print("Current thresholds:")
print("  High Risk:   >= 62%")
print("  Medium Risk: 35% - 61%") 
print("  Low Risk:    < 35%")
print()
print("Issue: Even low-demand skills are showing < 35% (Low risk)")
print("Solution: Adjust thresholds or improve skill scoring")