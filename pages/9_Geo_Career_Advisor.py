"""
Page 9 â€” Geo-Aware Career Advisor (Feature 8)

Folium map, city posting volume chart, location quotients with bar chart,
relocation ranking with colour-coded skill fit, and ML risk comparison
across all tiers for the current profile.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from src.geo_career_advisor import (
    aggregate_city_labour_market,
    build_folium_map,
    extract_user_skill_phrases,
    load_city_reference,
    normalize_city_key,
    postings_with_city_key,
    rank_relocation_targets,
    relocation_model_delta_pct,
    resolve_city_row,
    skill_location_quotients,
    skill_match_rate_in_subset,
)
from src.job_market_pulse import load_job_postings, phrase_in_blob
from src.live_data import fetch_labor_market_pulse, get_state_unemployment
from src.live_insights import generate_labor_market_insights
from src.ui_helpers import DARK_CSS, plotly_dark_layout, render_kpi_card

st.set_page_config(page_title="Geo Career | UIP", page_icon="ðŸ—ºï¸", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ðŸ—ºï¸ Geo Career Advisor")
    st.caption(
        "WGS84 + Folium + optional Nominatim (OSM). "
        "Metrics are computed from your posting CSV â€” swap in real feeds for production."
    )
    st.markdown("---")
    st.markdown("**ðŸŒ Navigation**")
    st.page_link("app.py", label="ðŸ  Home")
    st.page_link("pages/0_Help_Guide.py", label="â“ Help Guide")
    st.page_link("pages/1_Overview.py", label="ðŸ“Š Overview")
    st.page_link("pages/2_Simulator.py", label="ðŸ§ª Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="ðŸ­ Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="ðŸ’¼ Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="ðŸ¤– AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py", label="ðŸŽ¯ Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="ðŸ“¡ Market Pulse")


@st.cache_data(ttl=86400, show_spinner=False)
def cached_geocode(query: str):
    from src.geo_career_advisor import geocode_place
    return geocode_place(query)


st.markdown("""
<div class="page-hero">
    <div class="hero-title">ðŸ—ºï¸ Geo-Aware Career Advisor</div>
    <div class="hero-subtitle">
        Map hiring intensity by city, compare skill demand with location quotients,
        rank relocation targets, and model your risk change across location tiers.
    </div>
</div>""", unsafe_allow_html=True)

df_jobs = load_job_postings()
if df_jobs.empty:
    st.error("No job postings loaded. Add `data/market_pulse/job_postings_sample.csv` or upload from Market Pulse page.")
    st.stop()

agg = aggregate_city_labour_market(df_jobs)
dkey = postings_with_city_key(df_jobs)

loc_values = sorted(dkey["location"].dropna().astype(str).unique().tolist())
city_keys_in_data = sorted(dkey["city_key"].unique().tolist())

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    home_display = st.selectbox("Your city (from dataset)", loc_values, index=0)
with c2:
    skills = st.text_area(
        "Your skills (comma-separated)",
        placeholder="python, sql, aws",
        height=68,
        help="Used for skill match rate and location quotients.",
    )
with c3:
    geocode_query = st.text_input(
        "Optional: geocode another place (Nominatim)",
        placeholder="e.g. Indore",
        help="Respects OpenStreetMap usage policy; results cached 24h. Requires network.",
    )

# â”€â”€ Data Processing & Filtering â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if skills.strip():
    import re
    phrases = [p.strip() for p in re.split(r"[,;\n]+", skills.lower()) if p.strip()]
else:
    phrases = []

user_ck = normalize_city_key(home_display)

# â”€â”€ STEP 1: Mode Detection â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Determine if we're in personalized mode based on user input
# Personalized mode requires BOTH city AND skills to be entered
personalized_mode = bool(phrases) and bool(home_display != loc_values[0])
default_mode = not personalized_mode

# Show helpful prompt in default mode
if default_mode:
    st.markdown("""
    <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.25);
                border-radius:14px; padding:2rem; text-align:center; margin:2rem 0;">
        <div style="font-size:1.1rem; font-weight:700; color:#818cf8; margin-bottom:0.8rem;">
            ðŸ“ Enter your city and skills to personalize
        </div>
        <div style="font-size:0.9rem; color:#94a3b8; line-height:1.6;">
            Currently showing general market overview. Select your city and enter your skills (comma-separated) to unlock:
        </div>
        <ul style="text-align:left; display:inline-block; margin-top:0.8rem; color:#cbd5e1; font-size:0.85rem;">
            <li>ðŸŽ¯ Personalized relocation ranking</li>
            <li>ðŸ“Š Skill-filtered job opportunities</li>
            <li>ðŸ“ˆ Your location quotients</li>
            <li>âš ï¸ Modeled risk by tier (personalized)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Debug info (can be removed later)
# if personalized_mode:
#     st.caption(f"ðŸŽ¯ **Personalized Mode**: Analyzing for your skills: {', '.join(phrases) if phrases else 'None'} | City: {home_display}")
# else:
#     st.caption("ðŸ“Š **Default Mode**: Showing general market overview")

# Map Options UI
col_m1, col_m2 = st.columns([1, 1])
with col_m1:
    # Make map title mode-aware
    if personalized_mode and phrases:
        map_title = "ðŸ—ºï¸ Hiring demand for YOUR skills"
        map_subtitle = f"Skills: {', '.join(phrases[:3])}{'...' if len(phrases) > 3 else ''}"
    else:
        map_title = "ðŸ—ºï¸ Hiring intensity map"
        map_subtitle = "Basemap: CartoDB Positron (OSM). Circle area scales with posting count."
    
    st.markdown(f'<div class="section-title">{map_title}</div>', unsafe_allow_html=True)
    st.caption(map_subtitle)
    
with col_m2:
    # Auto-select skill mode when in personalized mode
    if personalized_mode and phrases:
        default_map_index = 1  # "Matched to My Skills (Dynamic)"
        map_options = ["Total Market Demand", "Matched to My Skills (Dynamic)"]
    else:
        default_map_index = 0  # "Total Market Demand"
        map_options = ["Total Market Demand"]
    
    map_mode = st.radio(
        "Map Data Source", 
        map_options,
        index=default_map_index,
        horizontal=True,
        help="Switch to 'My Skills' to see only job postings that match the skills you entered above." if personalized_mode else "Enter skills above to enable skill-filtered mapping."
    )

# Dynamic Filtering
if personalized_mode and phrases and map_mode == "Matched to My Skills (Dynamic)":
    # Filter the dataset to only include rows that match at least one user skill
    skill_filtered_jobs = []
    for _, row in df_jobs.iterrows():
        blob = row.get("_text", "")
        if any(phrase_in_blob(p, blob) for p in phrases):
            skill_filtered_jobs.append(row)
    
    if skill_filtered_jobs:
        df_for_map = pd.DataFrame(skill_filtered_jobs)
        st.success(f"Map updated: Showing {len(df_for_map)} jobs matching '{skills}'")
    else:
        st.warning(f"No jobs found matching your skills. Falling back to total market data.")
        df_for_map = df_jobs
else:
    df_for_map = df_jobs

# Recompute agg ONLY for the map, so the tabs still have full dataset context
map_agg = aggregate_city_labour_market(df_for_map)

extra_pin = None
if geocode_query.strip():
    geo = cached_geocode(geocode_query.strip())
    if geo:
        extra_pin = (geo[0], geo[1], geo[2])
    else:
        st.caption("Geocoder returned no result â€” check spelling or try a larger nearby city.")

# â”€â”€ Personalized Recommendation Header â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# STEP 2: Conditional rendering - show personalized header only in personalized mode
if personalized_mode and phrases and not map_agg.empty:
    rk_quick = rank_relocation_targets(df_jobs, user_ck, phrases)
    lq_quick = skill_location_quotients(df_jobs, user_ck, phrases)
    
    best_city = rk_quick.iloc[0]["display_name"] if not rk_quick.empty else "N/A"
    
    top_skill = ""
    top_lq = 0.0
    if not lq_quick.empty:
        top_skill = lq_quick.iloc[0]["skill"]
        top_lq = lq_quick.iloc[0]["lq"]
    
    st.markdown(f"""
    <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.3);
                border-radius:14px; padding:1.2rem; margin-bottom:1.5rem;">
        <div style="display:flex; gap:0.6rem; align-items:center; margin-bottom:0.8rem;">
            <span style="font-size:1.3rem;">ðŸŽ¯</span>
            <span style="font-size:0.95rem; font-weight:700; color:#10b981;
                          text-transform:uppercase; letter-spacing:1px;">
                Your Geo-Alignment summary
            </span>
        </div>
        <div style="font-size:0.95rem; color:#cbd5e1; line-height:1.7;">
            Based on your skills, your top relocation target is <strong style="color:#f8fafc;">{best_city}</strong>.<br>
            In your current city (<strong style="color:#f8fafc;">{home_display}</strong>), 
            your highest-demand skill is <strong style="color:#34d399;">'{top_skill}'</strong> 
            (Location Quotient: <strong>{top_lq}</strong>).
        </div>
    </div>
    """, unsafe_allow_html=True)


import hashlib
map_key = f"folium_map_{hashlib.md5(str(phrases).encode()).hexdigest()[:8]}_{map_mode.split()[0]}"
m = build_folium_map(map_agg, highlight_city_key=user_ck, extra_marker=extra_pin)
st_folium(m, width=None, height=480, returned_objects=[], key=map_key)

st.markdown("<br>", unsafe_allow_html=True)

# â”€â”€ City posting volume + salary chart â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# STEP 2: Show in both modes, but with different context
# Use map_agg which is already filtered by skills if in skill-filtered mode
chart_agg = map_agg if map_mode == "Matched to My Skills (Dynamic)" and phrases else agg

if not chart_agg.empty:
    
    # Different titles based on mode
    if personalized_mode:
        chart_title = f"ðŸ“Š Job opportunities by city (Your context: {home_display})"
        if map_mode == "Matched to My Skills (Dynamic)" and phrases:
            chart_subtitle = f"Filtered to jobs matching: {', '.join(phrases[:3])}{'...' if len(phrases) > 3 else ''}"
        else:
            chart_subtitle = "Cities highlighted based on your profile and skills"
    else:
        chart_title = "ðŸ“Š City hiring volume & median salary"
        chart_subtitle = "General market overview across all cities"
    
    st.markdown(f'<div class="section-title">{chart_title}</div>', unsafe_allow_html=True)
    st.caption(chart_subtitle)
    agg_disp = chart_agg.copy()
    agg_disp["City"] = agg_disp.get("display_name", agg_disp["city_key"])
    agg_disp = agg_disp.sort_values("postings", ascending=False).head(15)

    fig_city = go.Figure()
    fig_city = go.Figure()
    fig_city.add_trace(go.Bar(
        x=agg_disp["City"],
        y=agg_disp["postings"],
        name="Postings",
        marker_color=[
            "#06b6d4" if ck == user_ck else "#6366f1"
            for ck in agg_disp["city_key"]
        ],
        text=agg_disp["postings"],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Postings: %{y}<extra></extra>",
    ))
    
    # Only add salary line if we have meaningful salary data
    salary_data = agg_disp.dropna(subset=["median_lpa"])
    if len(salary_data) >= 1 and "median_lpa" in agg_disp.columns:
        # Filter to cities with reasonable salary coverage (>10% of jobs have salary data)
        if "salary_coverage_pct" in agg_disp.columns:
            salary_data = salary_data[salary_data["salary_coverage_pct"] >= 1]
        
        if len(salary_data) >= 1:
            fig_city.add_trace(go.Scatter(
                x=salary_data["City"],
                y=salary_data["median_lpa"],
                name=f"Median salary (LPA) - {len(salary_data)} cities",
                mode="lines+markers",
                marker=dict(color="#34d399", size=8),
                line=dict(color="#34d399", width=2),
                yaxis="y2",
                hovertemplate="<b>%{x}</b><br>Median: %{y:.1f} LPA<extra></extra>",
            ))
            fig_city.update_layout(
                yaxis2=dict(
                    title="Median LPA",
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    color="#34d399",
                )
            )
        else:
            st.caption("âš ï¸ Insufficient salary data for trend line (need â‰¥3 cities with >10% salary coverage)")
    else:
        st.caption("âš ï¸ No salary data available for median salary trend line")
    fig_city.update_layout(**plotly_dark_layout(height=380))
    fig_city.update_layout(
        xaxis_title="City",
        yaxis_title="Job postings",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        barmode="group",
    )
    st.plotly_chart(fig_city, use_container_width=True)
    
    # Add data quality indicators
    col_qual1, col_qual2, col_qual3 = st.columns(3)
    with col_qual1:
        total_cities = len(agg_disp)
        cities_with_coords = len(agg_disp.dropna(subset=["lat", "lon"]))
        coord_pct = cities_with_coords / total_cities * 100 if total_cities > 0 else 0
        st.metric("Cities with coordinates", f"{cities_with_coords}/{total_cities}", f"{coord_pct:.0f}%")
    
    with col_qual2:
        if "salary_coverage_pct" in agg_disp.columns:
            avg_salary_coverage = agg_disp["salary_coverage_pct"].mean()
            cities_with_salary = len(agg_disp.dropna(subset=["median_lpa"]))
            st.metric("Avg salary coverage", f"{avg_salary_coverage:.1f}%", f"{cities_with_salary} cities")
        else:
            st.metric("Salary data", "Limited", "Check source")
    
    with col_qual3:
        if "salary_count" in agg_disp.columns:
            total_salary_jobs = agg_disp["salary_count"].sum()
            total_jobs = agg_disp["postings"].sum()
            overall_coverage = total_salary_jobs / total_jobs * 100 if total_jobs > 0 else 0
            st.metric("Overall salary coverage", f"{overall_coverage:.1f}%", f"{total_salary_jobs:,} jobs")
        else:
            st.metric("Data quality", "Unknown", "")

    st.caption("✅ Cyan bar = your selected city. Salary trend shown where data available.")
    st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "ðŸ“ Relocation Ranking",
    "ðŸ“Š Location Quotients",
    "ðŸ’° Cost of Living & Salary",
    "ðŸŒ India Labor Context",
])

with tab1:
    if personalized_mode:
        st.markdown(
            "Ranks cities by a **transparent composite**: "
            "55% normalized posting volume vs your city, 45% share of local jobs matching **your skills**."
        )
    else:
        st.markdown(
            "Ranks cities by a **transparent composite**: "
            "55% normalized posting volume vs your city, 45% share of local jobs in the market."
        )
    
    rk = rank_relocation_targets(df_jobs, user_ck, phrases if personalized_mode else [])
    if rk.empty:
        st.info("Not enough city-level rows to rank.")
    else:
        rk_disp = rk.rename(columns={
            "display_name": "City",
            "postings": "Postings",
            "volume_vs_yours": "Volume vs yours (Ã—)",
            "your_skill_match_rate": "Skill match rate",
            "score": "Composite score",
        })[["City", "Postings", "Volume vs yours (Ã—)", "Skill match rate", "Composite score"]]

        def _style_skill_fit(val) -> str:
            try:
                v = float(val)
            except (TypeError, ValueError):
                return ""
            if v >= 0.5:
                return "background-color: rgba(16,185,129,0.15); color: #34d399; font-weight:700;"
            if v >= 0.25:
                return "color: #fbbf24;"
            return "color: #f87171;"

        def _style_score(val) -> str:
            try:
                v = float(val)
            except (TypeError, ValueError):
                return ""
            if v >= 0.5:
                return "color: #34d399; font-weight: 700;"
            if v >= 0.3:
                return "color: #6366f1;"
            return ""

        st.dataframe(
            rk_disp.style
                .map(_style_skill_fit, subset=["Skill match rate"])
                .map(_style_score, subset=["Composite score"]), use_container_width=True,
            hide_index=True,
        )

        csv_rk = rk_disp.to_csv(index=False).encode()
        st.download_button(
            "â¬‡ Export relocation ranking (CSV)",
            data=csv_rk,
            file_name="relocation_ranking.csv",
            mime="text/csv",
        )

        top5 = rk_disp.head(5)
        fig_rk = px.bar(
            top5,
            x="Composite score",
            y="City",
            orientation="h",
            color="Skill match rate",
            color_continuous_scale=["#f87171", "#fbbf24", "#34d399"],
            title="Top 5 relocation targets",
        )
        fig_rk.update_layout(**plotly_dark_layout(height=280))
        fig_rk.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_rk, use_container_width=True)

with tab2:
    st.markdown(
        "**Location quotient (LQ)** â‰ˆ (local mention rate) Ã· (national mention rate). "
        "LQ > 1 means the skill appears more often in that city than in the full sample."
    )
    if not phrases and personalized_mode:
        st.info("Enter your skills above to compute LQs for your city.")
    elif not personalized_mode:
        st.info("Enter your city and skills above to compute location quotients for your profile.")
    else:
        lq = skill_location_quotients(df_jobs, user_ck, phrases)
        if lq.empty:
            st.warning("Could not resolve your city in the posting extract for LQ â€” try a city from the dataset list.")
        else:
            col_lq1, col_lq2 = st.columns([2, 3])
            with col_lq1:
                st.dataframe(lq, use_container_width=True)
            with col_lq2:
                lq_plot = lq.dropna(subset=["lq"]).copy()
                lq_plot["lq"] = lq_plot["lq"].astype(float)
                lq_plot["above"] = lq_plot["lq"] >= 1.0
                fig_lq = px.bar(
                    lq_plot,
                    x="lq",
                    y="skill",
                    orientation="h",
                    color="above",
                    color_discrete_map={True: "#34d399", False: "#f87171"},
                    title=f"Location quotients â€” {home_display}",
                )
                fig_lq.add_vline(x=1.0, line_dash="dot", line_color="#fbbf24",
                                 annotation_text="National avg", annotation_position="top right")
                fig_lq.update_layout(**plotly_dark_layout(height=max(240, 30 * len(lq_plot))))
                fig_lq.update_yaxes(autorange="reversed")
                fig_lq.update_layout(showlegend=False)
                st.plotly_chart(fig_lq, use_container_width=True)

            local_df = dkey[dkey["city_key"] == user_ck]
            if len(local_df) and phrases:
                rate = skill_match_rate_in_subset(local_df, phrases)
                st.metric(
                    "Your skill coverage in this city",
                    f"{rate:.1%} of local postings",
                    help="Share of local job postings that mention at least one of your skills.",
                )

# â”€â”€ Tab routing â€” 4-tab simplified structure
tab3_live = tab4   # India Labor Context
tab4_col  = tab3   # Cost of Living & Salary


with tab3_live:
    st.markdown("""
    <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.25);
                border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;
                display:flex; gap:0.75rem; align-items:flex-start;">
        <div style="font-size:1.3rem;">ðŸŒ</div>
        <div>
            <div style="font-size:0.82rem; font-weight:700; color:#818cf8;
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
                Real India Labor Data</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.55;">
                <strong style="color:#e2e8f0;">National trends</strong> are fetched live from the
                <strong style="color:#e2e8f0;">World Bank Open API</strong>.
                <strong style="color:#e2e8f0;">State-level data</strong> is from the official
                <strong style="color:#e2e8f0;">PLFS 2022-23 report</strong> (MOSPI, Govt. of India) â€”
                state unemployment is not available on the World Bank API.
                Use this view to ground your city decision in real macro and regional data.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # â”€â”€ National KPIs from World Bank
    st.markdown('<div class="section-title">ðŸ“Š India National Labor Snapshot (World Bank)</div>',
                unsafe_allow_html=True)

    with st.spinner("Fetching live data from World Bankâ€¦"):
        wb_data = fetch_labor_market_pulse("India")

    # â”€â”€ AI Insight Box â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    geo_insights = generate_labor_market_insights(wb_data)
    if geo_insights:
        bullets_html = "".join(
            f'<li style="margin-bottom:0.45rem; color:#cbd5e1; font-size:0.9rem; line-height:1.6;">'
            + s.replace("**", "<strong style='color:#e2e8f0;'>", 1).replace("**", "</strong>", 1)
            + "</li>"
            for s in geo_insights
        )
        st.markdown(f"""
        <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.25);
                    border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.4rem;">
            <div style="display:flex; gap:0.6rem; align-items:center; margin-bottom:0.6rem;">
                <span style="font-size:1.1rem;">ðŸ’¡</span>
                <span style="font-size:0.78rem; font-weight:700; color:#818cf8;
                              text-transform:uppercase; letter-spacing:1px;">
                    India Labor Market Context â€” What This Means for Your City Choice
                </span>
            </div>
            <ul style="margin:0; padding-left:1.2rem;">{bullets_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    KEY_KPIS = [
        ("Unemployment Rate (%)",       "ðŸ“Š", "neutral"),
        ("Youth Unemployment 15-24 (%)","ðŸ‘¶", "up"),
        ("Labor Force Participation (%)","ðŸ’ª", "neutral"),
        ("Employment-to-Population (%)","ðŸ­", "neutral"),
    ]
    kpi_cols = st.columns(len(KEY_KPIS))
    for col, (label, icon, dt) in zip(kpi_cols, KEY_KPIS):
        with col:
            series = wb_data.get(label)
            if series is not None and not series.empty:
                latest_val  = series.iloc[-1]["Value"]
                latest_year = int(series.iloc[-1]["Year"])
                delta_txt   = ""
                if len(series) >= 2:
                    prev = series.iloc[-2]["Value"]
                    chg = round(latest_val - prev, 2)
                    arrow = "â–²" if chg > 0 else "â–¼"
                    delta_txt = f"{arrow} {abs(chg)}pp vs {latest_year - 1}"
                st.markdown(
                    render_kpi_card(icon, label, f"{latest_val:.1f}%", delta_txt, dt),
                    unsafe_allow_html=True
                )
            else:
                st.markdown(render_kpi_card(icon, label, "N/A", "Unavailable", "neutral"),
                            unsafe_allow_html=True)

    # â”€â”€ National unemployment trend sparkline
    if wb_data.get("Unemployment Rate (%)") is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">ðŸ“ˆ India Unemployment Trend (World Bank, 1991â€“2023)</div>',
                    unsafe_allow_html=True)
        ue_series = wb_data["Unemployment Rate (%)"]
        fig_ue = go.Figure()
        fig_ue.add_trace(go.Scatter(
            x=ue_series["Year"], y=ue_series["Value"],
            mode="lines+markers", name="Unemployment Rate",
            line=dict(color="#6366f1", width=2.5),
            marker=dict(size=5, color="#6366f1"),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.08)",
            hovertemplate="<b>Year: %{x}</b><br>Rate: %{y:.2f}%<extra></extra>",
        ))
        youth = wb_data.get("Youth Unemployment 15-24 (%)")
        if youth is not None and not youth.empty:
            fig_ue.add_trace(go.Scatter(
                x=youth["Year"], y=youth["Value"],
                mode="lines", name="Youth Unemployment (15-24)",
                line=dict(color="#f59e0b", width=2, dash="dot"),
                hovertemplate="<b>Year: %{x}</b><br>Youth: %{y:.2f}%<extra></extra>",
            ))
        fig_ue.update_layout(**plotly_dark_layout(height=360))
        fig_ue.update_layout(
            xaxis_title="Year", yaxis_title="Unemployment Rate (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
        )
        st.plotly_chart(fig_ue, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # â”€â”€ State-level unemployment breakdown (PLFS 2022-23)
    
    st.markdown('<div class="section-title">ðŸ—ºï¸ State-Level Unemployment â€” PLFS 2022-23 (UPS, 15+ yrs)</div>',
                unsafe_allow_html=True)

    state_df = get_state_unemployment()

    view_type = st.radio("View", ["Combined", "Urban vs Rural comparison"],
                         horizontal=True, key="state_view_type")

    if view_type == "Combined":
        color_discrete = dict(
            North="#6366f1", South="#10b981", East="#f59e0b",
            West="#06b6d4", Central="#8b5cf6", Northeast="#ec4899",
        )
        fig_state = px.bar(
            state_df.sort_values("Combined_UE", ascending=True),
            x="Combined_UE", y="State", orientation="h",
            color="Region",
            color_discrete_map=color_discrete,
            text="Combined_UE",
            labels={"Combined_UE": "Unemployment Rate (%)"},
        )
        fig_state.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        india_avg = state_df["Combined_UE"].mean()
        fig_state.add_vline(x=india_avg, line_dash="dot", line_color="#94a3b8",
                            annotation_text=f"India avg ~{india_avg:.1f}%",
                            annotation_position="top right",
                            annotation_font=dict(color="#94a3b8", size=10))
        fig_state.update_layout(
            **plotly_dark_layout(height=max(560, 20 * len(state_df))),
            xaxis_title="Unemployment Rate (%)", yaxis_title="",
        )
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        state_plot = state_df.dropna(subset=["Urban_UE"]).sort_values("Combined_UE", ascending=False).head(20)
        fig_urvr = go.Figure()
        fig_urvr.add_trace(go.Bar(
            x=state_plot["State"], y=state_plot["Urban_UE"],
            name="Urban", marker_color="#6366f1",
        ))
        fig_urvr.add_trace(go.Bar(
            x=state_plot["State"], y=state_plot["Rural_UE"],
            name="Rural", marker_color="#10b981",
        ))
        fig_urvr.update_layout(**plotly_dark_layout(height=420))
        fig_urvr.update_layout(
            barmode="group",
            xaxis_title="State", yaxis_title="Unemployment Rate (%)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
            xaxis_tickangle=-45,
        )
        st.plotly_chart(fig_urvr, use_container_width=True)

    st.caption("Source: PLFS Annual Report 2022-23, MOSPI, Government of India | UPS = Usual Principal Status")

    # â”€â”€ Region comparison
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">ðŸ™ï¸ Average Unemployment by Region</div>',
                unsafe_allow_html=True)
    region_avg = (
        state_df.groupby("Region")["Combined_UE"]
        .mean().round(2)
        .reset_index()
        .rename(columns={"Combined_UE": "Avg Unemployment (%)"})
        .sort_values("Avg Unemployment (%)", ascending=False)
    )
    fig_reg = px.bar(
        region_avg, x="Region", y="Avg Unemployment (%)",
        color="Avg Unemployment (%)",
        color_continuous_scale=["#0d9488", "#6366f1", "#ef4444"],
        text="Avg Unemployment (%)",
    )
    fig_reg.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_reg.update_layout(
        **plotly_dark_layout(height=320),
        xaxis_title="Region", yaxis_title="Average Unemployment (%)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_reg, use_container_width=True)

    # â”€â”€ Export
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">ðŸ“¥ Export State Data</div>', unsafe_allow_html=True)
    csv_bytes = state_df.to_csv(index=False).encode()
    st.download_button(
        "â¬‡ Download PLFS State Unemployment Data (CSV)",
        csv_bytes,
        file_name="india_state_unemployment_plfs2023.csv",
        mime="text/csv",
    )
    st.caption("Source: PLFS Annual Report 2022-23 | Ministry of Statistics & Programme Implementation (MOSPI)")


# â”€â”€ TAB 4 â€” COST OF LIVING ANALYSIS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with tab4_col:
    # STEP 5: Transform component based on mode
    if personalized_mode and phrases:
        # Personalized mode: Real salary impact for user profile
        st.markdown("""
        <div style="background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.25);
                    border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
            <div style="font-size:0.82rem; font-weight:700; color:#f59e0b;
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
                ðŸ’° Real Salary Impact for Your Profile</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
                How cost of living affects YOUR earning potential in different cities.
                <strong style="color:#e2e8f0;">Your Effective Salary</strong> = Expected Salary Ã· (COL Index / 50).
                This shows your actual purchasing power based on your skills and local costs.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Default mode: Generic cost of living analysis
        st.markdown("""
        <div style="background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.25);
                    border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
            <div style="font-size:0.82rem; font-weight:700; color:#f59e0b;
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
                ðŸ’° Purchasing Power Analysis</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
                Cost of Living Index (base 50 = India average). Higher index = more expensive.
                <strong style="color:#e2e8f0;">Real Salary</strong> = Nominal Salary Ã· (COL Index / 50).
                This shows your actual purchasing power after adjusting for local costs.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    from src.geo_career_advisor import get_cost_of_living_index, calculate_real_salary, get_city_state
    
    # Get COL data for all cities in aggregation
    col_data = []
    for _, row in agg.iterrows():
        ck = row["city_key"]
        col_idx = get_cost_of_living_index(ck)
        state = get_city_state(ck)
        if col_idx is not None:
            med_salary = row.get("median_lpa")
            real_salary = None
            if pd.notna(med_salary) and med_salary > 0:
                real_salary = calculate_real_salary(med_salary, ck)
            
            col_data.append({
                "City": row.get("display_name", ck),
                "State": state or "Unknown",
                "COL_Index": col_idx,
                "Median_Nominal_LPA": med_salary if pd.notna(med_salary) else None,
                "Median_Real_LPA": real_salary,
                "Postings": row["postings"],
            })
    
    col_df = pd.DataFrame(col_data).sort_values("COL_Index", ascending=False)
    
    if not col_df.empty:
        col_chart1, col_chart2 = st.columns([1, 1])
        
        with col_chart1:
            st.markdown("**Cost of Living Index by City**")
            fig_col = px.bar(
                col_df.head(20),
                x="COL_Index",
                y="City",
                orientation="h",
                color="COL_Index",
                color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
                text="COL_Index",
            )
            fig_col.add_vline(x=50, line_dash="dot", line_color="#fbbf24",
                             annotation_text="India Avg (50)", annotation_position="top right")
            fig_col.update_traces(textposition="outside")
            fig_col.update_layout(**plotly_dark_layout(height=500))
            fig_col.update_layout(
                xaxis_title="Cost of Living Index",
                yaxis_title="",
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig_col, use_container_width=True)
        
        with col_chart2:
            st.markdown("**Real vs Nominal Salary (Top 15 Cities)**")
            salary_df = col_df.dropna(subset=["Median_Nominal_LPA", "Median_Real_LPA"]).head(15)
            
            if not salary_df.empty:
                fig_sal = go.Figure()
                fig_sal.add_trace(go.Bar(
                    x=salary_df["City"],
                    y=salary_df["Median_Nominal_LPA"],
                    name="Nominal Salary",
                    marker_color="#6366f1",
                ))
                fig_sal.add_trace(go.Bar(
                    x=salary_df["City"],
                    y=salary_df["Median_Real_LPA"],
                    name="Real Salary (PPP-adjusted)",
                    marker_color="#10b981",
                ))
                fig_sal.update_layout(**plotly_dark_layout(height=500))
                fig_sal.update_layout(
                    xaxis_title="City",
                    yaxis_title="Salary (LPA)",
                    barmode="group",
                    xaxis_tickangle=-45,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_sal, use_container_width=True)
            else:
                st.info("Salary data not available for cities with COL index.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Cost of Living Comparison Table**")
        
        display_col = col_df[["City", "State", "COL_Index", "Median_Nominal_LPA", "Median_Real_LPA", "Postings"]].copy()
        display_col.columns = ["City", "State", "COL Index", "Nominal Salary (LPA)", "Real Salary (LPA)", "Job Postings"]
        
        def _style_col(val):
            try:
                v = float(val)
                if v > 65:
                    return "color: #ef4444; font-weight: 700;"
                elif v < 40:
                    return "color: #10b981; font-weight: 700;"
            except:
                pass
            return ""
        
        st.dataframe(
            display_col.style.map(_style_col, subset=["COL Index"]), use_container_width=True,
            hide_index=True,
        )
        
        st.caption("""
        **Interpretation:** Mumbai (82) is 64% more expensive than India average (50).
        A 10 LPA salary in Mumbai has the same purchasing power as 6.1 LPA in a city with COL=50.
        """)
    else:
        st.info("Cost of living data not available. Ensure city reference CSV has cost_of_living_index column.")

# â”€â”€ TAB 5 â€” INDUSTRY CONCENTRATION â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# â”€â”€ STEP 8: FINAL RECOMMENDATION LAYER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if personalized_mode and phrases and not agg.empty:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Generate comprehensive recommendation using existing data
    rk_data = rank_relocation_targets(df_jobs, user_ck, phrases)
    lq_data = skill_location_quotients(df_jobs, user_ck, phrases)
    
    if not rk_data.empty:
        # Get top recommendation
        best_city = rk_data.iloc[0]["display_name"]
        best_score = rk_data.iloc[0]["score"]
        best_skill_match = rk_data.iloc[0]["your_skill_match_rate"]
        best_postings = rk_data.iloc[0]["postings"]
        
        # Get cost of living impact
        from src.geo_career_advisor import get_cost_of_living_index
        best_city_key = rk_data.iloc[0]["city_key"]
        col_index = get_cost_of_living_index(best_city_key)
        
        # Get competition level (state unemployment) - create mapping here
        state_df_rec = get_state_unemployment()
        state_ue_map_rec = dict(zip(state_df_rec["State"], state_df_rec["Combined_UE"]))
        best_state = get_city_state(best_city_key)
        state_ue = state_ue_map_rec.get(best_state, None) if best_state else None
        
        # Generate risk assessment
        risks = []
        opportunities = []
        
        if col_index and col_index > 60:
            risks.append(f"High cost of living (Index: {col_index})")
        elif col_index and col_index < 40:
            opportunities.append(f"Affordable living costs (Index: {col_index})")
        
        if state_ue and state_ue < 3:
            risks.append(f"Competitive job market ({state_ue:.1f}% unemployment)")
        elif state_ue and state_ue > 5:
            opportunities.append(f"Less competitive market ({state_ue:.1f}% unemployment)")
        
        if best_skill_match < 0.3:
            risks.append(f"Limited skill match ({best_skill_match:.1%} of jobs)")
        elif best_skill_match > 0.5:
            opportunities.append(f"Strong skill alignment ({best_skill_match:.1%} of jobs)")
        
        # Get current city comparison
        current_city_data = rk_data[rk_data["city_key"] == user_ck]
        current_postings = current_city_data.iloc[0]["postings"] if not current_city_data.empty else 0
        volume_improvement = best_postings / current_postings if current_postings > 0 else 1
        
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(99,102,241,0.1) 100%);
                    border:2px solid rgba(16,185,129,0.3); border-radius:16px; padding:2rem; margin:2rem 0;">
            <div style="display:flex; gap:1rem; align-items:center; margin-bottom:1.5rem;">
                <span style="font-size:2rem;">ðŸŽ¯</span>
                <div>
                    <div style="font-size:1.1rem; font-weight:800; color:#10b981;
                                text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.3rem;">
                        Final Recommendation
                    </div>
                    <div style="font-size:0.9rem; color:#94a3b8;">
                        Based on your skills: {', '.join(phrases[:3])}{'...' if len(phrases) > 3 else ''}
                    </div>
                </div>
            </div>
            
            <div style="background:rgba(0,0,0,0.2); border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
                <div style="font-size:1.3rem; font-weight:700; color:#f8fafc; margin-bottom:0.8rem;">
                    ðŸ† Best City: {best_city}
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div>
                        <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">
                            Composite Score
                        </div>
                        <div style="font-size:1.1rem; font-weight:700; color:#34d399;">
                            {best_score:.2f}/1.00
                        </div>
                    </div>
                    <div>
                        <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">
                            Skill Match Rate
                        </div>
                        <div style="font-size:1.1rem; font-weight:700; color:#34d399;">
                            {best_skill_match:.1%}
                        </div>
                    </div>
                    <div>
                        <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">
                            Job Volume vs Your City
                        </div>
                        <div style="font-size:1.1rem; font-weight:700; color:#34d399;">
                            {volume_improvement:.1f}Ã— more jobs
                        </div>
                    </div>
                    <div>
                        <div style="font-size:0.8rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">
                            Available Positions
                        </div>
                        <div style="font-size:1.1rem; font-weight:700; color:#34d399;">
                            {best_postings:,} jobs
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;">
                <div>
                    <div style="font-size:0.9rem; font-weight:700; color:#10b981; margin-bottom:0.8rem;">
                        âœ… Opportunities
                    </div>
                    <ul style="margin:0; padding-left:1.2rem; color:#cbd5e1; font-size:0.85rem; line-height:1.6;">
                        {"".join(f"<li>{opp}</li>" for opp in opportunities) if opportunities else "<li>Strong overall ranking in our analysis</li>"}
                        <li>Higher job volume than your current city</li>
                        {"<li>Good skill-job alignment</li>" if best_skill_match > 0.4 else ""}
                    </ul>
                </div>
                <div>
                    <div style="font-size:0.9rem; font-weight:700; color:#f59e0b; margin-bottom:0.8rem;">
                        âš ï¸ Considerations
                    </div>
                    <ul style="margin:0; padding-left:1.2rem; color:#cbd5e1; font-size:0.85rem; line-height:1.6;">
                        {"".join(f"<li>{risk}</li>" for risk in risks) if risks else "<li>Research local industry trends</li>"}
                        <li>Verify housing and commute options</li>
                        <li>Consider networking and cultural fit</li>
                    </ul>
                </div>
            </div>
            
            <div style="margin-top:1.5rem; padding-top:1.5rem; border-top:1px solid rgba(148,163,184,0.2);">
                <div style="font-size:0.8rem; color:#94a3b8; line-height:1.6;">
                    <strong style="color:#e2e8f0;">Methodology:</strong> Ranking based on 55% job volume vs your city + 45% skill match rate.
                    Cost of living and unemployment data from official sources. This is a data-driven suggestion â€” 
                    consider personal factors like family, lifestyle, and career goals in your final decision.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Alternative recommendations
        if len(rk_data) > 1:
            st.markdown("**ðŸ”„ Alternative Options**")
            alt_cities = rk_data.iloc[1:4]  # Top 2-4 cities
            
            alt_cols = st.columns(min(3, len(alt_cities)))
            for i, (_, city_row) in enumerate(alt_cities.iterrows()):
                if i < len(alt_cols):
                    with alt_cols[i]:
                        city_col_index = get_cost_of_living_index(city_row["city_key"])
                        col_indicator = ""
                        if city_col_index:
                            if city_col_index > 60:
                                col_indicator = "ðŸ’° Expensive"
                            elif city_col_index < 40:
                                col_indicator = "ðŸ’š Affordable"
                            else:
                                col_indicator = "ðŸ’› Moderate"
                        
                        st.markdown(f"""
                        <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.25);
                                    border-radius:10px; padding:1rem; text-align:center;">
                            <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.5rem;">
                                {city_row['display_name']}
                            </div>
                            <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.3rem;">
                                Score: {city_row['score']:.2f}
                            </div>
                            <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.3rem;">
                                Skills: {city_row['your_skill_match_rate']:.1%}
                            </div>
                            <div style="font-size:0.75rem; color:#6366f1;">
                                {col_indicator}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.caption("ðŸ’¡ **Tip:** Use the tabs above to dive deeper into cost of living, competition levels, and industry alignment for your shortlisted cities.")
    
    else:
        st.info("Enter your skills above to get personalized city recommendations based on job market analysis.")
