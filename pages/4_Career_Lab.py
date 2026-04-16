"""
Page 4 â€” Career Lab
Skill demand chart, growth vs risk bubble chart, career path cards.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, plotly_dark_layout, API_BASE_URL

st.set_page_config(page_title="Career Lab | UIP", page_icon="ðŸ’¼", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ðŸ’¼ Career Lab")
    shock_intensity = st.slider("Shock Intensity", 0.0, 0.6, 0.3, 0.05)
    recovery_rate   = st.slider("Recovery Rate", 0.05, 0.6, 0.3, 0.05)
    st.markdown("---")
    st.markdown("**ðŸŒ Navigation**")
    st.page_link("app.py", label="ðŸ  Home")
    st.page_link("pages/0_Help_Guide.py", label="â“ Help Guide")
    st.page_link("pages/1_Overview.py", label="ðŸ“Š Overview")
    st.page_link("pages/2_Simulator.py", label="ðŸ§ª Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="ðŸ­ Sector Analysis")
    st.page_link("pages/5_AI_Insights.py", label="ðŸ¤– AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py", label="ðŸŽ¯ Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="ðŸ“¡ Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py", label="ðŸ—ºï¸ Geo Career")

st.markdown("""
<div class="page-hero">
    <div class="hero-title">ðŸ’¼ Career Intelligence Lab</div>
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
    st.error("âš ï¸ Cannot connect to API. Start: `uvicorn src.api:app --reload`")
    st.stop()

career = data.get("career_advice", {})
sector_raw = data.get("sector_impact", [])
sector_df = pd.DataFrame(sector_raw) if sector_raw else pd.DataFrame()

growth_sectors  = career.get("growth_sectors", [])
risk_sectors    = career.get("risk_sectors", [])
skills          = career.get("recommended_skills", [])
narrative       = career.get("narrative", "No guidance available.")

# â”€â”€â”€ KPI cards â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(render_kpi_card("ðŸŒ±", "Growth Sectors", str(len(growth_sectors)), delta_type="down"), unsafe_allow_html=True)
with c2:
    st.markdown(render_kpi_card("âš ï¸", "Risk Sectors", str(len(risk_sectors)), delta_type="up"), unsafe_allow_html=True)
with c3:
    st.markdown(render_kpi_card("ðŸŽ“", "Skills to Learn", str(len(skills)), delta_type="neutral"), unsafe_allow_html=True)
with c4:
    ew = data.get("indices", {}).get("early_warning", "ðŸŸ¢ Stable")
    st.markdown(render_kpi_card("ðŸš¦", "Market Outlook", ew.split(" ",1)[-1] if " " in ew else ew, delta_type="neutral"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# â”€â”€â”€ Top row: Sector risk/growth + Skills chart â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
col_l, col_r = st.columns([1, 1])

with col_l:
    
    st.markdown('<div class="section-title">ðŸ“Š Sector Opportunity vs Risk</div>', unsafe_allow_html=True)

    if not sector_df.empty:
        sector_df_plot = sector_df.copy()
        # Normalize stress to 0-1 for plotting purposes
        sector_df_plot["Stress_Norm"] = sector_df_plot["Stress_Score"] / 100.0
        sector_df_plot["Opportunity"] = 1 - sector_df_plot["Stress_Norm"]
        sector_df_plot["Category"] = sector_df_plot.apply(
            lambda r: "ðŸŒ± Growth" if r["Resilience_Score"] > 60 and r["Stress_Score"] < 40 else "âš ï¸ Risk" if r["Stress_Score"] > 60 else "âš–ï¸ Neutral", axis=1
        )
        color_map = {"ðŸŒ± Growth": "#10b981", "âš ï¸ Risk": "#ef4444", "âš–ï¸ Neutral": "#f59e0b"}
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

with col_r:
    
    st.markdown('<div class="section-title">ðŸŽ“ In-Demand Skills Ranking</div>', unsafe_allow_html=True)
    
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
        
        if "Adzuna" in data_source and "dynamic extraction" in data_source:
            st.caption("ðŸ“¡ Skill demand dynamically extracted from real job postings (Adzuna API)")
        elif "INSUFFICIENT" in data_source:
            st.caption("âš ï¸ Adzuna API unavailable - Configure credentials in Streamlit secrets")
        else:
            st.caption("âš ï¸ Using cached data - Adzuna API unavailable")
        
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
                         "Avg Salary: â‚¹%{customdata[1]:,.0f}<br>" +
                         "<extra></extra>"
        ))
        fig_skill.update_layout(**plotly_dark_layout(height=340, showlegend=False, margin=dict(l=10, r=60, t=10, b=10)))
        fig_skill.update_xaxes(range=[0, 1.2], title_text="Demand Score (Real-Time)", showgrid=True, gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#64748b"))
        fig_skill.update_yaxes(title_text="", gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.08)", tickfont=dict(color="#64748b"))
        st.plotly_chart(fig_skill, use_container_width=True)
        
        # Show methodology
        with st.expander("ðŸ“Š How skills are detected"):
            st.markdown("""
            **Dynamic Skill Detection Algorithm:**
            
            **Phase 1: Data Collection**
            - Fetch 1,000+ job postings from Adzuna API
            - Use broad queries: "software engineer", "developer", "data", "analyst", "engineer"
            - Multiple pages per query for comprehensive coverage
            
            **Phase 2: Text Extraction**
            - Extract title and description from each job
            - Combine into text corpus for analysis
            
            **Phase 3: Skill Extraction**
            - Detect skills using keyword pattern matching
            - Count frequency of each skill mention
            - Track which jobs mention each skill
            - Calculate salary data per skill
            
            **Phase 4: Normalization**
            - Apply log scaling to prevent dominance:
              ```
              freq_score = log(frequency + 1) / log(max_frequency + 1)
              demand_score = (0.5 Ã— freq_score) + (0.3 Ã— salary_score) + (0.2 Ã— recency_score)
              ```
            
            **Phase 5: Ranking**
            - Sort skills by demand score (descending)
            - Return top 15-20 trending skills
            
            **Key Advantages:**
            - âœ… **No predefined lists** - Automatically discovers trending skills
            - âœ… **Future-proof** - Adapts to market changes automatically
            - âœ… **Real job data** - Based on actual job postings, not assumptions
            - âœ… **Hourly updates** - Reflects current market trends
            
            **Data Source:** Adzuna Job Search API (India)  
            **Update Frequency:** Hourly (with 1-hour cache)  
            **Jobs Analyzed:** 1,000+ per refresh  
            **Detection Method:** Frequency analysis with log-scaled normalization
            """)
    elif skills:
        # Fallback: Show skills without fake scores
        st.warning("âš ï¸ Real-time skill demand unavailable")
        
        # Check if API credentials are configured
        import os
        has_api_id = bool(os.getenv("ADZUNA_APP_ID"))
        has_api_key = bool(os.getenv("ADZUNA_APP_KEY"))
        
        if not has_api_id or not has_api_key:
            st.info("ðŸ’¡ **To enable real-time data:** Configure ADZUNA_APP_ID and ADZUNA_APP_KEY in Streamlit secrets")
            with st.expander("ðŸ”§ How to configure"):
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
        
        st.caption("ðŸ“‹ Showing recommended skills (ranked by sector growth)")
        
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

# â”€â”€â”€ Sector cards: growth vs risk â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("<br>", unsafe_allow_html=True)
col_g, col_rsk = st.columns(2)

with col_g:
    
    st.markdown('<div class="section-title">ðŸŒ± Growth Sectors</div>', unsafe_allow_html=True)
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

with col_rsk:
    
    st.markdown('<div class="section-title">âš ï¸ At-Risk Sectors</div>', unsafe_allow_html=True)
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

# â”€â”€â”€ Skills wall + Career narrative â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("<br>", unsafe_allow_html=True)
col_sw, col_nar = st.columns([1, 1])

with col_sw:
    
    st.markdown('<div class="section-title">ðŸ… Your Skill Roadmap</div>', unsafe_allow_html=True)
    if skills:
        chips = "".join([f'<span class="skill-chip">{s}</span>' for s in skills])
        st.markdown(f'<div style="line-height:2.5; padding:0.5rem 0;">{chips}</div>', unsafe_allow_html=True)
    else:
        st.info("No skills data available")

with col_nar:
    
    st.markdown('<div class="section-title">ðŸ“ Career Guidance Narrative</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.15);
                border-radius:14px; padding:1.2rem; line-height:1.7;">
        <p style="color:#cbd5e1; font-size:0.92rem; margin:0;">{narrative}</p>
    </div>
    """, unsafe_allow_html=True)


# â”€â”€â”€ Personalized Career Roadmap â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<div class="section-title">ðŸ—ºï¸ Personalized Career Roadmap Generator</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#94a3b8; font-size:0.9rem; margin-bottom:1.5rem;">Generate a step-by-step learning path based on your profile and real-time job market trends</p>', unsafe_allow_html=True)

from src.career_roadmap_generator import generate_career_roadmap, get_available_roles

# Roadmap input form
with st.form("roadmap_form"):
    col_form1, col_form2, col_form3 = st.columns(3)
    
    with col_form1:
        user_level = st.selectbox(
            "Your Experience Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=1
        )
    
    with col_form2:
        target_role = st.selectbox(
            "Target Role",
            get_available_roles(),
            index=0
        )
    
    with col_form3:
        st.markdown('<p style="color:#94a3b8; font-size:0.85rem; margin-bottom:0.3rem;">Known Skills (comma-separated)</p>', unsafe_allow_html=True)
        known_skills_input = st.text_input(
            "Known Skills",
            value="Python, SQL",
            label_visibility="collapsed"
        )
    
    submit_button = st.form_submit_button("ðŸš€ Generate My Roadmap", use_container_width=True)

if submit_button:
    # Parse known skills
    known_skills = [s.strip() for s in known_skills_input.split(",") if s.strip()]
    
    # Generate roadmap
    with st.spinner("ðŸ” Analyzing job market trends and generating your personalized roadmap..."):
        roadmap_data = generate_career_roadmap(
            user_level=user_level,
            known_skills=known_skills,
            target_role=target_role
        )
    
    # Display roadmap
    if roadmap_data["roadmap_steps"]:
        st.success(f"âœ… Personalized roadmap generated for **{target_role}** ({user_level} level)")
        
        # Summary metrics
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Missing Skills", len(roadmap_data["missing_skills"]))
        with col_m2:
            st.metric("Learning Steps", len([s for s in roadmap_data["roadmap_steps"] if s["category"] != "project"]))
        with col_m3:
            st.metric("Projects", len([s for s in roadmap_data["roadmap_steps"] if s["category"] == "project"]))
        with col_m4:
            st.metric("Est. Duration", f"{roadmap_data['total_duration_months']} months")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Priority Skills (Trending)
        if roadmap_data["priority_skills"]:
            st.markdown("### ðŸ”¥ Priority Skills (Trending in Job Market)")
            priority_chips = "".join([
                f'<span style="display:inline-block; background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); '
                f'color:#fca5a5; padding:0.4rem 0.8rem; border-radius:8px; margin:0.3rem; font-size:0.85rem; font-weight:600;">'
                f'ðŸ”¥ {skill}</span>'
                for skill in roadmap_data["priority_skills"]
            ])
            st.markdown(f'<div style="line-height:2.5; padding:0.5rem 0;">{priority_chips}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Roadmap Steps
        st.markdown("### ðŸ“‹ Your Learning Roadmap")
        st.caption("ðŸ“¡ Personalized roadmap generated using your profile and real-time job market trends")
        
        # Group steps by category
        foundation_steps = [s for s in roadmap_data["roadmap_steps"] if s["category"] == "foundation"]
        intermediate_steps = [s for s in roadmap_data["roadmap_steps"] if s["category"] == "intermediate"]
        advanced_steps = [s for s in roadmap_data["roadmap_steps"] if s["category"] == "advanced"]
        project_steps = [s for s in roadmap_data["roadmap_steps"] if s["category"] == "project"]
        
        # Display each category
        if foundation_steps:
            st.markdown("#### ðŸŽ¯ Foundation Skills")
            for step in foundation_steps:
                priority_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#64748b"}[step["priority"]]
                trending_badge = "ðŸ”¥ TRENDING" if step["is_trending"] else ""
                
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:1rem; padding:0.8rem; 
                            background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
                            border-radius:10px; margin-bottom:0.5rem;">
                    <div style="background:{priority_color}20; border:1px solid {priority_color}40;
                                border-radius:50%; width:32px; height:32px; display:flex; align-items:center;
                                justify-content:center; font-size:0.8rem; font-weight:700; color:{priority_color};">
                        {step['step']}
                    </div>
                    <div style="flex:1;">
                        <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">{step['skill']}</div>
                        <div style="color:#64748b; font-size:0.8rem; margin-top:0.2rem;">
                            {step['weeks']} weeks Â· {step['priority'].upper()} priority {trending_badge}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        if intermediate_steps:
            st.markdown("#### ðŸš€ Intermediate Skills")
            for step in intermediate_steps:
                priority_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#64748b"}[step["priority"]]
                trending_badge = "ðŸ”¥ TRENDING" if step["is_trending"] else ""
                
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:1rem; padding:0.8rem; 
                            background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
                            border-radius:10px; margin-bottom:0.5rem;">
                    <div style="background:{priority_color}20; border:1px solid {priority_color}40;
                                border-radius:50%; width:32px; height:32px; display:flex; align-items:center;
                                justify-content:center; font-size:0.8rem; font-weight:700; color:{priority_color};">
                        {step['step']}
                    </div>
                    <div style="flex:1;">
                        <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">{step['skill']}</div>
                        <div style="color:#64748b; font-size:0.8rem; margin-top:0.2rem;">
                            {step['weeks']} weeks Â· {step['priority'].upper()} priority {trending_badge}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        if advanced_steps:
            st.markdown("#### ðŸ’Ž Advanced Skills")
            for step in advanced_steps:
                priority_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#64748b"}[step["priority"]]
                trending_badge = "ðŸ”¥ TRENDING" if step["is_trending"] else ""
                
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:1rem; padding:0.8rem; 
                            background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05);
                            border-radius:10px; margin-bottom:0.5rem;">
                    <div style="background:{priority_color}20; border:1px solid {priority_color}40;
                                border-radius:50%; width:32px; height:32px; display:flex; align-items:center;
                                justify-content:center; font-size:0.8rem; font-weight:700; color:{priority_color};">
                        {step['step']}
                    </div>
                    <div style="flex:1;">
                        <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">{step['skill']}</div>
                        <div style="color:#64748b; font-size:0.8rem; margin-top:0.2rem;">
                            {step['weeks']} weeks Â· {step['priority'].upper()} priority {trending_badge}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        if project_steps:
            st.markdown("#### ðŸŽ¨ Capstone Projects")
            for step in project_steps:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:1rem; padding:0.8rem; 
                            background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
                            border-radius:10px; margin-bottom:0.5rem;">
                    <div style="background:rgba(99,102,241,0.3); border:1px solid rgba(99,102,241,0.5);
                                border-radius:50%; width:32px; height:32px; display:flex; align-items:center;
                                justify-content:center; font-size:0.8rem; font-weight:700; color:#a5b4fc;">
                        {step['step']}
                    </div>
                    <div style="flex:1;">
                        <div style="color:#e2e8f0; font-weight:600; font-size:0.95rem;">{step['skill']}</div>
                        <div style="color:#94a3b8; font-size:0.8rem; margin-top:0.2rem;">
                            {step['weeks']} weeks Â· Portfolio project
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Methodology
        with st.expander("ðŸ“Š How this roadmap was generated"):
            st.markdown("""
            **9-Phase Personalized Roadmap Algorithm:**
            
            **Phase 1: Input Analysis**
            - Your experience level: Determines starting point
            - Known skills: Identifies what you already know
            - Target role: Defines required skill set
            
            **Phase 2: Role Requirements**
            - Lookup required skills for target role
            - Categorized by: Foundation â†’ Intermediate â†’ Advanced
            - Includes practical projects
            
            **Phase 3: Skill Gap Analysis**
            - Compare required skills vs your known skills
            - Identify missing skills you need to learn
            - Remove skills you already know
            
            **Phase 4: Trend Integration**
            - Fetch trending skills from job market (Adzuna API)
            - Check which missing skills are currently trending
            - Prioritize trending skills for faster job readiness
            
            **Phase 5: Roadmap Generation**
            - Create ordered learning path
            - Maintain logical dependencies (e.g., Python before ML)
            - Foundation â†’ Intermediate â†’ Advanced progression
            
            **Phase 6: Personalization**
            - **Beginner:** Start from foundation, cover all levels
            - **Intermediate:** Skip basics, focus on intermediate + advanced
            - **Advanced:** Focus on specialization + projects
            
            **Phase 7: Project Integration**
            - Add 2-3 capstone projects at the end
            - Projects match your target role
            - Build portfolio while learning
            
            **Phase 8: Timeline Estimation**
            - Foundation skills: 3 weeks each
            - Intermediate skills: 4 weeks each
            - Advanced skills: 4 weeks each
            - Projects: 4 weeks each
            
            **Phase 9: Output Formatting**
            - Structured step-by-step roadmap
            - Priority indicators (trending skills highlighted)
            - Estimated duration for planning
            
            **Key Features:**
            - âœ… **Personalized** - Based on YOUR profile
            - âœ… **Data-driven** - Uses real job market trends
            - âœ… **Logical** - Maintains skill dependencies
            - âœ… **Practical** - Includes hands-on projects
            - âœ… **Adaptive** - Adjusts to your experience level
            
            **Data Sources:**
            - Role requirements: Curated from industry standards
            - Trending skills: Adzuna API (1,000+ job postings analyzed)
            - Prioritization: Real-time job market demand scores
            """)
    
    else:
        st.info(f"ðŸŽ‰ Great news! You already know all required skills for **{target_role}**. Focus on building projects to showcase your expertise!")
        
        if roadmap_data["suggested_projects"]:
            st.markdown("### ðŸŽ¨ Suggested Projects")
            for i, project in enumerate(roadmap_data["suggested_projects"], 1):
                st.markdown(f"""
                <div style="padding:0.8rem; background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
                            border-radius:10px; margin-bottom:0.5rem;">
                    <div style="color:#e2e8f0; font-weight:600;">{i}. {project}</div>
                </div>
                """, unsafe_allow_html=True)
