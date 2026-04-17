"""
Full API + page-level integration test.
Run with: python -X utf8 api_test.py
"""
import sys, os, requests, json, traceback, subprocess, time
sys.path.insert(0, ".")
PORT = 8002
BASE = f"http://127.0.0.1:{PORT}"
all_ok = True

def ok(label):  print(f"  OK   {label}")
def err(label, msg=""):
    global all_ok
    all_ok = False
    print(f"  ERR  {label}: {msg}")
def warn(label, msg=""): print(f"  WARN {label}: {msg}")

# ── Backend bootstrap (so the test is runnable) ────────────────────────────────
def _start_backend_if_needed():
    try:
        r = requests.get(f"{BASE}/data-status", timeout=2)
        if r.status_code == 200:
            return True
    except Exception:
        pass

    try:
        subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.api:app",
             "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        err("backend start", str(e))
        return False

    # Wait briefly for startup
    for _ in range(30):
        time.sleep(0.25)
        try:
            r = requests.get(f"{BASE}/data-status", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass

    err("backend start", "timed out waiting for /data-status")
    return False


# ── 1. FastAPI health endpoints ───────────────────────────────────────────────
print("=" * 60)
print("1. FASTAPI ENDPOINTS")
print("=" * 60)

_start_backend_if_needed()

def get(path, label):
    try:
        r = requests.get(f"{BASE}{path}", timeout=10)
        if r.status_code == 200:
            ok(f"GET {path}  [{label}]")
            return r.json()
        else:
            err(f"GET {path}", f"HTTP {r.status_code}")
    except Exception as e:
        err(f"GET {path}", str(e))
    return None

def post(path, payload, label):
    try:
        r = requests.post(f"{BASE}{path}", json=payload, timeout=20)
        if r.status_code == 200:
            ok(f"POST {path}  [{label}]")
            return r.json()
        else:
            err(f"POST {path}", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        err(f"POST {path}", str(e))
    return None

get("/data-status",   "data status")
get("/health",        "health check")
get("/events",        "historical events")

sim_payload = {"shock_intensity": 0.3, "shock_duration": 6,
               "recovery_rate": 0.15, "forecast_horizon": 6}
sim_result = post("/simulate", sim_payload, "basic simulation")
if sim_result:
    has_keys = all(k in sim_result for k in ["baseline", "scenario", "indices"])
    if has_keys:
        ok("  simulate response has baseline + scenario + indices")
    else:
        err("  simulate response", f"missing keys, got: {list(sim_result.keys())}")

# ── 2. Live data modules ──────────────────────────────────────────────────────
print()
print("=" * 60)
print("2. LIVE DATA MODULES")
print("=" * 60)
try:
    from src.live_data import fetch_labor_market_pulse, fetch_gdp_growth
    data = fetch_labor_market_pulse("India")
    if data:
        ok(f"fetch_labor_market_pulse(India): {len(data)} indicators")
        for k, v in list(data.items())[:3]:
            latest = v.iloc[-1] if v is not None and not v.empty else None
            if latest is not None:
                print(f"       {k[:45]:<45} latest={int(latest['Year'])} val={latest['Value']:.2f}%")
    else:
        warn("fetch_labor_market_pulse", "returned empty — API may be slow or unavailable")
except Exception as e:
    err("live_data", str(e))

try:
    gdp = fetch_gdp_growth("India")
    if gdp is not None and not gdp.empty:
        ok(f"fetch_gdp_growth(India): {len(gdp)} rows, latest={gdp.iloc[-1].to_dict()}")
    else:
        warn("fetch_gdp_growth", "returned empty")
except Exception as e:
    err("fetch_gdp_growth", str(e))

# ── 3. Per-page src module simulation ────────────────────────────────────────
print()
print("=" * 60)
print("3. PAGE-LEVEL SRC MODULE CHECKS")
print("=" * 60)

# Overview (page 1) — forecasting + recession signals
try:
    from src.forecasting import ForecastingEngine
    from src.preprocessing import Preprocessor
    from src.live_data import fetch_world_bank
    pre = Preprocessor()
    df = pre.preprocess(fetch_world_bank("India"))
    if df is not None and not df.empty:
        ok(f"Overview: Preprocessor loaded {len(df)} rows")
        fe = ForecastingEngine(forecast_horizon=6)
        fdf = fe.forecast(df)
        ok(f"Overview: ForecastingEngine forecast={len(fdf)} rows")
    else:
        warn("Overview: Preprocessor returned empty df")
except Exception as e:
    err("Overview page modules", str(e)); traceback.print_exc()

# Sector Analysis (page 3) — sector analysis module
try:
    from src.sector_analysis import SectorAnalysis
    from src.shock_scenario import ShockScenario
    from src.forecasting import ForecastingEngine
    from src.preprocessing import Preprocessor
    from src.live_data import fetch_world_bank

    df = Preprocessor().preprocess(fetch_world_bank("India"))
    baseline = ForecastingEngine(forecast_horizon=6).forecast(df)
    scenario_df = ShockScenario(0.3, 6, 0.15).apply(baseline)
    result = SectorAnalysis.analyze_sectors(scenario_df=scenario_df, shock_intensity=0.3, recovery_rate=0.15)
    if result is not None and len(result):
        ok(f"Sector Analysis: analyze_sectors() returned {len(result)} sectors")
    else:
        err("Sector Analysis", "returned empty")
except Exception as e:
    err("Sector Analysis page modules", str(e))

# Job Risk Predictor (page 7) — full risk + salary + recommendations
try:
    from src.analytics.salary_analyzer import SalaryAnalyzer
    from src.analytics.recommendation_engine import RecommendationEngine
    from src.risk_calculators import UserProfile, RiskProfile
    from src.job_risk_model import predict_job_risk

    res = predict_job_risk("Python, SQL, machine learning", "Bachelor's degree",
                           5, "Metro / Tier-1 city", "Technology / software")
    ok(f"Job Risk Predictor: risk={res.high_risk_probability_pct}% level={res.risk_level}")

    # Check salary is in INR range
    sa_analyzer = SalaryAnalyzer()
    rm = sa_analyzer.BASE_SALARY_FACTORS["role_level_multiplier"]["Mid"]
    im = sa_analyzer.BASE_SALARY_FACTORS["industry_multiplier"]["Technology / software"]
    em = 1 + 5 * 0.03
    base = sa_analyzer.BASE_SALARY_INR * rm * im * em
    lm = sa_analyzer.LOCATION_MULTIPLIERS["Metro / Tier-1 city"]
    loc_adj = base * lm
    lpa = loc_adj / 100_000
    if 5 <= lpa <= 50:
        ok(f"Salary Analyzer: Mid IT 5yr Metro = {lpa:.1f} LPA (INR, realistic)")
    else:
        err("Salary Analyzer", f"{lpa:.1f} LPA looks wrong (expected 5-50 LPA for Mid 5yr)")
except Exception as e:
    err("Job Risk Predictor modules", str(e)); traceback.print_exc()

# Job Market Pulse (page 8) — all new functions
try:
    from src.job_market_pulse import (
        load_job_postings, posting_volume_over_time, salary_range_by_role,
        skill_cooccurrence, remote_vs_onsite_counts, skill_demand_counts,
    )
    df = load_job_postings()
    if not df.empty:
        vol = posting_volume_over_time(df)
        sr  = salary_range_by_role(df)
        rem = remote_vs_onsite_counts(df)
        cooc= skill_cooccurrence(df, top_n=8)
        top = skill_demand_counts(df).head(5)
        ok(f"Job Market Pulse: {len(df):,} rows, {len(vol)} weeks vol, {len(sr)} salary roles")
        ok(f"  cooc matrix={cooc.shape}, remote={rem}")
        ok(f"  top skills: {', '.join(list(top.index))}")
    else:
        warn("Job Market Pulse", "CSV not found - Tab 1 will show upload prompt only")
except Exception as e:
    err("Job Market Pulse modules", str(e)); traceback.print_exc()

# Geo Career Advisor (page 9)
try:
    from src.geo_career_advisor import normalize_city_key, resolve_city_row, get_cost_of_living_index, calculate_real_salary
    ck = normalize_city_key("Bangalore")
    row = resolve_city_row(ck)
    col = get_cost_of_living_index(ck)
    real = calculate_real_salary(10.0, ck)  # 10 LPA nominal
    if row is not None:
        ok("Geo Career Advisor: resolve_city_row() returned a match")
    else:
        warn("Geo Career Advisor", "city reference not found for Bangalore")
    if col is not None and real is not None:
        ok(f"Geo Career Advisor: COL index={col:.1f}, real salary for 10 LPA={real:.1f} LPA")
except Exception as e:
    err("Geo Career Advisor modules", str(e))

# AI Insights (page 5)
try:
    from src.llm_insights import generate_insights
    from src.live_insights import generate_labor_market_insights
    ok("AI Insights: llm_insights + live_insights imported OK")
except Exception as e:
    err("AI Insights modules", str(e))

# ── 4. Check encoding in key files ────────────────────────────────────────────
print()
print("=" * 60)
print("4. MOJIBAKE ENCODING CHECK (look for garbled chars)")
print("=" * 60)
import re
GARBLE_PAT = re.compile(r'[ð\x80-\x9f\xc2-\xef]{2,}|â€|Ã')
files_to_check = [
    "pages/8_Job_Market_Pulse.py",
    "pages/3_Sector_Analysis.py",
    "pages/1_Overview.py",
    "pages/7_Job_Risk_Predictor.py",
    "pages/9_Geo_Career_Advisor.py",
]
for fpath in files_to_check:
    try:
        content = open(fpath, encoding="utf-8").read()
        matches = GARBLE_PAT.findall(content)
        if matches:
            err(f"Encoding {fpath}", f"Found {len(matches)} garbled patterns: {matches[:3]}")
        else:
            ok(f"Encoding clean: {fpath}")
    except Exception as e:
        err(f"Encoding check {fpath}", str(e))

# ── Result ────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("OVERALL:", "ALL CHECKS PASSED" if all_ok else "SOME ISSUES FOUND — see above")
print("=" * 60)
sys.exit(0 if all_ok else 1)
