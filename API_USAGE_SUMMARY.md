# API Usage Summary - Unemployment Intelligence Platform

**Date**: 2026-04-13  
**Status**: DOCUMENTED

---

## 🌐 WHERE APIS ARE USED

Your project uses **3 types of APIs**:

### **1. Internal FastAPI Backend** (Your Own API)
### **2. External Free APIs** (World Bank, Groq, Gemini)
### **3. External Paid APIs** (Adzuna, OpenAI - Optional)

---

## 📊 DETAILED API BREAKDOWN

### **1. INTERNAL API (FastAPI Backend)**

**File**: `src/api.py`

**Purpose**: Your own backend API that Streamlit pages call

**Base URL**: `http://127.0.0.1:8000` (local) or your deployed URL

**Endpoints**:
```python
POST /simulate              # Scenario simulation
POST /backtest              # Model backtesting
GET  /validate              # Model validation
GET  /events                # Historical events
POST /sensitivity_analysis  # Sensitivity analysis
GET  /data-status           # Data source status
```

**How It's Used**:
```python
# In Streamlit pages (e.g., pages/1_Overview.py)
from src.api import simulate_scenario, ScenarioRequest

# Call internal API
req = ScenarioRequest(
    shock_intensity=0.0,
    shock_duration=0,
    recovery_rate=0.0,
    forecast_horizon=6
)
result = simulate_scenario(req)
```

**Status**: ✅ Working (your own API)

---

### **2. WORLD BANK OPEN DATA API** (Free, No Key Required)

**File**: `src/live_data.py`

**Purpose**: Fetch unemployment, GDP, and sector data

**Base URL**: `https://api.worldbank.org/v2/`

**Endpoints Used**:
```
GET /country/{iso}/indicator/SL.UEM.TOTL.ZS        # Unemployment rate
GET /country/{iso}/indicator/NY.GDP.MKTP.KD.ZG     # GDP growth
GET /country/{iso}/indicator/SL.AGR.EMPL.ZS        # Agriculture employment
GET /country/{iso}/indicator/SL.IND.EMPL.ZS        # Industry employment
GET /country/{iso}/indicator/SL.SRV.EMPL.ZS        # Services employment
... and more
```

**How It's Used**:
```python
# In src/live_data.py
def fetch_world_bank(country: str = "India") -> pd.DataFrame:
    url = "https://api.worldbank.org/v2/country/IN/indicator/SL.UEM.TOTL.ZS"
    params = {"format": "json", "per_page": 65}
    resp = requests.get(url, params=params, timeout=10)
    # ... process response
```

**Features**:
- ✅ Free (no API key required)
- ✅ No rate limits
- ✅ Automatic fallback to local CSV if API fails
- ✅ 24-hour caching to reduce API calls

**Status**: ✅ Working (with fallback to local data)

**Note**: Currently using **local curated data** as primary source because World Bank data for India has quality issues post-2019. API is fallback only.

---

### **3. LLM APIs** (For AI Insights)

**File**: `src/llm_insights.py`

**Purpose**: Generate AI-powered insights and explanations

**Priority Order** (tries each until one works):

#### **3a. Groq API** (Free, Recommended)
- **URL**: `https://api.groq.com/openai/v1/chat/completions`
- **Model**: `llama-3.1-8b-instant`
- **Free Tier**: 14,400 requests/day
- **API Key**: `GROQ_API_KEY` (environment variable)
- **Get Key**: https://console.groq.com (free signup)

```python
# In src/llm_insights.py
def _try_groq(prompt: str) -> Optional[str]:
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]}
    )
```

**Status**: ⚠️ Optional (requires API key)

#### **3b. Google Gemini API** (Free)
- **URL**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
- **Model**: `gemini-1.5-flash`
- **Free Tier**: 15 requests/minute, 1M tokens/day
- **API Key**: `GEMINI_API_KEY` (environment variable)
- **Get Key**: https://aistudio.google.com/app/apikey

```python
def _try_gemini(prompt: str) -> Optional[str]:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
```

**Status**: ⚠️ Optional (requires API key)

#### **3c. OpenAI API** (Paid)
- **URL**: `https://api.openai.com/v1/chat/completions`
- **Model**: `gpt-4o-mini`
- **Cost**: Paid (requires billing)
- **API Key**: `OPENAI_API_KEY` (environment variable)

```python
def _try_openai(prompt: str) -> Optional[str]:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]}
    )
```

**Status**: ⚠️ Optional (requires paid API key)

#### **3d. Rule-Based Fallback** (Always Works)
- **No API**: Uses deterministic rules
- **No Cost**: Free
- **No Setup**: Always available

```python
def _rule_based_insights(scenario_name: str, indices: dict, sector_impact: pd.DataFrame) -> list[str]:
    # Generate insights using rules and thresholds
    # Always works, no API needed
```

**Status**: ✅ Always works (no API required)

---

### **4. ADZUNA JOB SEARCH API** (Paid/Free Tier)

**File**: `src/data_providers/adzuna_client.py`

**Purpose**: Fetch live job market data (job postings, salaries, skills)

**Base URL**: `https://api.adzuna.com/v1/api/jobs`

**Endpoints Used**:
```
GET /in/search/1        # Search jobs in India
GET /in/histogram       # Salary distribution
```

**How It's Used**:
```python
# In src/data_providers/adzuna_client.py
class AdzunaClient:
    def search_jobs(self, role: str, location: str = "india"):
        url = f"{self.BASE_URL}/in/search/1"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": role,
            "where": location
        }
        response = requests.get(url, params=params)
```

**API Keys**:
- `ADZUNA_APP_ID` (environment variable)
- `ADZUNA_APP_KEY` (environment variable)

**Features**:
- Job search by role and location
- Salary data
- Top skills extraction
- Top companies
- Remote job percentage

**Status**: ⚠️ Optional (requires API key, used in Career Path Modeler)

---

## 📋 API USAGE BY FEATURE

### **Overview Page** (`pages/1_Overview.py`)
- ✅ Internal API (`/simulate`) - Baseline forecast
- ✅ World Bank API - GDP growth data
- ⚠️ LLM APIs - AI insights (optional)

### **Simulator Page** (`pages/2_Simulator.py`)
- ✅ Internal API (`/simulate`) - Scenario simulation
- ✅ World Bank API - Historical data
- ⚠️ LLM APIs - AI insights (optional)

### **Sector Analysis** (`pages/3_Sector_Analysis.py`)
- ✅ World Bank API - Sector employment/GDP data
- ⚠️ LLM APIs - Sector insights (optional)

### **Career Lab** (`pages/4_Career_Lab.py`)
- ⚠️ Adzuna API - Job market data (optional)
- ✅ Rule-based fallback if API unavailable

### **Job Risk Predictor** (`pages/7_Job_Risk_Predictor.py`)
- ✅ Internal calculations (no external API)
- ✅ Uses local data only

### **Job Market Pulse** (`pages/8_Job_Market_Pulse.py`)
- ✅ World Bank API - Labor market indicators
- ⚠️ LLM APIs - Insights (optional)

### **Geo Career Advisor** (`pages/9_Geo_Career_Advisor.py`)
- ✅ Local PLFS data (no API)
- ✅ Curated state-level data

### **Skill Obsolescence** (`pages/10_Skill_Obsolescence.py`)
- ✅ Local job posting data (2019 dataset)
- ✅ No external API

---

## 🔑 API KEYS REQUIRED

### **Required for Full Functionality**:
None! The platform works without any API keys.

### **Optional for Enhanced Features**:

**1. LLM APIs** (for AI insights):
```bash
# .env file
GROQ_API_KEY=your_groq_key_here          # Free, 14,400 req/day
GEMINI_API_KEY=your_gemini_key_here      # Free, 15 RPM
OPENAI_API_KEY=your_openai_key_here      # Paid
```

**2. Adzuna API** (for live job data):
```bash
# .env file
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

---

## 🚀 HOW TO GET API KEYS

### **Groq API** (Recommended - Free)
1. Go to https://console.groq.com
2. Sign up (free, no credit card)
3. Create API key
4. Add to `.env`: `GROQ_API_KEY=your_key`

### **Google Gemini API** (Free)
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Add to `.env`: `GEMINI_API_KEY=your_key`

### **OpenAI API** (Paid)
1. Go to https://platform.openai.com
2. Sign up and add billing
3. Create API key
4. Add to `.env`: `OPENAI_API_KEY=your_key`

### **Adzuna API**
1. Go to https://developer.adzuna.com
2. Sign up for developer account
3. Get App ID and App Key
4. Add to `.env`:
   ```
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_app_key
   ```

---

## 📊 API USAGE STATISTICS

### **Current Setup**:
```
✅ Working without API keys:
   - Internal FastAPI backend
   - World Bank Open Data API
   - Local curated data (primary)
   - Rule-based AI insights

⚠️ Optional (requires API keys):
   - Groq/Gemini/OpenAI (LLM insights)
   - Adzuna (live job data)
```

### **API Call Frequency**:
```
World Bank API:
- Cached for 24 hours
- ~5-10 calls per page load (first time)
- ~0 calls after caching

Internal API:
- Called on every simulation
- No external network calls
- Instant response

LLM APIs (if enabled):
- Called for AI insights
- ~1-3 calls per insight generation
- Cached results

Adzuna API (if enabled):
- Called for job searches
- ~1 call per career path query
- Results cached
```

---

## 🔒 API SECURITY

### **Best Practices**:
1. ✅ API keys stored in `.env` file (not in code)
2. ✅ `.env` file in `.gitignore` (not committed)
3. ✅ Environment variables used for all keys
4. ✅ Graceful fallbacks if APIs fail
5. ✅ Timeout limits on all API calls
6. ✅ Error handling for all API requests

### **Current Security Status**:
```
✅ No API keys in code
✅ No API keys in Git repository
✅ Environment variables used
✅ Fallback mechanisms in place
✅ Error handling implemented
```

---

## 🐛 TROUBLESHOOTING

### **"API connection failed"**
- Check internet connection
- Verify API key in `.env` file
- Check API service status
- System will use fallback data automatically

### **"World Bank API unavailable"**
- System automatically uses local CSV data
- No action needed - fallback is automatic
- Quality: Local data is actually better quality

### **"LLM API not responding"**
- System automatically tries next provider
- Falls back to rule-based insights
- No action needed - always works

### **"Adzuna API error"**
- Check API keys in `.env`
- Verify API quota not exceeded
- System uses historical data as fallback

---

## 📈 RECOMMENDATIONS

### **For Production Deployment**:

**1. Keep Current Setup** (No API keys needed):
- ✅ Use local curated data (better quality)
- ✅ Use rule-based insights (always works)
- ✅ Use World Bank API as fallback only
- ✅ No external dependencies

**2. Add LLM API** (Optional, for better insights):
- Recommended: Groq (free, 14,400 req/day)
- Alternative: Gemini (free, 15 RPM)
- Benefit: Better AI-generated insights
- Cost: Free

**3. Add Adzuna API** (Optional, for live job data):
- Benefit: Real-time job market data
- Cost: Check Adzuna pricing
- Alternative: Use historical data (already included)

---

## ✅ SUMMARY

### **APIs Currently Used**:
1. ✅ **Internal FastAPI** - Your own backend (always works)
2. ✅ **World Bank API** - Free, no key (with local fallback)
3. ⚠️ **LLM APIs** - Optional (Groq/Gemini/OpenAI)
4. ⚠️ **Adzuna API** - Optional (job market data)

### **What Works Without API Keys**:
- ✅ All core functionality
- ✅ Unemployment forecasting
- ✅ Scenario simulation
- ✅ Risk prediction
- ✅ Sector analysis
- ✅ Career advice
- ✅ Data validation
- ✅ All visualizations

### **What Requires API Keys**:
- ⚠️ Advanced LLM insights (optional)
- ⚠️ Live job market data (optional)

### **Recommendation**:
**Deploy as-is** - Everything works without API keys. Add LLM API (Groq - free) later if you want better AI insights.

---

**Last Updated**: 2026-04-13  
**Status**: DOCUMENTED  
**API Keys Required**: None (all optional)
