"""Adzuna API client for live job market data."""

import requests
import os
from typing import Dict, List, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class AdzunaClient:
    """Client for Adzuna Job Search API"""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "4a3a122e")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "82c616e066d400fd33c5ad78aeb2f6f3")
    
    def search_jobs(self, role: str, location: str = "india", max_results: int = 50) -> Dict:
        """
        Search for jobs on Adzuna
        
        Args:
            role: Job role to search for
            location: Location to search in
            max_results: Maximum number of results to fetch
            
        Returns:
            Dictionary with job market data
        """
        
        url = f"{self.BASE_URL}/in/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": role,
            "where": location,
            "results_per_page": min(max_results, 50),  # API limit
            "content-type": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            jobs = data.get("results", [])
            
            return {
                "total_jobs": data.get("count", 0),
                "avg_salary": data.get("mean", 0),
                "jobs": jobs,
                "top_skills": self._extract_skills(jobs),
                "top_companies": self._extract_companies(jobs),
                "remote_percentage": self._calculate_remote_percentage(jobs),
                "source": "adzuna",
                "success": True
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Adzuna API request failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Adzuna API error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_salary_histogram(self, role: str, location: str = "india") -> Dict:
        """Get salary distribution for a role"""
        
        url = f"{self.BASE_URL}/in/histogram"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": role,
            "where": location,
            "content-type": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Salary histogram API error: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_skills(self, jobs: List[Dict]) -> List[str]:
        """Extract top skills from job descriptions"""
        
        # Comprehensive skill keywords
        skill_keywords = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust",
            "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css",
            
            # Frameworks & Libraries
            "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "laravel",
            "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn",
            
            # Cloud & DevOps
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible",
            "microservices", "serverless", "ci/cd", "devops",
            
            # Databases
            "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", "oracle",
            
            # Data & Analytics
            "machine learning", "deep learning", "data science", "data analysis", "big data",
            "hadoop", "spark", "tableau", "power bi", "excel",
            
            # Soft Skills
            "leadership", "project management", "agile", "scrum", "communication", "teamwork",
            "problem solving", "analytical thinking",
            
            # Other Tech
            "api", "rest", "graphql", "blockchain", "iot", "mobile development", "web development",
            "cybersecurity", "network security", "testing", "qa", "automation testing"
        ]
        
        skill_counts = Counter()
        
        for job in jobs:
            description = job.get("description", "").lower()
            title = job.get("title", "").lower()
            
            # Check both title and description
            full_text = f"{title} {description}"
            
            for skill in skill_keywords:
                if skill.lower() in full_text:
                    skill_counts[skill] += 1
        
        # Return top 10 skills with counts
        top_skills = skill_counts.most_common(10)
        return [skill for skill, count in top_skills if count > 0]
    
    def _extract_companies(self, jobs: List[Dict]) -> List[str]:
        """Extract top companies from job listings"""
        
        companies = []
        for job in jobs:
            company = job.get("company", {})
            if isinstance(company, dict):
                company_name = company.get("display_name", "")
            else:
                company_name = str(company)
            
            if company_name and company_name.lower() not in ["confidential", "private", "undisclosed"]:
                companies.append(company_name)
        
        # Return top 10 companies
        company_counts = Counter(companies)
        return [company for company, count in company_counts.most_common(10)]
    
    def _calculate_remote_percentage(self, jobs: List[Dict]) -> float:
        """Calculate percentage of remote jobs"""
        
        if not jobs:
            return 0.0
        
        remote_keywords = ["remote", "work from home", "wfh", "telecommute", "distributed"]
        remote_count = 0
        
        for job in jobs:
            description = job.get("description", "").lower()
            title = job.get("title", "").lower()
            location = job.get("location", {}).get("display_name", "").lower()
            
            full_text = f"{title} {description} {location}"
            
            if any(keyword in full_text for keyword in remote_keywords):
                remote_count += 1
        
        return (remote_count / len(jobs)) * 100
    
    def test_connection(self) -> bool:
        """Test if API credentials are working"""
        
        try:
            result = self.search_jobs("software engineer", "india", max_results=1)
            return result.get("success", False)
        except Exception:
            return False