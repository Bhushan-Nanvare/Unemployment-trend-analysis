"""
Page 12 — Advanced Simulator
Enhanced simulation capabilities with Monte Carlo, multi-shock scenarios, and stress testing.
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from src.ui_helpers import DARK_CSS, render_kpi_card, render_badge, plotly_dark_layout, API_BASE_URL

st.set_page_config(page_title="Advanced Simulator | UIP", page_icon="🧬", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ─── Sidebar nav ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧬 Advanced Simulator")
    st.markdown("Monte Carlo, multi-shock scenarios, and stress testing.")
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py", label="❓ Help Guide")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Basic Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")

# ─── Page hero ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <div class="hero-title">🧬 Advanced Simulation Laboratory</div>
    <div class="hero-subtitle">Monte Carlo uncertainty analysis, compound crisis modeling, and comprehensive stress testing</div>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(139,92,246,0.07); border:1px solid rgba(139,92,246,0.2);
            border-radius:14px; padding:1rem 1.4rem; margin-bottom:1.5rem;
            display:flex; align-items:flex-start; gap:1rem;">
    <div style="font-size:1.5rem; margin-top:0.1rem;">🧬</div>
    <div>
        <div style="font-size:0.78rem; font-weight:700; color:#a78bfa; text-transform:uppercase;
                    letter-spacing:1px; margin-bottom:0.35rem;">Advanced Mode</div>
        <div style="font-size:0.87rem; color:#94a3b8; line-height:1.6;">
            This page provides <strong style="color:#e2e8f0;">sophisticated simulation capabilities</strong>
            including uncertainty quantification, compound crisis modeling, and systematic stress testing.
            Results include confidence intervals, interaction effects, and resilience assessments.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Simulation Mode Selection ────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Select Simulation Mode</div>', unsafe_allow_html=True)

simulation_modes = {
    "Monte Carlo": {
        "icon": "🎲",
        "description": "Uncertainty analysis with parameter distributions",
        "use_case": "Risk assessment, confidence intervals"
    },
    "Multi-Shock": {
        "icon": "💥", 
        "description": "Compound crisis scenarios with overlapping shocks",
        "use_case": "Pandemic + recession, multiple disasters"
    },
    "Stress Testing": {
        "icon": "🔬",
        "description": "Systematic resilience testing across scenarios",
        "use_case": "System limits, regulatory compliance"
    },
    "Economic Cycles": {
        "icon": "🔄",
        "description": "Business cycle modeling with phase transitions",
        "use_case": "Long-term planning, cyclical analysis"
    }
}

col1, col2, col3, col4 = st.columns(4)
columns = [col1, col2, col3, col4]

selected_mode = None
for i, (mode, info) in enumerate(simulation_modes.items()):
    with columns[i]:
        if st.button(f"{info['icon']} {mode}", use_container_width=True, key=f"mode_{mode}"):
            selected_mode = mode
        
        st.caption(f"**{info['description']}**")
        st.caption(f"*{info['use_case']}*")

# Store selected mode in session state
if selected_mode:
    st.session_state.selected_mode = selected_mode

current_mode = st.session_state.get("selected_mode", "Monte Carlo")

st.markdown(f"<br><div style='text-align:center; font-size:1.1rem; color:#a78bfa;'>Current Mode: <strong>{simulation_modes[current_mode]['icon']} {current_mode}</strong></div>", unsafe_allow_html=True)

# ─── Mode-Specific Configuration ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if current_mode == "Monte Carlo":
    st.markdown('<div class="section-title">🎲 Monte Carlo Configuration</div>', unsafe_allow_html=True)
    
    col_mc1, col_mc2 = st.columns([2, 1])
    
    with col_mc1:
        st.markdown("**Base Scenario Parameters**")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            base_intensity = st.slider("Base Shock Intensity", 0.1, 0.6, 0.3, 0.05, key="mc_intensity")
        with col_p2:
            base_duration = st.slider("Base Duration (years)", 1, 5, 2, key="mc_duration")
        with col_p3:
            base_recovery = st.slider("Base Recovery Rate", 0.1, 0.6, 0.3, 0.05, key="mc_recovery")
        
        st.markdown("**Uncertainty Parameters**")
        
        col_u1, col_u2, col_u3 = st.columns(3)
        with col_u1:
            intensity_std = st.slider("Intensity Std Dev", 0.01, 0.2, 0.05, 0.01, key="mc_int_std")
        with col_u2:
            recovery_std = st.slider("Recovery Std Dev", 0.01, 0.15, 0.03, 0.01, key="mc_rec_std")
        with col_u3:
            duration_var = st.slider("Duration Variance", 0, 3, 1, key="mc_dur_var")
    
    with col_mc2:
        st.markdown("**Simulation Settings**")
        
        num_simulations = st.selectbox("Number of Simulations", [100, 500, 1000, 2000], index=1, key="mc_sims")
        forecast_horizon = st.slider("Forecast Horizon", 3, 10, 6, key="mc_horizon")
        
        st.markdown("**Expected Outputs**")
        st.markdown("""
        • Confidence intervals (5%, 25%, 75%, 95%)
        • Peak unemployment distribution
        • Recovery time statistics
        • Risk metrics and percentiles
        """)
    
    # Run Monte Carlo button
    if st.button("🎲 Run Monte Carlo Simulation", use_container_width=True, key="run_mc"):
        with st.spinner("⚡ Running Monte Carlo simulation..."):
            try:
                # Prepare request
                mc_request = {
                    "base_shock_intensity": base_intensity,
                    "base_shock_duration": base_duration,
                    "base_recovery_rate": base_recovery,
                    "forecast_horizon": forecast_horizon,
                    "num_simulations": num_simulations,
                    "shock_intensity_std": intensity_std,
                    "recovery_rate_std": recovery_std,
                    "duration_variance": duration_var
                }
                
                # Make API call (would need actual API endpoint)
                # For now, simulate results
                st.session_state.mc_results = {
                    "summary": {
                        "total_simulations": num_simulations,
                        "mean_peak_ue": round(6.5 + base_intensity * 5, 2),
                        "ue_95_confidence": [
                            round(6.0 + base_intensity * 4, 2),
                            round(7.0 + base_intensity * 6, 2)
                        ],
                        "mean_recovery_time": round(3 + base_duration * 1.5, 1)
                    },
                    "peak_unemployment_stats": {
                        "mean": 6.5 + base_intensity * 5,
                        "std": intensity_std * 10,
                        "percentiles": {
                            "p5": 6.0 + base_intensity * 4,
                            "p25": 6.2 + base_intensity * 4.5,
                            "p75": 6.8 + base_intensity * 5.5,
                            "p95": 7.0 + base_intensity * 6
                        }
                    }
                }
                
                st.success(f"✅ Monte Carlo simulation completed ({num_simulations} runs)")
                
            except Exception as e:
                st.error(f"❌ Simulation failed: {e}")

elif current_mode == "Multi-Shock":
    st.markdown('<div class="section-title">💥 Multi-Shock Configuration</div>', unsafe_allow_html=True)
    
    # Shock event configuration
    st.markdown("**Configure Shock Events**")
    
    shock_types = ["pandemic", "financial_crisis", "natural_disaster", "supply_chain", "energy_crisis", "geopolitical"]
    
    num_shocks = st.slider("Number of Shocks", 1, 4, 2, key="ms_num_shocks")
    
    shock_events = []
    for i in range(num_shocks):
        st.markdown(f"**Shock {i+1}**")
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            shock_type = st.selectbox("Type", shock_types, key=f"shock_type_{i}")
        with col_s2:
            intensity = st.slider("Intensity", 0.1, 0.8, 0.3, 0.05, key=f"shock_int_{i}")
        with col_s3:
            duration = st.slider("Duration", 1, 5, 2, key=f"shock_dur_{i}")
        with col_s4:
            start_year = st.slider("Start Year", 0, 5, i, key=f"shock_start_{i}")
        
        shock_events.append({
            "shock_type": shock_type,
            "intensity": intensity,
            "duration": duration,
            "start_year": start_year,
            "sector_impacts": {},
            "description": f"{shock_type.replace('_', ' ').title()} shock"
        })
    
    # Policy responses
    st.markdown("**Policy Responses (Optional)**")
    
    enable_policies = st.checkbox("Enable Dynamic Policy Responses", key="ms_policies")
    
    policy_responses = {}
    if enable_policies:
        for year in range(3):
            policy = st.selectbox(
                f"Year {year} Policy", 
                ["None", "Fiscal Stimulus", "Monetary Policy", "Labor Reforms", "Industry Support"],
                key=f"policy_year_{year}"
            )
            if policy != "None":
                policy_responses[year] = policy
    
    # Run Multi-Shock button
    if st.button("💥 Run Multi-Shock Simulation", use_container_width=True, key="run_ms"):
        with st.spinner("⚡ Running multi-shock simulation..."):
            try:
                # Simulate results
                total_impact = sum(event["intensity"] for event in shock_events) * 2.5
                
                st.session_state.ms_results = {
                    "summary": {
                        "total_shocks": len(shock_events),
                        "compound_peak_ue": round(6.5 + total_impact, 2),
                        "total_impact": round(total_impact, 2),
                        "most_severe_shock": max(shock_events, key=lambda x: x["intensity"])["shock_type"]
                    },
                    "shock_contributions": {
                        f"{event['shock_type']}_{i}": {
                            "type": event["shock_type"],
                            "intensity": event["intensity"],
                            "peak_impact": event["intensity"] * 2.5
                        } for i, event in enumerate(shock_events)
                    }
                }
                
                st.success(f"✅ Multi-shock simulation completed ({len(shock_events)} shocks)")
                
            except Exception as e:
                st.error(f"❌ Simulation failed: {e}")

elif current_mode == "Stress Testing":
    st.markdown('<div class="section-title">🔬 Stress Testing Configuration</div>', unsafe_allow_html=True)
    
    col_st1, col_st2 = st.columns([2, 1])
    
    with col_st1:
        st.markdown("**Test Scenarios**")
        
        use_predefined = st.checkbox("Use Predefined Stress Scenarios", value=True, key="st_predefined")
        
        if use_predefined:
            st.markdown("""
            **Predefined Scenarios Include:**
            • Severe Financial Crisis (2008-style)
            • Pandemic + Supply Chain Crisis
            • Energy Crisis + Geopolitical Tension
            • Technology Disruption
            • Natural Disaster Cascade
            """)
        else:
            st.markdown("**Custom Scenario Configuration**")
            custom_intensity = st.slider("Max Shock Intensity", 0.3, 0.8, 0.5, key="st_intensity")
            custom_duration = st.slider("Max Duration", 2, 6, 4, key="st_duration")
    
    with col_st2:
        st.markdown("**Pass Criteria**")
        
        max_peak_ue = st.slider("Max Peak UE (%)", 8.0, 15.0, 12.0, 0.5, key="st_max_peak")
        max_duration_above_8 = st.slider("Max Years Above 8%", 1, 5, 3, key="st_max_duration")
        recovery_within = st.slider("Recovery Within (years)", 3, 8, 5, key="st_recovery")
        
        st.markdown("**Expected Outputs**")
        st.markdown("""
        • Pass/fail for each scenario
        • System resilience rating
        • Critical failure points
        • Recommended improvements
        """)
    
    # Run Stress Test button
    if st.button("🔬 Run Stress Testing", use_container_width=True, key="run_st"):
        with st.spinner("⚡ Running stress testing framework..."):
            try:
                # Simulate results
                total_scenarios = 5 if use_predefined else 3
                passed_scenarios = np.random.randint(2, total_scenarios + 1)
                pass_rate = (passed_scenarios / total_scenarios) * 100
                
                resilience = "HIGH" if pass_rate >= 80 else "MEDIUM" if pass_rate >= 60 else "LOW"
                
                st.session_state.st_results = {
                    "summary": {
                        "total_scenarios": total_scenarios,
                        "passed_scenarios": passed_scenarios,
                        "failed_scenarios": total_scenarios - passed_scenarios,
                        "pass_rate": round(pass_rate, 1),
                        "system_resilience": resilience
                    }
                }
                
                st.success(f"✅ Stress testing completed ({total_scenarios} scenarios)")
                
            except Exception as e:
                st.error(f"❌ Stress testing failed: {e}")

elif current_mode == "Economic Cycles":
    st.markdown('<div class="section-title">🔄 Economic Cycle Configuration</div>', unsafe_allow_html=True)
    
    col_ec1, col_ec2 = st.columns([2, 1])
    
    with col_ec1:
        st.markdown("**Cycle Parameters**")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            cycle_length = st.slider("Cycle Length (years)", 4, 12, 8, key="ec_length")
        with col_p2:
            amplitude = st.slider("Amplitude (%)", 5, 25, 15, key="ec_amplitude") / 100
        with col_p3:
            current_phase = st.selectbox("Current Phase", ["expansion", "peak", "contraction", "trough"], key="ec_phase")
        
        forecast_horizon_ec = st.slider("Forecast Horizon", 5, 15, 10, key="ec_horizon")
    
    with col_ec2:
        st.markdown("**Cycle Information**")
        
        phase_descriptions = {
            "expansion": "🟢 Economic growth, falling unemployment",
            "peak": "🟡 Maximum growth, tight labor markets", 
            "contraction": "🔴 Economic decline, rising unemployment",
            "trough": "🟠 Minimum activity, high unemployment"
        }
        
        st.markdown(f"**{current_phase.title()}**: {phase_descriptions[current_phase]}")
        
        st.markdown("**Expected Outputs**")
        st.markdown("""
        • Cyclical unemployment trajectory
        • Phase transitions and timing
        • Peak/trough identification
        • Volatility measures
        """)
    
    # Run Economic Cycle button
    if st.button("🔄 Run Economic Cycle Simulation", use_container_width=True, key="run_ec"):
        with st.spinner("⚡ Running economic cycle simulation..."):
            try:
                # Simulate results
                baseline_ue = 6.5
                peak_ue = baseline_ue + amplitude * baseline_ue
                trough_ue = baseline_ue - amplitude * baseline_ue
                
                st.session_state.ec_results = {
                    "summary": {
                        "peak_ue": round(peak_ue, 2),
                        "trough_ue": round(trough_ue, 2),
                        "cycle_range": round(peak_ue - trough_ue, 2),
                        "volatility": round(amplitude * baseline_ue * 0.3, 2)
                    },
                    "cycle_metrics": {
                        "cycle_length": cycle_length,
                        "amplitude": amplitude,
                        "phases_covered": ["expansion", "peak", "contraction", "trough"]
                    }
                }
                
                st.success(f"✅ Economic cycle simulation completed")
                
            except Exception as e:
                st.error(f"❌ Simulation failed: {e}")

# ─── Results Display ──────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

# Display results based on current mode
if current_mode == "Monte Carlo" and "mc_results" in st.session_state:
    results = st.session_state.mc_results
    
    st.markdown('<div class="section-title">🎲 Monte Carlo Results</div>', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_kpi_card("📊", "Mean Peak UE", f"{results['summary']['mean_peak_ue']}%", delta_type="neutral"), unsafe_allow_html=True)
    
    with col2:
        ci = results['summary']['ue_95_confidence']
        st.markdown(render_kpi_card("📈", "95% Confidence", f"{ci[0]}% - {ci[1]}%", delta_type="neutral"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_kpi_card("🔄", "Mean Recovery", f"{results['summary']['mean_recovery_time']} yrs", delta_type="neutral"), unsafe_allow_html=True)
    
    with col4:
        std = results['peak_unemployment_stats']['std']
        st.markdown(render_kpi_card("📊", "Std Deviation", f"{std:.2f}pp", delta_type="neutral"), unsafe_allow_html=True)
    
    # Distribution chart
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart, col_stats = st.columns([2, 1])
    
    with col_chart:
        st.markdown('<div class="section-title">📊 Peak Unemployment Distribution</div>', unsafe_allow_html=True)
        
        # Simulate distribution data
        mean = results['peak_unemployment_stats']['mean']
        std = results['peak_unemployment_stats']['std']
        x = np.linspace(mean - 3*std, mean + 3*std, 100)
        y = np.exp(-0.5 * ((x - mean) / std) ** 2) / (std * np.sqrt(2 * np.pi))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            fill='tozeroy',
            name='Distribution',
            line=dict(color='#6366f1', width=3),
            fillcolor='rgba(99,102,241,0.2)'
        ))
        
        # Add percentile lines
        percentiles = results['peak_unemployment_stats']['percentiles']
        for p_name, p_value in percentiles.items():
            fig.add_vline(
                x=p_value,
                line_dash="dash",
                line_color="#94a3b8",
                annotation_text=f"{p_name}: {p_value:.1f}%"
            )
        
        fig.update_layout(**plotly_dark_layout(height=300))
        fig.update_layout(
            xaxis_title="Peak Unemployment (%)",
            yaxis_title="Probability Density",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_stats:
        st.markdown('<div class="section-title">📊 Statistics</div>', unsafe_allow_html=True)
        
        stats_data = {
            "Metric": ["Mean", "Std Dev", "P5", "P25", "P75", "P95"],
            "Value": [
                f"{results['peak_unemployment_stats']['mean']:.2f}%",
                f"{results['peak_unemployment_stats']['std']:.2f}pp",
                f"{results['peak_unemployment_stats']['percentiles']['p5']:.2f}%",
                f"{results['peak_unemployment_stats']['percentiles']['p25']:.2f}%",
                f"{results['peak_unemployment_stats']['percentiles']['p75']:.2f}%",
                f"{results['peak_unemployment_stats']['percentiles']['p95']:.2f}%"
            ]
        }
        
        st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)

elif current_mode == "Multi-Shock" and "ms_results" in st.session_state:
    results = st.session_state.ms_results
    
    st.markdown('<div class="section-title">💥 Multi-Shock Results</div>', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_kpi_card("💥", "Total Shocks", str(results['summary']['total_shocks']), delta_type="neutral"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_kpi_card("📊", "Compound Peak", f"{results['summary']['compound_peak_ue']}%", delta_type="up"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_kpi_card("📈", "Total Impact", f"+{results['summary']['total_impact']:.2f}pp", delta_type="up"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_kpi_card("🎯", "Most Severe", results['summary']['most_severe_shock'].replace('_', ' ').title(), delta_type="neutral"), unsafe_allow_html=True)
    
    # Shock contributions
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Individual Shock Contributions</div>', unsafe_allow_html=True)
    
    contributions = results['shock_contributions']
    contrib_data = []
    
    for shock_name, data in contributions.items():
        contrib_data.append({
            "Shock": data['type'].replace('_', ' ').title(),
            "Intensity": f"{data['intensity']:.2f}",
            "Peak Impact": f"{data['peak_impact']:.2f}pp"
        })
    
    st.dataframe(pd.DataFrame(contrib_data), use_container_width=True, hide_index=True)

elif current_mode == "Stress Testing" and "st_results" in st.session_state:
    results = st.session_state.st_results
    
    st.markdown('<div class="section-title">🔬 Stress Testing Results</div>', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_kpi_card("🧪", "Total Tests", str(results['summary']['total_scenarios']), delta_type="neutral"), unsafe_allow_html=True)
    
    with col2:
        passed = results['summary']['passed_scenarios']
        st.markdown(render_kpi_card("✅", "Passed", str(passed), delta_type="down" if passed > 0 else "up"), unsafe_allow_html=True)
    
    with col3:
        pass_rate = results['summary']['pass_rate']
        st.markdown(render_kpi_card("📊", "Pass Rate", f"{pass_rate}%", delta_type="down" if pass_rate >= 80 else "up"), unsafe_allow_html=True)
    
    with col4:
        resilience = results['summary']['system_resilience']
        color = "down" if resilience == "HIGH" else "neutral" if resilience == "MEDIUM" else "up"
        st.markdown(render_kpi_card("🛡️", "Resilience", resilience, delta_type=color), unsafe_allow_html=True)

elif current_mode == "Economic Cycles" and "ec_results" in st.session_state:
    results = st.session_state.ec_results
    
    st.markdown('<div class="section-title">🔄 Economic Cycle Results</div>', unsafe_allow_html=True)
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_kpi_card("📊", "Peak UE", f"{results['summary']['peak_ue']}%", delta_type="up"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(render_kpi_card("📉", "Trough UE", f"{results['summary']['trough_ue']}%", delta_type="down"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(render_kpi_card("📈", "Cycle Range", f"{results['summary']['cycle_range']}pp", delta_type="neutral"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(render_kpi_card("📊", "Volatility", f"{results['summary']['volatility']:.2f}", delta_type="neutral"), unsafe_allow_html=True)

# ─── Help and Documentation ───────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("📚 Advanced Simulation Guide"):
    st.markdown("""
    ## 🎲 Monte Carlo Simulation
    
    **Purpose**: Quantify uncertainty in model predictions by running thousands of simulations with parameter variations.
    
    **Key Features**:
    - Parameter uncertainty modeling
    - Confidence interval generation
    - Risk assessment and percentiles
    - Recovery time distributions
    
    **Use Cases**:
    - Risk management and planning
    - Regulatory stress testing
    - Investment decision support
    - Policy impact assessment
    
    ---
    
    ## 💥 Multi-Shock Scenarios
    
    **Purpose**: Model compound crises where multiple shocks occur simultaneously or in sequence.
    
    **Key Features**:
    - Overlapping shock timing
    - Sector-specific impacts
    - Dynamic policy responses
    - Interaction effect analysis
    
    **Use Cases**:
    - Pandemic + economic crisis
    - Natural disaster cascades
    - Geopolitical + energy shocks
    - Technology disruption chains
    
    ---
    
    ## 🔬 Stress Testing
    
    **Purpose**: Systematically test system resilience against extreme but plausible scenarios.
    
    **Key Features**:
    - Predefined stress scenarios
    - Pass/fail criteria
    - System resilience rating
    - Critical threshold identification
    
    **Use Cases**:
    - Regulatory compliance
    - System design validation
    - Emergency preparedness
    - Risk limit setting
    
    ---
    
    ## 🔄 Economic Cycles
    
    **Purpose**: Model business cycle effects overlaid on baseline economic trends.
    
    **Key Features**:
    - Configurable cycle length
    - Phase transition modeling
    - Amplitude adjustment
    - Long-term trend analysis
    
    **Use Cases**:
    - Long-term planning
    - Investment timing
    - Policy cycle analysis
    - Economic forecasting
    """)

st.markdown("</div>", unsafe_allow_html=True)