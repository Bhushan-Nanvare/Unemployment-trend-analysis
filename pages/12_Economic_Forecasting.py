"""
Page 12 — Economic Forecasting with GDP Relationships
Shows how GDP growth affects unemployment through Okun's Law and economic modeling.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from src.ui_helpers import DARK_CSS, plotly_dark_layout, render_kpi_card
from src.live_data import fetch_world_bank, fetch_gdp_growth
from src.economic_forecasting import EconomicForecastingEngine

st.set_page_config(page_title="Economic Forecasting | UIP", page_icon="📈", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📈 Economic Forecasting")
    st.caption("GDP-driven unemployment forecasting using Okun's Law")
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py", label="❓ Help Guide")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Simulator")
    st.page_link("pages/11_Phillips_Curve.py", label="📉 Phillips Curve")

st.markdown("""
<div class="page-hero">
    <div class="hero-title">📈 Economic Forecasting Engine</div>
    <div class="hero-subtitle">
        GDP-driven unemployment forecasting using Okun's Law and economic relationships
    </div>
</div>""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=3600, show_spinner=False)
def load_economic_data():
    unemployment_df = fetch_world_bank("India")
    gdp_df = fetch_gdp_growth("India")
    return unemployment_df, gdp_df

with st.spinner("Loading economic data..."):
    unemployment_df, gdp_df = load_economic_data()

if unemployment_df.empty or gdp_df.empty:
    st.error("Could not load economic data. Please check World Bank API connectivity.")
    st.stop()

# Merge data for analysis
merged_data = pd.merge(
    unemployment_df.rename(columns={"Unemployment_Rate": "UE"}),
    gdp_df.rename(columns={"Value": "GDP_Growth"}),
    on="Year", how="inner"
).sort_values("Year")

if len(merged_data) < 10:
    st.error("Insufficient overlapping data for economic analysis.")
    st.stop()

# Initialize economic forecasting engine
engine = EconomicForecastingEngine(forecast_horizon=6)

# Estimate Okun coefficient
okun_coef = engine.estimate_okun_coefficient(unemployment_df, gdp_df)
engine.okun_coefficient = okun_coef

# ── Key Metrics ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔬 Economic Relationship Analysis</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(render_kpi_card("📊", "Okun Coefficient", f"{okun_coef:.3f}", "GDP → Unemployment", "neutral"), unsafe_allow_html=True)

with col2:
    correlation = merged_data["GDP_Growth"].corr(merged_data["UE"])
    corr_label = "Strong Inverse" if correlation < -0.5 else ("Moderate Inverse" if correlation < -0.2 else "Weak")
    st.markdown(render_kpi_card("🔗", "GDP-UE Correlation", f"{correlation:.3f}", corr_label, "neutral"), unsafe_allow_html=True)

with col3:
    latest_gdp = merged_data["GDP_Growth"].iloc[-1]
    latest_year = int(merged_data["Year"].iloc[-1])
    st.markdown(render_kpi_card("📈", f"Latest GDP ({latest_year})", f"{latest_gdp:.1f}%", delta_type="neutral"), unsafe_allow_html=True)

with col4:
    latest_ue = merged_data["UE"].iloc[-1]
    st.markdown(render_kpi_card("📉", f"Latest UE ({latest_year})", f"{latest_ue:.1f}%", delta_type="neutral"), unsafe_allow_html=True)

st.markdown(f"""
<div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
            border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8; margin-bottom:1.5rem;">
    📐 <strong style="color:#818cf8;">Okun's Law for India:</strong>
    A <strong style="color:#e2e8f0;">{abs(okun_coef):.1f} percentage point</strong> decrease in unemployment
    for every <strong style="color:#e2e8f0;">1% increase</strong> in GDP growth above potential (6%).
    {'This is weaker than developed economies (~0.5) due to India\'s large informal sector.' if abs(okun_coef) < 0.4 else 'This is similar to developed economy relationships.'}
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Historical Relationship ────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Historical GDP Growth vs Unemployment</div>', unsafe_allow_html=True)

# Calculate unemployment change for Okun's Law visualization
merged_data["UE_Change"] = merged_data["UE"].diff()

# Remove outliers for cleaner visualization
clean_data = merged_data[
    (merged_data["UE_Change"].abs() < 3) & 
    (merged_data["GDP_Growth"] > -5) & 
    (merged_data["GDP_Growth"] < 15)
].dropna()

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("**GDP Growth vs Unemployment Level**")
    fig_level = px.scatter(
        merged_data, x="GDP_Growth", y="UE", color="Year",
        color_continuous_scale="Viridis",
        hover_data={"Year": True, "GDP_Growth": ":.1f", "UE": ":.2f"},
        labels={"GDP_Growth": "GDP Growth (%)", "UE": "Unemployment (%)"},
    )
    
    # Add trend line
    from scipy.stats import linregress
    if len(clean_data) >= 5:
        slope, intercept, r_value, p_value, std_err = linregress(clean_data["GDP_Growth"], clean_data["UE"])
        x_trend = [clean_data["GDP_Growth"].min(), clean_data["GDP_Growth"].max()]
        y_trend = [slope * x + intercept for x in x_trend]
        
        fig_level.add_trace(go.Scatter(
            x=x_trend, y=y_trend,
            mode="lines",
            name=f"Trend (R²={r_value**2:.2f})",
            line=dict(color="#f43f5e", width=2, dash="dash"),
        ))
    
    fig_level.update_layout(**plotly_dark_layout(height=350))
    st.plotly_chart(fig_level, use_container_width=True)

with col_chart2:
    st.markdown("**GDP Growth vs Unemployment Change (Okun's Law)**")
    if len(clean_data) >= 5:
        fig_change = px.scatter(
            clean_data, x="GDP_Growth", y="UE_Change", color="Year",
            color_continuous_scale="Plasma",
            hover_data={"Year": True, "GDP_Growth": ":.1f", "UE_Change": ":.2f"},
            labels={"GDP_Growth": "GDP Growth (%)", "UE_Change": "Unemployment Change (pp)"},
        )
        
        # Add Okun's Law line
        slope_okun, intercept_okun, r_okun, p_okun, std_okun = linregress(clean_data["GDP_Growth"], clean_data["UE_Change"])
        x_okun = [clean_data["GDP_Growth"].min(), clean_data["GDP_Growth"].max()]
        y_okun = [slope_okun * x + intercept_okun for x in x_okun]
        
        fig_change.add_trace(go.Scatter(
            x=x_okun, y=y_okun,
            mode="lines",
            name=f"Okun's Law (β={slope_okun:.3f})",
            line=dict(color="#10b981", width=3),
        ))
        
        fig_change.add_hline(y=0, line_dash="dot", line_color="#94a3b8", annotation_text="No Change")
        fig_change.update_layout(**plotly_dark_layout(height=350))
        st.plotly_chart(fig_change, use_container_width=True)
    else:
        st.info("Insufficient clean data for Okun's Law visualization")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── GDP Scenario Forecasts ─────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔮 GDP Scenario Forecasts</div>', unsafe_allow_html=True)

# Generate scenario forecasts
scenario_forecasts = engine.forecast_multiple_scenarios(unemployment_df)

# Create forecast visualization
fig_scenarios = go.Figure()

colors = {"Optimistic": "#10b981", "Baseline": "#6366f1", "Pessimistic": "#f59e0b", "Recession": "#f43f5e"}

for scenario in scenario_forecasts["Scenario"].unique():
    subset = scenario_forecasts[scenario_forecasts["Scenario"] == scenario]
    fig_scenarios.add_trace(go.Scatter(
        x=subset["Year"], y=subset["Predicted_Unemployment"],
        mode="lines+markers",
        name=f"{scenario} (GDP: {subset['GDP_Growth'].mean():.1f}%)",
        line=dict(color=colors.get(scenario, "#94a3b8"), width=3),
        marker=dict(size=6),
        hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Unemployment: %{y:.2f}%<extra></extra>",
    ))

# Add historical data
fig_scenarios.add_trace(go.Scatter(
    x=unemployment_df["Year"].tail(10), 
    y=unemployment_df["Unemployment_Rate"].tail(10),
    mode="lines+markers",
    name="Historical",
    line=dict(color="#e2e8f0", width=2),
    marker=dict(size=5, color="#94a3b8"),
))

# Add divider
last_hist_year = unemployment_df["Year"].max()
fig_scenarios.add_vline(
    x=last_hist_year + 0.5,
    line=dict(color="rgba(148,163,184,0.4)", width=1.5, dash="dash"),
)

fig_scenarios.update_layout(**plotly_dark_layout(height=450))
fig_scenarios.update_layout(
    xaxis_title="Year",
    yaxis_title="Unemployment Rate (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_scenarios, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Scenario Comparison Table ──────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Scenario Impact Analysis</div>', unsafe_allow_html=True)

# Calculate scenario statistics
scenario_stats = []
current_ue = unemployment_df["Unemployment_Rate"].iloc[-1]

for scenario in scenario_forecasts["Scenario"].unique():
    subset = scenario_forecasts[scenario_forecasts["Scenario"] == scenario]
    
    scenario_stats.append({
        "Scenario": scenario,
        "Avg GDP Growth (%)": f"{subset['GDP_Growth'].mean():.1f}",
        "Peak Unemployment (%)": f"{subset['Predicted_Unemployment'].max():.2f}",
        "Final Unemployment (%)": f"{subset['Predicted_Unemployment'].iloc[-1]:.2f}",
        "Change from Current (pp)": f"{subset['Predicted_Unemployment'].iloc[-1] - current_ue:+.2f}",
        "GDP Impact": f"{(subset['GDP_Growth'].mean() - 6.0):+.1f}pp vs potential",
    })

scenario_df = pd.DataFrame(scenario_stats)

def style_scenario_impact(val):
    try:
        num_val = float(val.replace("+", "").replace("pp", ""))
        if num_val < -1:
            return "background-color: rgba(16,185,129,0.2); color: #10b981; font-weight: 700;"
        elif num_val > 1:
            return "background-color: rgba(239,68,68,0.2); color: #ef4444; font-weight: 700;"
    except:
        pass
    return ""

st.dataframe(
    scenario_df.style.map(style_scenario_impact, subset=["Change from Current (pp)"]),
    use_container_width=True, hide_index=True
)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Interactive GDP Impact Calculator ──────────────────────────────────────────
st.markdown('<div class="section-title">🧮 GDP Impact Calculator</div>', unsafe_allow_html=True)

col_calc1, col_calc2, col_calc3 = st.columns(3)

with col_calc1:
    target_gdp = st.slider("Target GDP Growth (%)", 2.0, 10.0, 6.5, 0.5)
    years_ahead = st.slider("Years Ahead", 1, 5, 3)

with col_calc2:
    # Calculate impact
    gdp_deviation = target_gdp - 6.0  # Deviation from potential
    ue_impact = okun_coef * gdp_deviation
    projected_ue = current_ue + ue_impact
    
    st.metric("GDP Deviation from Potential", f"{gdp_deviation:+.1f}pp")
    st.metric("Unemployment Impact", f"{ue_impact:+.2f}pp")
    st.metric("Projected Unemployment", f"{projected_ue:.2f}%")

with col_calc3:
    # Policy implications
    if projected_ue < 3.5:
        policy_msg = "🟢 **Low unemployment** - Monitor for wage inflation"
        policy_color = "#10b981"
    elif projected_ue > 6.0:
        policy_msg = "🔴 **High unemployment** - Stimulus may be needed"
        policy_color = "#ef4444"
    else:
        policy_msg = "🟡 **Moderate unemployment** - Balanced policy stance"
        policy_color = "#f59e0b"
    
    st.markdown(f"""
    <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
                border-radius:10px; padding:1rem; margin-top:1rem;">
        <div style="color:{policy_color}; font-weight:700; margin-bottom:0.5rem;">Policy Implication</div>
        <div style="color:#94a3b8; font-size:0.9rem;">{policy_msg}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Model Comparison ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⚖️ Economic vs Time-Series Forecasting</div>', unsafe_allow_html=True)

# Generate time-series forecast for comparison
from src.forecasting import ForecastingEngine
ts_engine = ForecastingEngine(forecast_horizon=6)
ts_forecast = ts_engine.forecast(unemployment_df)

# Economic baseline forecast
econ_forecast = engine.forecast_with_gdp(unemployment_df)

# Comparison chart
fig_compare = go.Figure()

fig_compare.add_trace(go.Scatter(
    x=unemployment_df["Year"].tail(5), 
    y=unemployment_df["Unemployment_Rate"].tail(5),
    mode="lines+markers",
    name="Historical",
    line=dict(color="#e2e8f0", width=2),
))

fig_compare.add_trace(go.Scatter(
    x=ts_forecast["Year"], y=ts_forecast["Predicted_Unemployment"],
    mode="lines+markers",
    name="Time-Series Model",
    line=dict(color="#94a3b8", width=2, dash="dot"),
))

fig_compare.add_trace(go.Scatter(
    x=econ_forecast["Year"], y=econ_forecast["Predicted_Unemployment"],
    mode="lines+markers",
    name="Economic Model (GDP-driven)",
    line=dict(color="#6366f1", width=3),
))

fig_compare.add_vline(
    x=unemployment_df["Year"].max() + 0.5,
    line=dict(color="rgba(148,163,184,0.4)", width=1.5, dash="dash"),
)

fig_compare.update_layout(**plotly_dark_layout(height=400))
fig_compare.update_layout(
    xaxis_title="Year",
    yaxis_title="Unemployment Rate (%)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig_compare, use_container_width=True)

# Model comparison metrics
ts_final = ts_forecast["Predicted_Unemployment"].iloc[-1]
econ_final = econ_forecast["Predicted_Unemployment"].iloc[-1]
difference = abs(ts_final - econ_final)

st.markdown(f"""
<div style="background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.2);
            border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8;">
    📊 <strong style="color:#f59e0b;">Model Comparison:</strong>
    Time-series projects <strong style="color:#e2e8f0;">{ts_final:.2f}%</strong> unemployment vs 
    Economic model <strong style="color:#e2e8f0;">{econ_final:.2f}%</strong> 
    (difference: <strong style="color:#e2e8f0;">{difference:.2f}pp</strong>).
    Economic model incorporates GDP growth assumptions while time-series extrapolates historical trends.
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Export Data ────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">📥 Export Analysis</div>', unsafe_allow_html=True)

export_data = scenario_forecasts.copy()
csv_data = export_data.to_csv(index=False)

st.download_button(
    "⬇️ Download GDP Scenario Forecasts (CSV)",
    csv_data.encode(),
    file_name="gdp_scenario_forecasts.csv",
    mime="text/csv"
)

st.caption(f"Economic model uses Okun coefficient of {okun_coef:.3f} estimated from {len(merged_data)} years of India data")
st.markdown("</div>", unsafe_allow_html=True)