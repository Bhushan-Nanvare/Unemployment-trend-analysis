"""
Page 3 — Sector Analysis
Tab 1: Scenario stress simulation — heatmap, radar chart, treemap, sector cards.
Tab 2: Live Data — real World Bank sector employment & GDP indicators for India.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, plotly_dark_layout
from src.live_data import fetch_sector_indicators
from src.live_insights import generate_sector_insights

st.set_page_config(page_title="Sector Analysis | UIP", page_icon="🏭", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏭 Sector Analysis")
    st.markdown("**Simulation Parameters** *(Tab 1 only)*")
    shock_intensity = st.slider("Shock Intensity", 0.0, 0.6, 0.3, 0.05,
                                help="Severity of the economic shock applied to each sector")
    recovery_rate   = st.slider("Recovery Rate", 0.05, 0.6, 0.3, 0.05,
                                help="Speed at which sectors recover after the shock")
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py",                           label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py",             label="❓ Help Guide")
    st.page_link("pages/1_Overview.py",               label="📊 Overview")
    st.page_link("pages/2_Simulator.py",              label="🧪 Simulator")
    st.page_link("pages/4_Career_Lab.py",             label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py",            label="🤖 AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py",     label="🎯 Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py",       label="📡 Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py",     label="🗺️ Geo Career")

# ── Page hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <div class="hero-title">🏭 Sector Intelligence</div>
    <div class="hero-subtitle">Scenario stress analysis alongside real World Bank sector indicators for India</div>
</div>""", unsafe_allow_html=True)

from src.api import simulate_scenario, ScenarioRequest

tab_sim, tab_live = st.tabs(["🧪 Scenario Simulation", "🌐 Live World Bank Data"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SCENARIO SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
with tab_sim:

    # ── Simulation context notice ─────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.22);
                border-radius:12px; padding:0.85rem 1.2rem; margin-bottom:1.2rem;">
        <div style="font-size:0.78rem; font-weight:700; color:#818cf8;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
            🧪 Model Simulation — Not Historical Data
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.55;">
            The <strong style="color:#e2e8f0;">Stress Score</strong> and
            <strong style="color:#e2e8f0;">Resilience Score</strong> below are
            <em>model-computed outputs</em> based on each sector's historical shock sensitivity
            and the parameters you set in the sidebar.
            They reflect <strong style="color:#e2e8f0;">relative vulnerability</strong> under
            the chosen shock scenario — not absolute real-world measurements.
            Adjust Shock Intensity and Recovery Rate in the sidebar to explore different scenarios.
        </div>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=60)
    def get_sector_data(si, rr):
        try:
            req = ScenarioRequest(
                shock_intensity=si,
                shock_duration=2,
                recovery_rate=rr,
                forecast_horizon=6
            )
            return simulate_scenario(req)
        except Exception as e:
            return None

    data = get_sector_data(shock_intensity, recovery_rate)

    if not data:
        st.error("⚠️ Simulation unavailable. This tab requires the local API to be running: "
                 "`uvicorn src.api:app --reload`")
    else:
        sector_raw = data.get("sector_impact", [])
        if not sector_raw:
            st.warning("No sector data returned from the simulation. Try adjusting parameters.")
        else:
            df = pd.DataFrame(sector_raw)

            # ── Summary KPIs ──────────────────────────────────────────────────
            most_stressed  = df.loc[df["Stress_Score"].idxmax(), "Sector"]
            most_resilient = df.loc[df["Resilience_Score"].idxmax(), "Sector"]
            avg_stress     = round(df["Stress_Score"].mean(), 1)
            high_risk_count = len(df[df["Stress_Score"] >= 60.0])

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(render_kpi_card("🔥", "Most Stressed Sector", most_stressed,
                                            delta_type="neutral"), unsafe_allow_html=True)
            with c2:
                st.markdown(render_kpi_card("💪", "Most Resilient Sector", most_resilient,
                                            delta_type="neutral"), unsafe_allow_html=True)
            with c3:
                at = "up" if avg_stress > 40 else "down"
                st.markdown(render_kpi_card("📊", "Avg Stress Score", f"{avg_stress:.1f} / 100",
                                            delta_type=at), unsafe_allow_html=True)
            with c4:
                bt = "up" if high_risk_count > 2 else "neutral"
                st.markdown(render_kpi_card("⚠️", "High-Risk Sectors (≥60)", str(high_risk_count),
                                            delta_type=bt), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Heatmap + Radar ───────────────────────────────────────────────
            col_heat, col_radar = st.columns([3, 2])

            with col_heat:
                st.markdown('<div class="section-title">🌡️ Stress vs Resilience Heatmap</div>',
                            unsafe_allow_html=True)
                heat_df     = df[["Sector", "Stress_Score", "Resilience_Score"]].copy()
                heat_matrix = heat_df.set_index("Sector").T

                fig_heat = go.Figure(go.Heatmap(
                    z=heat_matrix.values.tolist(),
                    x=heat_matrix.columns.tolist(),
                    y=["Stress Score", "Resilience Score"],
                    colorscale=[
                        [0.0, "#0a0e1a"], [0.3, "#1e3a5f"],
                        [0.6, "#6366f1"], [0.8, "#f59e0b"], [1.0, "#ef4444"],
                    ],
                    showscale=True,
                    text=[[f"{v:.1f}" for v in row] for row in heat_matrix.values.tolist()],
                    texttemplate="%{text}",
                    textfont=dict(color="white", size=11),
                    hovertemplate="<b>%{x}</b><br>%{y}: %{z:.1f}<extra></extra>",
                    colorbar=dict(
                        tickfont=dict(color="#94a3b8"),
                        title=dict(text="Score (0–100)", font=dict(color="#94a3b8")),
                    ),
                ))
                fig_heat.update_layout(**plotly_dark_layout(height=280))
                fig_heat.update_layout(margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_heat, use_container_width=True)

            with col_radar:
                st.markdown('<div class="section-title">🕸️ Resilience Radar</div>',
                            unsafe_allow_html=True)
                sectors         = df["Sector"].tolist()
                resilience_vals = df["Resilience_Score"].tolist()
                stress_vals     = df["Stress_Score"].tolist()

                fig_r = go.Figure()
                fig_r.add_trace(go.Scatterpolar(
                    r=resilience_vals + [resilience_vals[0]],
                    theta=sectors + [sectors[0]],
                    fill="toself", name="Resilience",
                    fillcolor="rgba(16,185,129,0.15)",
                    line=dict(color="#10b981", width=2),
                    marker=dict(color="#10b981", size=5),
                ))
                fig_r.add_trace(go.Scatterpolar(
                    r=stress_vals + [stress_vals[0]],
                    theta=sectors + [sectors[0]],
                    fill="toself", name="Stress",
                    fillcolor="rgba(239,68,68,0.10)",
                    line=dict(color="#ef4444", width=2, dash="dot"),
                    marker=dict(color="#ef4444", size=5),
                ))
                fig_r.update_layout(
                    **plotly_dark_layout(height=380, showlegend=True),
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0, 100],
                                        gridcolor="rgba(255,255,255,0.08)",
                                        tickfont=dict(color="#64748b", size=9)),
                        angularaxis=dict(gridcolor="rgba(255,255,255,0.06)",
                                         tickfont=dict(color="#94a3b8", size=9)),
                    ),
                )
                st.plotly_chart(fig_r, use_container_width=True)

            # ── Treemap ───────────────────────────────────────────────────────
            st.markdown('<div class="section-title">🗺️ Sector Impact Treemap — Stress Score</div>',
                        unsafe_allow_html=True)
            fig_tree = px.treemap(
                df, path=["Sector"], values="Stress_Score",
                color="Stress_Score",
                color_continuous_scale=["#0d1b2a", "#1e3a5f", "#6366f1", "#f59e0b", "#ef4444"],
                hover_data={"Resilience_Score": ":.1f", "Stress_Score": ":.1f"},
            )
            fig_tree.update_traces(textfont=dict(color="white", size=13),
                                   marker=dict(cornerradius=5))
            fig_tree.update_layout(
                **plotly_dark_layout(height=320),
                coloraxis_colorbar=dict(
                    tickfont=dict(color="#94a3b8"),
                    title=dict(text="Stress (0–100)", font=dict(color="#94a3b8")),
                ),
            )
            st.plotly_chart(fig_tree, use_container_width=True)

            # ── Sector Cards ──────────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">🏷️ Sector Detail Cards</div>',
                        unsafe_allow_html=True)

            cols = st.columns(min(len(df), 4))
            for i, row in df.iterrows():
                col  = cols[i % len(cols)]
                stress = row["Stress_Score"]
                res    = row["Resilience_Score"]

                if stress >= 60:
                    badge = render_badge("🔴 High Risk", "danger")
                elif stress >= 35:
                    badge = render_badge("🟡 Moderate", "warning")
                else:
                    badge = render_badge("🟢 Stable", "success")

                sp = int(min(100, stress))
                rp = int(min(100, res))

                with col:
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom:1rem;">
                        <div style="display:flex; justify-content:space-between;
                                    align-items:flex-start; margin-bottom:0.8rem;">
                            <div style="font-size:1rem; font-weight:700; color:#e2e8f0;">
                                {row["Sector"]}
                            </div>
                            {badge}
                        </div>
                        <div style="margin-bottom:0.5rem;">
                            <div style="display:flex; justify-content:space-between;
                                        font-size:0.78rem; color:#94a3b8; margin-bottom:3px;">
                                <span>Stress Score</span>
                                <span style="color:#ef4444;">{stress:.1f} / 100</span>
                            </div>
                            <div style="background:rgba(255,255,255,0.05); border-radius:4px; height:6px;">
                                <div style="width:{sp}%; height:100%; background:#ef4444; border-radius:4px;"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between;
                                        font-size:0.78rem; color:#94a3b8; margin-bottom:3px;">
                                <span>Resilience Score</span>
                                <span style="color:#10b981;">{res:.1f} / 100</span>
                            </div>
                            <div style="background:rgba(255,255,255,0.05); border-radius:4px; height:6px;">
                                <div style="width:{rp}%; height:100%; background:#10b981; border-radius:4px;"></div>
                            </div>
                        </div>
                        <div style="font-size:0.75rem; color:#475569; margin-top:0.6rem;">
                            Sensitivity: {row.get("Sensitivity", "N/A")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Methodology note ──────────────────────────────────────────────
            st.markdown("""
            <div style="background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.15);
                        border-radius:10px; padding:0.8rem 1.2rem; font-size:0.8rem; color:#64748b;
                        line-height:1.6; margin-top:1rem;">
                <strong style="color:#818cf8;">How scores are computed:</strong>
                Stress Score = (scenario peak unemployment ÷ India's historical peak 9.5%) × sector shock sensitivity × 100.
                Resilience Score = base resilience − (stress × 0.35) + (recovery rate × 25).
                Sectors with higher shock sensitivity (e.g. Construction, Manufacturing) score higher stress
                for the same economic shock than defensive sectors (e.g. Healthcare, Education).
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LIVE WORLD BANK DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab_live:
    st.markdown("""
    <div style="background:rgba(6,182,212,0.07); border:1px solid rgba(6,182,212,0.2);
                border-radius:14px; padding:1rem 1.4rem; margin-bottom:1.5rem;">
        <div style="font-size:0.78rem; font-weight:700; color:#06b6d4; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:0.3rem;">🌐 Data Source</div>
        <div style="font-size:0.88rem; color:#94a3b8; line-height:1.6;">
            Employment and GDP share figures come from the
            <strong style="color:#e2e8f0;">World Bank Open Data API</strong> (free, no key required).
            Values are the most recently published annual figures — typically 1–2 years behind the
            current calendar year due to national statistical reporting lags.
            Indicators: <code>SL.AGR/IND/SRV.EMPL.ZS</code> (employment share) ·
            <code>NV.AGR/IND/SRV/IND.MANF.ZS</code> (GDP share). Cached for 24 hours.
        </div>
    </div>
    """, unsafe_allow_html=True)

    @st.cache_data(ttl=86400)
    def load_live_sector_data():
        return fetch_sector_indicators("India")

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("🔄 Refresh Live Data", key="refresh_live"):
            st.cache_data.clear()
            st.rerun()

    with st.spinner("Fetching sector data from World Bank API…"):
        live_df = load_live_sector_data()

    if live_df.empty:
        st.warning("""
        ⚠️ Could not retrieve live sector data from the World Bank API.
        This may be due to network issues or API rate limiting.
        Please check your internet connection and try refreshing.
        """)
    else:
        # ── AI Insights ────────────────────────────────────────────────────────
        sector_insights = generate_sector_insights(live_df)
        if sector_insights:
            bullets_html = "".join(
                f'<li style="margin-bottom:0.45rem; color:#cbd5e1; font-size:0.9rem; line-height:1.6;">'
                + s.replace("**", "<strong style='color:#e2e8f0;'>", 1).replace("**", "</strong>", 1)
                + "</li>"
                for s in sector_insights
            )
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.22);
                        border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.4rem;">
                <div style="display:flex; gap:0.6rem; align-items:center; margin-bottom:0.6rem;">
                    <span style="font-size:1.1rem;">💡</span>
                    <span style="font-size:0.78rem; font-weight:700; color:#34d399;
                                  text-transform:uppercase; letter-spacing:1px;">
                        Sector Intelligence — Key Insights
                    </span>
                </div>
                <ul style="margin:0; padding-left:1.2rem;">{bullets_html}</ul>
            </div>
            """, unsafe_allow_html=True)

        # ── KPI strip ──────────────────────────────────────────────────────────
        live_valid_emp = live_df.dropna(subset=["Employment_Share"])
        live_valid_gdp = live_df.dropna(subset=["GDP_Share"])

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            if not live_valid_emp.empty:
                top_emp = live_valid_emp.loc[live_valid_emp["Employment_Share"].idxmax(), "Sector"]
                st.markdown(render_kpi_card("👷", "Largest Employer", top_emp,
                                            delta_type="neutral"), unsafe_allow_html=True)
        with k2:
            if not live_valid_gdp.empty:
                top_gdp = live_valid_gdp.loc[live_valid_gdp["GDP_Share"].idxmax(), "Sector"]
                st.markdown(render_kpi_card("💰", "Largest GDP Sector", top_gdp,
                                            delta_type="neutral"), unsafe_allow_html=True)
        with k3:
            live_count = int((live_df["Source"] == "World Bank (live)").sum())
            st.markdown(render_kpi_card("🟢", "Live Indicators", str(live_count),
                                        delta_type="neutral"), unsafe_allow_html=True)
        with k4:
            total = len(live_df)
            st.markdown(render_kpi_card("📋", "Sectors Tracked", str(total),
                                        delta_type="neutral"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Bar charts: Employment Share | GDP Share ───────────────────────────
        col_emp, col_gdp = st.columns(2)

        with col_emp:
            st.markdown('<div class="section-title">👷 Employment Share by Sector (%)</div>',
                        unsafe_allow_html=True)
            emp_df = live_df.dropna(subset=["Employment_Share"]).sort_values(
                "Employment_Share", ascending=True)
            if emp_df.empty:
                st.info("Employment share data not available from World Bank for these sectors.")
            else:
                fig_emp = go.Figure(go.Bar(
                    x=emp_df["Employment_Share"],
                    y=emp_df["Sector"],
                    orientation="h",
                    marker=dict(
                        color=emp_df["Employment_Share"],
                        colorscale=[[0, "#1e3a5f"], [0.5, "#6366f1"], [1, "#06b6d4"]],
                        line=dict(width=0),
                    ),
                    text=[f"{v:.1f}%" for v in emp_df["Employment_Share"]],
                    textposition="outside",
                    textfont=dict(color="#e2e8f0"),
                    hovertemplate="<b>%{y}</b><br>Employment share: %{x:.2f}%<extra></extra>",
                ))
                fig_emp.update_layout(
                    **plotly_dark_layout(height=320, showlegend=False),
                    xaxis_title="% of total employment",
                    xaxis=dict(range=[0, emp_df["Employment_Share"].max() * 1.3]),
                )
                st.plotly_chart(fig_emp, use_container_width=True)

        with col_gdp:
            st.markdown('<div class="section-title">💰 GDP Contribution by Sector (%)</div>',
                        unsafe_allow_html=True)
            gdp_df2 = live_df.dropna(subset=["GDP_Share"]).sort_values(
                "GDP_Share", ascending=True)
            if gdp_df2.empty:
                st.info("GDP share data not available from World Bank for these sectors.")
            else:
                fig_gdp2 = go.Figure(go.Bar(
                    x=gdp_df2["GDP_Share"],
                    y=gdp_df2["Sector"],
                    orientation="h",
                    marker=dict(
                        color=gdp_df2["GDP_Share"],
                        colorscale=[[0, "#312e81"], [0.5, "#8b5cf6"], [1, "#34d399"]],
                        line=dict(width=0),
                    ),
                    text=[f"{v:.1f}%" for v in gdp_df2["GDP_Share"]],
                    textposition="outside",
                    textfont=dict(color="#e2e8f0"),
                    hovertemplate="<b>%{y}</b><br>GDP share: %{x:.2f}%<extra></extra>",
                ))
                fig_gdp2.update_layout(
                    **plotly_dark_layout(height=320, showlegend=False),
                    xaxis_title="% of GDP",
                    xaxis=dict(range=[0, gdp_df2["GDP_Share"].max() * 1.3]),
                )
                st.plotly_chart(fig_gdp2, use_container_width=True)

        # ── Scatter: Employment Share vs GDP Share ────────────────────────────
        scatter_df = live_df.dropna(subset=["Employment_Share", "GDP_Share"])
        if not scatter_df.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-title">📌 Employment Share vs GDP Contribution</div>',
                unsafe_allow_html=True,
            )
            st.markdown("""
            <div style="font-size:0.83rem; color:#64748b; margin-bottom:1rem; line-height:1.5;">
                Sectors <strong style="color:#e2e8f0;">above the diagonal</strong> employ a larger workforce share
                than they contribute to GDP — indicating <em>lower productivity per worker</em> (e.g. Agriculture).
                Sectors <strong style="color:#e2e8f0;">below the diagonal</strong> are higher-productivity
                (e.g. Services, Finance). This gap reflects India's central structural challenge.
            </div>
            """, unsafe_allow_html=True)

            fig_sc = px.scatter(
                scatter_df,
                x="GDP_Share", y="Employment_Share",
                text="Sector",
                size=[30] * len(scatter_df),
                color="Sector",
                color_discrete_sequence=["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"],
            )
            # Diagonal reference line (equal contribution)
            max_val = float(scatter_df[["Employment_Share", "GDP_Share"]].max().max()) * 1.15
            fig_sc.add_trace(go.Scatter(
                x=[0, max_val], y=[0, max_val],
                mode="lines", name="Equal contribution",
                line=dict(color="rgba(255,255,255,0.15)", width=1.5, dash="dot"),
                showlegend=True,
            ))
            fig_sc.update_traces(
                textposition="top center",
                textfont=dict(color="white", size=11),
                selector=dict(mode="markers+text"),
            )
            fig_sc.update_layout(
                **plotly_dark_layout(height=400, showlegend=True),
                xaxis_title="GDP Share (%)",
                yaxis_title="Employment Share (%)",
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        # ── Raw data table ────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Raw Indicator Values</div>',
                    unsafe_allow_html=True)
        display_df = live_df.copy()
        display_df["Employment_Share"] = display_df["Employment_Share"].apply(
            lambda v: f"{v:.2f}%" if pd.notna(v) else "N/A"
        )
        display_df["GDP_Share"] = display_df["GDP_Share"].apply(
            lambda v: f"{v:.2f}%" if pd.notna(v) else "N/A"
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption(
            "Source: World Bank Open Data · "
            "Indicators: SL.AGR/IND/SRV.EMPL.ZS · NV.AGR/IND/SRV/IND.MANF.ZS · "
            "Values are the most recent available annual figures."
        )
