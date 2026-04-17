"""
Page 1 — Overview Dashboard
Live KPIs, forecast trajectory with confidence bands, historical event overlays,
and an evidence-based forecast seeded from real World Bank historical data.
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, plotly_dark_layout, API_BASE_URL
from src.historical_events import get_events_in_range
from src.live_data import fetch_world_bank, fetch_gdp_growth, get_data_source_label
from src.forecasting import ForecastingEngine

st.set_page_config(page_title="Overview | UIP", page_icon="📊", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ─── Data fetching ─────────────────────────────────────────────────────────────
from src.api import simulate_scenario, ScenarioRequest

@st.cache_data(ttl=120)
def get_baseline(horizon: int):
    try:
        req = ScenarioRequest(
            shock_intensity=0.0,
            shock_duration=0,
            recovery_rate=0.0,
            forecast_horizon=horizon
        )
        return simulate_scenario(req)
    except Exception as e:
        st.error(f"Error fetching baseline: {e}")
    return None

# ─── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Overview Controls")
    horizon = st.slider("Forecast Horizon (years)", 3, 10, 6)
    show_events = st.checkbox("Show Historical Events", value=True)
    show_band = st.checkbox("Show Uncertainty Band", value=True)
    
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py", label="❓ Help Guide")
    st.page_link("pages/2_Simulator.py", label="🧪 Scenario Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py", label="🎯 Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="📡 Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py", label="🗺️ Geo Career")
    st.page_link("pages/10_Pricing.py", label="💰 Pricing")
    st.page_link("pages/11_For_Business.py", label="🏢 For Business")

# ─── Page hero ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <div class="hero-title">📊 Live Overview Dashboard</div>
    <div class="hero-subtitle">Real-time baseline forecast with uncertainty bands and historical event markers</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

data = get_baseline(horizon)

if not data:
    st.error("⚠️ Cannot connect to API. Start: `uvicorn src.api:app --reload`")
    st.stop()

baseline_df   = pd.DataFrame(data["baseline"])
conf_df       = pd.DataFrame(data.get("baseline_confidence", []))
indices       = data.get("indices", {})
data_src      = data.get("data_source", "🟡 Offline — Local CSV")
forecast_method = data.get("forecasting_method", "Time Series")

# ─── KPI Row ────────────────────────────────────────────────────────────────────
peak = round(baseline_df["Predicted_Unemployment"].max(), 2)
peak_year = int(baseline_df.loc[baseline_df["Predicted_Unemployment"].idxmax(), "Year"])
current = round(baseline_df["Predicted_Unemployment"].iloc[0], 2)
end_val = round(baseline_df["Predicted_Unemployment"].iloc[-1], 2)
ew = indices.get("early_warning", "🟢 Stable")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(render_kpi_card("📈", "Baseline Start", f"{current}%", delta_type="neutral"), unsafe_allow_html=True)
with col2:
    d = round(peak - current, 2)
    st.markdown(render_kpi_card("🎯", "Forecast Peak", f"{peak}%", f"▲ {d}pp · {peak_year}", "up"), unsafe_allow_html=True)
with col3:
    d6 = round(end_val - current, 2)
    dtype = "up" if d6 > 0 else "down"
    st.markdown(render_kpi_card("📉", f"{horizon}-Year Outlook", f"{end_val}%", f"{'▲' if d6>0 else '▼'} {abs(d6)}pp", dtype), unsafe_allow_html=True)
with col4:
    label = ew.split(" ", 1)[-1] if " " in ew else ew
    st.markdown(render_kpi_card("🚦", "Risk Status", label, delta_type="neutral"), unsafe_allow_html=True)
with col5:
    try:
        gdp_df = fetch_gdp_growth("India")
        if not gdp_df.empty:
            gdp_latest = round(float(gdp_df.iloc[-1]["Value"]), 2)
            gdp_yr = int(gdp_df.iloc[-1]["Year"])
            gdp_prev = round(float(gdp_df.iloc[-2]["Value"]), 2) if len(gdp_df) >= 2 else None
            gdp_delta = f"{'▲' if gdp_latest > (gdp_prev or 0) else '▼'} vs {gdp_prev}% prior yr" if gdp_prev else ""
            gdp_type = "down" if gdp_latest > 0 else "up"  # high GDP = good for jobs
            st.markdown(render_kpi_card("💹", f"GDP Growth ({gdp_yr})", f"{gdp_latest}%", gdp_delta, gdp_type), unsafe_allow_html=True)
        else:
            st.markdown(render_kpi_card("💹", "GDP Growth", "N/A", delta_type="neutral"), unsafe_allow_html=True)
    except Exception as e:
        st.markdown(render_kpi_card("💹", "GDP Growth", "N/A", delta_type="neutral"), unsafe_allow_html=True)

st.markdown(
    f'<div style="text-align:right; margin-bottom:0.5rem; font-size:0.85rem; color:#64748b;">{data_src} · Method: {forecast_method}</div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Chart ─────────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">📈 Unemployment Forecast Trajectory</div>', unsafe_allow_html=True)

# Show forecasting method info
method_color = "#10b981" if "Economic" in forecast_method else "#6366f1"
method_icon = "🔬" if "Economic" in forecast_method else "📊"

st.markdown(f"""
<div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
            border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8; margin-bottom:1rem;">
    {method_icon} <strong style="color:{method_color};">Forecasting Method:</strong>
    <strong style="color:#e2e8f0;">{forecast_method}</strong>
    {'— based on historical unemployment trends and patterns' if 'Time Series' in forecast_method else '— statistical analysis of unemployment data'}
</div>
""", unsafe_allow_html=True)

years  = baseline_df["Year"].tolist()
values = baseline_df["Predicted_Unemployment"].tolist()

fig = go.Figure()

# Real Monte Carlo confidence bands from API
if show_band and not conf_df.empty and "Lower_95" in conf_df.columns:
    c_years = conf_df["Year"].tolist()
    fig.add_trace(go.Scatter(
        x=c_years + c_years[::-1],
        y=conf_df["Upper_95"].tolist() + conf_df["Lower_95"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(99,102,241,0.06)",
        line=dict(color="rgba(0,0,0,0)"),
        name="95% CI (Monte Carlo)",
        hoverinfo="skip",
        showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=c_years + c_years[::-1],
        y=conf_df["Upper_80"].tolist() + conf_df["Lower_80"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(99,102,241,0.13)",
        line=dict(color="rgba(0,0,0,0)"),
        name="80% CI (Monte Carlo)",
        hoverinfo="skip",
        showlegend=True,
    ))

fig.add_trace(go.Scatter(
    x=years, y=values,
    mode="lines+markers",
    name="Baseline Forecast",
    line=dict(color="#6366f1", width=3.5),
    marker=dict(size=7, color="#818cf8", line=dict(color="#6366f1", width=2)),
    hovertemplate="<b>Year %{x}</b><br>Unemployment: %{y:.2f}%<extra></extra>",
))

# Historical events overlay — loaded from curated events module
if show_events:
    events = get_events_in_range(min(years), max(years))
    for ev in events:
        year  = ev["year"]
        color = ev.get("color", "#f59e0b")
        fig.add_vline(
            x=year,
            line=dict(color=color.replace(")", ",0.35)").replace("rgb", "rgba"), width=1.5, dash="dot"),
        )
        fig.add_annotation(
            x=year, y=max(values) * 0.95, text=ev["short"],
            showarrow=False, font=dict(size=9, color=color),
            bgcolor="rgba(0,0,0,0.35)", bordercolor=color + "55",
            borderwidth=1, borderpad=3,
        )

fig.update_layout(**plotly_dark_layout(height=420))
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Unemployment Rate (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─── GDP Growth vs Unemployment Chart ─────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">💹 GDP Growth vs Unemployment Rate — India</div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.85rem; color:#64748b; margin-bottom:1rem;">
    The inverse relationship between GDP growth and unemployment (Okun's Law) —
    when the economy grows faster, unemployment tends to fall.
</div>
""", unsafe_allow_html=True)

try:
    gdp_df_chart = fetch_gdp_growth("India")
    wb_hist = fetch_world_bank("India")
except Exception as e:
    gdp_df_chart = pd.DataFrame()
    wb_hist = pd.DataFrame()

if not gdp_df_chart.empty and not wb_hist.empty:
    merged = pd.merge(
        wb_hist.rename(columns={"Unemployment_Rate": "UE"}),
        gdp_df_chart.rename(columns={"Value": "GDP_Growth"}),
        on="Year", how="inner"
    ).sort_values("Year")

    fig_gdp = go.Figure()

    # Historical GDP Growth
    fig_gdp.add_trace(go.Scatter(
        x=merged["Year"], y=merged["GDP_Growth"],
        mode="lines+markers",
        name="GDP Growth (%) - Historical",
        line=dict(color="#10b981", width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>GDP Growth: %{y:.2f}%<extra></extra>",
        yaxis="y1",
    ))

    # Historical Unemployment
    fig_gdp.add_trace(go.Scatter(
        x=merged["Year"], y=merged["UE"],
        mode="lines+markers",
        name="Unemployment (%) - Historical",
        line=dict(color="#f43f5e", width=2.5, dash="dot"),
        marker=dict(size=5, symbol="diamond"),
        hovertemplate="<b>%{x}</b><br>Unemployment: %{y:.2f}%<extra></extra>",
        yaxis="y2",
    ))

    # Add economic forecast if available
    if "Time Series" in forecast_method:
        try:
            # Skip economic forecasting - use time series only
            pass
            
        except Exception as e:
            # Continue with historical data only
            pass

    # Shade COVID shock
    fig_gdp.add_vrect(
        x0=2019.5, x1=2021.5,
        fillcolor="rgba(239,68,68,0.07)",
        line_width=0,
        annotation_text="COVID-19",
        annotation_position="top left",
        annotation_font=dict(color="#f87171", size=10),
    )

    layout = plotly_dark_layout(height=380)
    layout.update(
        yaxis=dict(title="GDP Growth (%)", color="#10b981",
                   gridcolor="rgba(255,255,255,0.04)"),
        yaxis2=dict(title="Unemployment (%)", color="#f43f5e",
                    overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
        xaxis_title="Year",
    )
    fig_gdp.update_layout(**layout)
    st.plotly_chart(fig_gdp, use_container_width=True)

    # Economic relationship analysis
    corr = merged["GDP_Growth"].corr(merged["UE"])
    direction = "inverse" if corr < 0 else "positive"
    
    # Calculate Okun coefficient if time series model is being used
    okun_info = ""
    if "Time Series" in forecast_method:
        # No economic modeling - just show correlation
        pass
    
    # Show data quality info based on source
    data_source_info = get_data_source_label("India")
    if "Realistic Data" in data_source_info:
        quality_color = "#10b981"
        quality_icon = "✅"
        quality_msg = "Using curated realistic unemployment data that reflects actual India economic conditions including proper COVID impact (23.5% peak in 2020) and gradual recovery."
    else:
        quality_color = "#f59e0b"
        quality_icon = "⚠️"
        quality_msg = "World Bank unemployment data for India shows questionable trends post-2019: COVID impact appears understated and 2022-2025 rates seem unrealistically low."
    
    st.markdown(f"""
    <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.2);
                border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8; margin-bottom:1rem;">
        {quality_icon} <strong style="color:{quality_color};">Data Quality:</strong>
        {quality_msg}
    </div>
    """, unsafe_allow_html=True)
    
# ── Forward-Looking Recession Risk Indicator ───────────────────────────────────

st.markdown('<div class="section-title">🚨 Forward-Looking Recession Risk Indicator</div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.85rem; color:#64748b; margin-bottom:1rem; line-height:1.6;">
    A <strong style="color:#e2e8f0;">forward-looking</strong> composite built from five independent
    leading signals — Sahm Rule, GDP momentum, output gap, 2-year forecast trajectory, and
    Okun's Law consistency — calibrated for India's economic structure.
    Each signal independently detects deteriorating conditions <em>before</em> a recession is confirmed.
</div>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_forward_recession_risk():
    """
    Forward-looking recession risk indicator for India.
    Five independent leading signals, each scored 0-100, then weighted into a composite.

    Signal 1 — Sahm Rule (adapted for annual data)
        Classic NBER early-warning: recession flags when UE rises ≥0.5pp above recent trough.
        Adapted here for annual data (India); threshold calibrated at 0.4pp (annual series
        are smoother than monthly, so a lower delta is equally informative).

    Signal 2 — GDP Growth Momentum (2nd derivative)
        Not just whether GDP is low, but whether it is *decelerating*.
        Rapid deceleration (falling >1.5pp/yr) historically precedes recessions.

    Signal 3 — Output Gap vs Potential (6.5%)
        India's consensus potential growth is ~6-7%. GDP growing well below potential
        signals excess slack and rising recession risk.

    Signal 4 — 2-Year UE Forecast Trajectory
        Uses the in-app ForecastingEngine (ensemble) to check whether unemployment
        is statistically projected to rise over the next two years — a genuine
        forward-looking signal.

    Signal 5 — Okun's Law Consistency Check
        Okun's Law: GDP growth and unemployment move in opposite directions.
        Violation (both rising, or GDP high but UE also high) flags structural stress.
    """
    gdp_df = fetch_gdp_growth("India")
    ue_df  = fetch_world_bank("India")

    if gdp_df.empty or ue_df.empty or len(gdp_df) < 4 or len(ue_df) < 4:
        return None, "Insufficient historical data (need ≥4 years)"

    gdp_sorted = gdp_df.sort_values("Year").reset_index(drop=True)
    ue_sorted  = ue_df.sort_values("Year").reset_index(drop=True)
    gdp_vals   = gdp_sorted["Value"].values
    ue_vals    = ue_sorted["Unemployment_Rate"].values

    signals = {}

    # ── Signal 1: Adapted Sahm Rule ────────────────────────────────────────────
    # Original Sahm: 3-month UE avg rises ≥0.5pp above prior 12-month minimum.
    # Annual adaptation: current UE vs minimum of the last 4 years.
    recent_trough = float(ue_vals[-4:].min())
    current_ue    = float(ue_vals[-1])
    sahm_delta    = current_ue - recent_trough

    if sahm_delta >= 1.0:
        sahm_score, sahm_sig = 95, "🔴 Triggered (≥1.0pp rise)"
    elif sahm_delta >= 0.4:
        sahm_score, sahm_sig = 65, "🟡 Warning (≥0.4pp rise)"
    elif sahm_delta >= 0.15:
        sahm_score, sahm_sig = 30, "🟡 Watch (edging up)"
    else:
        sahm_score, sahm_sig = 8, "🟢 Clear"

    signals["Sahm Rule (UE Rise from Trough)"] = {
        "score": sahm_score,
        "signal": sahm_sig,
        "detail": f"UE {sahm_delta:+.2f}pp above {recent_trough:.1f}% trough (threshold: 0.4pp)",
        "weight": 0.30,
    }

    # ── Signal 2: GDP Growth Momentum (2nd derivative) ─────────────────────────
    # Rate of change of the growth rate — deceleration is the leading signal,
    # not the level. We take the 2-year average momentum to reduce noise.
    if len(gdp_vals) >= 4:
        mom_1 = float(gdp_vals[-1] - gdp_vals[-2])   # latest year-on-year change
        mom_2 = float(gdp_vals[-2] - gdp_vals[-3])   # prior year-on-year change
        momentum = (mom_1 + mom_2) / 2.0              # 2-year average momentum

        if momentum < -2.0:
            mom_score, mom_sig = 92, "🔴 Sharp Deceleration (>2pp/yr)"
        elif momentum < -0.8:
            mom_score, mom_sig = 62, "🟡 Decelerating (0.8–2pp/yr)"
        elif momentum < -0.2:
            mom_score, mom_sig = 30, "🟡 Mild Slowdown"
        else:
            mom_score, mom_sig = 6, "🟢 Stable / Accelerating"

        signals["GDP Momentum (2nd Derivative)"] = {
            "score": mom_score,
            "signal": mom_sig,
            "detail": f"Avg 2-yr GDP momentum: {momentum:+.2f}pp/yr",
            "weight": 0.25,
        }

    # ── Signal 3: Potential Output Gap ─────────────────────────────────────────
    # India's consensus potential growth ≈ 6.5% (IMF / RBI estimates).
    # Large negative gap = output running well below capacity = recession risk.
    INDIA_POTENTIAL = 6.5
    gdp_latest = float(gdp_vals[-1])
    gap = gdp_latest - INDIA_POTENTIAL     # negative → below potential

    if gap < -3.5:
        gap_score, gap_sig = 90, "🔴 Large Negative Gap (>3.5pp below)"
    elif gap < -2.0:
        gap_score, gap_sig = 60, "🟡 Below Potential (2–3.5pp)"
    elif gap < -0.5:
        gap_score, gap_sig = 28, "🟡 Marginally Below Potential"
    else:
        gap_score, gap_sig = 5, "🟢 At / Above Potential"

    signals["Output Gap (Potential ≈ 6.5%)"] = {
        "score": gap_score,
        "signal": gap_sig,
        "detail": f"GDP at {gdp_latest:.1f}% vs potential {INDIA_POTENTIAL}% (gap: {gap:+.1f}pp)",
        "weight": 0.20,
    }

    # ── Signal 4: 2-Year UE Forecast Trajectory ────────────────────────────────
    # Run the ensemble forecasting engine; if UE is projected to rise
    # over the next 2 years that is a genuine forward-looking warning.
    try:
        engine = ForecastingEngine(forecast_horizon=3, method="ensemble")
        fc = engine.forecast_with_confidence(ue_sorted)
        if fc is not None and len(fc) >= 2:
            fc_2yr    = float(fc["Predicted_Unemployment"].iloc[1])
            fc_delta  = fc_2yr - current_ue

            if fc_delta > 1.2:
                traj_score, traj_sig = 90, "🔴 Rising Sharply (+>1.2pp forecast)"
            elif fc_delta > 0.5:
                traj_score, traj_sig = 62, "🟡 Rising (+0.5–1.2pp forecast)"
            elif fc_delta > 0.15:
                traj_score, traj_sig = 32, "🟡 Edging Up"
            else:
                traj_score, traj_sig = 8, "🟢 Stable / Falling"

            signals["2-Year UE Forecast (Ensemble)"] = {
                "score": traj_score,
                "signal": traj_sig,
                "detail": (
                    f"UE projected at {fc_2yr:.1f}% in 2 yrs "
                    f"({fc_delta:+.2f}pp from current {current_ue:.1f}%)"
                ),
                "weight": 0.15,
            }
    except Exception:
        pass   # forecast unavailable → signal omitted, weights renormalise

    # ── Signal 5: Okun's Law Consistency Check ─────────────────────────────────
    # Okun's Law: when GDP grows robustly, unemployment should fall.
    # A violation (both moving the wrong way, or GDP well above potential
    # while UE is also elevated) flags structural fragility.
    if len(gdp_vals) >= 2 and len(ue_vals) >= 2:
        gdp_chg = float(gdp_vals[-1] - gdp_vals[-2])
        ue_chg  = float(ue_vals[-1]  - ue_vals[-2])

        # Hard violation: growth collapsing AND UE rising
        # Soft violation: GDP merely slowing while UE also rises
        if gdp_chg < 1.5 and ue_chg > 0.25:
            okun_score, okun_sig = 85, "🔴 Okun Violation (growth & UE diverging)"
            okun_detail = (
                f"GDP Δ {gdp_chg:+.1f}pp — UE Δ {ue_chg:+.2f}pp: "
                "labour market not responding to growth"
            )
        elif gdp_chg < 4.0 and ue_chg > 0.0:
            okun_score, okun_sig = 45, "🟡 Weak Okun Relationship"
            okun_detail = (
                f"GDP slowing ({gdp_chg:+.1f}pp) while UE also rising ({ue_chg:+.2f}pp)"
            )
        else:
            okun_score, okun_sig = 8, "🟢 Normal (GDP ↑ → UE ↓)"
            okun_detail = "GDP and unemployment moving in expected opposing directions"

        signals["Okun's Law Consistency"] = {
            "score": okun_score,
            "signal": okun_sig,
            "detail": okun_detail,
            "weight": 0.10,
        }

    # ── Weighted composite ──────────────────────────────────────────────────────
    total_w   = sum(s["weight"] for s in signals.values())
    composite = (
        sum(s["score"] * s["weight"] for s in signals.values()) / total_w
        if total_w > 0 else 0
    )
    composite = min(round(composite, 1), 100)

    if composite >= 65:
        label   = "🔴 High Risk"
        color   = "#ef4444"
        outlook = (
            "Multiple leading indicators are flashing red. "
            "Elevated probability of economic contraction within 12 months."
        )
    elif composite >= 40:
        label   = "🟡 Moderate Risk"
        color   = "#f59e0b"
        outlook = (
            "Several forward-looking signals are weakening. "
            "Monitor closely — conditions could deteriorate."
        )
    elif composite >= 20:
        label   = "🟡 Low-Moderate Risk"
        color   = "#84cc16"
        outlook = (
            "Economy is showing resilience but one or two signals warrant caution."
        )
    else:
        label   = "🟢 Low Risk"
        color   = "#10b981"
        outlook = (
            "Leading indicators broadly positive. "
            "Continued expansion is the base-case scenario."
        )

    return {
        "score":   composite,
        "label":   label,
        "color":   color,
        "outlook": outlook,
        "signals": signals,
    }, None


risk_data, risk_err = compute_forward_recession_risk()

if risk_err:
    st.info(f"Recession risk indicator unavailable: {risk_err}")
else:
    # ── Layout: gauge left | signal cards right ─────────────────────────────
    col_gauge, col_signals = st.columns([1, 2])

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_data["score"],
            title={"text": "Composite Risk Score", "font": {"color": "#e2e8f0", "size": 14}},
            number={"suffix": " / 100", "font": {"color": "#e2e8f0", "size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b",
                          "tickvals": [0, 20, 40, 65, 100],
                          "ticktext": ["0", "20", "40", "65", "100"]},
                "bar":  {"color": risk_data["color"]},
                "bgcolor":     "rgba(0,0,0,0.2)",
                "borderwidth": 2,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0,  20], "color": "rgba(16,185,129,0.18)"},
                    {"range": [20, 40], "color": "rgba(132,204,22,0.15)"},
                    {"range": [40, 65], "color": "rgba(245,158,11,0.15)"},
                    {"range": [65,100], "color": "rgba(239,68,68,0.15)"},
                ],
                "threshold": {
                    "line": {"color": risk_data["color"], "width": 4},
                    "thickness": 0.75,
                    "value": risk_data["score"],
                },
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#e2e8f0"},
            height=300,
            margin=dict(l=20, r=20, t=50, b=10),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown(f"""
        <div style="text-align:center; font-size:1.15rem; font-weight:700;
                    color:{risk_data['color']}; margin-top:-0.5rem;">
            {risk_data['label']}
        </div>
        <div style="text-align:center; font-size:0.8rem; color:#64748b;
                    margin-top:0.5rem; line-height:1.5; padding:0 0.5rem;">
            {risk_data['outlook']}
        </div>
        """, unsafe_allow_html=True)

    with col_signals:
        st.markdown(
            '<div style="font-size:0.87rem; font-weight:700; color:#94a3b8; '
            'margin-bottom:0.7rem; text-transform:uppercase; letter-spacing:1px;">'
            '⚡ Leading Signal Dashboard</div>',
            unsafe_allow_html=True,
        )

        def _signal_color(score):
            if score >= 65:
                return "rgba(239,68,68,0.10)", "rgba(239,68,68,0.35)"
            elif score >= 38:
                return "rgba(245,158,11,0.10)", "rgba(245,158,11,0.35)"
            else:
                return "rgba(16,185,129,0.10)", "rgba(16,185,129,0.30)"

        for sig_name, sig_info in risk_data["signals"].items():
            bg, border = _signal_color(sig_info["score"])
            weight_pct  = int(sig_info["weight"] * 100)
            score_bar_w = int(sig_info["score"])
            if sig_info["score"] >= 65:
                bar_col = "#ef4444"
            elif sig_info["score"] >= 38:
                bar_col = "#f59e0b"
            else:
                bar_col = "#10b981"

            st.markdown(f"""
            <div style="background:{bg}; border:1px solid {border}; border-radius:12px;
                        padding:0.8rem 1.1rem; margin-bottom:0.65rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.84rem; font-weight:700; color:#e2e8f0;">
                        {sig_name}
                    </span>
                    <span style="font-size:0.78rem; color:#64748b; white-space:nowrap; margin-left:0.5rem;">
                        weight: {weight_pct}%
                    </span>
                </div>
                <div style="display:flex; align-items:center; gap:0.7rem; margin-top:0.4rem;">
                    <span style="font-size:0.83rem; color:#cbd5e1; min-width:230px;">
                        {sig_info['signal']}
                    </span>
                    <div style="flex:1; background:rgba(255,255,255,0.06); border-radius:999px; height:6px;">
                        <div style="width:{score_bar_w}%; background:{bar_col};
                                    border-radius:999px; height:6px;"></div>
                    </div>
                    <span style="font-size:0.78rem; color:#64748b; white-space:nowrap;">
                        {int(sig_info['score'])}/100
                    </span>
                </div>
                <div style="font-size:0.78rem; color:#64748b; margin-top:0.35rem; line-height:1.45;">
                    {sig_info['detail']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Methodology note ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.18);
                border-radius:12px; padding:1rem 1.4rem; font-size:0.82rem; color:#64748b; line-height:1.7;">
        <strong style="color:#818cf8;">Methodology — 5 Leading Signals (India-calibrated):</strong>
        <ul style="margin:0.5rem 0 0; padding-left:1.2rem; color:#94a3b8;">
            <li><strong style="color:#e2e8f0;">Sahm Rule (30%)</strong> — Flags when unemployment rises ≥0.4pp above its 4-year trough (annual adaptation of Claudia Sahm's NBER indicator).</li>
            <li><strong style="color:#e2e8f0;">GDP Momentum (25%)</strong> — 2nd derivative of GDP growth — rapid deceleration historically leads recessions by 2–4 quarters.</li>
            <li><strong style="color:#e2e8f0;">Output Gap (20%)</strong> — Difference between actual and potential GDP growth (~6.5% for India per IMF/RBI estimates). Large negative gap = excess slack.</li>
            <li><strong style="color:#e2e8f0;">2-Year UE Forecast (15%)</strong> — Ensemble time-series projection of unemployment trajectory. A rising forecast is a genuine forward-looking signal.</li>
            <li><strong style="color:#e2e8f0;">Okun's Law (10%)</strong> — Checks GDP–unemployment consistency. Violations (UE rising despite GDP growth) flag structural deterioration.</li>
        </ul>
        <div style="margin-top:0.6rem;">
            Score 0–20 = Low Risk &nbsp;|&nbsp; 20–40 = Low-Moderate &nbsp;|&nbsp;
            40–65 = Moderate &nbsp;|&nbsp; 65–100 = High Risk.
            This is a <strong style="color:#94a3b8;">leading early-warning tool</strong>, not a recession prediction.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Metrics + Table ──────────────────────────────────────────────────────────
col_l, col_r = st.columns([1, 1])

with col_l:
    
    st.markdown('<div class="section-title">📋 Scenario Indices</div>', unsafe_allow_html=True)
    idx_rows = [
        ("Unemployment Stress Index", indices.get("unemployment_stress_index", "N/A")),
        ("Recovery Quality Index", indices.get("rqi_label", "N/A")),
        ("Policy Cushion Score", indices.get("policy_cushion_score", "N/A")),
        ("Peak Delta (pp)", indices.get("peak_delta", "N/A")),
        ("Early Warning", indices.get("early_warning", "N/A")),
    ]
    for label, val in idx_rows:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:0.6rem 0; border-bottom:1px solid rgba(255,255,255,0.05);">
            <span style="color:#94a3b8; font-size:0.88rem;">{label}</span>
            <span style="color:#e2e8f0; font-weight:700; font-size:0.88rem;">{val}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_r:
    
    st.markdown('<div class="section-title">📊 Forecast Data Table</div>', unsafe_allow_html=True)
    display_df = baseline_df[["Year", "Predicted_Unemployment"]].rename(
        columns={"Predicted_Unemployment": "Unemployment Rate (%)"}
    ).round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=260)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Evidence-Based Real-Data Forecast ─────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-title">🔮 Real-Data Forecast</div>',
            unsafe_allow_html=True)


@st.cache_data(ttl=86400, show_spinner=False)
def get_real_forecast(fc_horizon: int):
    wb_df = fetch_world_bank("India")

    if wb_df.empty:
        return None, None, "No unemployment data"

    wb_df = wb_df.sort_values("Year").tail(35).copy()
    wb_df["Unemployment_Smoothed"] = (
        wb_df["Unemployment_Rate"]
        .rolling(3, min_periods=1, center=True)
        .mean()
        .round(4)
    )

    try:
        engine = ForecastingEngine(forecast_horizon=fc_horizon, method="ensemble")
        fc_df = engine.forecast_with_confidence(wb_df)
        return wb_df, fc_df, "Time Series (Ensemble)"
    except Exception as e:
        return None, None, f"Forecasting error: {e}"

fc_horizon_real = st.slider("Forecast horizon (real-data)", 3, 8, 5, key="real_fc_horizon")

with st.spinner("Running evidence-based forecast on real World Bank data…"):
    hist_df, fc_df_real, forecast_method_used = get_real_forecast(fc_horizon_real)

if hist_df is None or fc_df_real is None:
    st.warning("Could not fetch World Bank data. Check connectivity.")
else:
    # Show forecasting method used
    st.markdown(f"""
    <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.25);
                border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8; margin-bottom:1rem;">
        🔬 <strong style="color:#10b981;">Forecasting Method:</strong>
        {forecast_method_used}
        {'— pure time-series analysis of historical patterns' if 'Time Series' in forecast_method_used else '— statistical forecasting approach'}
    </div>
    """, unsafe_allow_html=True)

    # ── Auto-generate forecast insights from data
    def _gen_forecast_insights(hist_df, fc_df):
        insights = []
        try:
            last_actual = round(float(hist_df["Unemployment_Rate"].iloc[-1]), 2)
            last_yr     = int(hist_df["Year"].iloc[-1])
            fc_end      = round(float(fc_df["Predicted_Unemployment"].iloc[-1]), 2)
            fc_end_yr   = int(fc_df["Year"].iloc[-1])
            direction   = "rise" if fc_end > last_actual else "fall"
            delta       = abs(round(fc_end - last_actual, 2))
            insights.append(
                f"**Starting point:** Unemployment is at **{last_actual}%** ({last_yr}) "
                f"and is projected to **{direction} by {delta} pp** to {fc_end}% by {fc_end_yr}."
            )
            peak_val = round(float(fc_df["Predicted_Unemployment"].max()), 2)
            peak_yr  = int(fc_df.loc[fc_df["Predicted_Unemployment"].idxmax(), "Year"])
            if peak_yr != fc_end_yr:
                insights.append(f"**Peak forecast:** The model projects a peak of **{peak_val}%** in {peak_yr} before declining.")
            upper_80  = round(float(fc_df["Upper_80"].iloc[-1]), 2)
            lower_80  = round(float(fc_df["Lower_80"].iloc[-1]), 2)
            insights.append(
                f"**Uncertainty range:** 80% confidence band for {fc_end_yr} spans **{lower_80}% – {upper_80}%**, "
                "reflecting structural uncertainty in India's informal-sector economy."
            )
        except Exception:
            pass
        return insights

    fc_insights = _gen_forecast_insights(hist_df, fc_df_real)
    if fc_insights:
        bullets_html = "".join(
            f'<li style="margin-bottom:0.45rem; color:#cbd5e1; font-size:0.9rem; line-height:1.6;">'
            + s.replace("**", "<strong style='color:#e2e8f0;'>", 1).replace("**", "</strong>", 1)
            + "</li>"
            for s in fc_insights
        )
        st.markdown(f"""
        <div style="background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.25);
                    border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.4rem;">
            <div style="display:flex; gap:0.6rem; align-items:center; margin-bottom:0.6rem;">
                <span style="font-size:1.1rem;">💡</span>
                <span style="font-size:0.78rem; font-weight:700; color:#f59e0b;
                              text-transform:uppercase; letter-spacing:1px;">
                    Forecast Insights
                </span>
            </div>
            <ul style="margin:0; padding-left:1.2rem;">{bullets_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    # ── Combined historical + forecast chart
    fig_real = go.Figure()

    # Historical actual data
    fig_real.add_trace(go.Scatter(
        x=hist_df["Year"],
        y=hist_df["Unemployment_Rate"],
        mode="lines+markers",
        name="Historical (World Bank)",
        line=dict(color="#10b981", width=2.5),
        marker=dict(size=5, color="#10b981"),
        hovertemplate="<b>%{x}</b><br>Actual: %{y:.2f}%<extra></extra>",
    ))

    # 80% confidence band
    fc_years  = fc_df_real["Year"].tolist()
    fig_real.add_trace(go.Scatter(
        x=fc_years + fc_years[::-1],
        y=fc_df_real["Upper_80"].tolist() + fc_df_real["Lower_80"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(99,102,241,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="80% Confidence Band",
        hoverinfo="skip",
    ))

    # 95% confidence band
    fig_real.add_trace(go.Scatter(
        x=fc_years + fc_years[::-1],
        y=fc_df_real["Upper_95"].tolist() + fc_df_real["Lower_95"].tolist()[::-1],
        fill="toself",
        fillcolor="rgba(99,102,241,0.05)",
        line=dict(color="rgba(0,0,0,0)"),
        name="95% Confidence Band",
        hoverinfo="skip",
    ))

    # Forecast central estimate
    fig_real.add_trace(go.Scatter(
        x=fc_df_real["Year"],
        y=fc_df_real["Predicted_Unemployment"],
        mode="lines+markers",
        name="Ensemble Forecast",
        line=dict(color="#6366f1", width=3, dash="dot"),
        marker=dict(size=7, color="#818cf8", symbol="diamond"),
        hovertemplate="<b>%{x} (forecast)</b><br>Central: %{y:.2f}%<extra></extra>",
    ))

    # Divider line at the forecast start
    last_hist_yr = int(hist_df["Year"].iloc[-1])
    fig_real.add_vline(
        x=last_hist_yr + 0.5,
        line=dict(color="rgba(148,163,184,0.4)", width=1.5, dash="dash"),
    )
    fig_real.add_annotation(
        x=last_hist_yr + 0.5,
        y=hist_df["Unemployment_Rate"].max() * 0.96,
        text="← History | Forecast →",
        showarrow=False,
        font=dict(size=10, color="#64748b"),
        bgcolor="rgba(0,0,0,0.4)",
        borderpad=4,
    )

    fig_real.update_layout(**plotly_dark_layout(height=440))
    fig_real.update_layout(
        xaxis_title="Year",
        yaxis_title="Unemployment Rate (%)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1"),
        ),
    )
    st.plotly_chart(fig_real, use_container_width=True)

    # ── Side-by-side: forecast table + method explanation
    col_fc1, col_fc2 = st.columns([1, 1])
    with col_fc1:
        st.markdown("**Forecast values**")
        fc_display = fc_df_real[["Year", "Predicted_Unemployment", "Lower_80", "Upper_80"]].round(2)
        fc_display.columns = ["Year", "Central (%)", "Lower 80% (%)", "Upper 80% (%)"]
        st.dataframe(fc_display, use_container_width=True, hide_index=True)
        st.caption("Ensemble forecast with Monte Carlo confidence bands, trained on World Bank data.")

    with col_fc2:
        st.markdown("**How this forecast works**")
        st.markdown("""
        <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.18);
                    border-radius:12px; padding:1rem; font-size:0.85rem; color:#94a3b8; line-height:1.7;">
            <strong style="color:#818cf8;">Ensemble method</strong> combines three time-series models:
            <ul style="margin:0.5rem 0 0; padding-left:1.2rem; color:#cbd5e1;">
                <li><strong>Linear Trend</strong> — captures long-run trajectory</li>
                <li><strong>Exponential Smoothing</strong> — weights recent data higher</li>
                <li><strong>Moving Average</strong> — smooths short-term noise</li>
            </ul>
            <div style="margin-top:0.7rem;">
                Confidence bands are generated via <strong style="color:#818cf8;">Monte Carlo simulation</strong>
                (1,000 paths) seeded from historical variance.
            </div>
        </div>
        """, unsafe_allow_html=True)


    st.caption(
        "Note: This forecast reflects historical trends — it does not incorporate policy changes, "
        "shocks, or structural breaks not already present in the data. Use the Simulator page "
        "to layer shocks on top of this baseline."
    )

st.markdown("</div>", unsafe_allow_html=True)
