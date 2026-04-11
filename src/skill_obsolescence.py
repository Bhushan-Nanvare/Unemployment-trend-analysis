"""
skill_obsolescence.py

Analyzes skill demand patterns from job postings to identify high-demand vs low-demand skills.
Since the available data has a narrow time range (33 days), we focus on skill popularity 
and market demand analysis rather than time-series trend detection.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Optional

from src.job_market_pulse import phrase_in_blob, skill_phrase_list


def analyze_skill_demand_patterns(
    df: pd.DataFrame,
    top_k: int = 25,
    min_mentions: int = 20,
    demand_threshold: float = 3.0
) -> Optional[pd.DataFrame]:
    """
    Analyze skill demand patterns from job postings.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Job postings DataFrame with _text and salary columns
    top_k : int
        Number of top skills to analyze
    min_mentions : int
        Minimum mentions required for a skill to be included
    demand_threshold : float
        Percentage threshold for high-demand classification
        
    Returns:
    --------
    pd.DataFrame with columns:
        - skill: skill name
        - mentions: total mentions
        - demand_percentage: percentage of jobs mentioning this skill
        - job_coverage: percentage coverage
        - avg_salary_lpa: average salary for jobs mentioning this skill
        - category: High-Demand, Moderate-Demand, Low-Demand, or Emerging
    """
    
    if df.empty or "_text" not in df.columns:
        return None
    
    skills = skill_phrase_list()
    total_jobs = len(df)
    
    # Calculate salary data
    salary_min = pd.to_numeric(df.get("salary_min_lpa"), errors="coerce")
    salary_max = pd.to_numeric(df.get("salary_max_lpa"), errors="coerce")
    df_with_salary = df.copy()
    df_with_salary["salary_mid"] = (salary_min + salary_max) / 2.0
    
    skill_stats = []
    
    for skill in skills:
        # Count mentions
        mentions = 0
        salary_values = []
        
        for _, row in df.iterrows():
            text = row.get("_text", "")
            if phrase_in_blob(skill, text):
                mentions += 1
                # Collect salary if available
                salary_mid = df_with_salary.loc[row.name, "salary_mid"]
                if pd.notna(salary_mid) and salary_mid > 0:
                    salary_values.append(salary_mid)
        
        if mentions >= min_mentions:
            demand_percentage = (mentions / total_jobs) * 100
            job_coverage = (mentions / total_jobs) * 100
            avg_salary = np.mean(salary_values) if salary_values else 0
            
            # Categorize skills
            if demand_percentage >= demand_threshold * 2:  # 6%+
                category = "High-Demand"
            elif demand_percentage >= demand_threshold:  # 3%+
                category = "Moderate-Demand"
            elif demand_percentage >= 1.0:  # 1%+
                category = "Low-Demand"
            else:
                category = "Emerging"
            
            skill_stats.append({
                "skill": skill,
                "mentions": mentions,
                "demand_percentage": round(demand_percentage, 2),
                "job_coverage": round(job_coverage, 2),
                "avg_salary_lpa": round(avg_salary, 1) if avg_salary > 0 else 0,
                "category": category,
                "salary_jobs": len(salary_values)
            })
    
    if not skill_stats:
        return None
    
    # Create DataFrame and sort by mentions
    results_df = pd.DataFrame(skill_stats)
    results_df = results_df.sort_values("mentions", ascending=False).head(top_k)
    
    return results_df


def detect_skill_obsolescence(
    df: pd.DataFrame,
    freq: str = "M",
    top_k: int = 12,
    min_total_mentions: int = 6,
    alpha: float = 0.05,
    slope_threshold_log: float = 0.02,
    category_min_change_ratio: float = 1.8,
    fade_threshold_mentions: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Legacy function for backward compatibility.
    Returns empty DataFrames since time-series analysis isn't possible with current data.
    """
    return pd.DataFrame(), pd.DataFrame()


def _bucket_series(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    """Build a skill × bucket mention pivot from a prepared jobs DataFrame."""
    if df.empty or "post_date" not in df.columns or df["post_date"].isna().all():
        return pd.DataFrame()

    phrases = skill_phrase_list()
    df2 = df.dropna(subset=["post_date"]).copy()

    if freq == "W":
        df2["bucket"] = df2["post_date"].dt.to_period("W").apply(
            lambda p: str(p.start_time.date())
        )
    else:
        df2["bucket"] = df2["post_date"].dt.to_period("M").apply(
            lambda p: str(p.start_time.date())[:7]
        )

    records = []
    for _, row in df2.iterrows():
        blob = row.get("_text", "")
        b = row["bucket"]
        for ph in phrases:
            if phrase_in_blob(ph, blob):
                records.append({"bucket": b, "skill": ph})

    if not records:
        return pd.DataFrame()

    tall = pd.DataFrame(records)
    pivot = (
        tall.groupby(["bucket", "skill"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    pivot.index.name = "bucket"
    return pivot


def _months_to_threshold(
    last_val: float,
    slope_raw: float,
    threshold: float,
    freq: str,
    direction: str,
) -> float | None:
    """Estimate periods until mention count crosses threshold; convert to months."""
    if abs(slope_raw) < 1e-9:
        return None
    if direction == "fade" and slope_raw >= 0:
        return None
    if direction == "emerge" and slope_raw <= 0:
        return None
    steps = (threshold - last_val) / slope_raw
    if steps < 0:
        return None
    weeks_per_step = 4.0 if freq == "M" else 1.0
    months = steps * weeks_per_step / 4.0
    return round(months, 1)
