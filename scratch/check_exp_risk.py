
import sys
import os
sys.path.append(os.getcwd())

from src.job_risk_model import predict_job_risk, get_pipeline, FEATURE_NAMES

def test_experience_sensitivity():
    skills = "python, sql"
    edu = "Bachelor's degree"
    loc = "Metro / Tier-1 city"
    ind = "Technology / software"
    
    print(f"{'Exp':>5} | {'Risk %':>10}")
    print("-" * 20)
    for exp in range(0, 31, 5):
        result = predict_job_risk(skills, edu, exp, loc, ind)
        print(f"{exp:>5} | {result.high_risk_probability_pct:>10}%")
    
    pipe = get_pipeline()
    clf = pipe.named_steps["clf"]
    coefs = clf.coef_.ravel()
    print("\nModel Coefficients:")
    for name, val in zip(FEATURE_NAMES, coefs):
        print(f"{name:20}: {val:.4f}")

if __name__ == "__main__":
    test_experience_sensitivity()
