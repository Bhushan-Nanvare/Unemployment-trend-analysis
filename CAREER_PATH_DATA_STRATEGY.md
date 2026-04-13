# 🌐 Career Path Data Strategy - Live + Historical

## 🎯 Multi-Source Data Approach

We'll use a **hybrid strategy** combining:
1. **Your existing dataset** (baseline/fallback)
2. **Free live APIs** (real-time market data)
3. **Web scraping** (job boards)
4. **Smart caching** (performance + reliability)

---

## 📊 Data Sources Strategy

### **Tier 1: Your Existing Data** (Baseline - Always Available)

#### What You Have:
```
✅ marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv
   - 30,000+ job postings
   - Skills, roles, industries
   - Salary data
   - Location information
```

#### How We'll Use It:
```python
# Baseline career graph
# Skill demand weights
# Industry patterns
# Fallback when APIs fail
```

**Advantage:** Always works, no API limits, fast

---

### **Tier 2: Free Live APIs** (Real-Time Market Data)

#### 🔥 **Option 1: Adzuna API** (RECOMMENDED)
**Website:** https://developer.adzuna.com/
**Free Tier:** 250 calls/month
**Coverage:** Global job market data

```python
# Example API call
import requests

def get_live_job_data(role, location="india"):
    """Get current job market data from Adzuna"""
    
    APP_ID = "your_app_id"  # Free registration
    APP_KEY = "your_app_key"
    
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": role,
        "where": location,
        "results_per_page": 50,
        "content-type": "application/json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return {
        "total_jobs": data["count"],
        "avg_salary": data.get("mean", 0),
        "top_skills": extract_skills(data["results"]),
        "companies_hiring": len(set([j["company"]["display_name"] for j in data["results"]]))
    }
```

**What You Get:**
- ✅ Current job openings count
- ✅ Average salaries
- ✅ Top companies hiring
- ✅ Required skills
- ✅ Location-based data

---

#### 🔥 **Option 2: GitHub Jobs API** (Tech Roles)
**Website:** https://jobs.github.com/api
**Free Tier:** Unlimited
**Coverage:** Tech jobs globally

```python
def get_github_jobs(role="software engineer"):
    """Get tech job data from GitHub"""
    
    url = "https://jobs.github.com/positions.json"
    params = {
        "description": role,
        "location": "india"
    }
    
    response = requests.get(url, params=params)
    jobs = response.json()
    
    return {
        "total_jobs": len(jobs),
        "remote_percentage": sum(1 for j in jobs if j["type"] == "Remote") / len(jobs) * 100,
        "top_skills": extract_skills_from_descriptions(jobs),
        "companies": [j["company"] for j in jobs]
    }
```

---

#### 🔥 **Option 3: LinkedIn Job Search API** (via RapidAPI)
**Website:** https://rapidapi.com/jaypat87/api/linkedin-jobs-search
**Free Tier:** 100 calls/month
**Coverage:** LinkedIn job data

```python
def get_linkedin_jobs(role, location="India"):
    """Get LinkedIn job data"""
    
    url = "https://linkedin-jobs-search.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": "your_key",
        "X-RapidAPI-Host": "linkedin-jobs-search.p.rapidapi.com"
    }
    params = {
        "keywords": role,
        "location": location,
        "datePosted": "month"
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

---

#### 🔥 **Option 4: Indeed Job Search** (Web Scraping)
**Free, No API Key Needed**

```python
from bs4 import BeautifulSoup
import requests

def scrape_indeed_jobs(role, location="India"):
    """Scrape Indeed for job data"""
    
    url = f"https://in.indeed.com/jobs?q={role}&l={location}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract job count
    job_count_elem = soup.find('div', {'id': 'searchCountPages'})
    job_count = extract_number(job_count_elem.text) if job_count_elem else 0
    
    # Extract job titles and companies
    jobs = soup.find_all('div', {'class': 'job_seen_beacon'})
    
    return {
        "total_jobs": job_count,
        "sample_jobs": [extract_job_info(job) for job in jobs[:20]]
    }
```

---

### **Tier 3: Economic Indicators** (Macro Trends)

#### 🔥 **World Bank API** (Free, No Key)
**Website:** https://datahelpdesk.worldbank.org/knowledgebase/articles/889392

```python
def get_economic_indicators(country="IND"):
    """Get economic data from World Bank"""
    
    # GDP Growth
    gdp_url = f"https://api.worldbank.org/v2/country/{country}/indicator/NY.GDP.MKTP.KD.ZG?format=json&date=2020:2024"
    
    # Unemployment Rate
    unemp_url = f"https://api.worldbank.org/v2/country/{country}/indicator/SL.UEM.TOTL.ZS?format=json&date=2020:2024"
    
    gdp_data = requests.get(gdp_url).json()
    unemp_data = requests.get(unemp_url).json()
    
    return {
        "gdp_growth": gdp_data[1][0]["value"],
        "unemployment_rate": unemp_data[1][0]["value"],
        "trend": "growing" if gdp_data[1][0]["value"] > 0 else "declining"
    }
```

---

## 🏗️ Implementation Architecture

### **Smart Data Manager**

```python
# File: src/data_providers/career_data_manager.py

class CareerDataManager:
    """Manages multiple data sources with fallback"""
    
    def __init__(self):
        self.cache = DataCache(ttl_hours=24)
        self.historical_data = self._load_historical_data()
        
        # API clients
        self.adzuna = AdzunaClient()
        self.github_jobs = GitHubJobsClient()
        self.indeed_scraper = IndeedScraper()
        self.world_bank = WorldBankClient()
    
    def get_role_market_data(self, role: str, location: str = "India") -> dict:
        """
        Get market data with fallback strategy:
        1. Try cache (fast)
        2. Try live APIs (current)
        3. Fall back to historical data (reliable)
        """
        
        cache_key = f"market_{role}_{location}"
        
        # Try cache first
        if cached := self.cache.get(cache_key):
            return cached
        
        # Try live APIs
        try:
            live_data = self._fetch_live_data(role, location)
            self.cache.set(cache_key, live_data)
            return live_data
        except Exception as e:
            logger.warning(f"Live API failed: {e}, using historical data")
            return self._get_historical_data(role, location)
    
    def _fetch_live_data(self, role: str, location: str) -> dict:
        """Fetch from multiple sources and aggregate"""
        
        results = {}
        
        # Try Adzuna (primary)
        try:
            results["adzuna"] = self.adzuna.search(role, location)
        except:
            pass
        
        # Try GitHub Jobs (tech roles)
        if "engineer" in role.lower() or "developer" in role.lower():
            try:
                results["github"] = self.github_jobs.search(role)
            except:
                pass
        
        # Try Indeed scraping (backup)
        try:
            results["indeed"] = self.indeed_scraper.scrape(role, location)
        except:
            pass
        
        # Aggregate results
        return self._aggregate_sources(results)
    
    def _aggregate_sources(self, results: dict) -> dict:
        """Combine data from multiple sources"""
        
        total_jobs = sum(r.get("total_jobs", 0) for r in results.values())
        avg_salary = np.mean([r.get("avg_salary", 0) for r in results.values() if r.get("avg_salary")])
        
        # Combine skills from all sources
        all_skills = []
        for r in results.values():
            all_skills.extend(r.get("top_skills", []))
        
        top_skills = Counter(all_skills).most_common(10)
        
        return {
            "total_jobs": total_jobs,
            "avg_salary": avg_salary,
            "top_skills": [skill for skill, count in top_skills],
            "data_sources": list(results.keys()),
            "data_freshness": datetime.now().isoformat(),
            "confidence": len(results) / 3  # 0-1 based on sources available
        }
    
    def _get_historical_data(self, role: str, location: str) -> dict:
        """Fallback to your CSV data"""
        
        # Filter your existing dataset
        df = self.historical_data
        role_data = df[df["Role"].str.contains(role, case=False, na=False)]
        
        return {
            "total_jobs": len(role_data),
            "avg_salary": role_data["Salary"].mean(),
            "top_skills": self._extract_skills_from_df(role_data),
            "data_sources": ["historical_csv"],
            "data_freshness": "2019-07-01",  # Your data date
            "confidence": 0.5  # Lower confidence for old data
        }
```

---

## 📦 Complete Data Flow

```
User requests career path
        ↓
CareerDataManager.get_role_market_data()
        ↓
    ┌───────────────────────────────┐
    │  1. Check Cache (24h TTL)    │
    │     ✅ Hit → Return cached    │
    │     ❌ Miss → Continue        │
    └───────────────────────────────┘
        ↓
    ┌───────────────────────────────┐
    │  2. Try Live APIs             │
    │     • Adzuna API              │
    │     • GitHub Jobs             │
    │     • Indeed Scraping         │
    │     ✅ Success → Cache & Return│
    │     ❌ Fail → Continue        │
    └───────────────────────────────┘
        ↓
    ┌───────────────────────────────┐
    │  3. Fallback to Historical    │
    │     • Your CSV data           │
    │     • Always works            │
    │     ✅ Return with warning    │
    └───────────────────────────────┘
```

---

## 🎯 Recommended Setup

### **Phase 1: Start with Historical + Adzuna**
```python
# Quick setup (1 hour)
1. Use your CSV as baseline
2. Add Adzuna API (free, 250 calls/month)
3. Implement caching (24h TTL)
4. Show data freshness indicator
```

### **Phase 2: Add More Sources**
```python
# Enhanced setup (2 hours)
1. Add GitHub Jobs for tech roles
2. Add Indeed scraping as backup
3. Implement source aggregation
4. Add confidence scoring
```

### **Phase 3: Economic Indicators**
```python
# Advanced setup (1 hour)
1. Add World Bank API
2. Integrate GDP/unemployment data
3. Adjust career path probabilities
4. Show macro trend indicators
```

---

## 💰 Cost Analysis

| Data Source | Cost | Calls/Month | Coverage |
|-------------|------|-------------|----------|
| Your CSV | FREE | Unlimited | Baseline |
| Adzuna API | FREE | 250 | Global jobs |
| GitHub Jobs | FREE | Unlimited | Tech jobs |
| Indeed Scraping | FREE | Unlimited* | All jobs |
| World Bank | FREE | Unlimited | Economics |

*Rate limiting applies, use responsibly

**Total Cost: $0/month** 🎉

---

## 🚀 Implementation Code

### **File: `src/data_providers/adzuna_client.py`**
```python
import requests
from typing import Dict, List
import os

class AdzunaClient:
    """Client for Adzuna Job Search API"""
    
    BASE_URL = "https://api.adzuna.com/v1/api/jobs"
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "your_app_id")
        self.app_key = os.getenv("ADZUNA_APP_KEY", "your_app_key")
    
    def search(self, role: str, location: str = "india", max_results: int = 50) -> Dict:
        """Search for jobs on Adzuna"""
        
        url = f"{self.BASE_URL}/in/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": role,
            "where": location,
            "results_per_page": max_results,
            "content-type": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "total_jobs": data.get("count", 0),
                "avg_salary": data.get("mean", 0),
                "jobs": data.get("results", []),
                "top_skills": self._extract_skills(data.get("results", [])),
                "source": "adzuna"
            }
        except Exception as e:
            raise Exception(f"Adzuna API error: {e}")
    
    def _extract_skills(self, jobs: List[Dict]) -> List[str]:
        """Extract skills from job descriptions"""
        
        # Common tech skills to look for
        skill_keywords = [
            "python", "java", "javascript", "react", "node.js",
            "sql", "aws", "docker", "kubernetes", "machine learning",
            "data analysis", "project management", "agile", "scrum"
        ]
        
        skill_counts = {}
        for job in jobs:
            description = job.get("description", "").lower()
            for skill in skill_keywords:
                if skill in description:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Return top 10 skills
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, count in sorted_skills[:10]]
```

---

## 🎯 Quick Start Guide

### **Step 1: Register for Adzuna (5 minutes)**
1. Go to https://developer.adzuna.com/
2. Sign up (free)
3. Get your APP_ID and APP_KEY
4. Add to `.env` file:
```
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

### **Step 2: Test API (2 minutes)**
```python
from src.data_providers.adzuna_client import AdzunaClient

client = AdzunaClient()
data = client.search("software engineer", "bangalore")
print(f"Found {data['total_jobs']} jobs")
print(f"Top skills: {data['top_skills']}")
```

### **Step 3: Integrate with Career Path (1 hour)**
```python
# In career_path_modeler.py
data_manager = CareerDataManager()
market_data = data_manager.get_role_market_data("Senior Engineer", "India")

# Use market_data to adjust success probability
if market_data["total_jobs"] > 1000:
    success_probability *= 1.2  # High demand boost
```

---

## ✅ Summary

**Best Approach:**
1. ✅ **Start:** Your CSV + Adzuna API (FREE, reliable)
2. ✅ **Enhance:** Add GitHub Jobs + Indeed scraping
3. ✅ **Advanced:** Add World Bank economic data
4. ✅ **Always:** Cache + fallback to historical data

**Result:** 
- Real-time market data when available
- Always works (fallback to your CSV)
- $0/month cost
- Professional and reliable

**Ready to implement?** 🚀
