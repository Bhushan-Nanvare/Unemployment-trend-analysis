"""
validation_ui_helpers.py

UI HELPER FUNCTIONS FOR VALIDATION SYSTEM
==========================================

Streamlit UI components for displaying data quality indicators,
validation warnings, and system health status.

Author: System Integration
Date: 2026-04-13
Version: 1.0.0
"""

from typing import List, Dict, Optional


def get_quality_emoji(score: float) -> str:
    """
    Get quality indicator emoji based on score.
    
    Args:
        score: Quality score (0-100)
    
    Returns:
        Emoji indicator
    """
    if score >= 90:
        return "🟢"
    elif score >= 70:
        return "🟡"
    else:
        return "🔴"


def get_quality_label(score: float) -> str:
    """
    Get quality label based on score.
    
    Args:
        score: Quality score (0-100)
    
    Returns:
        Quality label
    """
    if score >= 90:
        return "Excellent"
    elif score >= 80:
        return "Good"
    elif score >= 70:
        return "Fair"
    elif score >= 50:
        return "Poor"
    else:
        return "Critical"


def get_quality_color(score: float) -> str:
    """
    Get color for quality score.
    
    Args:
        score: Quality score (0-100)
    
    Returns:
        Hex color code
    """
    if score >= 90:
        return "#10b981"
    elif score >= 70:
        return "#f59e0b"
    else:
        return "#ef4444"


def render_quality_badge(score: float, show_label: bool = True) -> str:
    """
    Render quality badge HTML.
    
    Args:
        score: Quality score (0-100)
        show_label: Whether to show label text
    
    Returns:
        HTML string
    """
    emoji = get_quality_emoji(score)
    color = get_quality_color(score)
    label = get_quality_label(score)
    
    if show_label:
        text = f"{emoji} {label} ({score:.0f}/100)"
    else:
        text = f"{emoji} {score:.0f}/100"
    
    return f"""
    <span style="background:{color}22; color:{color}; padding:0.3rem 0.8rem;
                 border-radius:20px; font-size:0.85rem; font-weight:600;
                 display:inline-block;">
        {text}
    </span>
    """


def render_data_source_info(
    source: str,
    quality_level: str,
    quality_score: Optional[float] = None
) -> str:
    """
    Render data source information.
    
    Args:
        source: Data source name
        quality_level: Quality level (HIGH, MEDIUM, LOW)
        quality_score: Optional quality score
    
    Returns:
        HTML string
    """
    quality_colors = {
        "HIGH": "#10b981",
        "MEDIUM": "#f59e0b",
        "LOW": "#ef4444",
        "UNKNOWN": "#64748b"
    }
    
    color = quality_colors.get(quality_level, "#64748b")
    
    score_text = ""
    if quality_score is not None:
        score_text = f" | Quality: {render_quality_badge(quality_score, show_label=False)}"
    
    return f"""
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
        📊 <strong style="color:#e2e8f0;">Source:</strong> {source}
        | <strong style="color:#e2e8f0;">Level:</strong>
        <span style="color:{color}; font-weight:600;">{quality_level}</span>
        {score_text}
    </div>
    """


def render_validation_warnings(warnings: List[str]) -> str:
    """
    Render validation warnings panel.
    
    Args:
        warnings: List of warning messages
    
    Returns:
        HTML string (empty if no warnings)
    """
    if not warnings:
        return ""
    
    # Filter to important warnings only
    important_warnings = [w for w in warnings if "⚠️" in w or "❌" in w]
    
    if not important_warnings:
        return ""
    
    warnings_html = "".join([
        f"<li style='margin-bottom:0.3rem; color:#cbd5e1;'>{w}</li>"
        for w in important_warnings[:5]  # Show max 5
    ])
    
    if len(important_warnings) > 5:
        warnings_html += f"<li style='color:#94a3b8;'>... and {len(important_warnings) - 5} more</li>"
    
    return f"""
    <div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3);
                border-radius:10px; padding:1rem; margin-bottom:1rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
            <span style="font-size:1.2rem;">⚠️</span>
            <strong style="color:#f59e0b; font-size:0.95rem;">Validation Warnings</strong>
        </div>
        <ul style="margin:0.5rem 0 0 1.2rem; padding:0;">{warnings_html}</ul>
    </div>
    """


def render_system_health(health: str) -> str:
    """
    Render system health indicator.
    
    Args:
        health: System health status (HEALTHY, DEGRADED, CRITICAL)
    
    Returns:
        HTML string
    """
    health_config = {
        "HEALTHY": {"emoji": "✅", "color": "#10b981", "label": "All Systems Operational"},
        "DEGRADED": {"emoji": "⚠️", "color": "#f59e0b", "label": "Some Quality Issues"},
        "CRITICAL": {"emoji": "❌", "color": "#ef4444", "label": "Critical Issues Detected"}
    }
    
    config = health_config.get(health, health_config["CRITICAL"])
    
    return f"""
    <div style="text-align:center; padding:1rem; background:{config['color']}11;
                border:2px solid {config['color']}; border-radius:10px;">
        <div style="font-size:2rem; margin-bottom:0.5rem;">{config['emoji']}</div>
        <div style="font-size:1.1rem; font-weight:700; color:{config['color']};">
            {health}
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">
            {config['label']}
        </div>
    </div>
    """


def render_quality_dashboard(report: Dict) -> str:
    """
    Render complete quality dashboard.
    
    Args:
        report: Data quality report from get_data_quality_report()
    
    Returns:
        HTML string
    """
    unemployment_score = report['unemployment']['data_quality_score']
    inflation_score = report['inflation']['data_quality_score']
    system_health = report['overall_system_health']
    
    unemployment_badge = render_quality_badge(unemployment_score)
    inflation_badge = render_quality_badge(inflation_score)
    
    health_emoji = "✅" if system_health == "HEALTHY" else "⚠️" if system_health == "DEGRADED" else "❌"
    health_color = "#10b981" if system_health == "HEALTHY" else "#f59e0b" if system_health == "DEGRADED" else "#ef4444"
    
    return f"""
    <div style="background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
                border-radius:12px; padding:1.2rem; margin-bottom:1.5rem;">
        <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem;">
            <span style="font-size:1.3rem;">🔍</span>
            <span style="font-size:1rem; font-weight:700; color:#818cf8;">
                Data Quality Dashboard
            </span>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1rem;">
            <div style="background:rgba(0,0,0,0.2); border-radius:8px; padding:0.8rem; text-align:center;">
                <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.5rem;">
                    Unemployment Data
                </div>
                <div>{unemployment_badge}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:0.5rem;">
                    {report['unemployment']['source']}
                </div>
            </div>
            
            <div style="background:rgba(0,0,0,0.2); border-radius:8px; padding:0.8rem; text-align:center;">
                <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.5rem;">
                    Inflation Data
                </div>
                <div>{inflation_badge}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:0.5rem;">
                    {report['inflation']['source']}
                </div>
            </div>
            
            <div style="background:rgba(0,0,0,0.2); border-radius:8px; padding:0.8rem; text-align:center;">
                <div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.5rem;">
                    System Health
                </div>
                <div style="font-size:1.5rem; margin:0.3rem 0;">{health_emoji}</div>
                <div style="font-size:0.9rem; font-weight:700; color:{health_color};">
                    {system_health}
                </div>
            </div>
        </div>
        
        <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.1);
                    font-size:0.8rem; color:#64748b; text-align:center;">
            All data automatically validated on load | Quality scores updated in real-time
        </div>
    </div>
    """


def render_quality_summary_compact(report: Dict) -> str:
    """
    Render compact quality summary (for sidebar or small spaces).
    
    Args:
        report: Data quality report from get_data_quality_report()
    
    Returns:
        HTML string
    """
    unemployment_score = report['unemployment']['data_quality_score']
    inflation_score = report['inflation']['data_quality_score']
    system_health = report['overall_system_health']
    
    unemployment_emoji = get_quality_emoji(unemployment_score)
    inflation_emoji = get_quality_emoji(inflation_score)
    health_emoji = "✅" if system_health == "HEALTHY" else "⚠️" if system_health == "DEGRADED" else "❌"
    
    return f"""
    <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1);
                border-radius:8px; padding:0.8rem; font-size:0.85rem;">
        <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.6rem;">
            📊 Data Quality
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
            <span style="color:#94a3b8;">Unemployment:</span>
            <span style="color:#e2e8f0;">{unemployment_emoji} {unemployment_score:.0f}/100</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
            <span style="color:#94a3b8;">Inflation:</span>
            <span style="color:#e2e8f0;">{inflation_emoji} {inflation_score:.0f}/100</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding-top:0.4rem;
                    border-top:1px solid rgba(255,255,255,0.1);">
            <span style="color:#94a3b8;">System:</span>
            <span style="color:#e2e8f0;">{health_emoji} {system_health}</span>
        </div>
    </div>
    """


def render_data_corrections_info(corrections: List[str]) -> str:
    """
    Render information about data corrections applied.
    
    Args:
        corrections: List of correction messages
    
    Returns:
        HTML string (empty if no corrections)
    """
    if not corrections:
        return ""
    
    corrections_html = "".join([
        f"<li style='margin-bottom:0.3rem; color:#cbd5e1; font-size:0.85rem;'>{c}</li>"
        for c in corrections[:5]  # Show max 5
    ])
    
    if len(corrections) > 5:
        corrections_html += f"<li style='color:#94a3b8; font-size:0.85rem;'>... and {len(corrections) - 5} more</li>"
    
    return f"""
    <div style="background:rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.2);
                border-radius:10px; padding:1rem; margin-bottom:1rem;">
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
            <span style="font-size:1.2rem;">✓</span>
            <strong style="color:#10b981; font-size:0.95rem;">Data Corrections Applied</strong>
        </div>
        <ul style="margin:0.5rem 0 0 1.2rem; padding:0;">{corrections_html}</ul>
        <div style="margin-top:0.8rem; padding-top:0.8rem; border-top:1px solid rgba(16,185,129,0.2);
                    font-size:0.8rem; color:#64748b;">
            All corrections follow strict validation rules to ensure data quality and consistency.
        </div>
    </div>
    """


def render_validation_status_badge(is_valid: bool, compact: bool = False) -> str:
    """
    Render validation status badge.
    
    Args:
        is_valid: Whether validation passed
        compact: Whether to use compact format
    
    Returns:
        HTML string
    """
    if is_valid:
        emoji, color, label = "✅", "#10b981", "Valid"
    else:
        emoji, color, label = "❌", "#ef4444", "Invalid"
    
    if compact:
        text = emoji
    else:
        text = f"{emoji} {label}"
    
    return f"""
    <span style="background:{color}22; color:{color}; padding:0.3rem 0.6rem;
                 border-radius:15px; font-size:0.8rem; font-weight:600;
                 display:inline-block;">
        {text}
    </span>
    """


# ═══════════════════════════════════════════════════════════════════════════
# STREAMLIT-SPECIFIC HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def display_quality_metrics(report: Dict, use_columns: bool = True):
    """
    Display quality metrics using Streamlit components.
    
    Args:
        report: Data quality report
        use_columns: Whether to use columns layout
    
    Note: This function uses Streamlit components and should only be called
          within a Streamlit app context.
    """
    import streamlit as st
    
    if use_columns:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Unemployment Quality",
                f"{report['unemployment']['data_quality_score']:.0f}/100",
                delta=None,
                help=f"Source: {report['unemployment']['source']}"
            )
        
        with col2:
            st.metric(
                "Inflation Quality",
                f"{report['inflation']['data_quality_score']:.0f}/100",
                delta=None,
                help=f"Source: {report['inflation']['source']}"
            )
        
        with col3:
            health = report['overall_system_health']
            health_emoji = "✅" if health == "HEALTHY" else "⚠️" if health == "DEGRADED" else "❌"
            st.metric(
                "System Health",
                f"{health_emoji} {health}",
                delta=None
            )
    else:
        st.markdown(render_quality_dashboard(report), unsafe_allow_html=True)


def display_validation_warnings(warnings: List[str]):
    """
    Display validation warnings using Streamlit components.
    
    Args:
        warnings: List of warning messages
    
    Note: This function uses Streamlit components and should only be called
          within a Streamlit app context.
    """
    import streamlit as st
    
    if not warnings:
        return
    
    # Filter to important warnings
    important_warnings = [w for w in warnings if "⚠️" in w or "❌" in w]
    
    if not important_warnings:
        return
    
    with st.expander(f"⚠️ Validation Warnings ({len(important_warnings)})", expanded=False):
        for warning in important_warnings:
            st.caption(warning)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test the UI helpers
    print("\n" + "="*80)
    print("VALIDATION UI HELPERS TEST")
    print("="*80 + "\n")
    
    # Test quality badge
    print("TEST 1: Quality badges")
    for score in [95, 85, 75, 60, 40]:
        print(f"Score {score}: {render_quality_badge(score)}")
    
    # Test system health
    print("\nTEST 2: System health indicators")
    for health in ["HEALTHY", "DEGRADED", "CRITICAL"]:
        print(f"{health}: {render_system_health(health)[:100]}...")
    
    # Test validation warnings
    print("\nTEST 3: Validation warnings")
    warnings = [
        "⚠️ WARNING: 3 missing values (10.0%)",
        "ℹ️ INFO: 2 statistical outliers detected"
    ]
    print(render_validation_warnings(warnings)[:200] + "...")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
