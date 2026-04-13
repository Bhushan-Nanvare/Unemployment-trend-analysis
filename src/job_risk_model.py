"""
Job unemployment risk predictor (Feature 1).

⚠️  EXPERIMENTAL MODEL - NOT VALIDATED WITH REAL DATA ⚠️

This model is trained on SYNTHETIC DATA derived from job postings.
The training data is NOT based on actual unemployment outcomes.

Data Quality Status:
- Training Data: SYNTHETIC (silver-labeled from job postings)
- Validation: NOT PERFORMED
- Confidence Level: EXPERIMENTAL
- Recommended Use: Educational/exploratory purposes only

The model learns relationships from job market signals (salary, role, sector)
but has NOT been validated against real unemployment outcomes.

Stronger skills, education, experience, industry growth, and better locations
→ lower estimated risk (based on market signals, not actual outcomes).

The UI calls this module directly; it does not depend on the FastAPI stack.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_NAMES = [
    "skill_demand_score",
    "industry_growth",
    "experience_years",
    "education_level",
    "location_risk_tier",
]

# Keyword → demand weight (0–1). Longer phrases matched first if we sort by length.
SKILL_DEMAND_WEIGHTS: List[Tuple[str, float]] = sorted(
    [
        # High-demand AI/ML/Data skills (0.90-1.0)
        ("machine learning", 0.98),
        ("deep learning", 0.97),
        ("data science", 0.96),
        ("artificial intelligence", 0.95),
        ("cloud computing", 0.94),
        ("kubernetes", 0.93),
        ("aws", 0.92),
        ("azure", 0.91),
        ("devops", 0.90),
        ("cybersecurity", 0.93),
        
        # Strong programming skills (0.75-0.89)
        ("python", 0.88),
        ("sql", 0.85),
        ("react", 0.84),
        ("node", 0.83),
        ("javascript", 0.82),
        ("java", 0.81),
        ("c++", 0.80),
        ("golang", 0.79),
        ("rust", 0.78),
        ("typescript", 0.77),
        ("docker", 0.76),
        ("git", 0.75),
        
        # Moderate-demand skills (0.60-0.74)
        ("product management", 0.72),
        ("project management", 0.70),
        ("agile", 0.68),
        ("scrum", 0.67),
        ("communication", 0.65),
        ("leadership", 0.63),
        ("analytics", 0.62),
        ("tableau", 0.61),
        ("power bi", 0.60),
        
        # Lower-demand but useful skills (0.45-0.59)
        ("php", 0.58),
        ("excel", 0.55),
        ("wordpress", 0.53),
        ("manual testing", 0.50),
        ("html", 0.48),
        ("css", 0.47),
        ("photoshop", 0.46),
        ("illustrator", 0.45),
        
        # Low-demand/outdated skills (0.25-0.44)
        ("data entry", 0.42),
        ("microsoft word", 0.40),
        ("powerpoint", 0.38),
        ("jquery", 0.35),
        ("flash", 0.30),
        ("vb.net", 0.28),
        ("cobol", 0.25),
        
        # Very low demand skills (0.15-0.24)
        ("typing", 0.22),
        ("filing", 0.20),
        ("fax", 0.18),
        ("basic computer", 0.15),
    ],
    key=lambda x: -len(x[0]),
)

EDUCATION_LEVELS = [
    "Less than high school",
    "High school / diploma",
    "Bachelor's degree",
    "Master's degree",
    "Doctorate / professional",
]

LOCATION_OPTIONS = [
    "Metro / Tier-1 city",
    "Tier-2 city",
    "Smaller town / rural",
]

INDUSTRY_GROWTH = {
    "Technology / software": 0.92,
    "Healthcare / biotech": 0.88,
    "Financial services / fintech": 0.82,
    "Renewable energy / climate": 0.86,
    "Education / edtech": 0.72,
    "Retail / e-commerce ops": 0.62,
    "Manufacturing (traditional)": 0.55,
    "Hospitality / tourism": 0.48,
    "Other / not listed": 0.60,
}


def _location_risk_tier(label: str) -> float:
    if label == LOCATION_OPTIONS[0]:
        return 0.0
    if label == LOCATION_OPTIONS[1]:
        return 1.0
    return 2.0


def parse_skills(text: str) -> List[str]:
    if not text or not str(text).strip():
        return []
    parts = re.split(r"[,;\n]+", str(text).lower())
    return [p.strip() for p in parts if p.strip()]


def compute_skill_demand_score(skills: List[str]) -> Tuple[float, List[str]]:
    """
    Returns score in [0, 1] and list of matched **high-demand** keywords (for UI).
    Phrases below STRONG_SKILL_THRESHOLD still affect the mean score but are not listed as "in-demand".
    """
    STRONG = 0.68
    if not skills:
        return 0.30, []  # Lower baseline for no skills

    blob = " ".join(skills)
    weights: List[float] = []
    strong_matched: List[str] = []
    for phrase, w in SKILL_DEMAND_WEIGHTS:
        if phrase in blob:
            weights.append(w)
            if w >= STRONG:
                strong_matched.append(phrase)
    if not weights:
        # Lower generic score for unrecognized skills
        generic = min(0.40, 0.25 + 0.015 * len(skills))  # Reduced from 0.35 + 0.02
        return generic, []

    return float(np.clip(np.mean(weights), 0.0, 1.0)), strong_matched


def build_feature_row(
    skills_text: str,
    education_label: str,
    experience_years: int,
    location_label: str,
    industry_label: str,
) -> Tuple[np.ndarray, Dict[str, Any]]:
    skills = parse_skills(skills_text)
    skill_score, matched = compute_skill_demand_score(skills)
    try:
        edu = float(EDUCATION_LEVELS.index(education_label))
    except ValueError:
        edu = 2.0
    ind = float(INDUSTRY_GROWTH.get(industry_label, 0.6))
    loc = _location_risk_tier(location_label)
    exp = float(np.clip(experience_years, 0, 40))

    row = np.array(
        [[skill_score, ind, exp, edu, loc]],
        dtype=np.float64,
    )
    meta = {
        "parsed_skills": skills,
        "matched_high_demand": matched,
        "skill_demand_score": skill_score,
        "industry_growth": ind,
        "experience_years": exp,
        "education_level": edu,
        "location_risk_tier": loc,
    }
    return row, meta


def _load_real_training_data(n_samples: int = 10000, random_state: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Loads real job postings CSV and creates a 'silver-labeled' training set.
    Risk Label (y):
      - 1 (High Risk) if salary is in the bottom 30th percentile for the role OR role is 'Other/General'.
      - 0 (Low Risk) if salary is above median OR in high-growth sector.
    """
    from src.job_market_pulse import load_job_postings, ROLE_TITLE_RULES

    df = load_job_postings()
    if df.empty:
        # Fallback to a smaller synthetic seed if CSV is missing
        return _synthetic_dataset(500, random_state)

    # Use a subset if dataset is too large, but 29K is fine
    df = df.sample(min(len(df), n_samples), random_state=random_state).copy()

    # Pre-calculate salary benchmarks for silver labeling
    df["_salary_mid"] = (pd.to_numeric(df["salary_min_lpa"], errors="coerce") +
                         pd.to_numeric(df["salary_max_lpa"], errors="coerce")) / 2.0
    global_median = df["_salary_mid"].median() or 6.0

    X_list = []
    y_list = []

    rng = np.random.default_rng(random_state)

    for _, row in df.iterrows():
        title = str(row.get("job_title", "")).lower()
        desc = str(row.get("description", "")).lower()
        loc_str = str(row.get("location", ""))

        # 1. Skill Demand Score
        skills = parse_skills(desc)
        skill_score, _ = compute_skill_demand_score(skills)

        # 2. Industry Growth
        # Simple mapping for training data synthesis
        ind_label = "Other / not listed"
        for needle, label in [("tech", "Technology / software"), ("health", "Healthcare / biotech"), ("finance", "Financial services / fintech")]:
            if needle in title:
                ind_label = label
                break
        ind_growth = INDUSTRY_GROWTH.get(ind_label, 0.6)

        # 3. Experience & Education (Inferred for training distribution)
        # Higher salary roles in the CSV are mapped to higher exp/edu to teach the model the correlation
        sal = row["_salary_mid"]
        if pd.isna(sal): sal = global_median
        
        # Heuristic: salary correlates with exp/edu in real markets
        # Improved formula to generate more realistic experience distribution (0-40 years)
        # Salary range in dataset is typically 2-30 LPA
        exp_base = np.clip((sal / 2.5) * 3.5, 0, 35)  # More realistic mapping
        exp = float(rng.normal(exp_base, 4.0))  # Increased variance
        exp = np.clip(exp, 0, 40)

        # Education also scales with salary but with more variance
        edu_base = np.clip((sal / 8.0) * 2.5, 0, 4)
        edu = float(rng.integers(max(0, int(edu_base-1)), min(4, int(edu_base+2))))
        edu = np.clip(edu, 0, 4)

        # 4. Location
        loc = 1.0 # Default Tier-2
        if any(m in loc_str.lower() for m in ["bangalore", "mumbai", "delhi", "hyderabad", "chennai"]):
            loc = 0.0 # Tier-1
        elif len(loc_str) < 3:
            loc = 2.0 # Rural/Unknown

        X_list.append([skill_score, ind_growth, exp, edu, loc])

        # --- Silver Label Logic ---
        # Recalibrated to ensure experience and growth strictly reduce risk.
        is_generic = "Other" in row.get("role_bucket", "Other")
        is_low_sal = sal < (global_median * 0.8)
        
        # Base probability (moderate)
        vuln_prob = 0.35
        
        # 1. Experience & Education (STRONGEST FACTORS - more reduces risk significantly)
        # Experience ranges 0-40, normalize and apply strong weight
        exp_factor = np.clip(exp / 40.0, 0, 1)  # 0 to 1
        vuln_prob -= exp_factor * 0.45  # Strong negative impact (up to -45%)
        
        # Education 0-4, normalize and apply moderate weight
        edu_factor = np.clip(edu / 4.0, 0, 1)  # 0 to 1
        vuln_prob -= edu_factor * 0.25  # Moderate negative impact (up to -25%)
        
        # 2. Industry Growth factor (Higher growth reduces risk)
        vuln_prob -= (ind_growth - 0.6) * 0.8  # Normalized around 0.6 baseline
        
        # 3. Location factor (Tier 1 is 0, Rural is 2)
        vuln_prob += (loc / 2.0) * 0.20
        
        # 4. Skill Score factor (Higher skills reduce risk)
        vuln_prob -= (skill_score - 0.5) * 0.6  # Normalized around 0.5 baseline
        
        # 5. Salary proxy (Real data signal)
        if is_low_sal: vuln_prob += 0.15
        if is_generic: vuln_prob += 0.12
        
        vuln_prob = np.clip(vuln_prob, 0.05, 0.95)
        y_list.append(1 if (rng.random() < vuln_prob) else 0)

    return np.array(X_list), np.array(y_list)


    # Ensure synthetic fallback data also respects the desired model behavior
    logit = 2.0 - 3.5*skill - 2.5*ind - 2.5*(exp/40.0) - 1.5*(edu/5.0) + 1.2*(loc/2.0)
    p = 1.0 / (1.0 + np.exp(-logit))
    y = (rng.random(n_samples) < p).astype(np.int32)
    return np.column_stack([skill, ind, exp, edu, loc]), y


@dataclass
class JobRiskResult:
    high_risk_probability_pct: float
    risk_level: str
    features: Dict[str, Any]
    reasons: List[str]
    suggestions: List[str]
    # Optional — callers must None-check before calling .items().
    contributions: Optional[Dict[str, float]] = None
    # Data quality metadata
    data_quality_warning: str = "⚠️  EXPERIMENTAL: Model trained on synthetic data, not validated"
    confidence_level: str = "LOW"
    model_version: str = MODEL_VERSION


def _risk_level_from_prob(p: float) -> str:
    if p >= 0.30:  # Lowered from 0.45 - more realistic for high risk
        return "High"
    if p >= 0.18:  # Lowered from 0.25 - more realistic for medium risk
        return "Medium"
    return "Low"


def _train_pipeline() -> Pipeline:
    X, y = _load_real_training_data()
    pipe = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=500,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )
    pipe.fit(X, y)
    return pipe


_PIPE: Optional[Pipeline] = None

# Precompute feature means once at module load — used for contribution attribution.
# _synthetic_dataset() is deterministic (seed=42), so means are always identical;
# recomputing them inside predict_job_risk() every call was pure waste.
_FEATURE_MEANS: Optional[np.ndarray] = None

# Model version for cache invalidation - increment when training logic changes
MODEL_VERSION = "2.1.0"  # Updated: Improved skill scoring and realistic risk thresholds


def get_pipeline() -> Pipeline:
    global _PIPE, _FEATURE_MEANS
    if _PIPE is None:
        _PIPE = _train_pipeline()
        X_all, _ = _load_real_training_data()
        _FEATURE_MEANS = X_all.mean(axis=0)
    return _PIPE


def get_model_info() -> Dict[str, Any]:
    """Returns model version and coefficient information for debugging."""
    pipe = get_pipeline()
    clf: LogisticRegression = pipe.named_steps["clf"]
    coefs = clf.coef_[0]
    return {
        "version": MODEL_VERSION,
        "experience_coefficient": float(coefs[2]),  # experience_years is index 2
        "coefficients": {name: float(coef) for name, coef in zip(FEATURE_NAMES, coefs)},
        "training_samples": len(_load_real_training_data()[0]),
    }


def _get_feature_means() -> np.ndarray:
    get_pipeline()   # ensures _FEATURE_MEANS is populated
    return _FEATURE_MEANS


def _linear_contributions(
    pipe: Pipeline, X_row: np.ndarray, feature_means: np.ndarray
) -> Dict[str, float]:
    clf: LogisticRegression = pipe.named_steps["clf"]
    scale: StandardScaler = pipe.named_steps["scale"]
    Xs = scale.transform(X_row)
    mu_s = scale.transform(feature_means.reshape(1, -1))
    diff = (Xs - mu_s).ravel()
    coef = clf.coef_.ravel()
    return {FEATURE_NAMES[i]: float(diff[i] * coef[i]) for i in range(len(FEATURE_NAMES))}


def predict_job_risk(
    skills_text: str,
    education_label: str,
    experience_years: int,
    location_label: str,
    industry_label: str,
) -> JobRiskResult:
    pipe = get_pipeline()
    X_row, meta = build_feature_row(
        skills_text, education_label, experience_years, location_label, industry_label
    )

    proba = float(pipe.predict_proba(X_row)[0, 1])
    level = _risk_level_from_prob(proba)

    # Use precomputed means — no need to regenerate 3,500-sample dataset each call.
    means = _get_feature_means()
    contribs = _linear_contributions(pipe, X_row, means)
    sorted_c = sorted(contribs.items(), key=lambda kv: abs(kv[1]), reverse=True)

    reasons: List[str] = []
    for name, c in sorted_c[:4]:
        if name == "skill_demand_score":
            if c > 0.15:
                reasons.append("Skill profile aligns weakly with high-demand areas (raises modeled risk).")
            elif c < -0.15:
                reasons.append("Strong match to in-demand skills (lowers modeled risk).")
        elif name == "industry_growth":
            if c > 0.12:
                reasons.append("Selected industry has below-average growth in the model (raises risk).")
            elif c < -0.12:
                reasons.append("Industry growth outlook supports employability (lowers risk).")
        elif name == "experience_years":
            if c > 0.1:
                reasons.append("Limited years of experience contribute to higher modeled risk.")
            elif c < -0.1:
                reasons.append("Experience depth reduces modeled unemployment risk.")
        elif name == "education_level":
            if c > 0.1:
                reasons.append("Formal education level is a drag on the risk score in this profile.")
            elif c < -0.1:
                reasons.append("Higher education level reduces modeled risk.")
        elif name == "location_risk_tier":
            if c > 0.12:
                reasons.append("Location tier suggests fewer local opportunities in the model.")
            elif c < -0.12:
                reasons.append("Location tier is favorable for job market access.")

    if not reasons:
        reasons.append("Risk is near the model’s average for similar synthetic profiles.")

    suggestions: List[str] = []
    if proba >= 0.35:
        if float(meta["skill_demand_score"]) < 0.72:
            suggestions.append("Add skills that appear frequently in growing roles (e.g. cloud, data, security).")
        if meta["education_level"] < 3:
            suggestions.append("Consider certifications or degree progress in a high-growth domain.")
        if meta["location_risk_tier"] >= 1.5:
            suggestions.append("Explore remote-first roles or hubs with stronger hiring in your field.")
        if meta["industry_growth"] < 0.65:
            suggestions.append("Research adjacent industries with higher hiring momentum.")
    else:
        suggestions.append("Maintain skills and monitor industry shifts; your profile looks comparatively resilient.")

    return JobRiskResult(
        high_risk_probability_pct=round(proba * 100.0, 1),
        risk_level=level,
        features=meta,
        reasons=reasons[:5],
        suggestions=suggestions[:5],
        contributions={k: round(v, 4) for k, v in contribs.items()},
    )


def industry_risk_comparison(
    skills_text: str,
    education_label: str,
    experience_years: int,
    location_label: str,
) -> List[Dict[str, Any]]:
    """Run the model across all industries to show where the user fits best."""
    rows = []
    for ind_label in INDUSTRY_GROWTH:
        r = predict_job_risk(skills_text, education_label, experience_years, location_label, ind_label)
        rows.append({
            "Industry": ind_label,
            "Risk (%)": r.high_risk_probability_pct,
            "Level": r.risk_level,
        })
    return sorted(rows, key=lambda x: x["Risk (%)"])


def what_if_improve_skills(
    skills_text: str,
    education_label: str,
    experience_years: int,
    location_label: str,
    industry_label: str,
    extra_skills_text: str,
) -> Tuple[JobRiskResult, JobRiskResult, float]:
    base = predict_job_risk(
        skills_text, education_label, experience_years, location_label, industry_label
    )
    merged = ", ".join(s for s in [skills_text.strip(), extra_skills_text.strip()] if s)
    improved = predict_job_risk(
        merged, education_label, experience_years, location_label, industry_label
    )
    delta = round(
        improved.high_risk_probability_pct - base.high_risk_probability_pct, 1
    )
    return base, improved, delta
