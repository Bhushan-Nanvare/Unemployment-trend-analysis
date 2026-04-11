import math
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel

from src.live_data import fetch_world_bank, get_data_source_label
from src.preprocessing import Preprocessor
from src.forecasting import ForecastingEngine
from src.shock_scenario import ShockScenario
from src.scenario_metrics import ScenarioMetrics
from src.policy_playbook import PolicyPlaybook
from src.sector_analysis import SectorAnalysis
from src.career_advisor import CareerAdvisor
from src.llm_insights import generate_insights
from src.story_generator import StoryGenerator
from src.model_validator import ModelValidator
from src.historical_events import get_all_events


app = FastAPI(title="Unemployment Intelligence Platform API v2")


# -------- Request Schemas --------
class ScenarioRequest(BaseModel):
    shock_intensity: float
    shock_duration: int
    recovery_rate: float
    forecast_horizon: int = 6
    policy_name: Optional[str] = None


class BacktestRequest(BaseModel):
    test_years: int = 5


class SensitivityRequest(BaseModel):
    base_shock_intensity: float
    base_shock_duration: int
    base_recovery_rate: float
    forecast_horizon: int = 6
    policy_name: Optional[str] = None


def _load_prepared_series():
    """
    Loads India unemployment series.
    Tries World Bank Live API first, falls back to local CSV automatically.
    """
    df = fetch_world_bank(country="India")
    df = Preprocessor().preprocess(df)
    return df


# -------- Simulation Endpoint --------
@app.post("/simulate")
def simulate_scenario(request: ScenarioRequest):
    df = _load_prepared_series()

    # Baseline forecast with confidence bands
    engine = ForecastingEngine(forecast_horizon=request.forecast_horizon)
    baseline = engine.forecast(df)
    baseline_conf = engine.forecast_with_confidence(df)

    # Scenario simulation (shock now hits immediately — fixed logic)
    scenario = ShockScenario(
        shock_intensity=request.shock_intensity,
        shock_duration=request.shock_duration,
        recovery_rate=request.recovery_rate,
    ).apply(baseline)

    # Metrics
    metrics = ScenarioMetrics.compute_delta(baseline, scenario)

    # Policy + Indices
    policy_cfg = PolicyPlaybook.get_policy(request.policy_name)
    indices = ScenarioMetrics.compute_indices(
        baseline_df=baseline,
        scenario_df=scenario,
        policy_name=request.policy_name or "None",
    )

    # Recovery Quality Index
    rqi = ScenarioMetrics.compute_rqi(scenario, request.recovery_rate)
    indices.update(rqi)

    # Early Warning
    usi = indices.get("unemployment_stress_index", 0)
    rqi_label = rqi.get("rqi_label", "")
    if usi > 40 or rqi_label == "Poor Recovery":
        status = "🔴 High Risk"
    elif usi > 20 or rqi_label == "Fast but Fragile":
        status = "🟡 Watch"
    else:
        status = "🟢 Stable"
    indices["early_warning"] = status

    # Sector Analysis (calibrated to India's historical peak)
    sector_impact = SectorAnalysis.analyze_sectors(
        scenario_df=scenario,
        shock_intensity=request.shock_intensity,
        recovery_rate=request.recovery_rate,
    )

    # Career Advice with dynamic thresholds
    career_advice = CareerAdvisor.generate_advice(
        sector_impact, shock_intensity=request.shock_intensity
    )

    # AI Insights (LLM or rule-based fallback)
    scen_name = (
        request.policy_name
        if request.policy_name and request.policy_name != "None"
        else "Shock Scenario"
    )
    ai_insights = generate_insights(
        scenario_name=scen_name,
        indices=indices,
        sector_impact=sector_impact,
    )

    # Story timeline
    story = StoryGenerator.generate_story(scenario, baseline)

    return {
        "baseline": baseline.to_dict(orient="records"),
        "baseline_confidence": baseline_conf.to_dict(orient="records"),
        "scenario": scenario.to_dict(orient="records"),
        "metrics": metrics.to_dict(orient="records"),
        "policy": policy_cfg,
        "indices": indices,
        "sector_impact": sector_impact.to_dict(orient="records"),
        "career_advice": career_advice,
        "ai_insights": ai_insights,
        "story": story,
        "data_source": get_data_source_label("India"),
    }


# -------- Backtesting Endpoint --------
@app.post("/backtest")
def backtest_model(request: BacktestRequest):
    df = _load_prepared_series()

    test_years = max(1, min(request.test_years, 10))
    if len(df) <= test_years + 5:
        test_years = min(3, max(1, len(df) - 3))

    train_df = df.iloc[:-test_years]
    test_df = df.iloc[-test_years:]

    engine = ForecastingEngine(forecast_horizon=test_years)
    forecast_df = engine.forecast(train_df)
    merged = test_df.merge(forecast_df, on="Year", how="inner")

    if merged.empty:
        return {"historical": [], "backtest": [], "mae": None, "mape": None}

    errors = merged["Predicted_Unemployment"] - merged["Unemployment_Rate"]
    mae = float(errors.abs().mean())
    non_zero = merged["Unemployment_Rate"].replace(0, float("nan"))
    mape = float((errors.abs() / non_zero * 100).mean())

    return {
        "historical": test_df.to_dict(orient="records"),
        "backtest": merged.to_dict(orient="records"),
        "mae": round(mae, 3),
        # math.isfinite catches both NaN and inf (inf when actual rate ≈ 0).
        "mape": round(mape, 2) if math.isfinite(mape) else None,
    }


# -------- Validation Endpoint --------
@app.get("/validate")
def validate_model():
    df = _load_prepared_series()
    
    # Adaptive validation strategy:
    # 1. Use only the most recent 15 years of data (if available) to train
    # 2. Test on the last 3 years
    # This ensures the model adapts to recent regime changes rather than
    # being anchored to 1990s-2000s patterns that no longer apply.
    
    # Step 1: Take only recent data
    recent_window = 15
    if len(df) > recent_window:
        df = df.tail(recent_window).reset_index(drop=True)
    
    # Step 2: Split recent data
    test_years = 3
    if len(df) <= test_years + 3:
        test_years = max(2, len(df) // 4)
    
    train_df = df.iloc[:-test_years]
    test_df = df.iloc[-test_years:]

    engine = ForecastingEngine(forecast_horizon=len(test_df))
    forecast_df = engine.forecast(train_df)
    return ModelValidator.get_validation_report(test_df, forecast_df)


# -------- Historical Events Endpoint --------
@app.get("/events")
def get_historical_events():
    return {"events": get_all_events()}


# -------- Sensitivity Analysis Endpoint --------
class SensitivityRequest(BaseModel):
    base_shock_intensity: float
    base_shock_duration: int
    base_recovery_rate: float
    forecast_horizon: int = 6
    policy_name: Optional[str] = None


@app.post("/sensitivity_analysis")
def sensitivity_analysis(request: SensitivityRequest):
    """
    Perform sensitivity analysis by varying each parameter independently.
    Returns tornado chart data and 2D heatmap data.
    """
    df = _load_prepared_series()
    
    # Base scenario
    base_params = {
        "shock_intensity": request.base_shock_intensity,
        "shock_duration": request.base_shock_duration,
        "recovery_rate": request.base_recovery_rate,
        "forecast_horizon": request.forecast_horizon,
        "policy_name": request.policy_name,
    }
    
    # Run base simulation
    engine = ForecastingEngine(forecast_horizon=request.forecast_horizon)
    baseline = engine.forecast(df)
    
    base_scenario = ShockScenario(
        shock_intensity=request.base_shock_intensity,
        shock_duration=request.base_shock_duration,
        recovery_rate=request.base_recovery_rate,
    ).apply(baseline)
    base_peak = float(base_scenario["Scenario_Unemployment"].max())
    
    # 1. TORNADO CHART DATA - Vary each parameter independently
    tornado_data = []
    
    # Vary shock intensity (±50% of base value, min 0.05)
    si_low = max(0.05, request.base_shock_intensity - 0.2)
    si_high = min(0.6, request.base_shock_intensity + 0.2)
    
    scen_low = ShockScenario(si_low, request.base_shock_duration, request.base_recovery_rate).apply(baseline)
    peak_low = float(scen_low["Scenario_Unemployment"].max())
    impact_low = peak_low - base_peak
    
    scen_high = ShockScenario(si_high, request.base_shock_duration, request.base_recovery_rate).apply(baseline)
    peak_high = float(scen_high["Scenario_Unemployment"].max())
    impact_high = peak_high - base_peak
    
    tornado_data.append({
        "parameter": "Shock Intensity",
        "low_value": round(si_low, 2),
        "high_value": round(si_high, 2),
        "low_impact": round(impact_low, 2),
        "high_impact": round(impact_high, 2),
        "total_range": round(abs(impact_high - impact_low), 2),
    })
    
    # Vary recovery rate (±0.15 absolute)
    rr_low = max(0.05, request.base_recovery_rate - 0.15)
    rr_high = min(0.6, request.base_recovery_rate + 0.15)
    
    scen_low = ShockScenario(request.base_shock_intensity, request.base_shock_duration, rr_low).apply(baseline)
    peak_low = float(scen_low["Scenario_Unemployment"].max())
    impact_low = peak_low - base_peak
    
    scen_high = ShockScenario(request.base_shock_intensity, request.base_shock_duration, rr_high).apply(baseline)
    peak_high = float(scen_high["Scenario_Unemployment"].max())
    impact_high = peak_high - base_peak
    
    tornado_data.append({
        "parameter": "Recovery Rate",
        "low_value": round(rr_low, 2),
        "high_value": round(rr_high, 2),
        "low_impact": round(impact_low, 2),
        "high_impact": round(impact_high, 2),
        "total_range": round(abs(impact_high - impact_low), 2),
    })
    
    # Vary shock duration (±2 years, min 0)
    sd_low = max(0, request.base_shock_duration - 2)
    sd_high = min(5, request.base_shock_duration + 2)
    
    scen_low = ShockScenario(request.base_shock_intensity, sd_low, request.base_recovery_rate).apply(baseline)
    peak_low = float(scen_low["Scenario_Unemployment"].max())
    impact_low = peak_low - base_peak
    
    scen_high = ShockScenario(request.base_shock_intensity, sd_high, request.base_recovery_rate).apply(baseline)
    peak_high = float(scen_high["Scenario_Unemployment"].max())
    impact_high = peak_high - base_peak
    
    tornado_data.append({
        "parameter": "Shock Duration",
        "low_value": sd_low,
        "high_value": sd_high,
        "low_impact": round(impact_low, 2),
        "high_impact": round(impact_high, 2),
        "total_range": round(abs(impact_high - impact_low), 2),
    })
    
    # Sort by total range (most sensitive first)
    tornado_data.sort(key=lambda x: x["total_range"], reverse=True)
    
    # 2. HEATMAP DATA - Shock Intensity × Recovery Rate
    heatmap_data = []
    
    # Create grid
    intensity_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    recovery_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    
    for intensity in intensity_values:
        for recovery in recovery_values:
            scen = ShockScenario(intensity, request.base_shock_duration, recovery).apply(baseline)
            peak = float(scen["Scenario_Unemployment"].max())
            
            heatmap_data.append({
                "shock_intensity": round(intensity, 1),
                "recovery_rate": round(recovery, 1),
                "peak_unemployment": round(peak, 2),
            })
    
    # 3. SAFE ZONE ANALYSIS - Find parameter combinations that keep UE below threshold
    threshold = 8.0  # Target: Keep peak UE below 8%
    safe_combinations = []
    unsafe_combinations = []
    
    for intensity in [0.1, 0.2, 0.3, 0.4, 0.5]:
        for recovery in [0.2, 0.3, 0.4, 0.5, 0.6]:
            scen = ShockScenario(intensity, request.base_shock_duration, recovery).apply(baseline)
            peak = float(scen["Scenario_Unemployment"].max())
            
            combo = {
                "shock_intensity": round(intensity, 1),
                "recovery_rate": round(recovery, 1),
                "peak_unemployment": round(peak, 2),
                "is_safe": peak < threshold,
            }
            
            if peak < threshold:
                safe_combinations.append(combo)
            else:
                unsafe_combinations.append(combo)
    
    # Find critical thresholds
    critical_thresholds = []
    for intensity in [0.2, 0.3, 0.4, 0.5]:
        # Binary search for minimum recovery rate needed
        min_recovery = 0.05
        max_recovery = 0.6
        
        for _ in range(10):  # 10 iterations for precision
            mid_recovery = (min_recovery + max_recovery) / 2
            scen = ShockScenario(intensity, request.base_shock_duration, mid_recovery).apply(baseline)
            peak = float(scen["Scenario_Unemployment"].max())
            
            if peak > threshold:
                min_recovery = mid_recovery
            else:
                max_recovery = mid_recovery
        
        required_recovery = (min_recovery + max_recovery) / 2
        
        critical_thresholds.append({
            "shock_intensity": round(intensity, 1),
            "required_recovery_rate": round(required_recovery, 2),
            "description": f"For shock intensity {intensity:.1f}, need recovery rate ≥ {required_recovery:.2f} to stay below {threshold}%"
        })
    
    return {
        "base_peak": round(base_peak, 2),
        "tornado_data": tornado_data,
        "heatmap_data": heatmap_data,
        "safe_combinations": safe_combinations[:10],  # Top 10 safe
        "unsafe_combinations": unsafe_combinations[:10],  # Top 10 unsafe
        "critical_thresholds": critical_thresholds,
        "threshold": threshold,
    }


# -------- Data Source Status --------
@app.get("/data-status")
def data_status():
    label = get_data_source_label("India")
    return {"source": label, "country": "India"}
