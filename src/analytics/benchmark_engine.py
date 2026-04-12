"""Benchmark engine for peer comparison using synthetic data."""

import numpy as np
from typing import List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_calculators import UserProfile, RiskProfile
from risk_calculators.orchestrator import RiskCalculatorOrchestrator
from analytics import BenchmarkResult


class BenchmarkEngine:
    """Generates synthetic peer data and computes rankings"""
    
    def generate_peers(
        self, 
        profile: UserProfile, 
        count: int = 100
    ) -> List[RiskProfile]:
        """
        Generate synthetic peer profiles matching industry and role level
        
        Algorithm:
        1. Create base profile matching user's industry and role_level
        2. Vary skills, experience, education with realistic distributions
        3. Calculate risk for each synthetic profile
        4. Ensure realistic variation (std dev ~15-20 points)
        """
        rng = np.random.default_rng(42)  # Fixed seed for reproducibility
        orchestrator = RiskCalculatorOrchestrator()
        
        peer_profiles = []
        
        # Define skill pools by industry
        skill_pools = {
            "Technology / software": ["python", "java", "javascript", "sql", "cloud computing", "machine learning", "devops"],
            "Healthcare / biotech": ["patient care", "medical knowledge", "research", "data analysis", "communication"],
            "Financial services / fintech": ["finance", "accounting", "data analysis", "excel", "sql", "compliance"],
            "default": ["communication", "teamwork", "problem solving", "project management", "leadership"],
        }
        
        industry_skills = skill_pools.get(profile.industry, skill_pools["default"])
        
        # Experience range based on role level
        exp_ranges = {
            "Entry": (0, 3),
            "Mid": (3, 8),
            "Senior": (8, 15),
            "Lead": (12, 20),
            "Executive": (15, 30),
        }
        exp_min, exp_max = exp_ranges.get(profile.role_level, (0, 10))
        
        for i in range(count):
            # Vary experience within role level range
            peer_exp = int(rng.normal((exp_min + exp_max) / 2, (exp_max - exp_min) / 4))
            peer_exp = np.clip(peer_exp, exp_min, exp_max)
            
            # Vary age (correlate with experience)
            peer_age = int(np.clip(22 + peer_exp + rng.normal(0, 3), 22, 70))
            
            # Vary skills (3-7 skills)
            num_skills = rng.integers(3, 8)
            peer_skills = list(rng.choice(industry_skills, size=min(num_skills, len(industry_skills)), replace=False))
            
            # Vary education
            edu_levels = [
                "High school / diploma",
                "Bachelor's degree",
                "Master's degree",
                "Doctorate / professional",
            ]
            # Higher role levels tend to have higher education
            role_edu_bias = {"Entry": 1, "Mid": 2, "Senior": 2, "Lead": 3, "Executive": 3}
            edu_idx = int(np.clip(rng.normal(role_edu_bias.get(profile.role_level, 2), 1), 0, 3))
            peer_edu = edu_levels[edu_idx]
            
            # Vary company size
            company_sizes = ["1-10", "11-50", "51-200", "201-1000", "1001-5000", "5000+"]
            peer_company = rng.choice(company_sizes)
            
            # Vary performance rating (normal distribution around 3)
            peer_perf = int(np.clip(rng.normal(3, 0.8), 1, 5))
            
            # Vary remote capability (60% have it)
            peer_remote = rng.random() < 0.6
            
            # Create peer profile
            peer_profile = UserProfile(
                skills=peer_skills,
                industry=profile.industry,  # Same industry
                role_level=profile.role_level,  # Same role level
                experience_years=peer_exp,
                education_level=peer_edu,
                location=profile.location,  # Same location for fair comparison
                age=peer_age,
                company_size=peer_company,
                remote_capability=peer_remote,
                performance_rating=peer_perf,
            )
            
            # Calculate risk for peer
            peer_risk = orchestrator.calculate_all_risks(peer_profile)
            peer_profiles.append(peer_risk)
        
        return peer_profiles
    
    def compute_benchmark(
        self, 
        user_risk: float, 
        peer_risks: List[float]
    ) -> BenchmarkResult:
        """
        Calculate percentile ranking and distribution markers
        
        Algorithm:
        1. Sort peer risks
        2. Find user's position in sorted list
        3. Calculate percentile = (position / total) * 100
        4. Compute quartile markers (25th, 50th, 75th, 90th)
        5. Generate comparison text
        """
        # Sort peer risks
        sorted_risks = sorted(peer_risks)
        
        # Find user's position
        position = sum(1 for r in sorted_risks if r < user_risk)
        percentile = (position / len(sorted_risks)) * 100
        
        # Compute percentile markers
        def get_percentile_value(risks: List[float], p: float) -> float:
            idx = int(len(risks) * p / 100)
            idx = min(idx, len(risks) - 1)
            return risks[idx]
        
        percentile_markers = {
            "25th": get_percentile_value(sorted_risks, 25),
            "50th": get_percentile_value(sorted_risks, 50),
            "75th": get_percentile_value(sorted_risks, 75),
            "90th": get_percentile_value(sorted_risks, 90),
        }
        
        # Generate comparison text
        lower_risk_pct = 100 - percentile
        if percentile < 25:
            comparison = f"You are in the {percentile:.0f}th percentile - lower risk than {lower_risk_pct:.0f}% of peers. Excellent position!"
        elif percentile < 50:
            comparison = f"You are in the {percentile:.0f}th percentile - lower risk than {lower_risk_pct:.0f}% of peers. Above average."
        elif percentile < 75:
            comparison = f"You are in the {percentile:.0f}th percentile - lower risk than {lower_risk_pct:.0f}% of peers. Average range."
        else:
            comparison = f"You are in the {percentile:.0f}th percentile - higher risk than {percentile:.0f}% of peers. Consider risk reduction strategies."
        
        return BenchmarkResult(
            user_risk=user_risk,
            percentile=round(percentile, 1),
            peer_distribution=sorted_risks,
            percentile_markers=percentile_markers,
            peer_count=len(peer_risks),
            comparison_text=comparison,
        )
