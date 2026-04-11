"""
Page 10 — Skill Demand Analysis (Fixed)

Analyzes skill demand patterns from job postings to identify high-demand vs low-demand skills.
Shows skill popularity, market demand, and provides career guidance based on current job market data.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.job_market_pulse import load_job_postings
from src.skill_obsolescence import analyze_skill_demand_patterns
from src.ui_helpers import DARK_CSS, plotly_dark_layout

st.set_page_config(page_title="Skill Analysis | UIP", page_icon="📊", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 Skill Demand Analysis")
    st.caption("Analyze skill popularity and market demand from job postings.")
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py", label="🎯 Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="📡 Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py", label="🗺️ Geo Career")

st.markdown("""
<div class="page-hero">
  <div class="hero-title">📊 Skill Demand Analysis</div>
  <div class="hero-subtitle">
    Discover which skills are in high demand, analyze market trends, and get personalized 
    career guidance based on current job market data from 29,000+ job postings.
  </div>
</div>
""", unsafe_allow_html=True)

# Load and analyze data automatically
df = load_job_postings()

if df.empty:
    st.error("No job postings data available. Please check the data source.")
    st.stop()

st.markdown(f"""
<div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.25);
            border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
    <div style="font-size:0.82rem; font-weight:700; color:#818cf8;
                text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
        📈 Data Source</div>
    <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
        Analyzing <strong style="color:#e2e8f0;">{len(df):,} job postings</strong> 
        from <strong style="color:#e2e8f0;">{df['post_date'].min().strftime('%B %Y')}</strong> 
        to identify skill demand patterns, popularity trends, and career opportunities.
    </div>
</div>
""", unsafe_allow_html=True)

# Analysis settings (simplified)
with st.expander("⚙️ Analysis Settings", expanded=False):
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        top_k = st.slider("Number of skills to analyze", 10, 50, 25, 5)
        min_mentions = st.slider("Minimum mentions required", 5, 100, 20, 5)
    with col_set2:
        demand_threshold = st.slider("High-demand threshold (%)", 1.0, 10.0, 3.0, 0.5)
        show_categories = st.multiselect(
            "Skill categories to show",
            ["High-Demand", "Moderate-Demand", "Low-Demand", "Emerging"],
            default=["High-Demand", "Moderate-Demand", "Low-Demand"]
        )

# Run analysis
with st.spinner("Analyzing skill demand patterns..."):
    analysis_results = analyze_skill_demand_patterns(
        df=df,
        top_k=top_k,
        min_mentions=min_mentions,
        demand_threshold=demand_threshold
    )

if analysis_results is None or analysis_results.empty:
    st.warning("Unable to analyze skill patterns. Please adjust the settings and try again.")
    st.stop()

# Filter by selected categories
if show_categories:
    analysis_results = analysis_results[analysis_results["category"].isin(show_categories)]

# ── KPI Summary ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Skill Market Overview</div>', unsafe_allow_html=True)

category_counts = analysis_results["category"].value_counts()
total_jobs = len(df)

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
with col_kpi1:
    high_demand = category_counts.get("High-Demand", 0)
    st.metric("🔥 High-Demand Skills", high_demand)
with col_kpi2:
    moderate_demand = category_counts.get("Moderate-Demand", 0)
    st.metric("📈 Moderate-Demand", moderate_demand)
with col_kpi3:
    low_demand = category_counts.get("Low-Demand", 0)
    st.metric("📉 Low-Demand", low_demand)
with col_kpi4:
    emerging = category_counts.get("Emerging", 0)
    st.metric("🌱 Emerging Skills", emerging)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Skill Demand Tables ───────────────────────────────────────────────────────
col_table1, col_table2 = st.columns(2)

with col_table1:
    st.markdown('<div class="section-title">🔥 High-Demand Skills</div>', unsafe_allow_html=True)
    high_demand_skills = analysis_results[analysis_results["category"] == "High-Demand"].head(15)
    
    if not high_demand_skills.empty:
        display_cols = ["skill", "mentions", "demand_percentage", "job_coverage", "avg_salary_lpa"]
        display_df = high_demand_skills[display_cols].copy()
        display_df.columns = ["Skill", "Mentions", "Demand %", "Job Coverage %", "Avg Salary (LPA)"]
        
        def style_high_demand(val):
            try:
                if float(val) >= 5.0:  # High demand threshold
                    return "background-color: rgba(239,68,68,0.15); color: #ef4444; font-weight: 700;"
            except:
                pass
            return ""
        
        st.dataframe(
            display_df.style.map(style_high_demand, subset=["Demand %"]),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No high-demand skills found with current settings.")
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_table2:
    st.markdown('<div class="section-title">📉 Skills to Watch</div>', unsafe_allow_html=True)
    low_demand_skills = analysis_results[analysis_results["category"] == "Low-Demand"].head(15)
    
    if not low_demand_skills.empty:
        display_cols = ["skill", "mentions", "demand_percentage", "job_coverage", "avg_salary_lpa"]
        display_df = low_demand_skills[display_cols].copy()
        display_df.columns = ["Skill", "Mentions", "Demand %", "Job Coverage %", "Avg Salary (LPA)"]
        
        def style_low_demand(val):
            try:
                if float(val) < 1.0:  # Low demand threshold
                    return "background-color: rgba(245,158,11,0.15); color: #f59e0b; font-weight: 700;"
            except:
                pass
            return ""
        
        st.dataframe(
            display_df.style.map(style_low_demand, subset=["Demand %"]),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No low-demand skills found with current settings.")
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Skill Demand Visualization ────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Skill Demand Landscape</div>', unsafe_allow_html=True)

# Create bubble chart
fig_bubble = px.scatter(
    analysis_results.head(30),
    x="demand_percentage",
    y="avg_salary_lpa",
    size="mentions",
    color="category",
    hover_name="skill",
    hover_data={"job_coverage": ":.1f", "mentions": True},
    color_discrete_map={
        "High-Demand": "#ef4444",
        "Moderate-Demand": "#f59e0b", 
        "Low-Demand": "#6b7280",
        "Emerging": "#10b981"
    },
    labels={
        "demand_percentage": "Market Demand (%)",
        "avg_salary_lpa": "Average Salary (LPA)",
        "mentions": "Total Mentions"
    }
)

fig_bubble.update_layout(**plotly_dark_layout(height=500))
fig_bubble.update_layout(
    xaxis_title="Market Demand (%)",
    yaxis_title="Average Salary (LPA)",
    legend_title="Skill Category"
)

st.plotly_chart(fig_bubble, use_container_width=True)
st.caption("Bubble size = total mentions · Position = (demand %, salary) · Color = demand category")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Personal Skills Analysis ──────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Your Skills Analysis</div>', unsafe_allow_html=True)
st.caption("Enter your skills to see how they rank in the current job market.")

user_skills_input = st.text_input(
    "Your skills (comma-separated)",
    placeholder="e.g. Python, JavaScript, SQL, React, AWS, Machine Learning",
    key="skill_analysis_input"
)

if user_skills_input.strip():
    user_skills = [s.strip().lower() for s in user_skills_input.split(",") if s.strip()]
    
    # Match user skills with analysis results
    skill_analysis_map = analysis_results.set_index("skill").to_dict("index")
    user_analysis = []
    
    for user_skill in user_skills:
        matched_skill = None
        best_match = None
        
        # Try exact match first
        for analyzed_skill in skill_analysis_map.keys():
            if user_skill == analyzed_skill.lower():
                matched_skill = analyzed_skill
                break
        
        # Try partial match
        if not matched_skill:
            for analyzed_skill in skill_analysis_map.keys():
                if user_skill in analyzed_skill.lower() or analyzed_skill.lower() in user_skill:
                    matched_skill = analyzed_skill
                    break
        
        if matched_skill:
            skill_data = skill_analysis_map[matched_skill]
            user_analysis.append({
                "Your Skill": user_skill.title(),
                "Matched To": matched_skill,
                "Category": skill_data["category"],
                "Demand %": skill_data["demand_percentage"],
                "Avg Salary": skill_data["avg_salary_lpa"],
                "Job Coverage %": skill_data["job_coverage"]
            })
        else:
            user_analysis.append({
                "Your Skill": user_skill.title(),
                "Matched To": "Not found",
                "Category": "Unknown",
                "Demand %": 0,
                "Avg Salary": 0,
                "Job Coverage %": 0
            })
    
    if user_analysis:
        user_df = pd.DataFrame(user_analysis)
        
        def style_user_category(val):
            color_map = {
                "High-Demand": "background-color: rgba(239,68,68,0.15); color: #ef4444; font-weight: 700;",
                "Moderate-Demand": "background-color: rgba(245,158,11,0.15); color: #f59e0b; font-weight: 700;",
                "Low-Demand": "background-color: rgba(107,114,128,0.15); color: #6b7280;",
                "Emerging": "background-color: rgba(16,185,129,0.15); color: #10b981; font-weight: 700;",
                "Unknown": "color: #9ca3af; font-style: italic;"
            }
            return color_map.get(str(val), "")
        
        st.dataframe(
            user_df.style.map(style_user_category, subset=["Category"]),
            use_container_width=True, hide_index=True
        )
        
        # Provide recommendations
        high_demand_skills = [row["Your Skill"] for row in user_analysis if row["Category"] == "High-Demand"]
        low_demand_skills = [row["Your Skill"] for row in user_analysis if row["Category"] == "Low-Demand"]
        unknown_skills = [row["Your Skill"] for row in user_analysis if row["Category"] == "Unknown"]
        
        if high_demand_skills:
            st.success(f"🔥 **High-demand skills in your portfolio:** {', '.join(high_demand_skills)}")
        
        if low_demand_skills:
            st.warning(f"📉 **Skills with lower market demand:** {', '.join(low_demand_skills)}")
        
        if unknown_skills:
            st.info(f"❓ **Skills not found in dataset:** {', '.join(unknown_skills)}")
        
        # Career recommendations
        st.markdown("**💡 Career Recommendations:**")
        if len(high_demand_skills) >= 2:
            st.markdown("- ✅ You have strong high-demand skills - focus on deepening expertise")
        elif len(high_demand_skills) == 1:
            st.markdown("- 🎯 Consider adding complementary high-demand skills to your portfolio")
        else:
            st.markdown("- 🚀 Consider learning high-demand skills from the analysis above")
        
        if low_demand_skills:
            st.markdown("- 📈 Consider upgrading or complementing lower-demand skills")
        
        avg_salary = sum(row["Avg Salary"] for row in user_analysis if row["Avg Salary"] > 0)
        if avg_salary > 0:
            avg_salary = avg_salary / len([row for row in user_analysis if row["Avg Salary"] > 0])
            st.markdown(f"- 💰 Your skills average salary potential: **{avg_salary:.1f} LPA**")

else:
    st.info("Enter your skills above to get personalized market analysis.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Export Results ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📥 Export Analysis</div>', unsafe_allow_html=True)

export_data = analysis_results.copy()
export_csv = export_data.to_csv(index=False)

st.download_button(
    label="⬇️ Download Skill Analysis (CSV)",
    data=export_csv.encode(),
    file_name="skill_demand_analysis.csv",
    mime="text/csv"
)

st.caption(f"Analysis based on {len(df):,} job postings · {len(analysis_results)} skills analyzed")
st.markdown("</div>", unsafe_allow_html=True)