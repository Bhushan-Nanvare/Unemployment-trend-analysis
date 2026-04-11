"""
Test scenarios that should show High risk
"""
from src.job_risk_model import predict_job_risk

print("=" * 80)
print("HIGH RISK SCENARIOS TEST")
print("=" * 80)

# Test scenarios that should show high risk
high_risk_scenarios = [
    # Very low skills + low education + low experience
    ("data entry", "Less than high school", 0, "Smaller town / rural", "Hospitality / tourism"),
    ("typing, filing", "High school / diploma", 1, "Smaller town / rural", "Retail / e-commerce ops"),
    ("basic computer", "Less than high school", 2, "Tier-2 city", "Manufacturing (traditional)"),
    
    # Outdated skills
    ("cobol, vb.net", "Bachelor's degree", 3, "Tier-2 city", "Manufacturing (traditional)"),
    ("flash, jquery", "High school / diploma", 2, "Smaller town / rural", "Other / not listed"),
    
    # No skills at all
    ("", "Less than high school", 0, "Smaller town / rural", "Hospitality / tourism"),
    ("", "High school / diploma", 1, "Smaller town / rural", "Manufacturing (traditional)"),
]

print("Testing scenarios that should show HIGH RISK:")
print("-" * 80)

for skills, edu, exp, loc, ind in high_risk_scenarios:
    result = predict_job_risk(skills, edu, exp, loc, ind)
    risk_icon = "🟢" if result.risk_level == "Low" else "🟡" if result.risk_level == "Medium" else "🔴"
    skills_display = skills if skills else "(no skills)"
    print(f"{skills_display:20s} | {edu:25s} | {exp}y | {loc:20s} | {ind:25s} → {result.high_risk_probability_pct:5.1f}% {risk_icon}")

print("\n" + "=" * 80)
print("CURRENT THRESHOLDS:")
print("🟢 Low Risk:    < 18%")
print("🟡 Medium Risk: 18% - 29%") 
print("🔴 High Risk:   >= 30%")
print("\nGoal: Get some scenarios above 30% for realistic High risk warnings")