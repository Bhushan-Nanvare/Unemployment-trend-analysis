"""
Page 0 — Help Guide
Comprehensive guide to all platform pages and features.
"""
import streamlit as st
from src.ui_helpers import DARK_CSS
from src.page_descriptions import PAGE_DESCRIPTIONS, get_recommended_journey

st.set_page_config(page_title="Help Guide | UIP", page_icon="❓", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ❓ Platform Help Guide")
    st.caption("Complete guide to all features and pages")
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
    st.page_link("pages/10_Skill_Obsolescence.py", label="📊 Skill Demand Analysis")
    st.page_link("pages/11_Phillips_Curve.py", label="📉 Phillips Curve")

st.markdown("""
<div class="page-hero">
    <div class="hero-title">❓ Platform Help Guide</div>
    <div class="hero-subtitle">
        Complete guide to understanding and using all features of the Unemployment Intelligence Platform
    </div>
</div>""", unsafe_allow_html=True)

# Quick Navigation
st.markdown('<div class="section-title">🚀 Quick Start</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.3);
                border-radius:12px; padding:1.5rem; margin-bottom:1rem;">
        <div style="font-size:1.2rem; margin-bottom:0.5rem;">👤 <strong>Individual Users</strong></div>
        <div style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
            Start with <strong>Job Risk Predictor</strong> → <strong>Career Lab</strong> → <strong>Skill Demand Analysis</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
                border-radius:12px; padding:1.5rem; margin-bottom:1rem;">
        <div style="font-size:1.2rem; margin-bottom:0.5rem;">🏛️ <strong>Policymakers</strong></div>
        <div style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
            Start with <strong>Overview</strong> → <strong>Simulator</strong> → <strong>Phillips Curve</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3);
                border-radius:12px; padding:1.5rem; margin-bottom:1rem;">
        <div style="font-size:1.2rem; margin-bottom:0.5rem;">📊 <strong>Researchers</strong></div>
        <div style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">
            Start with <strong>Overview</strong> → <strong>Phillips Curve</strong> → <strong>Sector Analysis</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Recommended Journey
st.markdown('<div class="section-title">🗺️ Recommended User Journey</div>', unsafe_allow_html=True)

journey = get_recommended_journey()

for i, step in enumerate(journey):
    if i % 3 == 0:
        cols = st.columns(3)
    
    with cols[i % 3]:
        page_info = PAGE_DESCRIPTIONS.get(step["page"], {})
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.1);
                    border-radius:10px; padding:1rem; margin-bottom:1rem; height:140px;">
            <div style="font-size:0.8rem; color:#6366f1; font-weight:700; margin-bottom:0.3rem;">
                STEP {step["step"]}
            </div>
            <div style="font-size:1rem; font-weight:700; margin-bottom:0.5rem; color:#e2e8f0;">
                {page_info.get("title", step["page"])}
            </div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.4;">
                {step["reason"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Detailed Page Descriptions
st.markdown('<div class="section-title">📚 Complete Page Reference</div>', unsafe_allow_html=True)

# Create tabs for different categories
tab1, tab2, tab3, tab4 = st.tabs(["📊 Core Analytics", "🎯 Personal Tools", "🏛️ Policy & Research", "🤖 Advanced Features"])

with tab1:
    st.markdown("### Core Analytics Pages")
    
    core_pages = ["Overview", "Job Market Pulse", "Sector Analysis"]
    
    for page_name in core_pages:
        if page_name in PAGE_DESCRIPTIONS:
            info = PAGE_DESCRIPTIONS[page_name]
            
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.2);
                        border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
                <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.8rem; color:#e2e8f0;">
                    {info["title"]}
                </div>
                <div style="font-size:0.95rem; color:#cbd5e1; margin-bottom:1rem; line-height:1.6;">
                    {info["description"]}
                </div>
                <div style="display:flex; gap:1rem; align-items:center;">
                    <div style="background:rgba(99,102,241,0.2); padding:0.3rem 0.8rem; border-radius:6px; font-size:0.8rem; color:#818cf8;">
                        👥 {info["use_case"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("### Personal Career Tools")
    
    personal_pages = ["Job Risk Predictor", "Career Lab", "Skill Demand Analysis", "Geo Career Advisor"]
    
    for page_name in personal_pages:
        if page_name in PAGE_DESCRIPTIONS:
            info = PAGE_DESCRIPTIONS[page_name]
            
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2);
                        border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
                <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.8rem; color:#e2e8f0;">
                    {info["title"]}
                </div>
                <div style="font-size:0.95rem; color:#cbd5e1; margin-bottom:1rem; line-height:1.6;">
                    {info["description"]}
                </div>
                <div style="display:flex; gap:1rem; align-items:center;">
                    <div style="background:rgba(16,185,129,0.2); padding:0.3rem 0.8rem; border-radius:6px; font-size:0.8rem; color:#34d399;">
                        👤 {info["use_case"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("### Policy & Research Tools")
    
    policy_pages = ["Simulator", "Phillips Curve"]
    
    for page_name in policy_pages:
        if page_name in PAGE_DESCRIPTIONS:
            info = PAGE_DESCRIPTIONS[page_name]
            
            st.markdown(f"""
            <div style="background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.2);
                        border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
                <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.8rem; color:#e2e8f0;">
                    {info["title"]}
                </div>
                <div style="font-size:0.95rem; color:#cbd5e1; margin-bottom:1rem; line-height:1.6;">
                    {info["description"]}
                </div>
                <div style="display:flex; gap:1rem; align-items:center;">
                    <div style="background:rgba(245,158,11,0.2); padding:0.3rem 0.8rem; border-radius:6px; font-size:0.8rem; color:#fbbf24;">
                        🏛️ {info["use_case"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    st.markdown("### Advanced Features")
    
    advanced_pages = ["AI Insights"]
    
    for page_name in advanced_pages:
        if page_name in PAGE_DESCRIPTIONS:
            info = PAGE_DESCRIPTIONS[page_name]
            
            st.markdown(f"""
            <div style="background:rgba(139,92,246,0.05); border:1px solid rgba(139,92,246,0.2);
                        border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
                <div style="font-size:1.3rem; font-weight:700; margin-bottom:0.8rem; color:#e2e8f0;">
                    {info["title"]}
                </div>
                <div style="font-size:0.95rem; color:#cbd5e1; margin-bottom:1rem; line-height:1.6;">
                    {info["description"]}
                </div>
                <div style="display:flex; gap:1rem; align-items:center;">
                    <div style="background:rgba(139,92,246,0.2); padding:0.3rem 0.8rem; border-radius:6px; font-size:0.8rem; color:#a78bfa;">
                        🤖 {info["use_case"]}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Key Features Summary
st.markdown('<div class="section-title">⭐ Key Platform Features</div>', unsafe_allow_html=True)

col_feat1, col_feat2 = st.columns(2)

with col_feat1:
    st.markdown("""
    ### 🔬 **Data & Technology**
    - **Real-time Data**: World Bank API integration with realistic India adjustments
    - **Machine Learning**: Advanced models for risk prediction and forecasting
    - **Economic Modeling**: Okun's Law, Phillips Curve, GDP-unemployment relationships
    - **AI Integration**: Groq LLaMA 3.1 for natural language insights
    - **Interactive Visualizations**: Plotly charts with zoom, hover, and export
    
    ### 📊 **Analysis Capabilities**
    - **29,000+ Job Postings**: Real market data analysis
    - **40+ Skills Tracking**: Comprehensive skill demand monitoring
    - **Multi-scenario Modeling**: Policy and shock simulation
    - **Geographic Analysis**: City-wise opportunities and cost of living
    - **Personal Risk Assessment**: Individual unemployment probability
    """)

with col_feat2:
    st.markdown("""
    ### 🎯 **User Benefits**
    - **Evidence-Based Decisions**: Data-driven career and policy choices
    - **Personalized Guidance**: Tailored recommendations for individuals
    - **Policy Impact Analysis**: Test interventions before implementation
    - **Market Intelligence**: Stay ahead of job market trends
    - **Risk Mitigation**: Identify and address unemployment vulnerabilities
    
    ### 🔧 **Technical Features**
    - **Export Capabilities**: Download analysis results as CSV
    - **Responsive Design**: Works on desktop, tablet, and mobile
    - **Performance Optimized**: Caching and efficient data loading
    - **Error Handling**: Graceful fallbacks when data unavailable
    - **Dark Theme**: Modern, professional interface design
    """)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# FAQ Section
st.markdown('<div class="section-title">❓ Frequently Asked Questions</div>', unsafe_allow_html=True)

with st.expander("🔍 **How accurate are the unemployment predictions?**"):
    st.markdown("""
    Our predictions use multiple approaches:
    - **Economic Model**: Based on GDP-unemployment relationships (Okun's Law) with India-specific coefficient
    - **Machine Learning**: Trained on 29,000+ real job postings for individual risk assessment
    - **Realistic Data**: We use curated India unemployment data that reflects actual economic conditions
    - **Confidence Intervals**: All forecasts include uncertainty bands to show prediction reliability
    
    The platform prioritizes transparency about data quality and model limitations.
    """)

with st.expander("📊 **What data sources do you use?**"):
    st.markdown("""
    - **Unemployment Data**: Curated realistic India trends (corrects World Bank API issues)
    - **GDP Data**: World Bank Open Data API (NY.GDP.MKTP.KD.ZG)
    - **Job Market Data**: 29,425 job postings from Indian job boards
    - **Geographic Data**: PLFS 2022-23 (Government of India) for state-level unemployment
    - **City Data**: Comprehensive India city reference with coordinates and cost of living
    
    All data sources are clearly labeled and quality indicators are provided.
    """)

with st.expander("🎯 **How do I use this for personal career planning?**"):
    st.markdown("""
    **Recommended workflow:**
    1. **Job Risk Predictor**: Assess your current unemployment risk
    2. **Career Lab**: Get personalized career guidance and transition recommendations
    3. **Skill Demand Analysis**: Evaluate your skills against market demand
    4. **Geo Career Advisor**: Consider location-based opportunities
    5. **Job Market Pulse**: Stay updated on market trends in your field
    
    Each tool provides specific, actionable recommendations for career development.
    """)

with st.expander("🏛️ **How can policymakers use this platform?**"):
    st.markdown("""
    **Key tools for policy analysis:**
    - **Simulator**: Test policy interventions (stimulus, training programs, benefits)
    - **Phillips Curve**: Analyze inflation-unemployment relationships for monetary policy
    - **Sector Analysis**: Identify vulnerable industries for targeted support
    - **Overview Dashboard**: Monitor real-time unemployment trends and recession risk
    
    All scenarios include quantitative metrics for policy effectiveness evaluation.
    """)

with st.expander("🔧 **What if I encounter technical issues?**"):
    st.markdown("""
    **Common solutions:**
    - **Slow loading**: First load takes 10-20 seconds due to data fetching - this is normal
    - **API offline warnings**: Platform automatically falls back to local data
    - **Charts not displaying**: Try refreshing the page or switching browsers
    - **Export not working**: Ensure pop-ups are enabled for CSV downloads
    
    The platform is designed with robust fallbacks to ensure functionality even when external APIs are unavailable.
    """)

st.markdown("</div>", unsafe_allow_html=True)

# Contact and Support
st.markdown('<div class="section-title">📞 Support & Contact</div>', unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
            border-radius:12px; padding:2rem; text-align:center;">
    <div style="font-size:1.2rem; font-weight:700; margin-bottom:1rem; color:#e2e8f0;">
        Need Help or Have Feedback?
    </div>
    <div style="color:#94a3b8; line-height:1.6; margin-bottom:1.5rem;">
        This platform is continuously evolving based on user needs and feedback.
        We welcome suggestions for new features, data sources, or analysis capabilities.
    </div>
    <div style="display:flex; gap:1rem; justify-content:center; flex-wrap:wrap;">
        <div style="background:rgba(99,102,241,0.2); padding:0.5rem 1rem; border-radius:8px; color:#818cf8;">
            📧 Platform Support
        </div>
        <div style="background:rgba(16,185,129,0.2); padding:0.5rem 1rem; border-radius:8px; color:#34d399;">
            💡 Feature Requests
        </div>
        <div style="background:rgba(245,158,11,0.2); padding:0.5rem 1rem; border-radius:8px; color:#fbbf24;">
            🐛 Bug Reports
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)