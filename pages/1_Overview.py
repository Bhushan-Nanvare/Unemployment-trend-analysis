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
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, render_data_source, plotly_dark_layout, API_BASE_URL
from src.historical_events import get_events_in_range
from src.live_data import fetch_world_bank, fetch_gdp_growth
from src.forecasting import ForecastingEngine
from src.live_insights import generate_forecast_insights

@st.cache_data(ttl=86400, show_spinner=False)
def get_gdp_growth():
    return fetch_gdp_growth("India")

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
        print(f"Error calling simulate_scenario: {e}")
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
    st.page_link("pages/2_Simulator.py", label="🧪 Scenario Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")

    st.page_link("pages/7_Job_Risk_Predictor.py", label="🎯 Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="📡 Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py", label="🗺️ Geo Career")
    st.page_link("pages/10_Skill_Obsolescence.py", label="⚡ Skill Obsolescence")

# ─── Page hero ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <div class="hero-title">📊 Live Overview Dashboard</div>
    <div class="hero-subtitle">Real-time baseline forecast with uncertainty bands and historical event markers</div>
</div>""", unsafe_allow_html=True)

data = get_baseline(horizon)

if not data:
    st.error("⚠️ Cannot connect to API. Start: `uvicorn src.api:app --reload`")
    st.stop()

baseline_df   = pd.DataFrame(data["baseline"])
conf_df       = pd.DataFrame(data.get("baseline_confidence", []))
indices       = data.get("indices", {})
data_src      = data.get("data_source", "🟡 Offline — Local CSV")

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
    gdp_df = get_gdp_growth()
    if not gdp_df.empty:
        gdp_latest = round(float(gdp_df.iloc[-1]["Value"]), 2)
        gdp_yr = int(gdp_df.iloc[-1]["Year"])
        gdp_prev = round(float(gdp_df.iloc[-2]["Value"]), 2) if len(gdp_df) >= 2 else None
        gdp_delta = f"{'▲' if gdp_latest > (gdp_prev or 0) else '▼'} vs {gdp_prev}% prior yr" if gdp_prev else ""
        gdp_type = "down" if gdp_latest > 0 else "up"  # high GDP = good for jobs
        st.markdown(render_kpi_card("💹", f"GDP Growth ({gdp_yr})", f"{gdp_latest}%", gdp_delta, gdp_type), unsafe_allow_html=True)
    else:
        st.markdown(render_kpi_card("💹", "GDP Growth", "N/A", delta_type="neutral"), unsafe_allow_html=True)

st.markdown(
    f'<div style="text-align:right; margin-bottom:0.5rem;">{render_data_source(data_src)}</div>',
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Chart ─────────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">📈 Unemployment Forecast Trajectory</div>', unsafe_allow_html=True)

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

gdp_df_chart = get_gdp_growth()
wb_hist = fetch_world_bank("India")

if not gdp_df_chart.empty and not wb_hist.empty:
    merged = pd.merge(
        wb_hist.rename(columns={"Unemployment_Rate": "UE"}),
        gdp_df_chart.rename(columns={"Value": "GDP_Growth"}),
        on="Year", how="inner"
    ).sort_values("Year")

    fig_gdp = go.Figure()

    fig_gdp.add_trace(go.Scatter(
        x=merged["Year"], y=merged["GDP_Growth"],
        mode="lines+markers",
        name="GDP Growth (%)",
        line=dict(color="#10b981", width=2.5),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b><br>GDP Growth: %{y:.2f}%<extra></extra>",
        yaxis="y1",
    ))

    fig_gdp.add_trace(go.Scatter(
        x=merged["Year"], y=merged["UE"],
        mode="lines+markers",
        name="Unemployment Rate (%)",
        line=dict(color="#f43f5e", width=2.5, dash="dot"),
        marker=dict(size=5, symbol="diamond"),
        hovertemplate="<b>%{x}</b><br>Unemployment: %{y:.2f}%<extra></extra>",
        yaxis="y2",
    ))

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

    # Correlation insight
    corr = merged["GDP_Growth"].corr(merged["UE"])
    direction = "inverse" if corr < 0 else "positive"
    st.markdown(f"""
    <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.2);
                border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8;">
        📐 <strong style="color:#10b981;">Okun's Law check:</strong>
        Correlation between GDP growth and unemployment = <strong style="color:#e2e8f0;">{corr:.2f}</strong>
        — a {direction} relationship
        {'(as expected — higher growth → lower unemployment)' if corr < 0 else '(weaker than expected for India due to informal sector)'}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("GDP growth data unavailable — check World Bank API connectivity.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Recession Risk Indicator ───────────────────────────────────────────────────

st.markdown('<div class="section-title">🚨 Recession Risk Indicator</div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.85rem; color:#64748b; margin-bottom:1rem; line-height:1.6;">
    A composite risk score based on <strong style="color:#e2e8f0;">GDP growth deceleration</strong>,
    <strong style="color:#e2e8f0;">unemployment trend</strong>, and
    <strong style="color:#e2e8f0;">forecast trajectory</strong>.
    Industry-standard early warning signal for economic downturns.
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400, show_spinner=False)
def compute_recession_risk():
    gdp_df = fetch_gdp_growth("India")
    ue_df = fetch_world_bank("India")
    
    if gdp_df.empty or ue_df.empty or len(gdp_df) < 3 or len(ue_df) < 3:
        return None, "Insufficient data"
    
    # GDP growth deceleration (last 3 years)
    gdp_recent = gdp_df.tail(3)
    gdp_trend = (gdp_recent.iloc[-1]["Value"] - gdp_recent.iloc[0]["Value"]) / 2
    gdp_latest = gdp_recent.iloc[-1]["Value"]
    
    # Unemployment trend (last 3 years)
    ue_recent = ue_df.tail(3)
    ue_trend = (ue_recent.iloc[-1]["Unemployment_Rate"] - ue_recent.iloc[0]["Unemployment_Rate"]) / 2
    ue_latest = ue_recent.iloc[-1]["Unemployment_Rate"]
    
    # Risk scoring (0-100 scale)
    risk_score = 0
    factors = []
    
    # Factor 1: GDP growth below 4% (India's potential growth ~6-7%)
    if gdp_latest < 4.0:
        risk_score += 30
        factors.append(f"GDP growth at {gdp_latest:.1f}% (below 4% threshold)")
    elif gdp_latest < 5.5:
        risk_score += 15
        factors.append(f"GDP growth at {gdp_latest:.1f}% (moderate)")
    
    # Factor 2: GDP decelerating
    if gdp_trend < -0.5:
        risk_score += 25
        factors.append(f"GDP decelerating ({gdp_trend:.1f}pp/yr)")
    elif gdp_trend < 0:
        risk_score += 10
        factors.append(f"GDP slowing ({gdp_trend:.1f}pp/yr)")
    
    # Factor 3: Unemployment rising
    if ue_trend > 0.3:
        risk_score += 25
        factors.append(f"Unemployment rising ({ue_trend:+.1f}pp/yr)")
    elif ue_trend > 0.1:
        risk_score += 10
        factors.append(f"Unemployment edging up ({ue_trend:+.1f}pp/yr)")
    
    # Factor 4: Unemployment above 6%
    if ue_latest > 6.0:
        risk_score += 20
        factors.append(f"Unemployment at {ue_latest:.1f}% (elevated)")
    
    risk_score = min(risk_score, 100)
    
    if risk_score >= 60:
        risk_label = "🔴 High Risk"
        risk_color = "#ef4444"
    elif risk_score >= 35:
        risk_label = "🟡 Moderate Risk"
        risk_color = "#f59e0b"
    else:
        risk_label = "🟢 Low Risk"
        risk_color = "#10b981"
    
    return {
        "score": risk_score,
        "label": risk_label,
        "color": risk_color,
        "factors": factors,
        "gdp_latest": gdp_latest,
        "ue_latest": ue_latest,
    }, None

risk_data, risk_err = compute_recession_risk()

if risk_err:
    st.info(f"Recession risk indicator unavailable: {risk_err}")
else:
    col_risk1, col_risk2 = st.columns([1, 2])
    
    with col_risk1:
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_data["score"],
            title={"text": "Risk Score", "font": {"color": "#e2e8f0", "size": 16}},
            number={"font": {"color": "#e2e8f0", "size": 32}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                "bar": {"color": risk_data["color"]},
                "bgcolor": "rgba(0,0,0,0.2)",
                "borderwidth": 2,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 35], "color": "rgba(16,185,129,0.15)"},
                    {"range": [35, 60], "color": "rgba(245,158,11,0.15)"},
                    {"range": [60, 100], "color": "rgba(239,68,68,0.15)"},
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
            height=280,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align:center; font-size:1.1rem; font-weight:700; color:{risk_data['color']}; margin-top:-1rem;">
            {risk_data['label']}
        </div>
        """, unsafe_allow_html=True)
    
    with col_risk2:
        st.markdown("**Risk Factors:**")
        if risk_data["factors"]:
            for factor in risk_data["factors"]:
                st.markdown(f"• {factor}")
        else:
            st.markdown("• No significant risk factors detected")
            st.markdown(f"• GDP growth healthy at {risk_data['gdp_latest']:.1f}%")
            st.markdown(f"• Unemployment stable at {risk_data['ue_latest']:.1f}%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem; color:#64748b; line-height:1.6;">
            <strong style="color:#94a3b8;">Methodology:</strong>
            Risk score combines GDP growth level & trend with unemployment level & trend.
            Thresholds calibrated for India's economic structure (potential growth ~6-7%, structural UE ~4-5%).
            This is an <strong style="color:#94a3b8;">early warning indicator</strong>, not a recession prediction.
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

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
        return None, None
    wb_df = wb_df.sort_values("Year").tail(35).copy()
    wb_df["Unemployment_Smoothed"] = (
        wb_df["Unemployment_Rate"]
        .rolling(3, min_periods=1, center=True)
        .mean()
        .round(4)
    )
    engine = ForecastingEngine(forecast_horizon=fc_horizon, method="ensemble")
    fc_df = engine.forecast_with_confidence(wb_df)
    return wb_df, fc_df

fc_horizon_real = st.slider("Forecast horizon (real-data)", 3, 8, 5, key="real_fc_horizon")

with st.spinner("Running evidence-based forecast on real World Bank data…"):
    hist_df, fc_df_real = get_real_forecast(fc_horizon_real)

if hist_df is None or fc_df_real is None:
    st.warning("Could not fetch World Bank data. Check connectivity.")
else:
    # ── Insights box
    fc_insights = generate_forecast_insights(hist_df, fc_df_real)
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


    st.caption(
        "Note: This forecast reflects historical trends — it does not incorporate policy changes, "
        "shocks, or structural breaks not already present in the data. Use the Simulator page "
        "to layer shocks on top of this baseline."
    )

st.markdown("</div>", unsafe_allow_html=True)
