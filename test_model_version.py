from src.job_risk_model import get_model_info, predict_job_risk

print("=" * 60)
print("MODEL VERSION CHECK")
print("=" * 60)

info = get_model_info()
print(f"Model Version: {info['version']}")
print(f"Experience Coefficient: {info['experience_coefficient']:.4f}")
print(f"Training Samples: {info['training_samples']:,}")
print()

if info['experience_coefficient'] < -0.25:
    print("✅ Status: FIXED - Experience has strong impact")
else:
    print("❌ Status: OLD MODEL - Experience impact is weak")

print("\n" + "=" * 60)
print("QUICK TEST: Python Developer")
print("=" * 60)

for exp in [5, 10, 20]:
    result = predict_job_risk(
        "python", "Bachelor's degree", exp, 
        "Metro / Tier-1 city", "Technology / software"
    )
    print(f"{exp:2d} years experience → {result.high_risk_probability_pct:5.1f}% risk")

print("\n✅ Risk should DECREASE as experience increases")
