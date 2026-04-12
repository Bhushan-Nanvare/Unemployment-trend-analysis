"""
Page 9 — Geo-Aware Career Advisor (Feature 8)

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
from src.job_risk_model import EDUCATION_LEVELS, INDUSTRY_GROWTH, LOCATION_OPTIONS, predict_job_risk
from src.live_data import fetch_labor_market_pulse, get_state_unemployment
from src.live_insights import generate_labor_market_insights
from src.ui_helpers import DARK_CSS, plotly_dark_layout, render_kpi_card

st.set_page_config(page_title="Geo Career | UIP", page_icon="🗺️", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🗺️ Geo Career Advisor")
    st.caption(
        "WGS84 + Folium + optional Nominatim (OSM). "
        "Metrics are computed from your posting CSV — swap in real feeds for production."
    )
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py", label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py", label="❓ Help Guide")
    st.page_link("pages/1_Overview.py", label="📊 Overview")
    st.page_link("pages/2_Simulator.py", label="🧪 Simulator")
    st.page_link("pages/3_Sector_Analysis.py", label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py", label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py", label="🤖 AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py", label="🎯 Job Risk (AI)")
    st.page_link("pages/8_Job_Market_Pulse.py", label="📡 Market Pulse")
    st.page_link("pages/10_Skill_Obsolescence.py", label="⚡ Skill Obsolescence")


@st.cache_data(ttl=86400, show_spinner=False)
def cached_geocode(query: str):
    from src.geo_career_advisor import geocode_place
    return geocode_place(query)


st.markdown("""
<div class="page-hero">
    <div class="hero-title">🗺️ Geo-Aware Career Advisor</div>
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

# ── Data Processing & Filtering ────────────────────────────────────────────────
if skills.strip():
    import re
    phrases = [p.strip() for p in re.split(r"[,;\n]+", skills.lower()) if p.strip()]
else:
    phrases = []

user_ck = normalize_city_key(home_display)

# Map Options UI

col_m1, col_m2 = st.columns([1, 1])
with col_m1:
    st.markdown('<div class="section-title">Hiring intensity map</div>', unsafe_allow_html=True)
    st.caption("Basemap: CartoDB Positron (OSM). Circle area scales with posting count.")
with col_m2:
    map_mode = st.radio(
        "Map Data Source", 
        ["Total Market Demand", "Matched to My Skills (Dynamic)"], 
        horizontal=True,
        help="Switch to 'My Skills' to see only job postings that match the skills you entered above."
    )

# Dynamic Filtering
if map_mode == "Matched to My Skills (Dynamic)" and phrases:
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
    if map_mode == "Matched to My Skills (Dynamic)" and not phrases:
        st.info("Enter skills above to use dynamic mapping. Showing total market data.")
    df_for_map = df_jobs

# Recompute agg ONLY for the map, so the tabs still have full dataset context
map_agg = aggregate_city_labour_market(df_for_map)

extra_pin = None
if geocode_query.strip():
    geo = cached_geocode(geocode_query.strip())
    if geo:
        extra_pin = (geo[0], geo[1], geo[2])
    else:
        st.caption("Geocoder returned no result — check spelling or try a larger nearby city.")

# ── Personalized Recommendation Header ─────────────────────────────────────────
if phrases and not map_agg.empty:
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
            <span style="font-size:1.3rem;">🎯</span>
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
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── City posting volume + salary chart ────────────────────────────────────────
if not agg.empty:
    
    st.markdown(
        '<div class="section-title">📊 City hiring volume & median salary</div>',
        unsafe_allow_html=True,
    )
    agg_disp = agg.copy()
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
    if len(salary_data) >= 3 and "median_lpa" in agg_disp.columns:
        # Filter to cities with reasonable salary coverage (>10% of jobs have salary data)
        if "salary_coverage_pct" in agg_disp.columns:
            salary_data = salary_data[salary_data["salary_coverage_pct"] >= 10]
        
        if len(salary_data) >= 3:
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
            st.caption("⚠️ Insufficient salary data for trend line (need ≥3 cities with >10% salary coverage)")
    else:
        st.caption("⚠️ No salary data available for median salary trend line")
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
    
    st.caption("Cyan bar = your selected city. Salary trend requires ≥3 cities with >10% salary coverage.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Relocation ranking", "Location quotients",
    "Modeled risk by tier", "🌐 Live India Context",
    "💰 Cost of Living", "🏭 Industry Hubs", "🗺️ State Unemployment Map"
])

with tab1:
    st.markdown(
        "Ranks cities by a **transparent composite**: "
        "55% normalized posting volume vs your city, 45% share of local jobs matching your skills."
    )
    rk = rank_relocation_targets(df_jobs, user_ck, phrases)
    if rk.empty:
        st.info("Not enough city-level rows to rank.")
    else:
        rk_disp = rk.rename(columns={
            "display_name": "City",
            "postings": "Postings",
            "volume_vs_yours": "Volume vs yours (×)",
            "your_skill_match_rate": "Skill match rate",
            "score": "Composite score",
        })[["City", "Postings", "Volume vs yours (×)", "Skill match rate", "Composite score"]]

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
            "⬇ Export relocation ranking (CSV)",
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
        "**Location quotient (LQ)** ≈ (local mention rate) ÷ (national mention rate). "
        "LQ > 1 means the skill appears more often in that city than in the full sample."
    )
    if not phrases:
        st.info("Enter your skills above to compute LQs for your city.")
    else:
        lq = skill_location_quotients(df_jobs, user_ck, phrases)
        if lq.empty:
            st.warning("Could not resolve your city in the posting extract for LQ — try a city from the dataset list.")
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
                    title=f"Location quotients — {home_display}",
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

with tab3:
    st.markdown(
        "Uses the **same logistic job-risk model** as the Job Risk page: "
        "only the location tier changes — no hard-coded percentage claims."
    )
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        education = st.selectbox("Education", EDUCATION_LEVELS, index=2, key="geo_edu")
    with col_b:
        experience = st.slider("Years experience", 0, 40, 3, key="geo_exp")
    with col_c:
        industry = st.selectbox("Industry", list(INDUSTRY_GROWTH.keys()), key="geo_ind")

    row = resolve_city_row(home_display)
    from_tier = int(row["market_tier_index"]) if row is not None else 1
    tier_labels = ["Metro / Tier-1", "Tier-2 city", "Smaller town / rural"]
    st.caption(f"Your city's reference tier: **{tier_labels[from_tier]}** (from `data/geo/india_city_reference.csv`).")

    target_opts = [r for r in city_keys_in_data if r != user_ck]
    if not target_opts:
        target_opts = city_keys_in_data
    ref_df = load_city_reference()
    labels = {
        r["city_key"]: str(r["display_name"])
        for _, r in ref_df.iterrows()
    } if not ref_df.empty else {}
    target_city = st.selectbox(
        "Compare modeled risk if you were based in",
        target_opts,
        format_func=lambda k: labels.get(k, k.replace("_", " ").title()),
    )
    match = ref_df[ref_df["city_key"] == target_city] if not ref_df.empty else pd.DataFrame()
    to_tier = int(match.iloc[0]["market_tier_index"]) if len(match) else 1

    p0, p1, dpp = relocation_model_delta_pct(
        skills, education, experience, industry, from_tier, to_tier
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Risk % (current tier)", f"{p0}%")
    m2.metric("Risk % (target tier)", f"{p1}%")
    delta_color = "normal" if dpp <= 0 else "inverse"
    m3.metric("Δ probability", f"{dpp:+} pp", delta=f"{dpp:+} pp", delta_color=delta_color,
              help="Percentage points; negative = lower modeled risk.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Risk across all 3 tiers
    all_tier_risks = []
    for ti, tlabel in enumerate(tier_labels):
        loc = LOCATION_OPTIONS[ti]
        r = predict_job_risk(skills, education, experience, loc, industry)
        all_tier_risks.append({
            "Tier": tlabel,
            "Risk %": r.high_risk_probability_pct,
            "is_current": ti == from_tier,
        })
    tier_df = pd.DataFrame(all_tier_risks)

    fig_tier = go.Figure(go.Bar(
        x=tier_df["Tier"],
        y=tier_df["Risk %"],
        marker_color=[
            "#06b6d4" if row["is_current"] else "#6366f1"
            for _, row in tier_df.iterrows()
        ],
        text=[f"{v}%" for v in tier_df["Risk %"]],
        textposition="outside",
    ))
    fig_tier.update_layout(
        **plotly_dark_layout(height=320),
        title="Modeled risk across all location tiers (same profile)",
        yaxis_title="High-risk probability (%)",
        xaxis_title="Location tier",
    )
    st.plotly_chart(fig_tier, use_container_width=True)
    st.caption("Cyan bar = your current city's tier.")

    if target_city == user_ck:
        st.caption("Pick a different target city to compare a different tier.")

# ── TAB 4 — LIVE INDIA CONTEXT ─────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.25);
                border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;
                display:flex; gap:0.75rem; align-items:flex-start;">
        <div style="font-size:1.3rem;">🌐</div>
        <div>
            <div style="font-size:0.82rem; font-weight:700; color:#818cf8;
                        text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
                Real India Labor Data</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.55;">
                <strong style="color:#e2e8f0;">National trends</strong> are fetched live from the
                <strong style="color:#e2e8f0;">World Bank Open API</strong>.
                <strong style="color:#e2e8f0;">State-level data</strong> is from the official
                <strong style="color:#e2e8f0;">PLFS 2022-23 report</strong> (MOSPI, Govt. of India) —
                state unemployment is not available on the World Bank API.
                Use this view to ground your city decision in real macro and regional data.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── National KPIs from World Bank
    st.markdown('<div class="section-title">📊 India National Labor Snapshot (World Bank)</div>',
                unsafe_allow_html=True)

    with st.spinner("Fetching live data from World Bank…"):
        wb_data = fetch_labor_market_pulse("India")

    # ── AI Insight Box ─────────────────────────────────────────────────────────
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
                <span style="font-size:1.1rem;">💡</span>
                <span style="font-size:0.78rem; font-weight:700; color:#818cf8;
                              text-transform:uppercase; letter-spacing:1px;">
                    India Labor Market Context — What This Means for Your City Choice
                </span>
            </div>
            <ul style="margin:0; padding-left:1.2rem;">{bullets_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    KEY_KPIS = [
        ("Unemployment Rate (%)",       "📊", "neutral"),
        ("Youth Unemployment 15-24 (%)","👶", "up"),
        ("Labor Force Participation (%)","💪", "neutral"),
        ("Employment-to-Population (%)","🏭", "neutral"),
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
                    arrow = "▲" if chg > 0 else "▼"
                    delta_txt = f"{arrow} {abs(chg)}pp vs {latest_year - 1}"
                st.markdown(
                    render_kpi_card(icon, label, f"{latest_val:.1f}%", delta_txt, dt),
                    unsafe_allow_html=True
                )
            else:
                st.markdown(render_kpi_card(icon, label, "N/A", "Unavailable", "neutral"),
                            unsafe_allow_html=True)

    # ── National unemployment trend sparkline
    if wb_data.get("Unemployment Rate (%)") is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">📈 India Unemployment Trend (World Bank, 1991–2023)</div>',
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
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── State-level unemployment breakdown (PLFS 2022-23)
    
    st.markdown('<div class="section-title">🗺️ State-Level Unemployment — PLFS 2022-23 (UPS, 15+ yrs)</div>',
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
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Region comparison
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">🏙️ Average Unemployment by Region</div>',
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
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Export
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📥 Export State Data</div>', unsafe_allow_html=True)
    csv_bytes = state_df.to_csv(index=False).encode()
    st.download_button(
        "⬇ Download PLFS State Unemployment Data (CSV)",
        csv_bytes,
        file_name="india_state_unemployment_plfs2023.csv",
        mime="text/csv",
    )
    st.caption("Source: PLFS Annual Report 2022-23 | Ministry of Statistics & Programme Implementation (MOSPI)")


# ── TAB 5 — COST OF LIVING ANALYSIS ────────────────────────────────────────────
with tab5:
    st.markdown("""
    <div style="background:rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.25);
                border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
        <div style="font-size:0.82rem; font-weight:700; color:#f59e0b;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
            💰 Purchasing Power Analysis</div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
            Cost of Living Index (base 50 = India average). Higher index = more expensive.
            <strong style="color:#e2e8f0;">Real Salary</strong> = Nominal Salary ÷ (COL Index / 50).
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

# ── TAB 6 — INDUSTRY CONCENTRATION ─────────────────────────────────────────────
with tab6:
    st.markdown("""
    <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.25);
                border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
        <div style="font-size:0.82rem; font-weight:700; color:#818cf8;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
            🏭 Industry Specialization Analysis</div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
            <strong style="color:#e2e8f0;">Location Quotient (LQ)</strong> measures industry concentration.
            LQ > 1.5 = city specializes in that industry. LQ < 0.7 = underrepresented.
            Based on keyword analysis of job descriptions.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    from src.geo_career_advisor import analyze_industry_concentration
    
    industry_city = st.selectbox(
        "Select city for industry analysis",
        options=city_keys_in_data,
        format_func=lambda k: labels.get(k, k.replace("_", " ").title()),
        key="industry_city_select",
    )
    
    with st.spinner("Analyzing industry concentration..."):
        industry_df = analyze_industry_concentration(df_jobs, industry_city)
    
    if not industry_df.empty:
        col_ind1, col_ind2 = st.columns([2, 3])
        
        with col_ind1:
            st.markdown("**Industry Concentration Table**")
            st.dataframe(
                industry_df[["Industry", "Local_Jobs", "Location_Quotient"]], use_container_width=True,
                hide_index=True,
            )
            
            # Highlight specializations
            specialized = industry_df[industry_df["Location_Quotient"] >= 1.5]
            if not specialized.empty:
                st.markdown("**🎯 City Specializations (LQ ≥ 1.5):**")
                for _, row in specialized.iterrows():
                    st.markdown(f"• **{row['Industry']}** (LQ: {row['Location_Quotient']})")
        
        with col_ind2:
            st.markdown("**Location Quotient by Industry**")
            fig_ind = px.bar(
                industry_df,
                x="Location_Quotient",
                y="Industry",
                orientation="h",
                color="Location_Quotient",
                color_continuous_scale=["#ef4444", "#fbbf24", "#10b981"],
                text="Location_Quotient",
            )
            fig_ind.add_vline(x=1.0, line_dash="dot", line_color="#94a3b8",
                             annotation_text="National Avg", annotation_position="top right")
            fig_ind.add_vline(x=1.5, line_dash="dash", line_color="#10b981",
                             annotation_text="Specialization", annotation_position="bottom right")
            fig_ind.update_traces(texttemplate="%{text:.2f}", textposition="outside")
            fig_ind.update_layout(**plotly_dark_layout(height=400))
            fig_ind.update_layout(
                xaxis_title="Location Quotient",
                yaxis_title="",
                coloraxis_showscale=False,
            )
            fig_ind.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_ind, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Industry Share Comparison**")
        
        fig_share = go.Figure()
        fig_share.add_trace(go.Bar(
            x=industry_df["Industry"],
            y=industry_df["Local_Share_Pct"],
            name=f"{industry_city.title()} Share",
            marker_color="#6366f1",
        ))
        fig_share.add_trace(go.Bar(
            x=industry_df["Industry"],
            y=industry_df["National_Share_Pct"],
            name="National Share",
            marker_color="#94a3b8",
        ))
        fig_share.update_layout(**plotly_dark_layout(height=350))
        fig_share.update_layout(
            xaxis_title="Industry",
            yaxis_title="Share of Jobs (%)",
            barmode="group",
            xaxis_tickangle=-45,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_share, use_container_width=True)
        
        st.caption("""
        **Example:** If Bengaluru has 45% IT-Software jobs vs 25% nationally, LQ = 1.8 (specialized).
        Use this to find cities that match your industry.
        """)
    else:
        st.warning("Could not analyze industry concentration for this city. Try a city with more job postings.")

# ── TAB 7 — STATE UNEMPLOYMENT CHOROPLETH ──────────────────────────────────────
with tab7:
    st.markdown("""
    <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.25);
                border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
        <div style="font-size:0.82rem; font-weight:700; color:#10b981;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
            🗺️ State-Level Unemployment Context</div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.6;">
            PLFS 2022-23 official data overlaid with city job demand.
            <strong style="color:#e2e8f0;">High state unemployment + high city job demand</strong>
            = opportunity for local talent. Low state unemployment = competitive labor market.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    state_df = get_state_unemployment()
    
    # Create state-to-unemployment mapping
    state_ue_map = dict(zip(state_df["State"], state_df["Combined_UE"]))
    
    # Add state unemployment to city aggregation
    agg_with_state = agg.copy()
    agg_with_state["State"] = agg_with_state["city_key"].apply(get_city_state)
    agg_with_state["State_UE"] = agg_with_state["State"].map(state_ue_map)
    
    # Filter to cities with state data
    agg_with_state = agg_with_state.dropna(subset=["State_UE", "lat", "lon"])
    
    if not agg_with_state.empty:
        st.markdown("**City Job Demand vs State Unemployment**")
        
        fig_state = px.scatter(
            agg_with_state.head(30),
            x="State_UE",
            y="postings",
            size="postings",
            color="State_UE",
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            hover_data={"display_name": True, "State": True, "State_UE": ":.1f", "postings": True},
            text="display_name",
            labels={"State_UE": "State Unemployment (%)", "postings": "Job Postings"},
        )
        fig_state.update_traces(textposition="top center", textfont_size=9)
        fig_state.update_layout(**plotly_dark_layout(height=450))
        fig_state.update_layout(
            xaxis_title="State Unemployment Rate (%)",
            yaxis_title="City Job Postings",
        )
        st.plotly_chart(fig_state, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**State Unemployment Heatmap**")
        
        # Group by state
        state_agg = (
            agg_with_state.groupby("State")
            .agg({"postings": "sum", "State_UE": "first"})
            .reset_index()
            .sort_values("State_UE", ascending=False)
        )
        
        fig_heat = px.bar(
            state_agg.head(20),
            x="State",
            y="State_UE",
            color="State_UE",
            color_continuous_scale=["#10b981", "#f59e0b", "#ef4444"],
            text="State_UE",
            hover_data={"postings": True},
        )
        fig_heat.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_heat.update_layout(**plotly_dark_layout(height=400))
        fig_heat.update_layout(
            xaxis_title="State",
            yaxis_title="Unemployment Rate (%)",
            xaxis_tickangle=-45,
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Opportunity Matrix**")
        
        # Classify cities
        median_ue = state_agg["State_UE"].median()
        median_postings = agg_with_state["postings"].median()
        
        agg_with_state["Opportunity"] = "Moderate"
        agg_with_state.loc[
            (agg_with_state["State_UE"] > median_ue) & (agg_with_state["postings"] > median_postings),
            "Opportunity"
        ] = "High (High demand + High UE)"
        agg_with_state.loc[
            (agg_with_state["State_UE"] < median_ue) & (agg_with_state["postings"] > median_postings),
            "Opportunity"
        ] = "Competitive (High demand + Low UE)"
        agg_with_state.loc[
            (agg_with_state["State_UE"] > median_ue) & (agg_with_state["postings"] < median_postings),
            "Opportunity"
        ] = "Limited (Low demand + High UE)"
        
        opportunity_df = agg_with_state[["display_name", "State", "State_UE", "postings", "Opportunity"]].copy()
        opportunity_df.columns = ["City", "State", "State UE (%)", "Job Postings", "Opportunity Type"]
        opportunity_df = opportunity_df.sort_values("Job Postings", ascending=False).head(20)
        
        def _style_opportunity(val):
            if "High" in str(val) and "Competitive" not in str(val):
                return "background-color: rgba(16,185,129,0.2); color: #10b981; font-weight: 700;"
            elif "Competitive" in str(val):
                return "background-color: rgba(245,158,11,0.2); color: #f59e0b; font-weight: 700;"
            elif "Limited" in str(val):
                return "background-color: rgba(239,68,68,0.2); color: #ef4444; font-weight: 700;"
            return ""
        
        st.dataframe(
            opportunity_df.style.map(_style_opportunity, subset=["Opportunity Type"]), use_container_width=True,
            hide_index=True,
        )
        
        st.caption("""
        **High Opportunity:** State has high unemployment but city has strong job demand — good for local talent.
        **Competitive:** Low state unemployment means tight labor market — harder to find jobs but better economy.
        **Limited:** High unemployment + low job demand — consider other locations.
        """)
    else:
        st.info("State unemployment data not available for cities in the dataset.")
