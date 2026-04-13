"""
Page 4 — Career Lab
Skill demand chart, growth vs risk bubble chart, career path cards.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, plotly_dark_layout, API_BASE_URL

st.set_page_config(page_title="Career Lab | UIP", page_icon="💼", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 💼 Career Lab")
    shock_intensity = st.slider("Shock Intensity", 0.0, 0.6, 0.3, 0.05)
    recovery_rate   = st.slider("Recovery Rate", 0.05, 0.6, 0.3, 0.05)
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py", label="❓ Help Guide")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py", label="🎯 Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="📡 Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py", label="🗺️ Geo Career")
    st.page_link("pages/10_Skill_Obsolescence.py", label="⚡ Skill Obsolescence")

st.markdown("""
<div class="page-hero">
    <div class="hero-title">💼 Career Intelligence Lab</div>
    <div class="hero-subtitle">Discover which sectors are growing, which are at risk, and what skills to build</div>
</div>""", unsafe_allow_html=True)


from src.api import simulate_scenario, ScenarioRequest

@st.cache_data(ttl=60)
def get_career_data(si, rr):
    try:
        req = ScenarioRequest(
            shock_intensity=si,
            shock_duration=2,
            recovery_rate=rr,
            forecast_horizon=6
        )
        return simulate_scenario(req)
    except Exception as e:
        print(f"Error calling simulate_scenario: {e}")
    return None

data = get_career_data(shock_intensity, recovery_rate)
if not data:
    st.error("⚠️ Cannot connect to API. Start: `uvicorn src.api:app --reload`")
    st.stop()

career = data.get("career_advice", {})
sector_raw = data.get("sector_impact", [])
sector_df = pd.DataFrame(sector_raw) if sector_raw else pd.DataFrame()

growth_sectors  = career.get("growth_sectors", [])
risk_sectors    = career.get("risk_sectors", [])
skills          = career.get("recommended_skills", [])
narrative       = career.get("narrative", "No guidance available.")

# ─── KPI cards ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_kpi_card("🌱", "Growth Sectors", str(len(growth_sectors)), delta_type="down"), unsafe_allow_html=True)
with c2:
    st.markdown(render_kpi_card("⚠️", "Risk Sectors", str(len(risk_sectors)), delta_type="up"), unsafe_allow_html=True)
with c3:
    st.markdown(render_kpi_card("🎓", "Skills to Learn", str(len(skills)), delta_type="neutral"), unsafe_allow_html=True)
with c4:
    ew = data.get("indices", {}).get("early_warning", "🟢 Stable")
    st.markdown(render_kpi_card("🚦", "Market Outlook", ew.split(" ",1)[-1] if " " in ew else ew, delta_type="neutral"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Top row: Sector risk/growth + Skills chart ───────────────────────────────
col_l, col_r = st.columns([1, 1])

with col_l:
    
    st.markdown('<div class="section-title">📊 Sector Opportunity vs Risk</div>', unsafe_allow_html=True)

    if not sector_df.empty:
        sector_df_plot = sector_df.copy()
        # Normalize stress to 0-1 for plotting purposes
        sector_df_plot["Stress_Norm"] = sector_df_plot["Stress_Score"] / 100.0
        sector_df_plot["Opportunity"] = 1 - sector_df_plot["Stress_Norm"]
        sector_df_plot["Category"] = sector_df_plot.apply(
            lambda r: "🌱 Growth" if r["Resilience_Score"] > 60 and r["Stress_Score"] < 40 else "⚠️ Risk" if r["Stress_Score"] > 60 else "⚖️ Neutral", axis=1
        )
        color_map = {"🌱 Growth": "#10b981", "⚠️ Risk": "#ef4444", "⚖️ Neutral": "#f59e0b"}
        fig_bub = px.scatter(
            sector_df_plot,
            x="Resilience_Score", y="Stress_Score",
            size="Opportunity",
            color="Category",
            text="Sector",
            color_discrete_map=color_map,
            size_max=50,
            range_x=[0, 100], range_y=[0, 100]
        )
        fig_bub.update_traces(
            textfont=dict(color="white", size=10),
            textposition="top center",
            marker=dict(line=dict(width=1, color="rgba(255,255,255,0.2)")),
        )
        fig_bub.update_layout(**plotly_dark_layout(height=340, showlegend=True))
        fig_bub.update_xaxes(title_text="Resilience Score", gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#64748b"))
        fig_bub.update_yaxes(title_text="Stress Score", gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#64748b"))
        st.plotly_chart(fig_bub, use_container_width=True)
    else:
        st.info("Sector data not available")
    st.markdown("</div>", unsafe_allow_html=True)

with col_r:
    
    st.markdown('<div class="section-title">🎓 In-Demand Skills Ranking</div>', unsafe_allow_html=True)
    
    # Get real-time skill demand data
    skill_demand_data = career.get("skill_demand_data", {})
    
    # Debug: Show what data we received
    # st.write("DEBUG - skill_demand_data keys:", list(skill_demand_data.keys()) if skill_demand_data else "None")
    # st.write("DEBUG - skills list:", skills[:3] if skills else "None")
    
    if skill_demand_data and skill_demand_data.get("skills"):
        # Use real-time data from Adzuna API
        skills_data = skill_demand_data["skills"]
        skill_df = pd.DataFrame(skills_data)
        
        # Display data source label
        data_source = skill_demand_data.get("data_source", "Unknown")
        algorithm = skill_demand_data.get("algorithm", "")
        
        if "Adzuna" in data_source:
            st.caption("📡 Skill demand based on real-time job market data (Adzuna API, log-normalized, keyword-expanded)")
        elif "INSUFFICIENT" in data_source:
            st.caption("⚠️ Adzuna API unavailable - Configure credentials in Streamlit secrets")
        else:
            st.caption("⚠️ Using cached data - Adzuna API unavailable")
        
        # Create bar chart with real demand scores
        fig_skill = go.Figure(go.Bar(
            x=skill_df["demand"],
            y=skill_df["name"],
            orientation="h",
            marker=dict(
                color=skill_df["demand"],
                colorscale=[[0, "#312e81"], [0.5, "#6366f1"], [1, "#06b6d4"]],
                line=dict(width=0),
            ),
            text=[f"{v:.0%}" for v in skill_df["demand"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0"),
            customdata=skill_df[["job_count", "avg_salary"]],
            hovertemplate="<b>%{y}</b><br>" +
                         "Demand Score: %{x:.1%}<br>" +
                         "Job Count: %{customdata[0]}<br>" +
                         "Avg Salary: ₹%{customdata[1]:,.0f}<br>" +
                         "<extra></extra>"
        ))
        fig_skill.update_layout(**plotly_dark_layout(height=340, showlegend=False, margin=dict(l=10, r=60, t=10, b=10)))
        fig_skill.update_xaxes(range=[0, 1.2], title_text="Demand Score (Real-Time)", showgrid=True, gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#64748b"))
        fig_skill.update_yaxes(title_text="", gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#64748b"))
        st.plotly_chart(fig_skill, use_container_width=True)
        
        # Show methodology
        with st.expander("📊 How demand is calculated"):
            st.markdown("""
            **Advanced Real-Time Demand Score Formula:**
            ```
            Demand = (0.5 × log_job_score) + (0.3 × salary_score) + (0.2 × recency_score)
            ```
            
            **Components:**
            - **Job Count (50%):** Log-scaled job count to prevent dominance
              - Formula: `log(job_count + 1) / log(max_job_count + 1)`
            - **Salary (30%):** Average salary offered (linear scaling)
            - **Recency (20%):** Percentage of recent postings (last 30 days)
            
            **Smart Keyword Expansion:**
            - Base keywords: 2-3 anchor terms per skill (e.g., "machine learning engineer")
            - Expanded keywords: Hidden variations detected in job descriptions
              - AI/ML: "nlp", "computer vision", "deep learning", "llm", "gpt"
              - Cloud: "aws", "azure", "gcp", "kubernetes", "docker"
              - Cybersecurity: "infosec", "penetration testing", "soc analyst"
            - Avoids double counting: Base matches prioritized over expanded matches
            
            **Why Log Scaling?**
            - Prevents single high-volume skill from dominating unfairly
            - Creates balanced distribution across all skills
            - Compresses range while preserving relative ordering
            
            **Data Source:** Adzuna Job Search API (India)  
            **Update Frequency:** Hourly (with 1-hour cache)  
            **No fake data:** All scores based on real job market analysis
            """)
    elif skills:
        # Fallback: Show skills without fake scores
        st.warning("⚠️ Real-time skill demand unavailable")
        
        # Check if API credentials are configured
        import os
        has_api_id = bool(os.getenv("ADZUNA_APP_ID"))
        has_api_key = bool(os.getenv("ADZUNA_APP_KEY"))
        
        if not has_api_id or not has_api_key:
            st.info("💡 **To enable real-time data:** Configure ADZUNA_APP_ID and ADZUNA_APP_KEY in Streamlit secrets")
            with st.expander("🔧 How to configure"):
                st.markdown("""
                **Step 1:** Get free API key from https://developer.adzuna.com/
                
                **Step 2:** In Streamlit Cloud dashboard:
                - Go to app settings
                - Click "Secrets"
                - Add:
                ```toml
                ADZUNA_APP_ID = "your_app_id"
                ADZUNA_APP_KEY = "your_app_key"
                ```
                - Save and restart app
                """)
        
        st.caption("📋 Showing recommended skills (ranked by sector growth)")
        
        # Show skills as simple list (no fake percentages)
        for idx, skill in enumerate(skills[:10]):
            st.markdown(f"""
            <div style="padding:0.5rem; border-bottom:1px solid rgba(255,255,255,0.05);">
                <span style="color:#64748b; font-weight:600;">{idx+1}.</span>
                <span style="color:#e2e8f0; margin-left:0.5rem;">{skill}</span>
                <span style="color:#64748b; font-size:0.85rem; margin-left:0.5rem;">(from growth sectors)</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No skills data available")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Sector cards: growth vs risk ────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_g, col_rsk = st.columns(2)

with col_g:
    
    st.markdown('<div class="section-title">🌱 Growth Sectors</div>', unsafe_allow_html=True)
    if growth_sectors:
        for idx, s in enumerate(growth_sectors):
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.7rem; padding:0.7rem 0;
                        border-bottom:1px solid rgba(255,255,255,0.05);">
                <div style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3);
                            border-radius:50%; width:28px; height:28px; display:flex; align-items:center;
                            justify-content:center; font-size:0.75rem; font-weight:700; color:#10b981;">
                    {idx+1}
                </div>
                <div style="flex:1;">
                    <div style="color:#e2e8f0; font-weight:600; font-size:0.9rem;">{s}</div>
                </div>
                <span class="badge badge-success">Growing</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No growth sectors identified")
    st.markdown("</div>", unsafe_allow_html=True)

with col_rsk:
    
    st.markdown('<div class="section-title">⚠️ At-Risk Sectors</div>', unsafe_allow_html=True)
    if risk_sectors:
        for idx, s in enumerate(risk_sectors):
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.7rem; padding:0.7rem 0;
                        border-bottom:1px solid rgba(255,255,255,0.05);">
                <div style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3);
                            border-radius:50%; width:28px; height:28px; display:flex; align-items:center;
                            justify-content:center; font-size:0.75rem; font-weight:700; color:#ef4444;">
                    {idx+1}
                </div>
                <div style="flex:1;">
                    <div style="color:#e2e8f0; font-weight:600; font-size:0.9rem;">{s}</div>
                </div>
                <span class="badge badge-danger">At Risk</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No high-risk sectors identified")
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Skills wall + Career narrative ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col_sw, col_nar = st.columns([1, 1])

with col_sw:
    
    st.markdown('<div class="section-title">🏅 Your Skill Roadmap</div>', unsafe_allow_html=True)
    if skills:
        chips = "".join([f'<span class="skill-chip">{s}</span>' for s in skills])
        st.markdown(f'<div style="line-height:2.5; padding:0.5rem 0;">{chips}</div>', unsafe_allow_html=True)
    else:
        st.info("No skills data available")
    st.markdown("</div>", unsafe_allow_html=True)

with col_nar:
    
    st.markdown('<div class="section-title">📝 Career Guidance Narrative</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.15);
                border-radius:14px; padding:1.2rem; line-height:1.7;">
        <p style="color:#cbd5e1; font-size:0.92rem; margin:0;">{narrative}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
