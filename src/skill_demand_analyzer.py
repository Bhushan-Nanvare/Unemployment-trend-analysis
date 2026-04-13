"""
skill_demand_analyzer.py

ADVANCED REAL-TIME SKILL DEMAND ANALYSIS
=========================================

Replaces fake positional scoring with real job market data from Adzuna API.

FEATURES:
- Log scaling normalization to prevent single skill dominance
- Smart skill expansion to detect hidden variations (e.g., "nlp", "computer vision" for AI/ML)
- Minimal base keywords with intelligent expansion mapping
- Avoids double counting when aggregating matches

Author: System Refactoring
Date: 2026-04-13
Version: 2.0.0 (Advanced)

CRITICAL RULES:
- NO fake data
- NO hardcoded percentages
- NO positional ranking
- ALL scores based on real API data
- Log scaling for fair distribution
- Smart expansion for comprehensive coverage
"""

import os
import time
import requests
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import math
import re


# ═══════════════════════════════════════════════════════════════════════════
# BASE SKILL CONFIGURATION (Minimal anchor keywords)
# ═══════════════════════════════════════════════════════════════════════════

BASE_SKILLS = {
    # Core Tech Skills
    "AI/ML": ["machine learning engineer", "ai engineer"],
    "Data Science": ["data scientist", "data analyst"],
    "Cloud Computing": ["cloud engineer", "aws engineer", "azure engineer"],
    "Cybersecurity": ["security analyst", "cybersecurity engineer"],
    "Web Development": ["frontend developer", "react developer", "full stack developer"],
    "DevOps": ["devops engineer", "site reliability engineer"],
    "Mobile Development": ["android developer", "ios developer", "mobile engineer"],
    "Backend Development": ["backend developer", "api developer"],
    
    # Healthcare Tech
    "Healthcare Tech": ["healthtech engineer", "medical software developer"],
    "Telemedicine": ["telemedicine developer", "telehealth engineer"],
    "Biotech": ["bioinformatics engineer", "biotech developer"],
    
    # Education Tech
    "EdTech": ["edtech developer", "educational technology engineer"],
    "E-Learning": ["elearning developer", "online education engineer"],
    
    # Finance Tech
    "FinTech": ["fintech developer", "financial technology engineer"],
    "Blockchain": ["blockchain developer", "cryptocurrency engineer"],
    
    # Other Domains
    "Digital Marketing": ["digital marketing specialist", "seo specialist"],
    "Product Management": ["product manager", "technical product manager"],
    "Data Engineering": ["data engineer", "etl developer"],
    "Business Intelligence": ["business intelligence analyst", "bi developer"],
}

# ═══════════════════════════════════════════════════════════════════════════
# SMART SKILL EXPANSION (Detect hidden variations)
# ═══════════════════════════════════════════════════════════════════════════

SKILL_EXPANSIONS = {
    "AI/ML": [
        "nlp", "natural language processing",
        "computer vision", "cv engineer",
        "deep learning", "neural network",
        "llm", "gpt", "transformer",
        "pytorch", "tensorflow",
        "ml engineer", "ai developer"
    ],
    "Data Science": [
        "data analyst", "analytics engineer",
        "statistical analyst", "quantitative analyst",
        "ml scientist", "research scientist"
    ],
    "Cloud Computing": [
        "aws", "azure", "gcp", "google cloud",
        "cloud architect", "cloud solutions",
        "kubernetes", "docker", "containerization"
    ],
    "Cybersecurity": [
        "infosec", "information security",
        "penetration testing", "ethical hacking",
        "security operations", "soc analyst",
        "threat intelligence", "incident response"
    ],
    "Web Development": [
        "react", "angular", "vue",
        "javascript developer", "typescript developer",
        "ui developer", "ux developer",
        "web designer", "frontend engineer"
    ],
    "DevOps": [
        "ci/cd", "jenkins", "gitlab",
        "infrastructure engineer", "platform engineer",
        "automation engineer", "release engineer"
    ],
    "Data Engineering": [
        "etl", "data pipeline", "data warehouse",
        "spark", "hadoop", "kafka",
        "big data engineer", "data platform engineer"
    ],
    "FinTech": [
        "payment systems", "digital banking",
        "financial software", "trading systems",
        "regtech", "insurtech"
    ],
    "Blockchain": [
        "smart contracts", "solidity", "ethereum",
        "web3", "defi", "nft",
        "cryptocurrency", "distributed ledger"
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SkillDemandMetrics:
    """Raw metrics from job market data."""
    skill_name: str
    job_count: int
    base_matches: int  # Matches from base keywords
    expanded_matches: int  # Matches from expansion keywords
    avg_salary: float
    recent_jobs: int
    total_jobs_checked: int
    data_source: str
    timestamp: datetime


@dataclass
class SkillDemandScore:
    """Normalized demand score with components."""
    skill_name: str
    demand_score: float  # 0-1
    job_score: float  # 0-1
    salary_score: float  # 0-1
    recency_score: float  # 0-1
    rank: int
    job_count: int
    avg_salary: float
    data_source: str


# ═══════════════════════════════════════════════════════════════════════════
# ADZUNA API CLIENT
# ═══════════════════════════════════════════════════════════════════════════

class AdzunaSkillAnalyzer:
    """Fetches real-time skill demand data from Adzuna API with smart expansion."""
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
        self.cache_dir = Path(".cache/skill_demand")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = 3600  # 1 hour cache
    
    def _get_cache_path(self, skill_name: str) -> Path:
        """Get cache file path for a skill."""
        safe_name = skill_name.replace(" ", "_").replace("/", "_")
        return self.cache_dir / f"{safe_name}.json"
    
    def _load_from_cache(self, skill_name: str) -> Optional[SkillDemandMetrics]:
        """Load cached data if available and fresh."""
        cache_path = self._get_cache_path(skill_name)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if cache is still fresh
            cached_time = datetime.fromisoformat(data['timestamp'])
            if (datetime.now() - cached_time).total_seconds() > self.cache_ttl:
                return None
            
            return SkillDemandMetrics(
                skill_name=data['skill_name'],
                job_count=data['job_count'],
                base_matches=data.get('base_matches', 0),
                expanded_matches=data.get('expanded_matches', 0),
                avg_salary=data['avg_salary'],
                recent_jobs=data['recent_jobs'],
                total_jobs_checked=data['total_jobs_checked'],
                data_source=data['data_source'],
                timestamp=cached_time
            )
        except Exception:
            return None
    
    def _save_to_cache(self, metrics: SkillDemandMetrics) -> None:
        """Save metrics to cache."""
        cache_path = self._get_cache_path(metrics.skill_name)
        
        try:
            data = {
                'skill_name': metrics.skill_name,
                'job_count': metrics.job_count,
                'base_matches': metrics.base_matches,
                'expanded_matches': metrics.expanded_matches,
                'avg_salary': metrics.avg_salary,
                'recent_jobs': metrics.recent_jobs,
                'total_jobs_checked': metrics.total_jobs_checked,
                'data_source': metrics.data_source,
                'timestamp': metrics.timestamp.isoformat()
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Cache failure is non-critical
    
    def _check_expansion_match(self, text: str, expansions: List[str]) -> bool:
        """
        Check if text contains any expansion keywords.
        Uses case-insensitive matching with word boundaries.
        """
        text_lower = text.lower()
        for expansion in expansions:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(expansion.lower()) + r'\b'
            if re.search(pattern, text_lower):
                return True
        return False
    
    def fetch_skill_metrics(self, skill_name: str, base_keywords: List[str]) -> Optional[SkillDemandMetrics]:
        """
        Fetch job market metrics for a skill using Adzuna API with smart expansion.
        
        Algorithm:
        1. Fetch jobs using base keywords
        2. Analyze job titles/descriptions for expansion matches
        3. Count base matches vs expanded matches (avoid double counting)
        4. Aggregate metrics
        
        Returns:
            SkillDemandMetrics or None if API unavailable
        """
        # Try cache first
        cached = self._load_from_cache(skill_name)
        if cached:
            return cached
        
        # Check if API credentials available
        if not self.app_id or not self.app_key:
            return None
        
        try:
            # Use first keyword as primary search term
            primary_keyword = base_keywords[0]
            
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key,
                "what": primary_keyword,
                "results_per_page": 50,
                "content-type": "application/json"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extract job count from API
            job_count = data.get("count", 0)
            results = data.get("results", [])
            
            # Phase 3: Smart Skill Expansion
            # Analyze jobs for expansion matches
            expansion_keywords = SKILL_EXPANSIONS.get(skill_name, [])
            
            base_match_ids: Set[int] = set()
            expanded_match_ids: Set[int] = set()
            
            for idx, job in enumerate(results):
                title = job.get("title", "").lower()
                description = job.get("description", "").lower()
                combined_text = f"{title} {description}"
                
                # Check if it's a base match (contains base keyword)
                is_base_match = any(
                    kw.lower() in combined_text 
                    for kw in base_keywords
                )
                
                # Check if it's an expansion match
                is_expansion_match = self._check_expansion_match(
                    combined_text, 
                    expansion_keywords
                )
                
                # Avoid double counting: prioritize base matches
                if is_base_match:
                    base_match_ids.add(idx)
                elif is_expansion_match:
                    expanded_match_ids.add(idx)
            
            base_matches = len(base_match_ids)
            expanded_matches = len(expanded_match_ids)
            
            # Phase 4: Metric Computation
            # Calculate average salary
            salaries = []
            for job in results:
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                if salary_min and salary_max:
                    salaries.append((salary_min + salary_max) / 2)
            
            avg_salary = sum(salaries) / len(salaries) if salaries else 0.0
            
            # Calculate recency (jobs posted in last 30 days)
            recent_jobs = 0
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for job in results:
                created = job.get("created")
                if created:
                    try:
                        job_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        if job_date >= cutoff_date:
                            recent_jobs += 1
                    except Exception:
                        pass
            
            metrics = SkillDemandMetrics(
                skill_name=skill_name,
                job_count=job_count,
                base_matches=base_matches,
                expanded_matches=expanded_matches,
                avg_salary=avg_salary,
                recent_jobs=recent_jobs,
                total_jobs_checked=len(results),
                data_source="Adzuna API (live, expanded)",
                timestamp=datetime.now()
            )
            
            # Cache the result
            self._save_to_cache(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"⚠️  Adzuna API error for {skill_name}: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════
# SKILL DEMAND CALCULATOR
# ═══════════════════════════════════════════════════════════════════════════

class SkillDemandCalculator:
    """
    Calculates normalized skill demand scores from raw metrics.
    
    Uses LOG SCALING to prevent single skill dominance and ensure fair distribution.
    """
    
    def __init__(self):
        self.analyzer = AdzunaSkillAnalyzer()
    
    def calculate_demand_scores(self, skills: List[str]) -> List[SkillDemandScore]:
        """
        Calculate demand scores for a list of skills.
        
        Algorithm:
        1. Fetch metrics for each skill (with expansion)
        2. Apply LOG SCALING normalization across all skills
        3. Compute weighted demand score
        4. Rank by demand score
        
        Returns:
            List of SkillDemandScore, sorted by demand (highest first)
        """
        # Phase 1: Fetch raw metrics
        raw_metrics = []
        
        for skill in skills:
            keywords = BASE_SKILLS.get(skill, [skill.lower()])
            metrics = self.analyzer.fetch_skill_metrics(skill, keywords)
            
            if metrics:
                raw_metrics.append(metrics)
        
        if not raw_metrics:
            # No data available - return insufficient data
            return []
        
        # Phase 5: LOG SCALING NORMALIZATION (CRITICAL)
        # This prevents single skill from dominating unfairly
        
        max_job_count = max(m.job_count for m in raw_metrics) or 1
        max_salary = max(m.avg_salary for m in raw_metrics) or 1
        
        scores = []
        
        for metrics in raw_metrics:
            # LOG SCALING for job count
            # Formula: log(job_count + 1) / log(max_job_count + 1)
            # This compresses the range and prevents dominance
            job_score = (
                math.log(metrics.job_count + 1) / math.log(max_job_count + 1)
                if max_job_count > 0 else 0.0
            )
            
            # Linear scaling for salary (already well-distributed)
            salary_score = metrics.avg_salary / max_salary if max_salary > 0 else 0.0
            
            # Calculate recency score (0-1)
            recency_score = (
                metrics.recent_jobs / metrics.total_jobs_checked
                if metrics.total_jobs_checked > 0 else 0.0
            )
            
            # Phase 6: FINAL DEMAND SCORE
            # Weights: 50% job count, 30% salary, 20% recency
            demand_score = (
                0.5 * job_score +
                0.3 * salary_score +
                0.2 * recency_score
            )
            
            scores.append(SkillDemandScore(
                skill_name=metrics.skill_name,
                demand_score=demand_score,
                job_score=job_score,
                salary_score=salary_score,
                recency_score=recency_score,
                rank=0,  # Will be set after sorting
                job_count=metrics.job_count,
                avg_salary=metrics.avg_salary,
                data_source=metrics.data_source
            ))
        
        # Phase 4: Sort by demand score and assign ranks
        scores.sort(key=lambda x: x.demand_score, reverse=True)
        
        for i, score in enumerate(scores):
            score.rank = i + 1
        
        return scores
    
    def get_demand_scores_dict(self, skills: List[str]) -> Dict:
        """
        Get demand scores as dictionary for API/UI consumption.
        
        Returns:
            {
                "skills": [{"name": str, "demand": float, "rank": int, ...}],
                "data_source": str,
                "timestamp": str,
                "total_skills": int
            }
        """
        scores = self.calculate_demand_scores(skills)
        
        if not scores:
            return {
                "skills": [],
                "data_source": "INSUFFICIENT DATA",
                "timestamp": datetime.now().isoformat(),
                "total_skills": 0,
                "message": "Adzuna API unavailable. Configure ADZUNA_APP_ID and ADZUNA_APP_KEY."
            }
        
        return {
            "skills": [
                {
                    "name": s.skill_name,
                    "demand": round(s.demand_score, 3),
                    "rank": s.rank,
                    "job_count": s.job_count,
                    "avg_salary": round(s.avg_salary, 2),
                    "job_score": round(s.job_score, 3),
                    "salary_score": round(s.salary_score, 3),
                    "recency_score": round(s.recency_score, 3),
                }
                for s in scores
            ],
            "data_source": scores[0].data_source if scores else "Unknown",
            "timestamp": datetime.now().isoformat(),
            "total_skills": len(scores),
            "algorithm": "Log-scaled normalization with smart keyword expansion"
        }
    
    def get_top_skills(self, n: int = 10) -> List[SkillDemandScore]:
        """
        Get top N in-demand skills from all available skills.
        
        Args:
            n: Number of top skills to return
        
        Returns:
            List of top N SkillDemandScore
        """
        all_skills = list(BASE_SKILLS.keys())
        scores = self.calculate_demand_scores(all_skills)
        return scores[:n]


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def get_skill_demand_scores(skills: List[str]) -> List[SkillDemandScore]:
    """
    Get real-time skill demand scores.
    
    Args:
        skills: List of skill names to analyze
    
    Returns:
        List of SkillDemandScore, sorted by demand (highest first)
    """
    calculator = SkillDemandCalculator()
    return calculator.calculate_demand_scores(skills)


def get_skill_demand_dict(skills: List[str]) -> Dict:
    """
    Get skill demand scores as dictionary.
    
    Args:
        skills: List of skill names to analyze
    
    Returns:
        Dictionary with skills, scores, and metadata
    """
    calculator = SkillDemandCalculator()
    return calculator.get_demand_scores_dict(skills)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with sample skills
    test_skills = [
        "AI/ML",
        "Cybersecurity",
        "Cloud Computing",
        "Data Engineering",
        "Digital Marketing"
    ]
    
    print("Testing Skill Demand Analyzer...")
    print("="*80)
    
    result = get_skill_demand_dict(test_skills)
    
    print(f"\nData Source: {result['data_source']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Total Skills: {result['total_skills']}")
    
    if result['skills']:
        print("\nSkill Demand Rankings:")
        print("-"*80)
        for skill in result['skills']:
            print(f"{skill['rank']}. {skill['name']}")
            print(f"   Demand Score: {skill['demand']:.1%}")
            print(f"   Job Count: {skill['job_count']}")
            print(f"   Avg Salary: ₹{skill['avg_salary']:,.0f}")
            print()
    else:
        print(f"\n⚠️  {result.get('message', 'No data available')}")
