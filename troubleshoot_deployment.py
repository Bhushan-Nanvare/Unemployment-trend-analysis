"""
Quick troubleshooting script to verify the model is working correctly
Run this to confirm the fix is active
"""
from src.job_risk_model import get_model_info, predict_job_risk

print("=" * 70)
print("JOB RISK PREDICTOR - DEPLOYMENT TROUBLESHOOTING")
print("=" * 70)

# Check model version
print("\n1. MODEL VERSION CHECK:")
print("-" * 70)
info = get_model_info()
print(f"   Model Version: {info['version']}")
print(f"   Training Samples: {info['training_samples']:,}")
print(f"   Experience Coefficient: {info['experience_coefficient']:.4f}")

if info['experience_coefficient'] < -0.25:
    print("   ✅ CORRECT: Experience has strong negative impact on risk")
else:
    print("   ❌ PROBLEM: Experience coefficient is too weak!")
    print("   → Old model is still loaded. Try restarting the app.")

# Test experience impact
print("\n2. EXPERIENCE IMPACT TEST:")
print("-" * 70)
print("   Profile: Python, Bachelor's, Tech, Metro")
print()

risks = []
for exp in [0, 5, 10, 20]:
    result = predict_job_risk(
        "python", "Bachelor's degree", exp,
        "Metro / Tier-1 city", "Technology / software"
    )
    risks.append(result.high_risk_probability_pct)
    print(f"   {exp:2d} years → {result.high_risk_probability_pct:5.1f}% risk")

# Verify decreasing trend
print()
is_decreasing = all(risks[i] > risks[i+1] for i in range(len(risks)-1))
if is_decreasing:
    print("   ✅ CORRECT: Risk decreases as experience increases")
    reduction = ((risks[0] - risks[-1]) / risks[0]) * 100
    print(f"   ✅ Total reduction: {reduction:.1f}% (from {risks[0]:.1f}% to {risks[-1]:.1f}%)")
else:
    print("   ❌ PROBLEM: Risk is NOT decreasing properly!")
    print("   → The old model is still active. Restart required.")

# Test education impact
print("\n3. EDUCATION IMPACT TEST:")
print("-" * 70)
print("   Profile: Python, 5 years exp, Tech, Metro")
print()

edu_risks = []
edu_levels = ["High school / diploma", "Bachelor's degree", "Master's degree"]
for edu in edu_levels:
    result = predict_job_risk(
        "python", edu, 5,
        "Metro / Tier-1 city", "Technology / software"
    )
    edu_risks.append(result.high_risk_probability_pct)
    print(f"   {edu:25s} → {result.high_risk_probability_pct:5.1f}% risk")

print()
is_edu_decreasing = all(edu_risks[i] > edu_risks[i+1] for i in range(len(edu_risks)-1))
if is_edu_decreasing:
    print("   ✅ CORRECT: Risk decreases with higher education")
else:
    print("   ❌ PROBLEM: Education impact is not working correctly")

# Overall status
print("\n" + "=" * 70)
print("OVERALL STATUS:")
print("=" * 70)

if is_decreasing and is_edu_decreasing and info['experience_coefficient'] < -0.25:
    print("✅ ALL TESTS PASSED - MODEL IS WORKING CORRECTLY!")
    print()
    print("The fix is active. You should see:")
    print("  • More experience = Lower risk")
    print("  • Higher education = Lower risk")
    print("  • Better skills = Lower risk")
else:
    print("❌ SOME TESTS FAILED - OLD MODEL MAY BE CACHED")
    print()
    print("Solutions:")
    print("  1. If testing locally: Restart Streamlit (Ctrl+C, then 'streamlit run app.py')")
    print("  2. If on Streamlit Cloud: Reboot the app from the dashboard")
    print("  3. Clear browser cache: Ctrl+Shift+R (hard refresh)")
    print("  4. Wait 5 minutes for auto-deployment to complete")

print("=" * 70)
