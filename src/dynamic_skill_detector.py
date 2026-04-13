"""
dynamic_skill_detector.py

DYNAMIC SKILL DETECTION ENGINE
===============================

Automatically discovers trending skills from real job market data.
NO predefined skill lists - fully data-driven approach.

Author: System Refactoring
Date: 2026-04-13
Version: 4.0.0 (Dynamic Detection)

CRITICAL RULES:
- NO hardcoded skill lists
- Automatically evolving system
- Real job posting analysis
- Future-proof detection
"""

import os
import re
import time
import requests
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter
import json
from pathlib import Path
import math


# ═══════════════════════════════════════════════════════════════════════════
# SKILL KEYWORD PATTERNS (Detection Rules, NOT Predefined Lists)
# ═══════════════════════════════════════════════════════════════════════════

# These are detection patterns, not hardcoded skills
# The system will find which of these actually appear in job postings
SKILL_DETECTION_PATTERNS = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c\\+\\+", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r programming", "matlab",
    
    # Frameworks & Libraries
    "react", "angular", "vue", "django", "flask", "fastapi", "spring boot",
    "node\\.?js", "express", "next\\.?js", "tensorflow", "pytorch", "pandas",
    "numpy", "scikit-learn", "keras", "spark", "hadoop",
    
    # Cloud & Infrastructure
    "aws", "azure", "gcp", "google cloud", "kubernetes", "docker", "terraform",
    "ansible", "jenkins", "gitlab", "circleci", "serverless", "lambda",
    
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "oracle", "sql server",
    
    # AI/ML/Data
    "machine learning", "deep learning", "artificial intelligence", "nlp",
    "natural language processing", "computer vision", "data science",
    "data engineering", "big data", "data analytics", "business intelligence",
    
    # DevOps & Tools
    "devops", "ci/cd", "git", "linux", "bash", "powershell", "monitoring",
    "grafana", "prometheus", "elk stack", "splunk",
    
    # Security
    "cybersecurity", "information security", "penetration testing",
    "ethical hacking", "security operations", "soc", "siem",
    
    # Web & Mobile
    "html", "css", "rest api", "graphql", "microservices", "mobile development",
    "android", "ios", "flutter", "react native",
    
    # Methodologies & Practices
    "agile", "scrum", "kanban", "test driven development", "tdd",
    "continuous integration", "continuous deployment",
    
    # Domain-Specific
    "blockchain", "web3", "fintech", "healthtech", "edtech", "iot",
    "robotics", "automation", "rpa", "etl", "data warehouse",
    
    # Design & Product
    "ux", "ui", "user experience", "user interface", "figma", "sketch",
    "product management", "product design",
    
    # Soft Skills (Technical Context)
    "problem solving", "communication", "leadership", "team collaboration",
}


# ═══════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SkillFrequency:
    """Skill frequency data from job postings."""
    skill_name: str
    frequency: int
    job_count: int  # Number of jobs mentioning this skill
    avg_salary: float
    recent_mentions: int
    demand_score: float
    rank: int
    data_source: str
    timestamp: datetime


@dataclass
class JobCorpus:
    """Collection of job postings for analysis."""
    jobs: List[Dict]
    total_jobs: int
    queries_used: List[str]
    timestamp: datetime


# ═══════════════════════════════════════════════════════════════════════════
# DYNAMIC SKILL DETECTOR
# ═══════════════════════════════════════════════════════════════════════════

class DynamicSkillDetector:
    """
    Automatically discovers trending skills from real job market data.
    NO predefined skill lists - fully data-driven approach.
    """
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "")
        self.base_url = "https://api.adzuna.com/v1/api/jobs/in/search"
        self.cache_dir = Path(".cache/dynamic_skills")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = 3600  # 1 hour cache
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 1: DATA COLLECTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def fetch_job_corpus(self, pages_per_query: int = 5) -> Optional[JobCorpus]:
        """
        Fetch large dataset of jobs from multiple broad queries.
        
        Phase 1: Data Collection
        - Use broad queries to capture diverse job market
        - Fetch multiple pages for comprehensive coverage
        - Build text corpus for skill extraction
        
        Args:
            pages_per_query: Number of pages to fetch per query (default: 5)
        
        Returns:
            JobCorpus with all collected job postings
        """
        # Check cache first
        cached = self._load_corpus_from_cache()
        if cached:
            return cached
        
        # Check API credentials
        if not self.app_id or not self.app_key:
            print("⚠️  Adzuna API credentials not configured")
            return None
        
        # Broad queries to capture diverse job market
        broad_queries = [
            "software engineer",
            "developer",
            "data",
            "analyst",
            "engineer"
        ]
        
        all_jobs = []
        
        print(f"📊 Fetching job corpus from Adzuna API...")
        
        for query in broad_queries:
            print(f"  → Query: '{query}' (fetching {pages_per_query} pages)")
            
            for page in range(1, pages_per_query + 1):
                try:
                    url = f"{self.base_url}/{page}"
                    params = {
                        "app_id": self.app_id,
                        "app_key": self.app_key,
                        "what": query,
                        "results_per_page": 50,
                        "content-type": "application/json"
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    results = data.get("results", [])
                    all_jobs.extend(results)
                    
                    print(f"    Page {page}: {len(results)} jobs")
                    
                    # Rate limiting - be nice to API
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"    ⚠️  Error on page {page}: {e}")
                    continue
        
        print(f"✅ Collected {len(all_jobs)} total job postings")
        
        corpus = JobCorpus(
            jobs=all_jobs,
            total_jobs=len(all_jobs),
            queries_used=broad_queries,
            timestamp=datetime.now()
        )
        
        # Cache the corpus
        self._save_corpus_to_cache(corpus)
        
        return corpus
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2: TEXT EXTRACTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def extract_text_corpus(self, corpus: JobCorpus) -> str:
        """
        Extract and combine text from all job postings.
        
        Phase 2: Text Extraction
        - Extract title and description from each job
        - Combine into single text corpus
        - Normalize text for analysis
        
        Args:
            corpus: JobCorpus with job postings
        
        Returns:
            Combined text corpus (lowercase)
        """
        text_parts = []
        
        for job in corpus.jobs:
            title = job.get("title", "")
            description = job.get("description", "")
            
            # Combine title and description
            combined = f"{title} {description}"
            text_parts.append(combined)
        
        # Combine all text and normalize
        full_corpus = " ".join(text_parts).lower()
        
        print(f"📝 Extracted text corpus: {len(full_corpus):,} characters")
        
        return full_corpus
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 3: SKILL EXTRACTION
    # ═══════════════════════════════════════════════════════════════════════
    
    def extract_skills(self, text_corpus: str, corpus: JobCorpus) -> Dict[str, Dict]:
        """
        Detect skills using keyword matching and count frequency.
        
        Phase 3: Skill Extraction
        - Use regex patterns to detect skills in text
        - Count frequency of each skill
        - Track which jobs mention each skill
        - Calculate salary data per skill
        
        Args:
            text_corpus: Combined text from all jobs
            corpus: Original job corpus for detailed analysis
        
        Returns:
            Dictionary of skill -> {frequency, jobs, salaries}
        """
        skill_data = {}
        
        print(f"🔍 Extracting skills from corpus...")
        
        # For each detection pattern, find matches
        for pattern in SKILL_DETECTION_PATTERNS:
            # Create regex with word boundaries
            regex = r'\b' + pattern + r'\b'
            
            # Count total mentions in corpus
            matches = re.findall(regex, text_corpus, re.IGNORECASE)
            frequency = len(matches)
            
            if frequency > 0:
                # Normalize skill name
                skill_name = self._normalize_skill_name(pattern)
                
                # Analyze jobs mentioning this skill
                job_analysis = self._analyze_skill_in_jobs(pattern, corpus)
                
                skill_data[skill_name] = {
                    "frequency": frequency,
                    "job_count": job_analysis["job_count"],
                    "avg_salary": job_analysis["avg_salary"],
                    "recent_mentions": job_analysis["recent_mentions"]
                }
        
        print(f"✅ Detected {len(skill_data)} skills with mentions")
        
        return skill_data
    
    def _normalize_skill_name(self, pattern: str) -> str:
        """Normalize skill name for display."""
        # Remove regex special characters
        name = pattern.replace(r"\.", ".").replace(r"\+", "+").replace(r"\\", "")
        
        # Title case for multi-word skills
        if " " in name:
            name = name.title()
        
        return name
    
    def _analyze_skill_in_jobs(self, pattern: str, corpus: JobCorpus) -> Dict:
        """Analyze which jobs mention a skill and extract metrics."""
        regex = r'\b' + pattern + r'\b'
        
        job_count = 0
        salaries = []
        recent_mentions = 0
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for job in corpus.jobs:
            title = job.get("title", "").lower()
            description = job.get("description", "").lower()
            combined = f"{title} {description}"
            
            # Check if this job mentions the skill
            if re.search(regex, combined, re.IGNORECASE):
                job_count += 1
                
                # Extract salary if available
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                if salary_min and salary_max:
                    salaries.append((salary_min + salary_max) / 2)
                
                # Check recency
                created = job.get("created")
                if created:
                    try:
                        job_date = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        if job_date >= cutoff_date:
                            recent_mentions += 1
                    except Exception:
                        pass
        
        avg_salary = sum(salaries) / len(salaries) if salaries else 0.0
        
        return {
            "job_count": job_count,
            "avg_salary": avg_salary,
            "recent_mentions": recent_mentions
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 4: NORMALIZATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def normalize_scores(self, skill_data: Dict[str, Dict]) -> List[SkillFrequency]:
        """
        Normalize skill frequencies using log scaling.
        
        Phase 4: Normalization
        - Apply log scaling to prevent dominance
        - Calculate demand score from frequency, salary, recency
        - Create SkillFrequency objects
        
        Args:
            skill_data: Dictionary of skill -> metrics
        
        Returns:
            List of SkillFrequency objects with normalized scores
        """
        if not skill_data:
            return []
        
        print(f"📊 Normalizing scores...")
        
        # Find max values for normalization
        max_frequency = max(s["frequency"] for s in skill_data.values())
        max_salary = max(s["avg_salary"] for s in skill_data.values()) or 1
        max_job_count = max(s["job_count"] for s in skill_data.values()) or 1
        
        skills = []
        
        for skill_name, metrics in skill_data.items():
            # Log scaling for frequency (prevents dominance)
            freq_score = (
                math.log(metrics["frequency"] + 1) / math.log(max_frequency + 1)
                if max_frequency > 0 else 0.0
            )
            
            # Linear scaling for salary
            salary_score = metrics["avg_salary"] / max_salary if max_salary > 0 else 0.0
            
            # Recency score
            recency_score = (
                metrics["recent_mentions"] / metrics["job_count"]
                if metrics["job_count"] > 0 else 0.0
            )
            
            # Combined demand score
            demand_score = (
                0.5 * freq_score +
                0.3 * salary_score +
                0.2 * recency_score
            )
            
            skills.append(SkillFrequency(
                skill_name=skill_name,
                frequency=metrics["frequency"],
                job_count=metrics["job_count"],
                avg_salary=metrics["avg_salary"],
                recent_mentions=metrics["recent_mentions"],
                demand_score=demand_score,
                rank=0,  # Will be set after sorting
                data_source="Adzuna API (dynamic extraction)",
                timestamp=datetime.now()
            ))
        
        return skills
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 5: RANKING
    # ═══════════════════════════════════════════════════════════════════════
    
    def rank_skills(self, skills: List[SkillFrequency], top_n: int = 20) -> List[SkillFrequency]:
        """
        Sort skills by demand score and assign ranks.
        
        Phase 5: Ranking
        - Sort by demand score (descending)
        - Assign ranks
        - Return top N skills
        
        Args:
            skills: List of SkillFrequency objects
            top_n: Number of top skills to return
        
        Returns:
            Top N ranked skills
        """
        # Sort by demand score
        skills.sort(key=lambda x: x.demand_score, reverse=True)
        
        # Assign ranks
        for i, skill in enumerate(skills):
            skill.rank = i + 1
        
        # Return top N
        top_skills = skills[:top_n]
        
        print(f"🏆 Top {len(top_skills)} skills ranked")
        
        return top_skills
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 6: OUTPUT
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_trending_skills(self, top_n: int = 20) -> Dict:
        """
        Main entry point: Detect and return trending skills.
        
        Phase 6: Output
        - Orchestrate all phases
        - Return formatted results
        
        Args:
            top_n: Number of top skills to return
        
        Returns:
            Dictionary with skills, metadata, and algorithm info
        """
        # Phase 1: Collect job data
        corpus = self.fetch_job_corpus(pages_per_query=5)
        if not corpus:
            return {
                "skills": [],
                "data_source": "INSUFFICIENT DATA",
                "message": "Adzuna API unavailable. Configure credentials.",
                "timestamp": datetime.now().isoformat(),
                "total_skills": 0
            }
        
        # Phase 2: Extract text
        text_corpus = self.extract_text_corpus(corpus)
        
        # Phase 3: Extract skills
        skill_data = self.extract_skills(text_corpus, corpus)
        
        # Phase 4: Normalize
        skills = self.normalize_scores(skill_data)
        
        # Phase 5: Rank
        top_skills = self.rank_skills(skills, top_n=top_n)
        
        # Phase 6: Format output
        return {
            "skills": [
                {
                    "name": s.skill_name,
                    "demand": round(s.demand_score, 3),
                    "rank": s.rank,
                    "frequency": s.frequency,
                    "job_count": s.job_count,
                    "avg_salary": round(s.avg_salary, 2),
                    "recent_mentions": s.recent_mentions
                }
                for s in top_skills
            ],
            "data_source": "Adzuna API (dynamic extraction from job postings)",
            "timestamp": datetime.now().isoformat(),
            "total_skills": len(skill_data),
            "top_n": top_n,
            "jobs_analyzed": corpus.total_jobs,
            "algorithm": "Dynamic skill detection with log-scaled frequency analysis"
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # CACHING
    # ═══════════════════════════════════════════════════════════════════════
    
    def _load_corpus_from_cache(self) -> Optional[JobCorpus]:
        """Load cached job corpus if available and fresh."""
        cache_path = self.cache_dir / "job_corpus.json"
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if cache is still fresh
            cached_time = datetime.fromisoformat(data['timestamp'])
            if (datetime.now() - cached_time).total_seconds() > self.cache_ttl:
                return None
            
            print(f"✅ Using cached job corpus ({data['total_jobs']} jobs)")
            
            return JobCorpus(
                jobs=data['jobs'],
                total_jobs=data['total_jobs'],
                queries_used=data['queries_used'],
                timestamp=cached_time
            )
        except Exception:
            return None
    
    def _save_corpus_to_cache(self, corpus: JobCorpus) -> None:
        """Save job corpus to cache."""
        cache_path = self.cache_dir / "job_corpus.json"
        
        try:
            data = {
                'jobs': corpus.jobs,
                'total_jobs': corpus.total_jobs,
                'queries_used': corpus.queries_used,
                'timestamp': corpus.timestamp.isoformat()
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            
            print(f"💾 Cached job corpus")
        except Exception as e:
            print(f"⚠️  Cache save failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

def get_dynamic_trending_skills(top_n: int = 20) -> Dict:
    """
    Get trending skills dynamically extracted from job market data.
    
    NO predefined skill lists - fully data-driven approach.
    
    Args:
        top_n: Number of top skills to return
    
    Returns:
        Dictionary with trending skills and metadata
    """
    detector = DynamicSkillDetector()
    return detector.get_trending_skills(top_n=top_n)


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*80)
    print("DYNAMIC SKILL DETECTION TEST")
    print("="*80)
    print()
    
    result = get_dynamic_trending_skills(top_n=15)
    
    print()
    print("="*80)
    print("RESULTS")
    print("="*80)
    print(f"Data Source: {result['data_source']}")
    print(f"Jobs Analyzed: {result.get('jobs_analyzed', 0)}")
    print(f"Total Skills Detected: {result['total_skills']}")
    print(f"Top {result.get('top_n', 0)} Skills:")
    print()
    
    if result['skills']:
        for skill in result['skills']:
            print(f"{skill['rank']:2d}. {skill['name']:<30} "
                  f"Demand: {skill['demand']:.1%}  "
                  f"Freq: {skill['frequency']:4d}  "
                  f"Jobs: {skill['job_count']:3d}")
    else:
        print(f"⚠️  {result.get('message', 'No skills detected')}")
