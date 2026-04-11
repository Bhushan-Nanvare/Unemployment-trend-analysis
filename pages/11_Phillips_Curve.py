"""
Page 11 — Phillips Curve Analysis
Inflation vs Unemployment trade-off — the foundational macroeconomic relationship.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.ui_helpers import DARK_CSS, plotly_dark_layout, render_kpi_card
from src.live_data import fetch_world_bank, fetch_gdp_growth, _fetch_indicator_series

st.set_page_config(page_title="Phillips Curve | UIP", page_icon="📉", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📉 Phillips Curve")
    st.caption("The inverse relationship between inflation and unemployment")
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")

st.markdown("""
<div class="page-hero">
    <div class="hero-title">📉 Phillips Curve — India</div>
    <div class="hero-subtitle">
        The trade-off between inflation and unemployment — a foundational macroeconomic relationship
    </div>
</div>""", unsafe_allow_html=True)

@st.cache_data(ttl=86400, show_spinner=False)
def load_phillips_data():
    import time as _time
    ue_df = fetch_world_bank("India")

    # CPI inflation can be slow — retry once
    cpi_df = _fetch_indicator_series("FP.CPI.TOTL.ZG", iso="IN", per_page=40)
    if cpi_df.empty:
        _time.sleep(1)
        cpi_df = _fetch_indicator_series("FP.CPI.TOTL.ZG", iso="IN", per_page=40)

    gdp_df = fetch_gdp_growth("India")

    if ue_df.empty or cpi_df.empty:
        return pd.DataFrame()

    merged = pd.merge(
        ue_df.rename(columns={"Unemployment_Rate": "UE"}),
        cpi_df.rename(columns={"Value": "Inflation"}),
        on="Year", how="inner"
    )
    merged = pd.merge(merged, gdp_df.rename(columns={"Value": "GDP_Growth"}), on="Year", how="left")
    return merged.sort_values("Year")

with st.spinner("Fetching live World Bank data..."):
    df = load_phillips_data()

if df.empty:
    st.error("""
    ⚠️ **Could not fetch data from World Bank API.**
    
    The Phillips Curve analysis requires both unemployment (SL.UEM.TOTL.ZS) and 
    inflation (FP.CPI.TOTL.ZG) data from the World Bank Open Data API.
    
    **Possible causes:**
    - World Bank API is experiencing high load or downtime
    - Network connectivity issues
    - API timeout (indicators can take 20-30 seconds to fetch)
    
    **Try:**
    - Refresh the page in a few minutes
    - Check your internet connection
    - The Overview page uses cached unemployment data and may still work
    """)
    st.stop()

# ── KPIs ───────────────────────────────────────────────────────────────────────
latest = df.iloc[-1]
prev = df.iloc[-2] if len(df) >= 2 else None

col1, col2, col3, col4 = st.columns(4)
with col1:
    ue_val = round(latest["UE"], 2)
    ue_delta = f"▼ {abs(round(latest['UE'] - prev['UE'], 2))}pp" if prev is not None and latest["UE"] < prev["UE"] else ""
    st.markdown(render_kpi_card("📊", f"Unemployment ({int(latest['Year'])})", f"{ue_val}%", ue_delta, "down" if ue_delta else "neutral"), unsafe_allow_html=True)

with col2:
    inf_val = round(latest["Inflation"], 2)
    inf_delta = f"▲ {abs(round(latest['Inflation'] - prev['Inflation'], 2))}pp" if prev is not None and latest["Inflation"] > prev["Inflation"] else ""
    st.markdown(render_kpi_card("💹", f"Inflation ({int(latest['Year'])})", f"{inf_val}%", inf_delta, "up" if inf_delta else "neutral"), unsafe_allow_html=True)

with col3:
    if pd.notna(latest.get("GDP_Growth")):
        gdp_val = round(latest["GDP_Growth"], 2)
        st.markdown(render_kpi_card("📈", f"GDP Growth ({int(latest['Year'])})", f"{gdp_val}%", delta_type="neutral"), unsafe_allow_html=True)
    else:
        st.markdown(render_kpi_card("📈", "GDP Growth", "N/A", delta_type="neutral"), unsafe_allow_html=True)

with col4:
    corr = df["UE"].corr(df["Inflation"])
    corr_label = "Inverse" if corr < -0.2 else ("Weak" if abs(corr) < 0.2 else "Positive")
    st.markdown(render_kpi_card("🔗", "UE-Inflation Correlation", f"{corr:.2f}", corr_label, "neutral"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Phillips Curve Scatter ─────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📉 Phillips Curve — Inflation vs Unemployment</div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.85rem; color:#64748b; margin-bottom:1rem; line-height:1.6;">
    The <strong style="color:#e2e8f0;">Phillips Curve</strong> posits an inverse relationship:
    when unemployment falls, inflation tends to rise (tight labor market → wage pressure → price increases).
    India's curve shows this relationship is <strong style="color:#e2e8f0;">weaker than in developed economies</strong>
    due to the large informal sector and supply-side shocks.
</div>
""", unsafe_allow_html=True)

fig_pc = px.scatter(
    df, x="UE", y="Inflation", color="Year",
    color_continuous_scale="Viridis",
    hover_data={"Year": True, "UE": ":.2f", "Inflation": ":.2f"},
    labels={"UE": "Unemployment Rate (%)", "Inflation": "Inflation (CPI, %)"},
)

# Add trend line
from scipy.stats import linregress
slope, intercept, r_value, p_value, std_err = linregress(df["UE"], df["Inflation"])
x_trend = [df["UE"].min(), df["UE"].max()]
y_trend = [slope * x + intercept for x in x_trend]

fig_pc.add_trace(go.Scatter(
    x=x_trend, y=y_trend,
    mode="lines",
    name=f"Trend (R²={r_value**2:.2f})",
    line=dict(color="#f43f5e", width=2, dash="dash"),
    showlegend=True,
))

fig_pc.update_layout(**plotly_dark_layout(height=480))
fig_pc.update_layout(
    xaxis_title="Unemployment Rate (%)",
    yaxis_title="Inflation (CPI, %)",
)
st.plotly_chart(fig_pc, use_container_width=True)

st.markdown(f"""
<div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
            border-radius:10px; padding:0.8rem 1.2rem; font-size:0.87rem; color:#94a3b8;">
    📐 <strong style="color:#818cf8;">Statistical Summary:</strong>
    Correlation = <strong style="color:#e2e8f0;">{corr:.3f}</strong> ·
    R² = <strong style="color:#e2e8f0;">{r_value**2:.3f}</strong> ·
    Slope = <strong style="color:#e2e8f0;">{slope:.3f}</strong>
    {'(inverse relationship — classic Phillips Curve)' if slope < 0 else '(positive relationship — supply shocks dominate)'}
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Time Series Dual Axis ──────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📈 Unemployment & Inflation Over Time</div>', unsafe_allow_html=True)

fig_ts = go.Figure()

fig_ts.add_trace(go.Scatter(
    x=df["Year"], y=df["UE"],
    mode="lines+markers",
    name="Unemployment Rate (%)",
    line=dict(color="#6366f1", width=2.5),
    marker=dict(size=5),
    yaxis="y1",
))

fig_ts.add_trace(go.Scatter(
    x=df["Year"], y=df["Inflation"],
    mode="lines+markers",
    name="Inflation (CPI, %)",
    line=dict(color="#f43f5e", width=2.5, dash="dot"),
    marker=dict(size=5, symbol="diamond"),
    yaxis="y2",
))

# Shade COVID period
fig_ts.add_vrect(
    x0=2019.5, x1=2021.5,
    fillcolor="rgba(239,68,68,0.07)",
    line_width=0,
    annotation_text="COVID-19",
    annotation_position="top left",
    annotation_font=dict(color="#f87171", size=10),
)

layout = plotly_dark_layout(height=400)
layout.update(
    yaxis=dict(title="Unemployment (%)", color="#6366f1", gridcolor="rgba(255,255,255,0.04)"),
    yaxis2=dict(title="Inflation (%)", color="#f43f5e", overlaying="y", side="right", showgrid=False),
    xaxis_title="Year",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
)
fig_ts.update_layout(**layout)
st.plotly_chart(fig_ts, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Decade Comparison ──────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 Phillips Curve by Decade</div>', unsafe_allow_html=True)

df["Decade"] = (df["Year"] // 10 * 10).astype(str) + "s"
decades = df["Decade"].unique()

fig_decades = go.Figure()
colors = {"1990s": "#10b981", "2000s": "#6366f1", "2010s": "#f59e0b", "2020s": "#f43f5e"}

for decade in sorted(decades):
    subset = df[df["Decade"] == decade]
    fig_decades.add_trace(go.Scatter(
        x=subset["UE"], y=subset["Inflation"],
        mode="markers",
        name=decade,
        marker=dict(size=10, color=colors.get(decade, "#94a3b8")),
        hovertemplate="<b>%{text}</b><br>UE: %{x:.2f}%<br>Inflation: %{y:.2f}%<extra></extra>",
        text=subset["Year"],
    ))

fig_decades.update_layout(**plotly_dark_layout(height=420))
fig_decades.update_layout(
    xaxis_title="Unemployment Rate (%)",
    yaxis_title="Inflation (CPI, %)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
)
st.plotly_chart(fig_decades, use_container_width=True)

st.markdown("""
<div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
    <strong style="color:#e2e8f0;">Interpretation:</strong>
    The Phillips Curve has <strong style="color:#e2e8f0;">shifted over time</strong>.
    In the 1990s-2000s, India experienced high inflation with moderate unemployment.
    Post-2010, inflation moderated (RBI inflation targeting since 2016) while unemployment remained structurally elevated.
    The 2020s show COVID disruption — unemployment spiked while inflation remained volatile due to supply chain shocks.
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Export ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📥 Export Data</div>', unsafe_allow_html=True)

csv_bytes = df[["Year", "UE", "Inflation", "GDP_Growth"]].rename(columns={
    "UE": "Unemployment_Rate_Pct",
    "Inflation": "CPI_Inflation_Pct",
    "GDP_Growth": "GDP_Growth_Pct",
}).to_csv(index=False).encode()

st.download_button(
    "⬇ Download Phillips Curve Data (CSV)",
    csv_bytes,
    file_name="india_phillips_curve_data.csv",
    mime="text/csv",
)

st.caption("Source: World Bank Open Data (SL.UEM.TOTL.ZS, FP.CPI.TOTL.ZG, NY.GDP.MKTP.KD.ZG)")
st.markdown("</div>", unsafe_allow_html=True)
