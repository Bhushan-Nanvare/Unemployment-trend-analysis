"""
career_advisor.py
Rule-based AI Career & Skill Advisor with Real-Time Skill Demand.

REFACTORED: 2026-04-13
- Removed fake positional scoring
- Integrated real-time Adzuna API data
- Skills ranked by actual job market demand

Fix: Thresholds for "growth" vs "risk" classification now scale dynamically
with shock_intensity so that a severe crisis produces appropriately pessimistic
advice rather than falsely optimistic sector labels.
"""
import pandas as pd
from src.skill_demand_analyzer import get_skill_demand_dict


class CareerAdvisor:

    # Updated to match balanced BASE_SKILLS in skill_demand_analyzer.py
    # Ensures comprehensive coverage across tech and domain skills
    SECTOR_SKILLS = {
        "Healthcare":        ["Healthcare Tech", "Biotech", "Data Science"],
        "Education":         ["EdTech", "Data Science", "UX/UI Design"],
        "IT":                ["AI/ML", "Data Science", "Cloud Computing", "Python"],
        "Energy & Utilities":["Data Engineering", "Cloud Computing", "Business Intelligence"],
        "Finance & Banking": ["FinTech", "Blockchain", "Data Science"],
        "Agriculture":       ["Data Science", "Cloud Computing", "Business Intelligence"],
        "Services":          ["Digital Marketing", "Product Management", "Web Development"],
        "Retail & Trade":    ["Data Science", "Digital Marketing", "Business Intelligence"],
        "Manufacturing":     ["Data Engineering", "Cloud Computing", "DevOps"],
        "Construction":      ["Product Management", "Data Science", "Cloud Computing"],
    }

    @staticmethod
    def _dynamic_thresholds(shock_intensity: float) -> dict:
        """
        As shock intensifies, the bar for being a "growth" sector rises
        and the bar for being "at risk" falls — matching economic reality.

        shock_intensity:  0.0 → 0.2   low shock   → generous thresholds
                          0.2 → 0.4   moderate    → slightly tightened
                          0.4+        severe/crisis → strict thresholds
        """
        if shock_intensity <= 0.2:
            return {"growth_resilience": 55, "growth_stress": 50, "risk_stress": 65}
        elif shock_intensity <= 0.4:
            return {"growth_resilience": 60, "growth_stress": 45, "risk_stress": 55}
        else:
            return {"growth_resilience": 70, "growth_stress": 35, "risk_stress": 45}

    @staticmethod
    def generate_advice(sector_impact_df: pd.DataFrame, shock_intensity: float = 0.0) -> dict:
        """
        Generates career advice based on sector stress and resilience.
        shock_intensity is used to set dynamic classification thresholds.
        
        REFACTORED: Now uses real-time skill demand data from Adzuna API.
        """
        thresholds = CareerAdvisor._dynamic_thresholds(shock_intensity)
        g_res = thresholds["growth_resilience"]
        g_str = thresholds["growth_stress"]
        r_str = thresholds["risk_stress"]

        sectors = sector_impact_df.to_dict(orient="records")

        advice = {
            "growth_sectors": [],
            "risk_sectors": [],
            "recommended_skills": [],
            "skill_demand_data": {},  # NEW: Real-time demand data
            "upskilling_pathways": [],
            "shock_severity": (
                "Low" if shock_intensity <= 0.2 else
                "Moderate" if shock_intensity <= 0.4 else
                "Severe"
            ),
        }

        # Collect skills from growth sectors
        all_skills = []
        for s in sectors:
            name = s["Sector"]
            resilience = s["Resilience_Score"]
            stress = s["Stress_Score"]

            if resilience > g_res and stress < g_str:
                advice["growth_sectors"].append(name)
                skills = CareerAdvisor.SECTOR_SKILLS.get(name, [])
                all_skills.extend(skills[:3])
            elif stress > r_str:
                advice["risk_sectors"].append(name)

        # Remove duplicates
        all_skills = list(set(all_skills))
        
        # Get real-time skill demand data
        if all_skills:
            skill_demand = get_skill_demand_dict(all_skills)
            advice["skill_demand_data"] = skill_demand
            
            # Extract top skills by demand score
            if skill_demand.get("skills"):
                advice["recommended_skills"] = [
                    s["name"] for s in skill_demand["skills"]
                ]
            else:
                # Fallback if API unavailable
                advice["recommended_skills"] = all_skills
        else:
            advice["recommended_skills"] = []

        narrative = []
        severity = advice["shock_severity"]
        if advice["growth_sectors"]:
            narrative.append(
                f"Under {severity.lower()} shock conditions, strongest growth potential remains in: "
                f"{', '.join(advice['growth_sectors'])}."
            )
        else:
            narrative.append(
                f"Under {severity.lower()} economic shock, no sector currently meets the growth threshold. "
                "Focus on resilience-building and transferable skills."
            )

        if advice["risk_sectors"]:
            narrative.append(
                f"High stress observed in: {', '.join(advice['risk_sectors'])}. "
                "Professionals in these areas should prioritize upskilling and pivot planning."
            )

        advice["narrative"] = " ".join(narrative)
        return advice
