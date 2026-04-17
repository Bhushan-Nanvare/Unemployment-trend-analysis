"""
Page 7 — AI-Based Job Risk Predictor (Feature 6)

User profile → ML risk estimate, feature contribution chart,
industry comparison, what-if skill simulation, and export report.
Runs entirely in-process (no FastAPI required).
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

from src.job_risk_model import (
    EDUCATION_LEVELS,
    FEATURE_NAMES,
    INDUSTRY_GROWTH,
    LOCATION_OPTIONS,
    predict_job_risk,
    what_if_improve_skills,
    get_model_info,
    parse_skills,
)
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, plotly_dark_layout
from src.risk_calculators import UserProfile
from src.risk_calculators.orchestrator import RiskCalculatorOrchestrator
from src.risk_calculators.time_prediction import TimePredictionCalculator
from src.analytics.salary_analyzer import SalaryAnalyzer
from src.analytics.benchmark_engine import BenchmarkEngine
from src.analytics.recommendation_engine import RecommendationEngine
from src.analytics.career_path_modeler import CareerPathModeler
from src.validation import ProfileValidator
from src.reporting import RiskMonitor
from src.ui_components.career_path_visualizer import CareerPathVisualizer

st.set_page_config(page_title="Job Risk (AI) | UIP", page_icon="🎯", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎯 Job Risk Predictor")
    st.markdown("---")
    
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py", label="❓ Help Guide")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")

    st.page_link("pages/8_Job_Market_Pulse.py", label="📡 Market Pulse")
    st.page_link("pages/9_Geo_Career_Advisor.py", label="🗺️ Geo Career")

st.markdown("""
<div class="page-hero">
    <div class="hero-title">🎯 AI Job Risk Predictor</div>
    <div class="hero-subtitle">
        Estimate unemployment-risk probability from skills, education, experience, industry, and location —
        with feature contributions, industry comparison, and what-if skill upgrades.
    </div>
</div>""", unsafe_allow_html=True)

# Session counter (kept for local analytics/debug, no pricing gate)
if 'risk_assessments_count' not in st.session_state:
    st.session_state.risk_assessments_count = 0

st.caption("🔍 Risk estimates trained on **real market demand data** (29,000+ job postings) — ground truths derive from salary benchmarks and hiring frequency trends.")

# Add model version info in an expander for debugging
with st.expander("🔧 Model Information (Debug)", expanded=False):
    model_info = get_model_info()
    st.caption(f"**Model Version:** {model_info['version']}")
    st.caption(f"**Training Samples:** {model_info['training_samples']:,}")
    st.caption(f"**Experience Coefficient:** {model_info['experience_coefficient']:.4f}")
    st.caption("*Negative coefficient means more experience reduces risk*")
    if model_info['experience_coefficient'] > -0.25:
        st.warning("⚠️ Old model detected! Experience coefficient is weak. Please refresh the page.")
    else:
        st.success("✅ Updated model loaded! Experience has strong impact.")



# ─── Profile Form ─────────────────────────────────────────────────────────────
col_form, col_out = st.columns([1, 1])

with col_form:
    
    st.markdown('<div class="section-title">Your profile</div>', unsafe_allow_html=True)
    skills = st.text_area(
        "Skills (comma-separated)",
        placeholder="e.g. Python, SQL, cloud computing, communication",
        height=100,
        help="We match phrases to an in-house demand lexicon to build a skill-demand score.",
    )
    education = st.selectbox("Education", EDUCATION_LEVELS, index=2)
    experience = st.slider("Years of experience", 0, 40, 3)
    industry = st.selectbox("Industry / sector", list(INDUSTRY_GROWTH.keys()))
    location = st.selectbox("Location (optional context)", LOCATION_OPTIONS)
    
    # Enhanced fields
    st.markdown("#### Additional Profile Details")
    age = st.slider("Age", 18, 80, 30, help="Your current age")
    
    role_level = st.selectbox(
        "Role Level",
        ["Entry", "Mid", "Senior", "Lead", "Executive"],
        index=1,
        help="Your current career level"
    )
    
    company_size = st.selectbox(
        "Company Size",
        ["1-10", "11-50", "51-200", "201-1000", "1001-5000", "5000+"],
        index=3,
        help="Number of employees at your company"
    )
    
    remote_capability = st.checkbox(
        "Remote Work Capable",
        value=True,
        help="Can you work remotely?"
    )
    
    performance_rating = st.slider(
        "Performance Rating",
        1, 5, 3,
        help="1=Below Average, 3=Average, 5=Top Performer"
    )
    
    run = st.button("🔮 Estimate risk", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">What-if: add skills</div>', unsafe_allow_html=True)
    extra_skills = st.text_input(
        "Skills to simulate adding",
        placeholder="e.g. machine learning, AWS",
        help="Appends to your profile and re-runs the model.",
    )
    run_whatif = st.button("⚡ Run what-if", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─── Results Panel ─────────────────────────────────────────────────────────────
with col_out:
    
    st.markdown('<div class="section-title">Results</div>', unsafe_allow_html=True)

    if run:
        # Increment usage counter (for demo purposes)
        st.session_state.risk_assessments_count += 1
        
        # Validate inputs
        validator = ProfileValidator()
        
        # Validate age
        age_valid, age_error = validator.validate_age(age)
        if not age_valid:
            st.error(f"❌ {age_error}")
            st.stop()
        
        # Validate experience
        exp_valid, exp_error = validator.validate_experience(experience, age)
        if not exp_valid:
            st.error(f"❌ {exp_error}")
            st.stop()
        
        # Validate performance rating
        perf_valid, perf_error = validator.validate_performance_rating(performance_rating)
        if not perf_valid:
            st.error(f"❌ {perf_error}")
            st.stop()
        
        # Validate required fields
        skills_list = parse_skills(skills)
        fields_valid, field_errors = validator.validate_required_fields(skills_list, industry, role_level)
        if not fields_valid:
            for error in field_errors:
                st.error(f"❌ {error}")
            st.stop()
        
        # Create user profile
        profile = UserProfile(
            skills=skills_list,
            industry=industry,
            role_level=role_level,
            experience_years=experience,
            education_level=education,
            location=location,
            age=age,
            company_size=company_size,
            remote_capability=remote_capability,
            performance_rating=performance_rating,
        )
        
        # Calculate all risks
        orchestrator = RiskCalculatorOrchestrator()
        risk_profile = orchestrator.calculate_all_risks(profile)
        
        # Calculate time-based predictions
        time_calc = TimePredictionCalculator()
        time_predictions = time_calc.predict_time_horizons(risk_profile, profile, assumes_learning=False)
        time_predictions_learning = time_calc.predict_time_horizons(risk_profile, profile, assumes_learning=True)
        
        # Calculate salary analysis
        salary_analyzer = SalaryAnalyzer()
        salary_estimate = salary_analyzer.analyze(profile, risk_profile)
        
        # Calculate benchmark (this may take a moment)
        with st.spinner("Generating peer comparison..."):
            benchmark_engine = BenchmarkEngine()
            peer_profiles = benchmark_engine.generate_peers(profile, count=100)
            peer_risks = [p.overall_risk for p in peer_profiles]
            benchmark_result = benchmark_engine.compute_benchmark(risk_profile.overall_risk, peer_risks)
        
        # Generate recommendations
        rec_engine = RecommendationEngine()
        recommendations = rec_engine.generate_recommendations(profile, risk_profile, salary_estimate.risk_adjusted)
        
        # Generate career paths
        with st.spinner("Analyzing career paths..."):
            career_modeler = CareerPathModeler()
            career_paths = career_modeler.generate_paths(profile)
        
        # Also get the detailed result for backward compatibility
        result = predict_job_risk(skills, education, experience, location, industry)
        
        # Store assessment in risk monitor
        risk_monitor = RiskMonitor()
        risk_monitor.store_assessment(risk_profile, user_id="default")
        
        st.session_state["last_job_risk"] = result
        st.session_state["risk_profile"] = risk_profile
        st.session_state["time_predictions"] = time_predictions
        st.session_state["time_predictions_learning"] = time_predictions_learning
        st.session_state["salary_estimate"] = salary_estimate
        st.session_state["benchmark_result"] = benchmark_result
        st.session_state["recommendations"] = recommendations
        st.session_state["career_paths"] = career_paths
        st.session_state["last_job_risk_inputs"] = {
            "skills": skills, "education": education,
            "experience": experience, "location": location, "industry": industry,
            "age": age, "role_level": role_level, "company_size": company_size,
            "remote_capability": remote_capability, "performance_rating": performance_rating,
        }

    if run_whatif:
        inp = st.session_state.get("last_job_risk_inputs")
        if inp:
            base_r, new_r, delta = what_if_improve_skills(
                inp["skills"], inp["education"], int(inp["experience"]),
                inp["location"], inp["industry"], extra_skills,
            )
            st.session_state["whatif"] = (base_r, new_r, delta)
        else:
            st.warning("Run **Estimate risk** first, then try what-if.")

    res = st.session_state.get("last_job_risk")
    risk_prof = st.session_state.get("risk_profile")
    
    if not res:
        st.info("Fill the form and click **Estimate risk**.")
    else:
        level_colors = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
        color = level_colors.get(res.risk_level, "#94a3b8")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Risk level", res.risk_level)
        with m2:
            st.metric("P(high risk)", f"{res.high_risk_probability_pct}%")
        with m3:
            st.markdown(
                f"<div style='margin-top:1.2rem;'><span style='color:{color};font-weight:700;'>"
                f"●</span> <span style='color:#94a3b8;font-size:0.85rem;'>"
                "High = modeled probability of being in a high-displacement-risk bucket</span></div>",
                unsafe_allow_html=True,
            )

        # Multi-Risk Dashboard (2x2 grid of gauges)
        if risk_prof:
            st.markdown("---")
            st.markdown("### 📊 Multi-Risk Dashboard")
            
            def create_gauge(title, value, color_hex):
                """Create a gauge chart"""
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=min(100, max(0, value)),
                    number={"suffix": "%", "font": {"color": "#e2e8f0", "size": 24}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                        "bar": {"color": color_hex},
                        "bgcolor": "rgba(255,255,255,0.04)",
                        "borderwidth": 0,
                        "steps": [
                            {"range": [0,  35], "color": "rgba(16,185,129,0.15)"},
                            {"range": [35, 62], "color": "rgba(245,158,11,0.12)"},
                            {"range": [62, 100],"color": "rgba(239,68,68,0.12)"},
                        ],
                    },
                    title={"text": title, "font": {"color": "#94a3b8", "size": 12}},
                ))
                fig.update_layout(**plotly_dark_layout(height=200))
                return fig
            
            # 2x2 grid
            row1_col1, row1_col2 = st.columns(2)
            row2_col1, row2_col2 = st.columns(2)
            
            with row1_col1:
                st.plotly_chart(
                    create_gauge("Overall Risk", risk_prof.overall_risk, "#6366f1"),
                    use_container_width=True
                )
            
            with row1_col2:
                st.plotly_chart(
                    create_gauge("Automation Risk", risk_prof.automation_risk, "#f59e0b"),
                    use_container_width=True
                )
            
            with row2_col1:
                st.plotly_chart(
                    create_gauge("Recession Risk", risk_prof.recession_risk, "#ef4444"),
                    use_container_width=True
                )
            
            with row2_col2:
                st.plotly_chart(
                    create_gauge("Age Discrimination Risk", risk_prof.age_discrimination_risk, "#8b5cf6"),
                    use_container_width=True
                )
            
            # Time Horizon Predictions
            time_preds = st.session_state.get("time_predictions")
            time_preds_learning = st.session_state.get("time_predictions_learning")
            
            if time_preds:
                st.markdown("---")
                st.markdown("### 📈 Risk Projections Over Time")
                
                # Toggle for learning assumption
                show_learning = st.checkbox(
                    "Assume continuous skill development",
                    value=False,
                    help="Shows how risk changes if you continuously learn new skills"
                )
                
                active_preds = time_preds_learning if show_learning else time_preds
                
                # Create line chart
                horizons = [p.horizon for p in active_preds]
                overall_risks = [p.overall_risk for p in active_preds]
                auto_risks = [p.automation_risk for p in active_preds]
                recession_risks = [p.recession_risk for p in active_preds]
                age_risks = [p.age_discrimination_risk for p in active_preds]
                
                fig_time = go.Figure()
                
                fig_time.add_trace(go.Scatter(
                    x=horizons, y=overall_risks,
                    mode='lines+markers',
                    name='Overall Risk',
                    line=dict(color='#6366f1', width=3),
                    marker=dict(size=8)
                ))
                
                fig_time.add_trace(go.Scatter(
                    x=horizons, y=auto_risks,
                    mode='lines+markers',
                    name='Automation Risk',
                    line=dict(color='#f59e0b', width=2),
                    marker=dict(size=6)
                ))
                
                fig_time.add_trace(go.Scatter(
                    x=horizons, y=recession_risks,
                    mode='lines+markers',
                    name='Recession Risk',
                    line=dict(color='#ef4444', width=2),
                    marker=dict(size=6)
                ))
                
                fig_time.add_trace(go.Scatter(
                    x=horizons, y=age_risks,
                    mode='lines+markers',
                    name='Age Discrimination',
                    line=dict(color='#8b5cf6', width=2),
                    marker=dict(size=6)
                ))
                
                layout_config = plotly_dark_layout(height=350)
                layout_config.update({
                    'title': dict(
                        text="Risk Trajectory" + (" (with continuous learning)" if show_learning else " (without skill development)"),
                        font=dict(color="#94a3b8", size=14)
                    ),
                    'xaxis_title': "Time Horizon",
                    'yaxis_title': "Risk Score (%)",
                    'hovermode': 'x unified'
                })
                layout_config['yaxis'].update({'range': [0, 100]})
                
                fig_time.update_layout(**layout_config)
                
                st.plotly_chart(fig_time, use_container_width=True)
                
                # Show key factors for each horizon
                with st.expander("🔍 Key Factors Driving Changes", expanded=False):
                    for pred in active_preds:
                        st.markdown(f"**{pred.horizon}**")
                        for factor in pred.key_factors:
                            st.markdown(f"- {factor}")
                        st.markdown("")
            
            # ── Salary Analysis ────────────────────────────────────────────
            salary_est = st.session_state.get("salary_estimate")
            if salary_est:
                st.markdown("---")
                st.markdown("### 💰 Salary Impact Analysis")
                st.caption("Estimate in Indian Rupees (INR) · Based on role level, industry, experience, and location.")

                col_sal1, col_sal2, col_sal3 = st.columns(3)
                with col_sal1:
                    st.metric("Base Salary", f"₹{salary_est.base_salary:,.0f}")
                with col_sal2:
                    st.metric(
                        "Location Adjusted",
                        f"₹{salary_est.location_adjusted:,.0f}",
                        f"{(salary_est.location_multiplier - 1) * 100:+.0f}%"
                    )
                with col_sal3:
                    st.metric(
                        "Risk Adjusted",
                        f"₹{salary_est.risk_adjusted:,.0f}",
                        f"-{salary_est.risk_penalty_pct:.1f}%" if salary_est.risk_penalty_pct > 0 else "No penalty"
                    )

                st.caption(
                    f"**80% Confidence Range:** "
                    f"₹{salary_est.confidence_interval[0]:,.0f} – ₹{salary_est.confidence_interval[1]:,.0f}"
                )

                with st.expander("📊 Salary Calculation Details", expanded=False):
                    st.markdown(salary_est.explanation)
            
            # Benchmark Comparison
            benchmark_res = st.session_state.get("benchmark_result")
            if benchmark_res:
                st.markdown("---")
                st.markdown("### 📊 Peer Comparison")
                
                st.info(benchmark_res.comparison_text)
                
                # Get user inputs for chart title
                user_inputs = st.session_state.get("last_job_risk_inputs", {})
                industry_label = user_inputs.get("industry", "your industry")
                role_label = user_inputs.get("role_level", "your level")
                
                # Distribution chart
                fig_bench = go.Figure()
                
                # Histogram of peer risks
                fig_bench.add_trace(go.Histogram(
                    x=benchmark_res.peer_distribution,
                    nbinsx=20,
                    name="Peer Distribution",
                    marker_color="rgba(99, 102, 241, 0.6)",
                    hovertemplate="Risk: %{x:.1f}%<br>Count: %{y}<extra></extra>"
                ))
                
                # User's position
                fig_bench.add_vline(
                    x=benchmark_res.user_risk,
                    line_dash="dash",
                    line_color="#10b981",
                    line_width=3,
                    annotation_text="You",
                    annotation_position="top"
                )
                
                # Percentile markers
                for label, value in benchmark_res.percentile_markers.items():
                    fig_bench.add_vline(
                        x=value,
                        line_dash="dot",
                        line_color="#64748b",
                        line_width=1,
                        annotation_text=label,
                        annotation_position="bottom",
                        annotation_font_size=10
                    )
                
                layout_config = plotly_dark_layout(height=300, showlegend=False)
                layout_config.update({
                    'title': dict(
                        text=f"Risk Distribution ({benchmark_res.peer_count} peers in {industry_label}, {role_label} level)",
                        font=dict(color="#94a3b8", size=13)
                    ),
                    'xaxis_title': "Overall Risk (%)",
                    'yaxis_title': "Number of Peers"
                })
                
                fig_bench.update_layout(**layout_config)
                
                st.plotly_chart(fig_bench, use_container_width=True)
            
            # Recommendations
            recs = st.session_state.get("recommendations")
            if recs:
                st.markdown("---")
                st.markdown("### 💡 Actionable Recommendations")
                
                for i, rec in enumerate(recs, 1):
                    priority_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                    priority_icon = priority_colors.get(rec.priority, "⚪")
                    
                    with st.expander(f"{priority_icon} {rec.action}", expanded=(i == 1)):
                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            st.metric("Risk Reduction", f"{rec.risk_reduction[0]}-{rec.risk_reduction[1]}%")
                        with col_r2:
                            st.metric("Salary Impact", f"₹{rec.salary_impact[0]:,} – ₹{rec.salary_impact[1]:,}")
                        with col_r3:
                            st.metric("Time to Implement", rec.time_to_implement)
                        
                        st.caption(f"**Priority:** {rec.priority} | **ROI Score:** {rec.roi_score:.2f}")
                        st.markdown(rec.explanation)
            
            # AI-Powered Career Path Modeler
            career_paths = st.session_state.get("career_paths")
            if career_paths:
                st.markdown("---")
                st.markdown("### 🚀 AI-Powered Career Path Recommendations")
                st.caption("Based on live job market data and your profile")
                
                # Test API connection indicator
                from src.data_providers.career_data_manager import CareerDataManager
                data_manager = CareerDataManager()
                api_working = data_manager.test_api_connection()
                
                if api_working:
                    st.success("✅ Live market data connected")
                else:
                    st.info("ℹ️ Using historical data (API unavailable)")
                
                # Career path visualizer
                visualizer = CareerPathVisualizer()
                
                # Path overview
                visualizer.render_path_overview(career_paths)
                
                # Path selector
                if career_paths:
                    selected_path_idx = visualizer.render_path_selector(career_paths)
                    selected_path = career_paths[selected_path_idx]
                    
                    # Detailed path view
                    col_path1, col_path2 = st.columns([2, 1])
                    
                    with col_path1:
                        visualizer.render_detailed_path(selected_path)
                    
                    with col_path2:
                        visualizer.render_action_plan(selected_path)
                        visualizer.render_salary_projection(selected_path)
                    
                    # Market comparison (if multiple paths)
                    if len(career_paths) > 1:
                        visualizer.render_market_comparison(career_paths)
                else:
                    st.info("No career paths available. Try adjusting your profile.")
            
            # Risk Monitoring Dashboard
            st.markdown("---")
            st.markdown("### 📊 Risk Monitoring Dashboard")
            
            risk_monitor = RiskMonitor()
            history = risk_monitor.get_history(user_id="default")
            
            if len(history) >= 2:
                # Display trend chart
                st.markdown("#### Risk Score Trends Over Time")
                
                # Extract data for chart
                timestamps = [h.timestamp for h in history]
                dates = [datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M") for ts in timestamps]
                overall_risks = [h.overall_risk for h in history]
                auto_risks = [h.automation_risk for h in history]
                recession_risks = [h.recession_risk for h in history]
                age_risks = [h.age_discrimination_risk for h in history]
                
                # Create line chart
                fig_monitor = go.Figure()
                
                fig_monitor.add_trace(go.Scatter(
                    x=dates, y=overall_risks,
                    mode='lines+markers',
                    name='Overall Risk',
                    line=dict(color='#6366f1', width=3),
                    marker=dict(size=8)
                ))
                
                fig_monitor.add_trace(go.Scatter(
                    x=dates, y=auto_risks,
                    mode='lines+markers',
                    name='Automation Risk',
                    line=dict(color='#f59e0b', width=2),
                    marker=dict(size=6)
                ))
                
                fig_monitor.add_trace(go.Scatter(
                    x=dates, y=recession_risks,
                    mode='lines+markers',
                    name='Recession Risk',
                    line=dict(color='#ef4444', width=2),
                    marker=dict(size=6)
                ))
                
                fig_monitor.add_trace(go.Scatter(
                    x=dates, y=age_risks,
                    mode='lines+markers',
                    name='Age Discrimination',
                    line=dict(color='#8b5cf6', width=2),
                    marker=dict(size=6)
                ))
                
                fig_monitor.update_layout(
                    **plotly_dark_layout(height=350),
                    title=dict(
                        text="Historical Risk Trends",
                        font=dict(color="#94a3b8", size=14)
                    ),
                    xaxis_title="Assessment Date",
                    yaxis_title="Risk Score (%)",
                    yaxis=dict(range=[0, 100]),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_monitor, use_container_width=True)
                
                # Rate of change metrics
                st.markdown("#### Rate of Change Analysis")
                rate_of_change = risk_monitor.compute_rate_of_change(user_id="default")
                
                col_roc1, col_roc2, col_roc3, col_roc4 = st.columns(4)
                
                with col_roc1:
                    roc_overall = rate_of_change["overall"]
                    st.metric(
                        "Overall Risk",
                        f"{roc_overall:+.2f} pts/mo",
                        delta=f"{roc_overall:+.2f}",
                        delta_color="inverse"
                    )
                
                with col_roc2:
                    roc_auto = rate_of_change["automation"]
                    st.metric(
                        "Automation Risk",
                        f"{roc_auto:+.2f} pts/mo",
                        delta=f"{roc_auto:+.2f}",
                        delta_color="inverse"
                    )
                
                with col_roc3:
                    roc_recession = rate_of_change["recession"]
                    st.metric(
                        "Recession Risk",
                        f"{roc_recession:+.2f} pts/mo",
                        delta=f"{roc_recession:+.2f}",
                        delta_color="inverse"
                    )
                
                with col_roc4:
                    roc_age = rate_of_change["age_discrimination"]
                    st.metric(
                        "Age Discrimination",
                        f"{roc_age:+.2f} pts/mo",
                        delta=f"{roc_age:+.2f}",
                        delta_color="inverse"
                    )
                
                # Generate rate of change summary text
                def format_rate_text(rate: float, risk_type: str) -> str:
                    """Format rate of change as human-readable text"""
                    if abs(rate) < 0.1:
                        return f"{risk_type} risk is stable"
                    elif rate > 0:
                        return f"{risk_type} risk is increasing by {abs(rate):.1f} points per month"
                    else:
                        return f"{risk_type} risk is decreasing by {abs(rate):.1f} points per month"
                
                st.caption(f"📈 {format_rate_text(roc_overall, 'Overall')}")
                
                # Significant changes
                significant_changes = risk_monitor.identify_significant_changes(user_id="default")
                
                if significant_changes:
                    st.markdown("#### ⚠️ Significant Changes Detected")
                    st.caption("Changes greater than 10 percentage points between consecutive assessments:")
                    
                    for change in significant_changes:
                        from_date = datetime.fromisoformat(change["from_timestamp"]).strftime("%Y-%m-%d")
                        to_date = datetime.fromisoformat(change["to_timestamp"]).strftime("%Y-%m-%d")
                        risk_type_label = change["risk_type"].replace("_", " ").title()
                        
                        direction_icon = "📈" if change["direction"] == "increased" else "📉"
                        direction_color = "red" if change["direction"] == "increased" else "green"
                        
                        st.markdown(
                            f"{direction_icon} **{risk_type_label}** {change['direction']} by "
                            f"**{abs(change['change']):.1f} points** "
                            f"({change['from_value']:.1f}% → {change['to_value']:.1f}%) "
                            f"from {from_date} to {to_date}"
                        )
                
            elif len(history) == 1:
                st.info("📊 Complete at least one more assessment to see risk trends over time.")
            else:
                st.info("📊 Complete your first risk assessment to start tracking trends.")

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=min(100, max(0, res.high_risk_probability_pct)),
            number={"suffix": "%", "font": {"color": "#e2e8f0"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                "bar": {"color": color},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  35], "color": "rgba(16,185,129,0.15)"},
                    {"range": [35, 62], "color": "rgba(245,158,11,0.12)"},
                    {"range": [62, 100],"color": "rgba(239,68,68,0.12)"},
                ],
            },
            title={"text": "High-risk probability", "font": {"color": "#94a3b8", "size": 14}},
        ))
        gauge.update_layout(**plotly_dark_layout(height=220))
        st.plotly_chart(gauge, use_container_width=True)

        st.markdown("**Engineered features**")
        feat = res.features
        fv = st.columns(len(FEATURE_NAMES))
        labels = {
            "skill_demand_score": "Skill demand",
            "industry_growth": "Industry growth",
            "experience_years": "Experience (yrs)",
            "education_level": "Education (0–4)",
            "location_risk_tier": "Location tier",
        }
        values = [
            feat["skill_demand_score"], feat["industry_growth"],
            feat["experience_years"], feat["education_level"], feat["location_risk_tier"],
        ]
        for i, name in enumerate(FEATURE_NAMES):
            with fv[i]:
                st.caption(labels[name])
                st.write(f"{values[i]:.2f}" if i < 2 else f"{values[i]:.1f}")

        if feat.get("matched_high_demand"):
            st.success("Matched in-demand keywords: **" + "**, **".join(feat["matched_high_demand"][:12]) + "**")
        elif feat.get("parsed_skills"):
            st.caption("No lexicon match — score inferred from profile breadth.")

        st.markdown("**Why this score**")
        for r in res.reasons:
            st.markdown(f"- {r}")
        st.markdown("**Suggestions**")
        for s in res.suggestions:
            st.markdown(f"- {s}")

    wf = st.session_state.get("whatif")
    if wf:
        base_r, new_r, delta = wf
        st.markdown("---")
        st.markdown("**What-if outcome**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Before", f"{base_r.high_risk_probability_pct}%")
        c2.metric("After", f"{new_r.high_risk_probability_pct}%")
        c3.metric("Change", f"{delta:+.1f} pp", delta_color="inverse")

        if new_r.contributions:
            # Show how contributions shifted
            labels_map = {
                "skill_demand_score": "Skill demand",
                "industry_growth":    "Industry growth",
                "experience_years":   "Experience",
                "education_level":    "Education",
                "location_risk_tier": "Location",
            }
            base_c = base_r.contributions or {}
            new_c  = new_r.contributions  or {}
            feat_labels = [labels_map.get(k, k) for k in FEATURE_NAMES]
            delta_vals  = [round(new_c.get(k, 0) - base_c.get(k, 0), 4) for k in FEATURE_NAMES]
            bar_colors  = ["#10b981" if v < 0 else "#ef4444" for v in delta_vals]
            fig_wi = go.Figure(go.Bar(
                x=feat_labels, y=delta_vals,
                marker_color=bar_colors,
                hovertemplate="%{x}: Δ%{y:.4f}<extra></extra>",
            ))
            fig_wi.add_hline(y=0, line=dict(color="#64748b", width=1, dash="dash"))
            fig_wi.update_layout(
                **plotly_dark_layout(height=200, showlegend=False),
                title=dict(text="Contribution shift after skill upgrade", font=dict(color="#94a3b8", size=13)),
                yaxis_title="Change in log-odds contribution",
            )
            st.plotly_chart(fig_wi, use_container_width=True)




# ─── Export Report ─────────────────────────────────────────────────────────────
inp = st.session_state.get("last_job_risk_inputs")


if res and inp:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📥 EXPORT COMPREHENSIVE RISK REPORT</div>', unsafe_allow_html=True)

    def _build_risk_report() -> bytes:
        risk_prof = st.session_state.get("risk_profile")
        salary_est = st.session_state.get("salary_estimate")
        benchmark_res = st.session_state.get("benchmark_result")
        recs = st.session_state.get("recommendations")
        time_preds = st.session_state.get("time_predictions")
        
        lines = [
            "=" * 80,
            "UNEMPLOYMENT INTELLIGENCE PLATFORM — COMPREHENSIVE JOB RISK ASSESSMENT",
            "=" * 80,
            "",
            "PROFILE SUMMARY",
            "-" * 80,
            f"  Skills       : {inp['skills'] or '(none provided)'}",
            f"  Education    : {inp['education']}",
            f"  Experience   : {inp['experience']} years",
            f"  Industry     : {inp['industry']}",
            f"  Location     : {inp['location']}",
            f"  Age          : {inp.get('age', 'N/A')}",
            f"  Role Level   : {inp.get('role_level', 'N/A')}",
            f"  Company Size : {inp.get('company_size', 'N/A')}",
            f"  Remote Work  : {'Yes' if inp.get('remote_capability') else 'No'}",
            f"  Performance  : {inp.get('performance_rating', 'N/A')}/5",
            "",
        ]
        
        if risk_prof:
            lines += [
                "MULTI-DIMENSIONAL RISK ASSESSMENT",
                "-" * 80,
                f"  Overall Risk            : {risk_prof.overall_risk:.1f}% ({risk_prof.risk_level})",
                f"  Automation Risk         : {risk_prof.automation_risk:.1f}%",
                f"  Recession Risk          : {risk_prof.recession_risk:.1f}%",
                f"  Age Discrimination Risk : {risk_prof.age_discrimination_risk:.1f}%",
                "",
            ]
        
        if time_preds:
            lines += [
                "RISK PROJECTIONS OVER TIME",
                "-" * 80,
            ]
            for pred in time_preds:
                lines.append(f"  {pred.horizon:12s}: Overall {pred.overall_risk:.1f}%, Auto {pred.automation_risk:.1f}%, Recession {pred.recession_risk:.1f}%")
            lines.append("")
        
        if salary_est:
            lines += [
                "SALARY ANALYSIS (INR — Indian Rupees)",
                "-" * 80,
                f"  Base Salary          : \u20b9{salary_est.base_salary:,.0f}",
                f"  Location Adjusted    : \u20b9{salary_est.location_adjusted:,.0f} ({salary_est.location_multiplier:.2f}x)",
                f"  Risk Adjusted        : \u20b9{salary_est.risk_adjusted:,.0f} (-{salary_est.risk_penalty_pct:.1f}%)",
                f"  Confidence Range     : \u20b9{salary_est.confidence_interval[0]:,.0f} \u2013 \u20b9{salary_est.confidence_interval[1]:,.0f}",
                "",
            ]
        
        if benchmark_res:
            lines += [
                "PEER COMPARISON",
                "-" * 80,
                f"  Your Risk Percentile : {benchmark_res.percentile:.1f}th",
                f"  {benchmark_res.comparison_text}",
                f"  25th Percentile      : {benchmark_res.percentile_markers['25th']:.1f}%",
                f"  50th Percentile      : {benchmark_res.percentile_markers['50th']:.1f}%",
                f"  75th Percentile      : {benchmark_res.percentile_markers['75th']:.1f}%",
                f"  90th Percentile      : {benchmark_res.percentile_markers['90th']:.1f}%",
                "",
            ]
        
        if recs:
            lines += [
                "TOP RECOMMENDATIONS (RANKED BY ROI)",
                "-" * 80,
            ]
            for i, rec in enumerate(recs, 1):
                lines += [
                    f"  {i}. {rec.action}",
                    f"     Priority: {rec.priority} | ROI Score: {rec.roi_score:.2f}",
                    f"     Risk Reduction: {rec.risk_reduction[0]}-{rec.risk_reduction[1]}%",
                    f"     Salary Impact: \u20b9{rec.salary_impact[0]:,}\u2013\u20b9{rec.salary_impact[1]:,}",
                    f"     Time: {rec.time_to_implement}",
                    f"     {rec.explanation}",
                    "",
                ]
        
        lines += [
            "ORIGINAL RISK ANALYSIS",
            "-" * 80,
            f"  Risk Level        : {res.risk_level}",
            f"  High-Risk Prob.   : {res.high_risk_probability_pct}%",
            "",
            "FEATURE VALUES",
            "-" * 80,
            f"  Skill Demand Score  : {res.features.get('skill_demand_score', 'N/A'):.2f}",
            f"  Industry Growth Idx : {res.features.get('industry_growth', 'N/A'):.2f}",
            f"  Experience (yrs)    : {res.features.get('experience_years', 'N/A'):.0f}",
            f"  Education (0–4)     : {res.features.get('education_level', 'N/A'):.0f}",
            f"  Location Tier       : {res.features.get('location_risk_tier', 'N/A'):.0f}",
        ]
        lines += ["", "WHY THIS SCORE", "-" * 80]
        for r in res.reasons:
            lines.append(f"  - {r}")
        lines += ["", "SUGGESTIONS", "-" * 80]
        for s in res.suggestions:
            lines.append(f"  - {s}")
        
        lines += ["", "=" * 80, "Generated by Unemployment Intelligence Platform", "=" * 80]
        return "\n".join(lines).encode("utf-8")

    st.download_button(
        label="⬇️ Download Comprehensive Risk Assessment Report (.txt)",
        data=_build_risk_report(),
        file_name="uip_comprehensive_risk_report.txt",
        mime="text/plain",
    )
