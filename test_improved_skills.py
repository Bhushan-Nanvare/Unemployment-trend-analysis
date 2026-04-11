"""
Test the improved skill scoring system
"""
from src.job_risk_model import predict_job_risk, get_model_info

print("=" * 80)
print("IMPROVED SKILL SCORING TEST")
print("=" * 80)

# Check model version
info = get_model_info()
print(f"Model Version: {info['version']}")
print()

# Test different skill categories
skill_categories = [
    # High-demand skills (should be very low risk)
    ("High-Demand AI/ML", [
        "machine learning, python, aws",
        "data science, sql, python", 
        "deep learning, tensorflow, python"
    ]),
    
    # Good programming skills (should be low risk)
    ("Programming Skills", [
        "python, javascript, react",
        "java, sql, git",
        "typescript, node, docker"
    ]),
    
    # Moderate skills (should be medium risk)
    ("Moderate Skills", [
        "project management, excel",
        "html, css, javascript",
        "php, wordpress, mysql"
    ]),
    
    # Low-demand skills (should be medium-high risk)
    ("Low-Demand Skills", [
        "html, css",
        "excel, powerpoint",
        "jquery, photoshop"
    ]),
    
    # Very low-demand skills (should be high risk)
    ("Very Low-Demand", [
        "data entry, typing",
        "microsoft word, filing",
        "basic computer, fax"
    ])
]

print("RISK PREDICTIONS (5 years exp, Bachelor's, Tech, Metro):")
print("-" * 80)

for category, skills_list in skill_categories:
    print(f"\n{category}:")
    for skills in skills_list:
        result = predict_job_risk(
            skills, "Bachelor's degree", 5,
            "Metro / Tier-1 city", "Technology / software"
        )
        risk_color = "🟢" if result.risk_level == "Low" else "🟡" if result.risk_level == "Medium" else "🔴"
        print(f"  {skills:30s} → {result.high_risk_probability_pct:5.1f}% {risk_color} {result.risk_level}")

print("\n" + "=" * 80)
print("EXPECTED PATTERN:")
print("🟢 High-Demand AI/ML: < 10% (Low)")
print("🟢 Programming Skills: 10-15% (Low)")  
print("🟡 Moderate Skills: 15-25% (Medium)")
print("🟡 Low-Demand Skills: 25-35% (Medium)")
print("🔴 Very Low-Demand: > 35% (High)")

print("\n" + "=" * 80)
print("CURRENT THRESHOLDS:")
print("🟢 Low Risk:    < 25%")
print("🟡 Medium Risk: 25% - 44%") 
print("🔴 High Risk:   >= 45%")