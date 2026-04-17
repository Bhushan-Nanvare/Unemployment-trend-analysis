"""
Page 8 — Job Market Pulse
Tab 1: Job Postings Analysis — skill demand, trends, salary range, co-occurrence.
Tab 2: Live India Labor Data — real World Bank labor indicators + India vs World benchmarks.
"""
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.job_market_pulse import (
    default_jobs_csv_path,
    experience_distribution,
    jobs_from_upload,
    load_job_postings,
    location_demand_counts,
    posting_volume_over_time,
    remote_vs_onsite_counts,
    role_demand_counts,
    salary_range_by_role,
    skill_cooccurrence,
    skill_demand_counts,
    skill_gap_analysis,
    skill_momentum,
    weekly_skill_trends,
)
from src.live_data import fetch_gdp_growth, fetch_labor_market_pulse
from src.live_insights import generate_labor_market_insights
from src.ui_helpers import DARK_CSS, render_kpi_card, plotly_dark_layout

st.set_page_config(page_title="Market Pulse | UIP", page_icon="📡", layout="wide")
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 Job Market Pulse")
    st.markdown("---")
    st.markdown("**🌐 Navigation**")
    st.page_link("app.py",                           label="🏠 Home")
    st.page_link("pages/0_Help_Guide.py",             label="❓ Help Guide")
    st.page_link("pages/1_Overview.py",               label="📊 Overview")
    st.page_link("pages/2_Simulator.py",              label="🧪 Simulator")
    st.page_link("pages/3_Sector_Analysis.py",        label="🏭 Sector Analysis")
    st.page_link("pages/4_Career_Lab.py",             label="💼 Career Lab")
    st.page_link("pages/5_AI_Insights.py",            label="🤖 AI Insights")
    st.page_link("pages/7_Job_Risk_Predictor.py",     label="🎯 Job Risk (AI)")
    st.page_link("pages/9_Geo_Career_Advisor.py",     label="🗺️ Geo Career")

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-hero">
    <div class="hero-title">📡 Job Market Pulse</div>
    <div class="hero-subtitle">
        Skill &amp; role demand from real job postings — plus live World Bank India labor indicators.
    </div>
</div>""", unsafe_allow_html=True)

tab_postings, tab_live = st.tabs(["📋 Job Postings Analysis", "📄 Offline Labor Data"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — JOB POSTINGS ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_postings:

    # ── CSV upload (optional) ─────────────────────────────────────────────────
    with st.expander("📂 Use your own data — Upload a CSV", expanded=False):
        st.markdown("""
        <div style="font-size:0.84rem; color:#94a3b8; line-height:1.6; margin-bottom:0.5rem;">
            Upload a job postings CSV with these columns (those available will be used):
            <code>job_title</code>, <code>description</code>, <code>location</code>,
            <code>post_date</code> (YYYY-MM-DD), <code>salary_min_lpa</code>,
            <code>salary_max_lpa</code>, <code>experience_min</code>.
            If no file is uploaded, the bundled 29K India job postings dataset is used.
        </div>
        """, unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload CSV", type=["csv"], key="pulse_upload",
            label_visibility="collapsed"
        )

    # ── Load data ─────────────────────────────────────────────────────────────
    if uploaded_file is not None:
        df = jobs_from_upload(uploaded_file)
        data_label = f"📂 Uploaded: {uploaded_file.name}"
    else:
        df = load_job_postings()
        data_label = f"📦 Bundled dataset: `{default_jobs_csv_path()}`"

    if df.empty:
        st.error(
            "⚠️ No job postings found. The bundled CSV may be missing. "
            "Upload your own CSV using the expander above, or add "
            "`data/market_pulse/job_postings_sample.csv` to the project."
        )
        st.caption(f"Expected path: `{default_jobs_csv_path()}`")
    else:
        st.caption(data_label)

        # ── Filters ───────────────────────────────────────────────────────────
        loc_opts = ["All locations"]
        if "location" in df.columns:
            loc_opts += sorted(df["location"].dropna().astype(str).unique().tolist())

        fc1, fc2, fc3 = st.columns([2, 1, 1])
        with fc1:
            loc = st.selectbox("Filter by location", loc_opts)
        with fc2:
            top_n = st.slider("Top skills to show", 5, 25, 12)
        with fc3:
            trend_skills = st.slider("Skills in trend chart", 3, 8, 5)

        filtered = df if loc == "All locations" else df[df["location"].astype(str) == loc]

        # ── Dataset snapshot KPIs ─────────────────────────────────────────────
        st.markdown('<div class="section-title">📊 Dataset Snapshot</div>',
                    unsafe_allow_html=True)
        remote_counts = remote_vs_onsite_counts(filtered)
        remote_pct = (
            f"{remote_counts.get('Remote', 0) / len(filtered) * 100:.0f}%"
            if len(filtered) > 0 else "N/A"
        )

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric("Total Postings", f"{len(filtered):,}")
        with k2:
            dmin = filtered["post_date"].min() if "post_date" in filtered.columns else None
            dmax = filtered["post_date"].max() if "post_date" in filtered.columns else None
            span = (
                f"{pd.Timestamp(dmin).date()} → {pd.Timestamp(dmax).date()}"
                if dmin is not None and pd.notna(dmin) and pd.notna(dmax)
                else "—"
            )
            st.metric("Date Span", span)
        with k3:
            titles = filtered.get("job_title", pd.Series(dtype=str))
            st.metric("Unique Job Titles", titles.nunique())
        with k4:
            if "location" in filtered.columns:
                st.metric("Unique Locations", filtered["location"].nunique())
        with k5:
            st.metric("Remote Postings", remote_pct)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Skill demand + Role families ──────────────────────────────────────
        skills = skill_demand_counts(filtered).head(top_n)
        roles  = role_demand_counts(filtered).head(12)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-title">🔑 Top Skills (Listing Mentions)</div>',
                        unsafe_allow_html=True)
            if skills.empty:
                st.info("No skill phrases matched in this dataset.")
            else:
                sf = skills.reset_index()
                sf.columns = ["skill", "count"]
                fig_s = px.bar(sf, x="count", y="skill", orientation="h", color="count",
                               color_continuous_scale=["#1e1b4b", "#6366f1", "#06b6d4"])
                fig_s.update_layout(**plotly_dark_layout(height=max(320, 24 * len(sf))))
                fig_s.update_yaxes(autorange="reversed")
                fig_s.update_layout(showlegend=False, coloraxis_showscale=False,
                                    xaxis_title="Postings mentioning skill")
                st.plotly_chart(fig_s, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-title">💼 Top Job Role Families</div>',
                        unsafe_allow_html=True)
            if roles.empty:
                st.info("No roles to chart.")
            else:
                rf = roles.reset_index()
                rf.columns = ["role", "count"]
                fig_r = px.bar(rf, x="count", y="role", orientation="h", color="count",
                               color_continuous_scale=["#312e81", "#8b5cf6", "#34d399"])
                fig_r.update_layout(**plotly_dark_layout(height=max(320, 22 * len(rf))))
                fig_r.update_yaxes(autorange="reversed")
                fig_r.update_layout(showlegend=False, coloraxis_showscale=False,
                                    xaxis_title="Postings")
                st.plotly_chart(fig_r, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Posting volume over time (NEW) ────────────────────────────────────
        vol_series = posting_volume_over_time(filtered, freq="W")
        if not vol_series.empty:
            st.markdown('<div class="section-title">📈 Posting Volume Over Time</div>',
                        unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
                Weekly count of job postings in the dataset — shows whether hiring is
                accelerating or slowing. Spikes often correspond to end-of-quarter
                recruitment pushes.
            </div>""", unsafe_allow_html=True)
            vol_df = vol_series.reset_index()
            vol_df.columns = ["week", "postings"]
            vol_df["week"] = pd.to_datetime(vol_df["week"])
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Scatter(
                x=vol_df["week"], y=vol_df["postings"],
                mode="lines+markers",
                fill="tozeroy",
                fillcolor="rgba(99,102,241,0.10)",
                line=dict(color="#6366f1", width=2.5),
                marker=dict(size=4),
                hovertemplate="<b>Week:</b> %{x|%d %b %Y}<br><b>Postings:</b> %{y}<extra></extra>",
            ))
            fig_vol.update_layout(
                **plotly_dark_layout(height=280),
                xaxis_title="Week",
                yaxis_title="Number of postings",
            )
            st.plotly_chart(fig_vol, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Remote vs On-site split (NEW) ─────────────────────────────────────
        if remote_counts and sum(remote_counts.values()) > 0:
            col_rem, col_mom = st.columns([1, 2])
            with col_rem:
                st.markdown('<div class="section-title">🏠 Work Mode Split</div>',
                            unsafe_allow_html=True)
                st.markdown("""
                <div style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
                    Detected from location field keywords ("remote", "hybrid").
                </div>""", unsafe_allow_html=True)
                rem_df = pd.DataFrame(
                    list(remote_counts.items()), columns=["mode", "count"]
                )
                fig_rem = px.pie(
                    rem_df, names="mode", values="count",
                    color_discrete_sequence=["#6366f1", "#06b6d4", "#10b981"],
                    hole=0.5,
                )
                fig_rem.update_traces(textinfo="percent+label",
                                      textfont=dict(color="#e2e8f0"))
                fig_rem.update_layout(**plotly_dark_layout(height=280, showlegend=False))
                st.plotly_chart(fig_rem, use_container_width=True)
        else:
            col_mom = st.container()

        # ── Skill momentum ────────────────────────────────────────────────────
        st.markdown(
            '<div class="section-title">📊 Skill Demand Momentum (Recent vs Earlier Weeks)</div>',
            unsafe_allow_html=True,
        )
        mom_df = skill_momentum(filtered, top_n_skills=top_n)
        if mom_df.empty:
            st.info("Need valid `post_date` values with multiple weeks to compute momentum.")
        else:
            MOMENTUM_COLORS = {
                "Rising":   "color: #34d399; font-weight: 700;",
                "Stable":   "color: #94a3b8;",
                "Declining":"color: #f87171; font-weight: 700;",
            }
            display_mom = mom_df.rename(columns={
                "skill":     "Skill",
                "recent":    "Recent weeks",
                "earlier":   "Earlier weeks",
                "delta_pct": "Δ% change",
                "momentum":  "Momentum",
            })
            col_m1, col_m2 = st.columns([3, 2])
            with col_m1:
                st.dataframe(
                    display_mom.style.map(
                        lambda v: MOMENTUM_COLORS.get(v, ""),
                        subset=["Momentum"]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            with col_m2:
                rising    = len(mom_df[mom_df["momentum"] == "Rising"])
                stable    = len(mom_df[mom_df["momentum"] == "Stable"])
                declining = len(mom_df[mom_df["momentum"] == "Declining"])
                fig_mom = go.Figure(go.Bar(
                    x=[rising, stable, declining],
                    y=["Rising 📈", "Stable ➡️", "Declining 📉"],
                    orientation="h",
                    marker_color=["#34d399", "#6366f1", "#f87171"],
                    text=[rising, stable, declining],
                    textposition="outside",
                ))
                fig_mom.update_layout(
                    **plotly_dark_layout(height=220),
                    xaxis_title="Skill count",
                )
                st.plotly_chart(fig_mom, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Weekly demand trend ───────────────────────────────────────────────
        st.markdown('<div class="section-title">📅 Weekly Skill Demand Trend</div>',
                    unsafe_allow_html=True)
        trend_df = weekly_skill_trends(filtered, top_n_skills=trend_skills)
        if trend_df.empty:
            st.info("Need valid `post_date` values for weekly trends.")
        else:
            twide = trend_df.reset_index()
            tlong = twide.melt(id_vars=["week"], var_name="skill", value_name="mentions")
            tlong["week"] = pd.to_datetime(tlong["week"])
            fig_t = px.line(tlong, x="week", y="mentions", color="skill", markers=True)
            fig_t.update_layout(**plotly_dark_layout(height=380))
            fig_t.update_xaxes(title_text="Week (start)")
            fig_t.update_yaxes(title_text="Postings mentioning skill")
            st.plotly_chart(fig_t, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Location demand ───────────────────────────────────────────────────
        loc_counts = location_demand_counts(filtered)
        if not loc_counts.empty and loc == "All locations":
            st.markdown('<div class="section-title">📍 Postings by Location</div>',
                        unsafe_allow_html=True)
            lf = loc_counts.reset_index()
            lf.columns = ["location", "postings"]
            fig_loc = px.bar(lf, x="postings", y="location", orientation="h",
                             color="postings",
                             color_continuous_scale=["#1e1b4b", "#7c3aed", "#06b6d4"])
            fig_loc.update_layout(**plotly_dark_layout(height=max(280, 24 * len(lf))))
            fig_loc.update_yaxes(autorange="reversed")
            fig_loc.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_loc, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Salary range distribution (IMPROVED) ──────────────────────────────
        st.markdown('<div class="section-title">💰 Salary Range by Role (LPA)</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
            Based on <code>salary_min_lpa</code> / <code>salary_max_lpa</code> from postings.
            Box shows 25th–75th percentile midpoint range; whiskers show min/max.
            All values in Lakhs Per Annum (LPA) — Indian salary convention.
        </div>""", unsafe_allow_html=True)
        sal_range = salary_range_by_role(filtered)
        if sal_range.empty:
            st.caption("Add numeric `salary_min_lpa` / `salary_max_lpa` columns to populate this chart.")
        else:
            sal_reset = sal_range.reset_index()
            sal_reset.columns = ["Role", "Min LPA", "P25 LPA", "Median LPA", "P75 LPA", "Max LPA", "Postings"]
            fig_sal = go.Figure()
            for _, row in sal_reset.iterrows():
                fig_sal.add_trace(go.Box(
                    name=row["Role"],
                    q1=[row["P25 LPA"]],
                    median=[row["Median LPA"]],
                    q3=[row["P75 LPA"]],
                    lowerfence=[row["Min LPA"]],
                    upperfence=[row["Max LPA"]],
                    orientation="h",
                    marker_color="#6366f1",
                    hovertemplate=(
                        f"<b>{row['Role']}</b><br>"
                        f"Min: {row['Min LPA']} LPA<br>"
                        f"P25: {row['P25 LPA']} LPA<br>"
                        f"Median: {row['Median LPA']} LPA<br>"
                        f"P75: {row['P75 LPA']} LPA<br>"
                        f"Max: {row['Max LPA']} LPA<br>"
                        f"Postings: {int(row['Postings'])}"
                        "<extra></extra>"
                    ),
                ))
            fig_sal.update_layout(
                **plotly_dark_layout(height=max(320, 35 * len(sal_reset)), showlegend=False),
                xaxis_title="Salary (LPA)",
                yaxis_title="",
                boxmode="group",
            )
            st.plotly_chart(fig_sal, use_container_width=True)

            with st.expander("📋 Salary Table", expanded=False):
                st.dataframe(sal_reset.set_index("Role"), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Experience distribution (NEW — if column present) ─────────────────
        exp_df = experience_distribution(filtered)
        if not exp_df.empty:
            st.markdown(
                '<div class="section-title">🎓 Experience Requirements by Role</div>',
                unsafe_allow_html=True,
            )
            st.markdown("""
            <div style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
                Distribution of experience level demanded in job postings (where recorded).
            </div>""", unsafe_allow_html=True)
            fig_exp = px.bar(
                exp_df, x="count", y="role_bucket", color="bracket",
                orientation="h", barmode="stack",
                color_discrete_sequence=["#6366f1", "#06b6d4", "#10b981",
                                         "#f59e0b", "#ef4444"],
            )
            fig_exp.update_layout(
                **plotly_dark_layout(height=max(300, 30 * exp_df["role_bucket"].nunique()),
                                     showlegend=True),
                xaxis_title="Number of postings",
                yaxis_title="",
                legend_title_text="Experience",
            )
            st.plotly_chart(fig_exp, use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)

        # ── Skill co-occurrence heatmap (NEW) ────────────────────────────────
        st.markdown(
            '<div class="section-title">🔗 Skill Co-occurrence Heatmap</div>',
            unsafe_allow_html=True,
        )
        st.markdown("""
        <div style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">
            How often do top skills appear together in the <em>same posting</em>?
            High co-occurrence means employers bundle these skills together —
            learning both increases your market fit significantly.
        </div>""", unsafe_allow_html=True)
        cooc = skill_cooccurrence(filtered, top_n=10)
        if cooc.empty:
            st.info("Not enough skill data to build co-occurrence matrix.")
        else:
            labels = list(cooc.columns)
            z = cooc.values.tolist()
            # Zero out diagonal for cleaner reading
            for i in range(len(z)):
                z[i][i] = 0
            fig_cooc = go.Figure(go.Heatmap(
                z=z,
                x=labels, y=labels,
                colorscale=[
                    [0.0, "#0a0e1a"], [0.3, "#1e3a5f"],
                    [0.6, "#6366f1"], [0.85, "#f59e0b"], [1.0, "#ef4444"],
                ],
                showscale=True,
                text=[[str(v) if v > 0 else "" for v in row] for row in z],
                texttemplate="%{text}",
                textfont=dict(color="white", size=10),
                hovertemplate="<b>%{x}</b> + <b>%{y}</b><br>Co-occurs in %{z} postings<extra></extra>",
                colorbar=dict(
                    title=dict(text="Postings", font=dict(color="#94a3b8")),
                    tickfont=dict(color="#94a3b8"),
                ),
            ))
            fig_cooc.update_layout(
                **plotly_dark_layout(height=420),
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig_cooc, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Personal skill gap analyzer ───────────────────────────────────────
        st.markdown(
            '<div class="section-title">🎯 Personal Skill Gap Analyzer</div>',
            unsafe_allow_html=True,
        )
        st.caption("Enter your current skills — see which top in-demand skills you have and which are gaps.")
        user_skill_input = st.text_input(
            "Your skills (comma-separated)",
            placeholder="e.g. Python, SQL, machine learning, agile, git",
            key="pulse_skill_gap",
        )
        if user_skill_input.strip():
            gap_df = skill_gap_analysis(filtered, user_skill_input, top_n=top_n)
            if gap_df.empty:
                st.info("No matching demand data. Try a larger dataset.")
            else:
                have_count = int(gap_df["You have it"].sum())
                miss_count = int((~gap_df["You have it"]).sum())
                g1, g2, g3 = st.columns(3)
                g1.metric("Top skills analysed", len(gap_df))
                g2.metric("You have", have_count)
                g3.metric("Gaps to close", miss_count, delta_color="inverse")

                st.dataframe(
                    gap_df.style.map(
                        lambda val: (
                            "background-color: rgba(16,185,129,0.12); color: #34d399; font-weight: 700;"
                            if val is True
                            else "background-color: rgba(248,113,113,0.10); color: #f87171; font-weight: 700;"
                            if val is False
                            else ""
                        ),
                        subset=["You have it"],
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                missing = gap_df[~gap_df["You have it"]]["Skill"].tolist()
                if missing:
                    st.markdown("**Priority gaps** (sorted by market demand):")
                    st.markdown(
                        " &nbsp;·&nbsp; ".join(
                            f'<span style="background:rgba(99,102,241,0.15); border:1px solid #6366f1;'
                            f'border-radius:4px; padding:2px 8px; color:#a5b4fc;">{sk}</span>'
                            for sk in missing[:8]
                        ),
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Type your skills above to see your gap analysis.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Export ────────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📥 Export Market Data</div>',
                    unsafe_allow_html=True)
        if not skills.empty:
            export_parts = []
            skills_export = skills.reset_index()
            skills_export.columns = ["Skill", "Demand Count"]
            export_parts.append("=== TOP SKILL DEMAND ===")
            export_parts.append(skills_export.to_csv(index=False))
            if not mom_df.empty:
                export_parts.append("\n=== SKILL MOMENTUM ===")
                export_parts.append(mom_df.to_csv(index=False))
            if not sal_range.empty:
                export_parts.append("\n=== SALARY RANGE BY ROLE ===")
                export_parts.append(sal_range.reset_index().to_csv(index=False))
            csv_bytes = "\n".join(export_parts).encode()
            st.download_button(
                "⬇️ Download market data (CSV)",
                csv_bytes,
                file_name="job_market_pulse_export.csv",
                mime="text/csv",
            )
        else:
            st.caption("No skill data to export.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LIVE INDIA LABOR DATA (World Bank)
# ══════════════════════════════════════════════════════════════════════════════
with tab_live:

    st.markdown("""
    <div style="background:rgba(16,185,129,0.06); border:1px solid rgba(16,185,129,0.2);
                border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.5rem;">
        <div style="font-size:0.82rem; font-weight:700; color:#34d399;
                    text-transform:uppercase; letter-spacing:1px; margin-bottom:0.3rem;">
            📄 Offline mode
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.55;">
            Live World Bank API data has been disabled for reliability on Streamlit Cloud.
            This view now shows only what’s available from bundled offline datasets.
        </div>
    </div>
    """, unsafe_allow_html=True)

    live_data = fetch_labor_market_pulse("India")
    world_data = {}
    gdp_df = None

    if not live_data:
        st.info("No offline labor indicator dataset is available here (job postings analysis is still fully functional).")
    else:
        # ── AI Insights ────────────────────────────────────────────────────────
        labor_insights = generate_labor_market_insights(live_data)
        if labor_insights:
            bullets_html = "".join(
                f'<li style="margin-bottom:0.45rem; color:#cbd5e1; font-size:0.9rem; line-height:1.6;">'
                + s.replace("**", "<strong style='color:#e2e8f0;'>", 1).replace("**", "</strong>", 1)
                + "</li>"
                for s in labor_insights
            )
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.25);
                        border-radius:14px; padding:1rem 1.5rem; margin-bottom:1.4rem;">
                <div style="display:flex; gap:0.6rem; align-items:center; margin-bottom:0.6rem;">
                    <span style="font-size:1.1rem;">💡</span>
                    <span style="font-size:0.78rem; font-weight:700; color:#818cf8;
                                  text-transform:uppercase; letter-spacing:1px;">
                        Labor Market Intelligence — Key Insights
                    </span>
                </div>
                <ul style="margin:0; padding-left:1.2rem;">{bullets_html}</ul>
            </div>
            """, unsafe_allow_html=True)

        # ── KPI strip (with data freshness label) ┤────────────────────────────
        KEY_KPIS = [
            ("Unemployment Rate (%)",        "📊", "neutral"),
            ("Youth Unemployment 15-24 (%)", "👶", "up"),
            ("Labor Force Participation (%)", "💪", "neutral"),
            ("Vulnerable Employment (%)",     "⚠️",  "up"),
        ]
        kpi_cols = st.columns(len(KEY_KPIS))
        for col, (label, icon, dt) in zip(kpi_cols, KEY_KPIS):
            with col:
                series = live_data.get(label)
                if series is not None and not series.empty:
                    latest_val  = float(series.iloc[-1]["Value"])
                    latest_year = int(series.iloc[-1]["Year"])
                    delta = ""
                    if len(series) >= 2:
                        prev = float(series.iloc[-2]["Value"])
                        chg  = round(latest_val - prev, 2)
                        arrow = "▲" if chg > 0 else "▼"
                        delta = f"{arrow} {abs(chg):.2f} pp vs {latest_year - 1}"
                    st.markdown(
                        render_kpi_card(icon, f"{label} ({latest_year})",
                                        f"{latest_val:.1f}%", delta, dt),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        render_kpi_card(icon, label, "N/A", "Data unavailable", "neutral"),
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Historical trend selector ─────────────────────────────────────────
        st.markdown(
            '<div class="section-title">📈 Historical Trend — Select Indicators</div>',
            unsafe_allow_html=True,
        )
        available_labels = list(live_data.keys())
        selected_indicators = st.multiselect(
            "Select indicators to compare",
            options=available_labels,
            default=available_labels[:3] if len(available_labels) >= 3 else available_labels,
            key="live_indicator_select",
        )

        if selected_indicators:
            COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444",
                      "#06b6d4", "#8b5cf6", "#ec4899", "#14b8a6"]
            fig_ts = go.Figure()
            for idx, lbl in enumerate(selected_indicators):
                series = live_data.get(lbl)
                if series is None or series.empty:
                    continue
                color = COLORS[idx % len(COLORS)]
                fig_ts.add_trace(go.Scatter(
                    x=series["Year"], y=series["Value"],
                    mode="lines+markers", name=lbl,
                    line=dict(color=color, width=2.5),
                    marker=dict(size=5, color=color),
                    hovertemplate=f"<b>{lbl}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}%<extra></extra>",
                ))
            fig_ts.update_layout(
                **plotly_dark_layout(height=420),
                xaxis_title="Year", yaxis_title="Percent (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="right", x=1,
                            bgcolor="rgba(0,0,0,0.3)", font=dict(color="#cbd5e1")),
            )
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("Select at least one indicator above.")

        st.markdown("<br>", unsafe_allow_html=True)

        # GDP growth overlay removed in offline-only mode.

        # ── Gender & age breakdown ─────────────────────────────────────────────
        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown(
                '<div class="section-title">👥 Unemployment by Gender &amp; Age Group</div>',
                unsafe_allow_html=True,
            )
            breakdown_labels = [
                "Unemployment Rate (%)",
                "Female Unemployment (%)",
                "Male Unemployment (%)",
                "Youth Unemployment 15-24 (%)",
            ]
            COLORS_B = ["#6366f1", "#ec4899", "#06b6d4", "#f59e0b"]
            breakdown_fig = go.Figure()
            for idx, lbl in enumerate(breakdown_labels):
                s = live_data.get(lbl)
                if s is None or s.empty:
                    continue
                breakdown_fig.add_trace(go.Scatter(
                    x=s["Year"], y=s["Value"],
                    mode="lines", name=lbl.replace(" (%)", ""),
                    line=dict(color=COLORS_B[idx % 4], width=2),
                    hovertemplate=f"<b>{lbl}</b><br>%{{y:.2f}}%<extra></extra>",
                ))
            breakdown_fig.update_layout(
                **plotly_dark_layout(height=340),
                xaxis_title="Year", yaxis_title="%",
            )
            st.plotly_chart(breakdown_fig, use_container_width=True)

        with col_r:
            st.markdown(
                '<div class="section-title">📋 Latest Snapshot — All Indicators</div>',
                unsafe_allow_html=True,
            )
            snapshot_rows = []
            for lbl, series in live_data.items():
                if series is None or series.empty:
                    continue
                latest = series.iloc[-1]
                yr = int(latest["Year"])
                val = round(float(latest["Value"]), 2)
                chg = None
                if len(series) >= 2:
                    chg = round(val - float(series.iloc[-2]["Value"]), 2)
                snapshot_rows.append({
                    "Indicator":   lbl.replace(" (%)", ""),
                    "Year":        yr,
                    "Value (%)":   val,
                    "YoY Change":  (
                        f"{'▲' if chg > 0 else '▼'} {abs(chg):.2f} pp"
                        if chg is not None else "—"
                    ),
                })
            if snapshot_rows:
                snap_df = pd.DataFrame(snapshot_rows)

                def _color_change(val):
                    if isinstance(val, str) and "▲" in val:
                        return "color: #f87171"
                    if isinstance(val, str) and "▼" in val:
                        return "color: #34d399"
                    return ""

                st.dataframe(
                    snap_df.style.map(_color_change, subset=["YoY Change"]),
                    use_container_width=True,
                    hide_index=True,
                    height=340,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── India vs World benchmarks (NEW) ────────────────────────────────────
        st.markdown(
            '<div class="section-title">🌍 Benchmarks</div>',
            unsafe_allow_html=True,
        )
        st.info("India vs World benchmarks are unavailable in offline-only mode.")

        BENCH_INDICATORS = [
            "Unemployment Rate (%)",
            "Youth Unemployment 15-24 (%)",
            "Labor Force Participation (%)",
            "Female Unemployment (%)",
            "Vulnerable Employment (%)",
        ]
        bench_rows = []
        for ind in BENCH_INDICATORS:
            india_s = live_data.get(ind)
            world_s = world_data.get(ind) if world_data else None
            india_v = float(india_s.iloc[-1]["Value"]) if india_s is not None and not india_s.empty else None
            world_v = float(world_s.iloc[-1]["Value"]) if world_s is not None and not world_s.empty else None
            if india_v is None:
                continue
            gap = round(india_v - world_v, 2) if world_v is not None else None
            bench_rows.append({
                "Indicator": ind.replace(" (%)", ""),
                "India (%)": round(india_v, 1),
                "World Avg (%)": round(world_v, 1) if world_v is not None else "N/A",
                "Gap (India − World)": (
                    f"{'▲ +' if gap > 0 else '▼ '}{gap:.2f} pp"
                    if gap is not None else "N/A"
                ),
            })

        if bench_rows:
            bench_df = pd.DataFrame(bench_rows)

            # Comparison bar chart
            bench_plot = bench_df[bench_df["World Avg (%)"] != "N/A"].copy()
            if not bench_plot.empty:
                bench_plot["World Avg (%)"] = bench_plot["World Avg (%)"].astype(float)
                fig_bench = go.Figure()
                fig_bench.add_trace(go.Bar(
                    name="India",
                    x=bench_plot["Indicator"],
                    y=bench_plot["India (%)"],
                    marker_color="#6366f1",
                    text=bench_plot["India (%)"].apply(lambda v: f"{v}%"),
                    textposition="outside",
                ))
                fig_bench.add_trace(go.Bar(
                    name="World Average",
                    x=bench_plot["Indicator"],
                    y=bench_plot["World Avg (%)"],
                    marker_color="rgba(100,116,139,0.6)",
                    text=bench_plot["World Avg (%)"].apply(lambda v: f"{v}%"),
                    textposition="outside",
                ))
                fig_bench.update_layout(
                    **plotly_dark_layout(height=360, showlegend=True),
                    barmode="group",
                    xaxis_title="",
                    yaxis_title="Percent (%)",
                    xaxis=dict(tickangle=-20),
                )
                st.plotly_chart(fig_bench, use_container_width=True)

            def _bench_style(val):
                if isinstance(val, str) and "▲" in val:
                    return "color: #f87171; font-weight: 700;"
                if isinstance(val, str) and "▼" in val:
                    return "color: #34d399; font-weight: 700;"
                return ""

            st.dataframe(
                bench_df.style.map(_bench_style, subset=["Gap (India − World)"]),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Source: World Bank Open Data API · SL.UEM.*, SL.TLF.*, SL.EMP.* · "
                "Latest available year (typically 2022–2023 for India)"
            )
        else:
            if world_data:
                st.info("Benchmark comparison unavailable — World Bank global aggregate data not returned for these indicators.")
            else:
                st.info("Benchmark comparison unavailable — could not fetch World average data. Check internet connection.")

        # ── Export offline data ───────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📥 Export Live Data</div>',
                    unsafe_allow_html=True)
        export_frames = []
        for lbl, series in live_data.items():
            if series is not None and not series.empty:
                temp = series.copy()
                temp["Indicator"] = lbl
                export_frames.append(temp)
        if export_frames:
            export_df = pd.concat(export_frames, ignore_index=True)[["Indicator", "Year", "Value"]]
            csv_bytes = export_df.to_csv(index=False).encode()
            st.download_button(
                "⬇️ Download India labor indicators (CSV)",
                csv_bytes,
                file_name="india_labor_market_offline.csv",
                mime="text/csv",
            )
            st.caption(
                "Source: Offline dataset bundled with this app."
            )
