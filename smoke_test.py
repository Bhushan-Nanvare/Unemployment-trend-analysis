"""
Smoke test — run with: python smoke_test.py
Checks syntax, imports, and functional outputs for all key modules.
"""
import sys, os, py_compile, importlib, traceback
sys.path.insert(0, ".")

all_ok = True

# ── 1. Syntax check all pages ────────────────────────────────────────────────
PAGES = [
    "pages/0_Help_Guide.py",
    "pages/1_Overview.py",
    "pages/2_Simulator.py",
    "pages/3_Sector_Analysis.py",
    "pages/5_AI_Insights.py",
    "pages/7_Job_Risk_Predictor.py",
    "pages/8_Job_Market_Pulse.py",
    "pages/9_Geo_Career_Advisor.py",
    "pages/12_Advanced_Simulator.py",
    "src/job_market_pulse.py",
    "src/analytics/salary_analyzer.py",
    "src/analytics/recommendation_engine.py",
]

print("=" * 60)
print("1. SYNTAX CHECK")
print("=" * 60)
for p in PAGES:
    try:
        py_compile.compile(p, doraise=True)
        print(f"  OK   {p}")
    except py_compile.PyCompileError as e:
        print(f"  ERR  {p}: {e}")
        all_ok = False

# ── 2. Import check src modules ──────────────────────────────────────────────
SRC_MODS = [
    "src.job_market_pulse",
    "src.analytics.salary_analyzer",
    "src.analytics.recommendation_engine",
    "src.job_risk_model",
]

print()
print("=" * 60)
print("2. MODULE IMPORT CHECK")
print("=" * 60)
for mod in SRC_MODS:
    try:
        importlib.import_module(mod)
        print(f"  OK   {mod}")
    except Exception as e:
        print(f"  ERR  {mod}: {e}")
        all_ok = False

# ── 3. Salary Analyzer (INR check) ──────────────────────────────────────────
print()
print("=" * 60)
print("3. SALARY ANALYZER — INR SANITY CHECK")
print("=" * 60)
try:
    from src.analytics.salary_analyzer import SalaryAnalyzer
    sa = SalaryAnalyzer()
    cases = [
        ("Entry", "Technology / software",  0, "Metro / Tier-1 city"),
        ("Mid",   "Technology / software",  5, "Metro / Tier-1 city"),
        ("Senior","Technology / software", 10, "Metro / Tier-1 city"),
        ("Lead",  "Technology / software", 12, "Metro / Tier-1 city"),
        ("Executive","Technology / software", 20, "Metro / Tier-1 city"),
    ]
    for role, ind, exp, loc in cases:
        rm = sa.BASE_SALARY_FACTORS["role_level_multiplier"][role]
        im = sa.BASE_SALARY_FACTORS["industry_multiplier"][ind]
        em = 1 + exp * 0.03
        base = sa.BASE_SALARY_INR * rm * im * em
        lm = sa.LOCATION_MULTIPLIERS[loc]
        loc_adj = base * lm
        lpa = loc_adj / 100_000
        flag = "  OK" if 3 <= lpa <= 200 else "  WARN SUSPICIOUS"
        print(f"  {role:12s} {exp:2d}yr  =>  base INR {base:>10,.0f}  loc-adj INR {loc_adj:>10,.0f}  ({lpa:.1f} LPA){flag}")
except Exception as e:
    print(f"  ERR: {e}")
    traceback.print_exc()
    all_ok = False

# ── 4. Recommendation salary_impact (INR check) ─────────────────────────────
print()
print("=" * 60)
print("4. RECOMMENDATION ENGINE — SALARY IMPACT CHECK (should be INR)")
print("=" * 60)
try:
    from src.analytics.recommendation_engine import RecommendationEngine, Recommendation
    re = RecommendationEngine()
    # Check hardcoded salary_impact values are in INR range (>10,000)
    # by inspecting a known recommendation
    class FRP:
        automation_risk = 70.0
        recession_risk  = 70.0
        overall_risk    = 70.0
        role_level      = "Entry"
        industry        = "Technology / software"
        experience_years= 2
        company_size    = "11-50"
        remote_capability = False
        education_level = "Bachelor's degree"
    recs = re.generate_recommendations(FRP(), FRP(), 500_000)
    for r in recs:
        lo, hi = r.salary_impact
        flag = "OK INR" if lo >= 10_000 else "WARN Looks like USD (too small)"
        print(f"  {r.action[:55]:<55} impact: INR {lo:,} to INR {hi:,}  {flag}")
except Exception as e:
    print(f"  ERR: {e}")
    traceback.print_exc()
    all_ok = False

# ── 5. Job Risk Model ────────────────────────────────────────────────────────
print()
print("=" * 60)
print("5. JOB RISK MODEL — PREDICTION CHECK")
print("=" * 60)
try:
    from src.job_risk_model import predict_job_risk
    cases = [
        ("Python, machine learning, AWS", "Master's degree", 8, "Metro / Tier-1 city", "Technology / software"),
        ("data entry, filing", "High school / diploma", 1, "Smaller town / rural", "Manufacturing (traditional)"),
    ]
    for skills, edu, exp, loc, ind in cases:
        r = predict_job_risk(skills, edu, exp, loc, ind)
        print(f"  risk={r.high_risk_probability_pct:5.1f}%  level={r.risk_level:6s}  ({edu[:20]}, {exp}yr, {ind[:20]})")
except Exception as e:
    print(f"  ERR: {e}")
    traceback.print_exc()
    all_ok = False

# ── 6. Job Market Pulse new functions ────────────────────────────────────────
print()
print("=" * 60)
print("6. JOB MARKET PULSE NEW FUNCTIONS")
print("=" * 60)
try:
    from src.job_market_pulse import (
        load_job_postings, posting_volume_over_time,
        salary_range_by_role, skill_cooccurrence,
        remote_vs_onsite_counts, experience_distribution,
    )
    df = load_job_postings()
    if df.empty:
        print("  WARN  CSV not found — data/market_pulse/job_postings_sample.csv missing")
        print("        (This is expected if data file is not present locally)")
    else:
        print(f"  OK    Loaded {len(df):,} rows from CSV")
        vol  = posting_volume_over_time(df)
        sr   = salary_range_by_role(df)
        rem  = remote_vs_onsite_counts(df)
        cooc = skill_cooccurrence(df, top_n=8)
        exp  = experience_distribution(df)
        print(f"  OK    posting_volume_over_time:  {len(vol)} weeks")
        print(f"  OK    salary_range_by_role:      {len(sr)} roles")
        print(f"  OK    remote_vs_onsite_counts:   {rem}")
        print(f"  OK    skill_cooccurrence:         {cooc.shape} matrix")
        print(f"  OK    experience_distribution:    {len(exp)} rows")
except Exception as e:
    print(f"  ERR: {e}")
    traceback.print_exc()
    all_ok = False

# ── Result ───────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("RESULT:", "ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED - see above")
print("=" * 60)
sys.exit(0 if all_ok else 1)
