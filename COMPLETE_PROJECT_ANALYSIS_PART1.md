# COMPLETE PROJECT ANALYSIS: Unemployment Trend Analysis (India)
## Expert-Level Deep Dive for Validation & Review

**Project Name:** Unemployment Intelligence Platform (UIP)  
**Domain:** Economics, Data Science, Labor Market Analysis  
**Technology Stack:** Python, Streamlit, FastAPI, Plotly, Scikit-learn  
**Analysis Date:** April 13, 2026  
**Analyst:** AI Expert System

---

## 📊 SECTION 1: DATA DETAILS

### 1.1 Primary Datasets

#### **Dataset 1: Unemployment Data**
- **File**: `data/raw/india_unemployment_realistic.csv` (CORRECTED VERSION)
- **Source**: Multi-source curated data
  - PLFS (Periodic Labour Force Survey) - Government of India
  - CMIE (Centre for Monitoring Indian Economy)
  - World Bank Open Data API (SL.UEM.TOTL.ZS)
- **Fields/Columns**:
  - `Year` (int): 1991-2024 (34 years)
  - `Unemployment_Rate` (float): Percentage (%)
- **Time Range**: 1991-2024 (34 years of historical data)
- **Units**: Percentage (%)
- **Data Quality**: ✅ HIGH - Corrected from unrealistic values
- **Key Characteristics**:
  - Range: 3.7% - 7.3%
  - Mean: 5.0%
  - Std Dev: 1.2%
  - COVID-19 Impact: 7.1% (2020 annual average, NOT 23.5% monthly peak)

#### **Dataset 2: Inflation Data**
- **File**: `data/raw/india_inflation_corrected.csv` (NEW)
- **Source**: 
  - RBI (Reserve Bank of India) - CPI data
  - World Bank API (FP.CPI.TOTL.ZG)
  - Ministry of Statistics - Official CPI
- **Fields/Columns**:
  - `Year` (int): 1991-2024
  - `Inflation_Rate` (float): CPI inflation (%)
- **Time Range**: 1991-2024 (34 years)
- **Units**: Percentage (%)
- **Data Quality**: ✅ HIGH - Corrected from 20%+ to realistic 4-14% range
- **Key Characteristics**:
  - Range: 3.4% - 13.9%
  - Mean: 6.8%
  - Std Dev: 3.1%
  - RBI Target: 4% ±2% (since 2016)

#### **Dataset 3: Job Market Data**
- **File**: `marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv`
- **Source**: Naukri.com (via Kaggle)
- **Records**: 29,425 real job postings
- **Time Period**: July-August 2019
- **Fields** (estimated):
  - Job Title/Role
  - Company
  - Skills Required
  - Salary (if available)
  - Location
  - Industry/Sector
- **Purpose**: Job market pulse analysis, skill demand trends
- **Limitation**: ⚠️ Data is from 2019 - may not reflect current market

#### **Dataset 4: State-Level Unemployment**
- **Source**: PLFS 2022-23 (MOSPI) - Hardcoded in `src/live_data.py`
- **Coverage**: 30 Indian states
- **Fields**:
  - State name
  - Urban_UE (%)
  - Rural_UE (%)
  - Combined_UE (%)
  - Region (North/South/East/West/Northeast/Central)
- **Data Quality**: ✅ HIGH - Official government source
- **Note**: State-level data NOT available via World Bank API

#### **Dataset 5: City Reference Data**
- **File**: `data/geo/india_city_reference.csv`
- **Records**: 55 cities
- **Fields**:
  - City name
  - Coordinates (lat/lon)
  - Cost of Living Index
  - Industry hubs
- **Purpose**: Geo-spatial career advice
- **Source**: Curated (no free API for Indian city COL data)

#### **Dataset 6: GDP Growth**
- **Source**: World Bank API (NY.GDP.MKTP.KD.ZG)
- **Live**: Yes (fetched on-demand)
- **Fields**: Year, GDP Growth Rate (%)
- **Purpose**: Economic context, Phillips Curve analysis

### 1.2 Synthetic/Generated Data

#### **Job Risk Model Training Data**
- **Source**: SYNTHETIC (generated in `src/job_risk_model.py`)
- **Records**: 3,500 synthetic samples
- **Features**: 5 features
  - Skills (encoded)
  - Education level
  - Experience years
  - Location
  - Industry
- **Target**: Binary risk classification (High/Low)
- **Purpose**: Train logistic regression model
- **⚠️ CRITICAL ISSUE**: Using synthetic data for ML model - not real-world validated

#### **Peer Benchmark Data**
- **Source**: SYNTHETIC (generated in `src/analytics/benchmark_engine.py`)
- **Records**: 100 synthetic peer profiles per user
- **Purpose**: Peer comparison for job risk assessment
- **Method**: Gaussian distribution around user profile
- **⚠️ LIMITATION**: Not based on real labor market data

---

## 🔌 SECTION 2: DATA SOURCES & APIs

### 2.1 Live APIs Used

#### **World Bank Open Data API**
- **URL**: `https://api.worldbank.org/v2/`
- **Reliability**: ✅ HIGH - Authoritative, free, no API key required
- **Indicators Used**:
  - `SL.UEM.TOTL.ZS` - Unemployment rate (%)
  - `FP.CPI.TOTL.ZG` - CPI inflation (%)
  - `NY.GDP.MKTP.KD.ZG` - GDP growth (%)
  - `SL.AGR.EMPL.ZS` - Agriculture employment share
  - `SL.IND.EMPL.ZS` - Industry employment share
  - `SL.SRV.EMPL.ZS` - Services employment share
  - `NV.AGR.TOTL.ZS` - Agriculture GDP share
  - `NV.IND.TOTL.ZS` - Industry GDP share
  - `NV.SRV.TOTL.ZS` - Services GDP share
  - `SL.UEM.1524.ZS` - Youth unemployment
  - `SL.UEM.TOTL.FE.ZS` - Female unemployment
  - `SL.TLF.CACT.ZS` - Labor force participation
- **Caching**: 24-hour TTL (Time To Live)
- **Fallback**: Local CSV if API unavailable
- **⚠️ DATA QUALITY ISSUE**: World Bank unemployment data for India shows questionable trends post-2019
  - COVID impact appears understated
  - 2022-2025 rates seem unrealistically low
  - **Solution**: Project now prioritizes curated realistic data

#### **Adzuna Job Search API**
- **URL**: `https://api.adzuna.com/v1/api/jobs`
- **Purpose**: Live job market data for career path modeling
- **Credentials**: 
  - APP_ID: `4a3a122e`
  - APP_KEY: `82c616e066d400fd33c5ad78aeb2f6f3`
- **Free Tier**: 250 calls/month
- **Coverage**: Global (India included)
- **Data Retrieved**:
  - Total job count
  - Average salary
  - Top skills in demand
  - Top companies hiring
  - Remote work percentage
- **Reliability**: ✅ GOOD - Commercial API, reliable
- **Implementation**: `src/data_providers/adzuna_client.py`
- **Caching**: 24-hour TTL
- **Test Results**: ✅ Working - Found 29,818 software engineer jobs

#### **Groq LLaMA 3.1 API** (AI Insights)
- **Purpose**: Generate economic narratives
- **Reliability**: ✅ HIGH - Fast, free LLM
- **Fallback Chain**: Groq → Gemini → OpenAI → Rule-based
- **Optional**: App works without API key

### 2.2 Data Source Reliability Assessment

| Source | Reliability | Coverage | Freshness | Issues |
|--------|-------------|----------|-----------|--------|
| **World Bank API** | ⭐⭐⭐⭐ (4/5) | Global | Annual | ⚠️ India data quality concerns post-2019 |
| **PLFS (MOSPI)** | ⭐⭐⭐⭐⭐ (5/5) | India only | Annual | ✅ Official government source |
| **CMIE** | ⭐⭐⭐⭐⭐ (5/5) | India | Monthly | ✅ Authoritative, but 23.5% was monthly peak |
| **RBI CPI Data** | ⭐⭐⭐⭐⭐ (5/5) | India | Monthly | ✅ Official central bank data |
| **Adzuna API** | ⭐⭐⭐⭐ (4/5) | Global | Real-time | ✅ Commercial, reliable |
| **Naukri.com CSV** | ⭐⭐⭐ (3/5) | India | 2019 only | ⚠️ Outdated (5+ years old) |
| **Synthetic Data** | ⭐⭐ (2/5) | N/A | N/A | ❌ Not validated against real data |

### 2.3 Missing or Suspicious Sources

#### **❌ Missing Sources:**
1. **Real-time unemployment data** - No API provides daily/weekly unemployment
2. **Skill-specific unemployment** - No breakdown by skill category
3. **Company-level hiring data** - Limited to job postings
4. **Wage distribution data** - Only averages available
5. **Informal sector data** - India's 80%+ informal sector not captured

#### **⚠️ Suspicious/Problematic:**
1. **Synthetic ML training data** - Job risk model trained on generated data, not real outcomes
2. **Old job posting data** - 2019 data used for 2024+ analysis
3. **World Bank India data** - Post-2019 trends don't match ground reality
4. **Cost of Living data** - Curated without clear source attribution

---

## 🧮 SECTION 3: CALCULATIONS & LOGIC

### 3.1 Unemployment Calculations

#### **3.1.1 Historical Unemployment**
- **Source**: Direct from datasets (no calculation)
- **Smoothing**: 3-year rolling average for forecasting
  ```python
  df["Unemployment_Smoothed"] = df["Unemployment_Rate"].rolling(3, min_periods=1, center=True).mean()
  ```
- **Purpose**: Reduce noise for trend analysis

#### **3.1.2 Unemployment Forecasting**
**Method**: Ensemble of 3 approaches (weighted)

**A. Trend + Mean Reversion (50% weight)**
```python
# Core formula:
forecast[t] = current_value + (slope * trend_weight) + (reversion_adjustment)

where:
- slope = linear trend from last 10 years
- trend_weight = 1.0 / (1.0 + 0.25 * horizon)  # Decays with time
- reversion_adjustment = mean_reversion_strength * reversion_weight * (long_run_mean - current_value)
- reversion_weight = min(1.0, horizon / 6.0)  # Increases with time
- mean_reversion_strength = 0.15 (default)
- long_run_mean = historical average unemployment
```

**Economic Rationale**:
- Short-term: Trend dominates (momentum)
- Long-term: Mean reversion dominates (markets adjust)
- Prevents runaway forecasts
- Max annual change capped at ±1.5pp

**B. Exponential Smoothing (20% weight)**
```python
# Simple exponential smoothing
smoothed[t] = alpha * actual[t] + (1 - alpha) * smoothed[t-1]
alpha = 0.3

# Forecast:
forecast[t] = last_smoothed + trend * t
trend = (smoothed[-1] - smoothed[-3]) / 3
```

**C. ARIMA-Inspired (30% weight)**
```python
# Simplified ARIMA logic
annual_trend = (series[-1] - series[-5]) / 4  # Per-year trend
forecast[t] = value[t-1] + annual_trend * 0.3 - (value[t-1] - historical_mean) * 0.1 * reversion_factor
```

**Final Ensemble**:
```python
final_forecast = 0.50 * trend_reversion + 0.30 * arima + 0.20 * exp_smoothing
```

**⚠️ CRITICAL ISSUE FOUND**: ARIMA calculation had a bug (fixed in recent update)
- **Old bug**: Used 5-year total trend instead of annual trend
- **Impact**: Overstated trend by ~4x
- **Status**: ✅ FIXED in current version

#### **3.1.3 Confidence Intervals**
**Method**: Monte Carlo simulation (500 runs)

```python
# Historical volatility
hist_std = df["Unemployment_Smoothed"].diff().dropna().std()

# For each simulation:
noise = random.normal(0, hist_std, forecast_horizon)
cumulative_noise = cumsum(noise) * 0.4  # Dampened
simulated_forecast = base_forecast + cumulative_noise

# Percentiles:
Lower_95 = 2.5th percentile
Lower_80 = 10th percentile
Upper_80 = 90th percentile
Upper_95 = 97.5th percentile
```

**Validation**: Confidence bands are realistic, not too wide/narrow

### 3.2 Inflation Calculations

#### **3.2.1 Inflation Data**
- **Source**: World Bank API (FP.CPI.TOTL.ZG) or corrected CSV
- **Calculation**: None - direct from source
- **Unit**: Annual percentage change in CPI

#### **3.2.2 Phillips Curve Analysis**
```python
# Correlation between unemployment and inflation
correlation = df["Unemployment"].corr(df["Inflation"])

# Linear regression
slope, intercept, r_value, p_value, std_err = linregress(df["UE"], df["Inflation"])

# R-squared
r_squared = r_value ** 2
```

**Expected for India**: Weak negative correlation (-0.15 to -0.25)
**Reason**: Large informal sector, supply-side shocks dominate

### 3.3 Shock Scenario Calculations

#### **3.3.1 Shock Model**
```python
# Immediate impact (year 0)
shock_impact = shock_intensity  # e.g., +3.0pp

# Decay over time
for year in range(1, shock_duration + recovery_years):
    if year <= shock_duration:
        # Full shock persists
        impact[year] = shock_intensity
    else:
        # Exponential decay
        years_since_shock_end = year - shock_duration
        impact[year] = shock_intensity * exp(-recovery_rate * years_since_shock_end)

# Final unemployment
scenario_unemployment[year] = baseline[year] + impact[year]
```

**Parameters**:
- `shock_intensity`: Immediate unemployment increase (pp)
- `shock_duration`: Years shock persists at full strength
- `recovery_rate`: Speed of exponential decay (0-1)

**Economic Rationale**: Shocks hit immediately, recovery is gradual

#### **3.3.2 Policy Interventions**
```python
# Policy cushion effect
policy_cushion = policy_effectiveness * policy_budget_multiplier

# Reduces shock impact
adjusted_shock = shock_intensity * (1 - policy_cushion)
```

**Policy Types**:
- Fiscal stimulus
- Training programs
- Unemployment benefits
- Infrastructure spending

**Effectiveness**: 0-40% shock reduction (configurable)

### 3.4 Job Risk Model Calculations

#### **3.4.1 Risk Score (Logistic Regression)**
```python
# Features (5):
X = [skills_encoded, education_level, experience_years, location_encoded, industry_encoded]

# Model: Logistic Regression
P(high_risk) = 1 / (1 + exp(-(β0 + β1*X1 + β2*X2 + ... + β5*X5)))

# Risk level classification:
if P(high_risk) > 0.65: "High"
elif P(high_risk) > 0.35: "Medium"
else: "Low"
```

**⚠️ CRITICAL ISSUE**: Model trained on 3,500 SYNTHETIC samples
- Not validated against real job displacement data
- Coefficients may not reflect reality
- **Recommendation**: Needs real-world validation

#### **3.4.2 Multi-Risk Assessment** (Enhanced Feature)
**A. Automation Risk**
```python
# Base automation risk by industry
base_risk = INDUSTRY_AUTOMATION_RISK[industry]  # 0-100

# Skill protection factor
skill_protection = sum(SKILL_WEIGHTS[skill] for skill in user_skills) / len(user_skills)

# Experience dampening
exp_factor = min(1.0, experience_years / 15)

# Final automation risk
automation_risk = base_risk * (1 - skill_protection * 0.4) * (1 - exp_factor * 0.2)
```

**B. Recession Risk**
```python
# Industry cyclicality
cyclical_factor = INDUSTRY_CYCLICALITY[industry]  # 0-1

# Role vulnerability
role_factor = ROLE_VULNERABILITY[role_level]  # 0-1

# Company size buffer
size_buffer = COMPANY_SIZE_BUFFER[company_size]  # 0-0.3

# Recession risk
recession_risk = (cyclical_factor * 0.6 + role_factor * 0.4) * 100 * (1 - size_buffer)
```

**C. Age Discrimination Risk**
```python
# Age curve (peaks at 50-55)
if age < 40:
    age_risk = 0
elif age < 50:
    age_risk = (age - 40) * 2  # Linear increase
elif age < 60:
    age_risk = 20 + (age - 50) * 3  # Steeper increase
else:
    age_risk = 50 + (age - 60) * 0.5  # Plateau

# Industry adjustment
age_risk *= INDUSTRY_AGE_SENSITIVITY[industry]

# Performance protection
if performance_rating >= 4:
    age_risk *= 0.7
```

**D. Overall Risk (Orchestrator)**
```python
# Weighted combination
overall_risk = (
    automation_risk * 0.35 +
    recession_risk * 0.30 +
    age_risk * 0.20 +
    base_job_risk * 0.15
)
```

### 3.5 Salary Calculations

#### **3.5.1 Base Salary Estimation**
```python
# Industry base salaries (USD)
BASE_SALARIES = {
    "Technology / software": 65000,
    "Financial services / fintech": 70000,
    "Healthcare / biotech": 60000,
    # ... etc
}

# Role level multipliers
ROLE_MULTIPLIERS = {
    "Entry": 1.0,
    "Mid": 1.4,
    "Senior": 1.9,
    "Lead": 2.5,
    "Executive": 3.5
}

# Experience bonus
exp_bonus = min(experience_years * 0.03, 0.30)  # Max 30%

# Base salary
base_salary = BASE_SALARIES[industry] * ROLE_MULTIPLIERS[role] * (1 + exp_bonus)
```

#### **3.5.2 Location Adjustment**
```python
LOCATION_MULTIPLIERS = {
    "Metro / Tier-1 city": 1.50,
    "Tier-2 city": 1.20,
    "Tier-3 city": 1.00,
    "Rural area": 0.85
}

location_adjusted = base_salary * LOCATION_MULTIPLIERS[location]
```

#### **3.5.3 Risk Penalty**
```python
# Risk penalty (0-30%)
risk_penalty_pct = (overall_risk / 100) * 0.30

# Risk-adjusted salary
risk_adjusted = location_adjusted * (1 - risk_penalty_pct)
```

#### **3.5.4 Confidence Interval**
```python
# ±15% confidence band
lower_bound = risk_adjusted * 0.85
upper_bound = risk_adjusted * 1.15
```

### 3.6 Derived Metrics

#### **3.6.1 Unemployment Stress Index (USI)**
```python
# Measures cumulative unemployment burden
USI = sum((scenario_unemployment[t] - baseline[t]) for t in forecast_horizon)

# Interpretation:
if USI > 40: "Severe stress"
elif USI > 20: "High stress"
elif USI > 10: "Moderate stress"
else: "Low stress"
```

#### **3.6.2 Recovery Quality Index (RQI)**
```python
# Measures how well economy recovers
peak_unemployment = max(scenario_unemployment)
end_unemployment = scenario_unemployment[-1]
baseline_end = baseline[-1]

recovery_pct = (peak_unemployment - end_unemployment) / (peak_unemployment - baseline_end)

if recovery_pct > 0.80: "Strong recovery"
elif recovery_pct > 0.60: "Moderate recovery"
elif recovery_pct > 0.40: "Weak recovery"
else: "Poor recovery"
```

#### **3.6.3 Policy Cushion Score**
```python
# Effectiveness of policy intervention
no_policy_peak = max(scenario_without_policy)
with_policy_peak = max(scenario_with_policy)

cushion_score = (no_policy_peak - with_policy_peak) / no_policy_peak * 100

# Interpretation: % of shock absorbed by policy
```

---

*[Continued in PART 2...]*
