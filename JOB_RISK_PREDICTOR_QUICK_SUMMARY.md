# Job Risk Predictor - Quick Summary

**What does it do?** Predicts unemployment risk based on your profile.

---

## 📊 DATA SOURCES

### Primary: 29,000+ Job Postings
- **File**: `data/market_pulse/job_postings_sample.csv`
- **Source**: Adzuna API (Indian job market)
- **Content**: Job titles, descriptions, salaries, locations, sectors

### How It's Used:
1. **Training Data**: Creates "silver labels" (proxy risk scores)
   - Low salary = High risk label
   - High salary = Low risk label
   - Generic role = High risk label

2. **Skill Scoring**: Extracts 80+ skills with demand weights
   - Machine Learning: 0.98 (very high demand)
   - Python: 0.88 (high demand)
   - Excel: 0.40 (low demand)

3. **Salary Benchmarks**: Calculates industry/role baselines

4. **Career Paths**: Analyzes job requirements and progressions

---

## 🧠 THE MODEL

**Algorithm**: Logistic Regression (sklearn)

**5 Input Features:**
1. **Skill Demand Score** (0-1) - How in-demand are your skills?
2. **Industry Growth** (0-1) - Is your sector growing?
3. **Experience Years** (0-40) - How much experience?
4. **Education Level** (0-4) - What's your education?
5. **Location Tier** (0-2) - Metro vs rural?

**Output**: Risk probability (0-100%)

**Risk Levels:**
- Low: < 18%
- Medium: 18-30%
- High: > 30%

---

## 🎯 WHAT IT SHOWS (11 Components)

### 1. Basic Risk Score
- Risk level (Low/Medium/High)
- Probability percentage
- Color-coded gauge

**Data**: Logistic regression prediction

---

### 2. Multi-Risk Dashboard (4 Gauges)
- **Overall Risk**: Composite score
- **Automation Risk**: AI/robot replacement risk
- **Recession Risk**: Economic downturn vulnerability
- **Age Discrimination**: Age-related bias risk

**Data**: `RiskCalculatorOrchestrator` calculations

---

### 3. Risk Projections Over Time
- 1 year, 3 years, 5 years
- With/without continuous learning
- Line chart showing trajectory

**Data**: `TimePredictionCalculator` using age progression + skill obsolescence

---

### 4. Salary Impact Analysis
- Base salary (industry baseline)
- Location adjusted (city multiplier)
- Risk adjusted (penalty for high risk)
- Confidence range

**Data**: `SalaryAnalyzer` using job posting salaries

---

### 5. Peer Comparison
- Your percentile (0-100th)
- Distribution histogram
- "Better than X% of peers"

**Data**: `BenchmarkEngine` generates 100 synthetic peers

---

### 6. Actionable Recommendations
- Top 3-5 actions ranked by ROI
- Risk reduction estimate
- Salary impact estimate
- Time to implement

**Data**: `RecommendationEngine` analyzes skill gaps + trends

---

### 7. AI-Powered Career Paths
- 3-5 career path options
- Required skills per path
- Timeline and salary projection
- Action plan with milestones

**Data**: `CareerPathModeler` using **live Adzuna API** (if available) or historical data

---

### 8. Risk Monitoring Dashboard
- Historical trends (line chart)
- Rate of change (points/month)
- Significant changes detection

**Data**: `RiskMonitor` stores all previous assessments

---

### 9. Feature Contributions
- 5 feature values
- Matched high-demand keywords
- Top 4 reasons for score
- Improvement suggestions

**Data**: Linear contribution analysis (log-odds)

---

### 10. What-If Skill Simulation
- Add hypothetical skills
- Compare before/after
- Contribution shift chart

**Data**: Re-runs model with modified skills

---

### 11. Export Report
- Comprehensive .txt report
- All metrics and recommendations
- Profile summary

**Data**: Aggregates all above components

---

## 📈 SKILL DEMAND LEXICON

**80+ Skills with Weights (Examples):**

| Skill | Weight | Category |
|-------|--------|----------|
| Machine Learning | 0.98 | AI/ML |
| Deep Learning | 0.97 | AI/ML |
| Cloud Computing | 0.94 | Cloud |
| AWS | 0.92 | Cloud |
| Python | 0.88 | Programming |
| SQL | 0.85 | Data |
| React | 0.84 | Web Dev |
| Product Management | 0.72 | Business |
| Excel | 0.40 | Office |
| Data Entry | 0.42 | Low-skill |
| COBOL | 0.25 | Outdated |

**How It Works:**
1. Parse user skills (comma-separated)
2. Match against lexicon (longest phrases first)
3. Average matched weights
4. Return score 0-1

---

## 🏭 INDUSTRY GROWTH INDICES

| Industry | Growth Score |
|----------|--------------|
| Technology / software | 0.92 |
| Healthcare / biotech | 0.88 |
| Renewable energy | 0.86 |
| Financial services | 0.82 |
| Education / edtech | 0.72 |
| Retail / e-commerce | 0.62 |
| Manufacturing | 0.55 |
| Hospitality / tourism | 0.48 |

---

## 📍 LOCATION TIERS

| Location | Risk Tier | Cities |
|----------|-----------|--------|
| Metro / Tier-1 | 0.0 (lowest) | Bangalore, Mumbai, Delhi, Hyderabad, Chennai |
| Tier-2 city | 1.0 (medium) | Pune, Jaipur, Ahmedabad |
| Smaller town / rural | 2.0 (highest) | Limited job market |

---

## ⚠️ DATA QUALITY WARNING

**IMPORTANT**: This is an **EXPERIMENTAL MODEL**

❌ **NOT trained on actual unemployment outcomes**  
❌ **NOT validated with real-world data**  
❌ **Uses "silver labels" (proxy labels from salary data)**  

✅ **Good for**: Education, exploration, skill gap analysis  
❌ **Not for**: Critical decisions, HR/legal use, financial planning  

**Confidence Level**: LOW  
**Recommended Use**: Educational/exploratory only

---

## 🔄 DATA FLOW DIAGRAM

```
USER PROFILE
    ↓
┌─────────────────────────────────────┐
│ INPUT VALIDATION                    │
│ - Age 18-80                         │
│ - Experience ≤ (age - 16)           │
│ - Performance 1-5                   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ FEATURE ENGINEERING                 │
│ 1. Skill Demand Score (lexicon)    │
│ 2. Industry Growth (lookup)        │
│ 3. Experience Years (normalize)    │
│ 4. Education Level (0-4)           │
│ 5. Location Tier (0-2)             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ LOGISTIC REGRESSION MODEL           │
│ - Trained on 29K job postings      │
│ - Silver-labeled data               │
│ - StandardScaler + LogReg           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ RISK PROBABILITY (0-100%)           │
│ - Low: < 18%                        │
│ - Medium: 18-30%                    │
│ - High: > 30%                       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ PARALLEL CALCULATIONS               │
│ ├─ Multi-Risk (4 dimensions)       │
│ ├─ Time Predictions (3 horizons)   │
│ ├─ Salary Analysis (3 adjustments) │
│ ├─ Peer Benchmark (100 peers)      │
│ ├─ Recommendations (ROI-ranked)    │
│ ├─ Career Paths (live API)         │
│ └─ Feature Contributions           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ STORE IN RISK MONITOR               │
│ - Assessment history                │
│ - Trend tracking                    │
│ - Change detection                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ DISPLAY RESULTS                     │
│ - 11 UI components                  │
│ - Interactive charts                │
│ - Export report                     │
└─────────────────────────────────────┘
```

---

## 📊 EXAMPLE CALCULATION

### Input Profile
```
Skills: "Python, SQL, machine learning, AWS"
Education: Bachelor's degree (2)
Experience: 5 years
Industry: Technology / software (0.92)
Location: Metro / Tier-1 (0.0)
```

### Feature Engineering
```
1. Skill Demand Score:
   - Python (0.88) + SQL (0.85) + ML (0.98) + AWS (0.92)
   - Average: 0.91

2. Industry Growth: 0.92 (Technology)

3. Experience: 5.0 years

4. Education: 2.0 (Bachelor's)

5. Location Tier: 0.0 (Metro)
```

### Model Prediction
```
Feature Vector: [0.91, 0.92, 5.0, 2.0, 0.0]
    ↓
StandardScaler normalization
    ↓
Logistic Regression
    ↓
Risk Probability: 18.3%
Risk Level: Medium (just above Low threshold)
```

### Why This Score?
```
✅ Strong skills (0.91) - REDUCES risk
✅ High-growth industry (0.92) - REDUCES risk
✅ Good experience (5 years) - REDUCES risk
✅ Metro location (0.0) - REDUCES risk
⚠️ Bachelor's only (2.0) - NEUTRAL

Result: Low-Medium risk (18.3%)
```

---

## 🎯 KEY TAKEAWAYS

### What Powers the Predictor

1. **29,000+ job postings** (primary data source)
2. **80+ skill lexicon** (manual weights)
3. **9 industry indices** (growth scores)
4. **3 location tiers** (risk levels)
5. **Logistic regression** (sklearn model)
6. **Live Adzuna API** (career paths)

### What It Calculates

1. ✅ Risk probability (0-100%)
2. ✅ 4 risk dimensions
3. ✅ 3 time horizons
4. ✅ Salary estimates
5. ✅ Peer comparison
6. ✅ Recommendations
7. ✅ Career paths
8. ✅ Historical trends

### What It's Good For

✅ Understanding risk factors  
✅ Identifying skill gaps  
✅ Career planning guidance  
✅ Comparative analysis  
✅ Educational exploration  

### What It's NOT

❌ Not validated with real data  
❌ Not for critical decisions  
❌ Not for HR/legal use  
❌ Not for financial planning  
❌ Not for academic research  

---

**Status**: EXPERIMENTAL - Educational Use Only  
**Version**: 2.1.0  
**Last Updated**: April 13, 2026
