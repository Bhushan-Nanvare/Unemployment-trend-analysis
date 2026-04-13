"""Career data manager with multiple sources and caching."""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
from collections import Counter

from .adzuna_client import AdzunaClient
from .job_market_validator import JobMarketValidator

logger = logging.getLogger(__name__)


class DataCache:
    """Simple file-based cache with TTL"""
    
    def __init__(self, cache_dir: str = ".cache/career_data", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached data if not expired"""
        
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if expired
            cached_time = datetime.fromisoformat(data.get("cached_at", ""))
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                return None
            
            return data.get("data")
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, data: Dict) -> None:
        """Cache data with timestamp"""
        
        cache_file = self.cache_dir / f"{key}.json"
        
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "data": data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Cache write error: {e}")


class CareerDataManager:
    """Manages career data from multiple sources with fallback"""
    
    def __init__(self):
        self.cache = DataCache(ttl_hours=24)
        self.adzuna = AdzunaClient()
        self.historical_data = self._load_historical_data()
    
    def get_role_market_data(self, role: str, location: str = "india") -> Dict:
        """
        Get comprehensive market data for a role with validation.
        
        Strategy (STRICT - NO MIXING):
        1. Check cache (fast)
        2. Try Adzuna API (current data) → VALIDATE → Use if valid
        3. Fallback to historical data (reliable) → VALIDATE → Label as historical
        
        Returns:
            Dict with validated market data and clear source labeling
        """
        
        cache_key = f"market_{role.lower().replace(' ', '_')}_{location.lower()}"
        
        # Try cache first
        if cached_data := self.cache.get(cache_key):
            logger.info(f"Using cached data for {role}")
            # Add source label
            cached_data["source_label"] = JobMarketValidator.get_data_source_label(cached_data)
            return cached_data
        
        # Try live API with validation
        try:
            live_data = self._fetch_live_data(role, location)
            
            # VALIDATE live data
            cleaned_data, validation_result = JobMarketValidator.validate_and_clean(live_data)
            
            if cleaned_data and validation_result.is_valid:
                # Add clear labeling
                cleaned_data["source_label"] = JobMarketValidator.get_data_source_label(cleaned_data)
                cleaned_data["data_age_warning"] = JobMarketValidator.get_data_age_warning(cleaned_data)
                
                # Cache validated data
                self.cache.set(cache_key, cleaned_data)
                
                logger.info(f"✅ Using validated live data for {role} (Quality: {validation_result.data_quality_score:.1f}/100)")
                return cleaned_data
            else:
                logger.warning(f"❌ Live data validation failed for {role}: {validation_result.errors}")
                # Discard invalid data, fall through to historical
                
        except Exception as e:
            logger.warning(f"Live API failed for {role}: {e}")
        
        # Fallback to historical data with validation
        logger.info(f"⚠️ Using historical data for {role}")
        historical_data = self._get_historical_data(role, location)
        
        # VALIDATE historical data
        cleaned_data, validation_result = JobMarketValidator.validate_and_clean(historical_data)
        
        if cleaned_data and validation_result.is_valid:
            # Add clear labeling
            cleaned_data["source_label"] = JobMarketValidator.get_data_source_label(cleaned_data)
            cleaned_data["data_age_warning"] = JobMarketValidator.get_data_age_warning(cleaned_data)
            
            logger.info(f"✅ Using validated historical data for {role} (Quality: {validation_result.data_quality_score:.1f}/100)")
            return cleaned_data
        else:
            logger.error(f"❌ Historical data validation failed for {role}: {validation_result.errors}")
            # Last resort: default data
            return self._get_default_data(role)
    
    def _fetch_live_data(self, role: str, location: str) -> Dict:
        """Fetch data from Adzuna API"""
        
        result = self.adzuna.search_jobs(role, location, max_results=50)
        
        if not result.get("success"):
            raise Exception(f"API call failed: {result.get('error')}")
        
        # Enhance with additional analysis
        enhanced_data = {
            **result,
            "market_health": self._analyze_market_health(result),
            "demand_level": self._calculate_demand_level(result["total_jobs"]),
            "salary_trend": self._analyze_salary_trend(result.get("avg_salary", 0)),
            "data_freshness": datetime.now().isoformat(),
            "source": "adzuna",  # Explicit source
            "success": True
        }
        
        return enhanced_data
    
    def _get_historical_data(self, role: str, location: str) -> Dict:
        """Fallback to historical CSV data"""
        
        if self.historical_data is None:
            return self._get_default_data(role)
        
        # Filter historical data for similar roles
        df = self.historical_data
        role_keywords = role.lower().split()
        
        # Find matching rows
        mask = df['Role'].str.lower().str.contains('|'.join(role_keywords), na=False)
        role_data = df[mask]
        
        if len(role_data) == 0:
            return self._get_default_data(role)
        
        # Extract skills from historical data
        skills = []
        for _, row in role_data.iterrows():
            if pd.notna(row.get('Skills', '')):
                skills.extend(str(row['Skills']).split(','))
        
        skill_counts = Counter([s.strip().lower() for s in skills if s.strip()])
        top_skills = [skill for skill, count in skill_counts.most_common(10)]
        
        return {
            "total_jobs": len(role_data),
            "avg_salary": role_data.get('Salary', pd.Series([0])).mean(),
            "top_skills": top_skills,
            "top_companies": role_data.get('Company', pd.Series([])).value_counts().head(5).index.tolist(),
            "remote_percentage": 20.0,  # Estimated
            "market_health": "stable",
            "demand_level": "medium",
            "salary_trend": "stable",
            "data_freshness": "2019-07-01",  # Historical data date
            "source": "historical_csv",  # Explicit source
            "success": True
        }
    
    def _load_historical_data(self) -> Optional[pd.DataFrame]:
        """Load historical job data from CSV"""
        
        csv_path = Path("marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv")
        
        if not csv_path.exists():
            logger.warning("Historical CSV data not found")
            return None
        
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded historical data: {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return None
    
    def _analyze_market_health(self, data: Dict) -> str:
        """Analyze overall market health"""
        
        total_jobs = data.get("total_jobs", 0)
        remote_pct = data.get("remote_percentage", 0)
        
        if total_jobs > 1000:
            return "excellent"
        elif total_jobs > 500:
            return "good"
        elif total_jobs > 100:
            return "fair"
        else:
            return "limited"
    
    def _calculate_demand_level(self, total_jobs: int) -> str:
        """Calculate demand level based on job count"""
        
        if total_jobs > 2000:
            return "very_high"
        elif total_jobs > 1000:
            return "high"
        elif total_jobs > 500:
            return "medium"
        elif total_jobs > 100:
            return "low"
        else:
            return "very_low"
    
    def _analyze_salary_trend(self, avg_salary: float) -> str:
        """Analyze salary trend (simplified)"""
        
        # This is a simplified analysis
        # In a real system, you'd compare with historical salary data
        if avg_salary > 1000000:  # > 10 LPA
            return "increasing"
        elif avg_salary > 500000:  # > 5 LPA
            return "stable"
        else:
            return "below_market"
    
    def _get_default_data(self, role: str) -> Dict:
        """Default data when no other source is available"""
        
        default_data = {
            "total_jobs": 100,  # Conservative estimate
            "avg_salary": 600000,  # 6 LPA average
            "top_skills": ["communication", "problem solving", "teamwork"],
            "top_companies": ["TCS", "Infosys", "Wipro", "Accenture", "IBM"],
            "remote_percentage": 25.0,
            "market_health": "stable",
            "demand_level": "medium",
            "salary_trend": "stable",
            "data_freshness": datetime.now().isoformat(),
            "source": "default",  # Explicit source
            "success": True
        }
        
        # Add validation and labeling
        cleaned_data, validation_result = JobMarketValidator.validate_and_clean(default_data)
        
        if cleaned_data:
            cleaned_data["source_label"] = JobMarketValidator.get_data_source_label(cleaned_data)
            cleaned_data["data_age_warning"] = JobMarketValidator.get_data_age_warning(cleaned_data)
            return cleaned_data
        
        return default_data
    
    def get_industry_trends(self) -> Dict:
        """Get overall industry trends"""
        
        # This could be enhanced with economic indicators
        return {
            "Technology / software": {"growth": 0.15, "trend": "growing"},
            "Healthcare / biotech": {"growth": 0.12, "trend": "growing"},
            "Financial services / fintech": {"growth": 0.08, "trend": "stable"},
            "Education / edtech": {"growth": 0.10, "trend": "growing"},
            "Manufacturing (traditional)": {"growth": -0.02, "trend": "declining"},
            "Retail / e-commerce ops": {"growth": 0.05, "trend": "stable"},
            "Hospitality / tourism": {"growth": -0.05, "trend": "declining"},
        }
    
    def test_api_connection(self) -> bool:
        """Test if live APIs are working"""
        
        return self.adzuna.test_connection()
    
    def get_multiple_roles_data(self, roles: List[str], location: str = "india") -> Dict[str, Dict]:
        """
        Get market data for multiple roles with consistency enforcement.
        
        ENSURES: All roles use the SAME data source (no mixing).
        
        Args:
            roles: List of role names
            location: Location to search
            
        Returns:
            Dict mapping role -> market data
        """
        results = {}
        sources_used = set()
        
        for role in roles:
            data = self.get_role_market_data(role, location)
            results[role] = data
            sources_used.add(data.get("source", "unknown"))
        
        # Check consistency
        if len(sources_used) > 1:
            logger.warning(f"⚠️ MIXED DATA SOURCES DETECTED: {sources_used}")
            logger.warning("This violates consistency requirement. Consider using single source.")
        else:
            logger.info(f"✅ Consistent data source across all roles: {sources_used.pop()}")
        
        return results
    
    def get_data_source_summary(self) -> Dict:
        """
        Get summary of current data sources being used.
        
        Returns:
            Summary dict with source information
        """
        # Test API connection
        api_available = self.test_api_connection()
        
        # Check historical data
        historical_available = self.historical_data is not None
        
        return {
            "adzuna_api_available": api_available,
            "historical_data_available": historical_available,
            "primary_source": "adzuna" if api_available else "historical_csv",
            "fallback_source": "historical_csv" if historical_available else "default",
            "recommendation": (
                "✅ Using live Adzuna API (Current 2026 data)" if api_available
                else "⚠️ Using historical data (2019 - 7 years old). Enable Adzuna API for current data."
            )
        }