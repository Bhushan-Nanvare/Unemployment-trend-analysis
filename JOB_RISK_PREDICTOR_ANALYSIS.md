# Job Risk Predictor - Complete Analysis

**Date**: April 13, 2026  
**Page**: `pages/7_Job_Risk_Predictor.py`  
**Model**: `src/job_risk_model.py`  
**Version**: 2.1.0

---

## 🎯 WHAT IS THE JOB RISK PREDICTOR?

The Job Risk Predictor is an **AI-powered unemployment risk assessment tool** that estimates the probability of job displacement based on user profile characteristics.

### Core Purpose
- Predict unemployment risk probability (0-100%)
- Classify risk level (Low/Medium/High)
- Provide multi-dimensional risk analysis
- Generate personalized recommendations
- Track risk changes over time

---

## 📊 DATA SOURCES & TRAINING

### ⚠️ IMPORTANT: DATA QUALITY STATUS

**Training Data**: **SYNTHETIC** (Silver-labeled from job postings)  
**Validation**: **NOT PERFORMED**  
**Confidence Level**: **EXPERIMENTAL**  
**Recommended Use**: Educational/exploratory purposes only

### Training Data Source

The model is trained on **29,000+ real job postings** from:
- **File**: `data/market_pulse/job_postings_sample.csv`
- **Source**: Adzuna API job market data
- **Coverage**: Indian job market (multiple cities and sectors)

### Silver Labeling Process

Since the job postings don't contain actual unemployment outcomes, the system creates **"silver labels"** (proxy labels) based on market signals:

```python
# Risk Label (y):
# - 1 (High Risk) if:
#   * Salary is in bottom 30th percentile for the role
#   * OR role is 'Other/General'
# - 0 (Low Risk) if:
#   * Salary is above median
#   * OR in high-growth sector
```

### Training Features (5 Features)

1. **Skill Demand Score** (0-1)
   - Computed from 80+ skill keywords
   - Weighted by market demand
   - Examples: ML (0.98), Python (0.88), Excel (0.55)

2. **Industry Growth** (0-1)
   - Pre-defined growth indices per sector
   - Technology: 0.92, Healthcare: 0.88, Hospitality: 0.48

3. **Experience Years** (0-40)
   - Direct user input
   - Normalized to 0-40 range

4. **Education Level** (0-4)
   - 0 = Less than high school
   - 1 = High school
   - 2 = Bachelor's
   - 3 = Master's
   - 4 = Doctorate

5. **Location Risk Tier** (0-2)
   - 0 = Metro/Tier-1 (Bangalore, Mumbai, Delhi)
   - 1 = Tier-2 city
   - 2 = Rural/smaller town

---

## 🧠 MODEL ARCHITECTURE

### Algorithm
**Logistic Regression** with StandardScaler preprocessing

```python
Pipeline([
    ("scale", StandardScaler()),
    ("clf", LogisticRegression(
        max_iter=500,
        class_weight="balanced",
        random_state=42
    ))
])
```

### Model Coefficients (Version 2.1.0)

The model learns these relationships:

- **Experience**: **Strong negative** coefficient (~-2.5)
  - More experience → Lower risk
  - Most important factor

- **Skill Demand**: **Strong negative** coefficient (~-3.5)
  - Better skills → Lower risk
  - Second most important

- **Industry Growth**: **Negative** coefficient (~-2.5)
  - Growing industry → Lower risk

- **Education**: **Negative** coefficient (~-1.5)
  - Higher education → Lower risk

- **Location Tier**: **Positive** coefficient (~+1.2)
  - Rural location → Higher risk

### Risk Thresholds

```python
if probability >= 0.30:  # High Risk
if probability >= 0.18:  # Medium Risk
else:                    # Low Risk
```

---

## 🔧 WHAT THE PREDICTOR SHOWS

### 1. **Basic Risk Assessment**

**Inputs:**
- Skills (comma-separated text)
- Education level (dropdown)
- Years of experience (slider 0-40)
- Industry/sector (dropdown)
- Location (dropdown)

**Enhanced Inputs:**
- Age (18-80)
- Role level (Entry/Mid/Senior/Lead/Executive)
- Company size (1-10 to 5000+)
- Remote work capability (checkbox)
- Performance rating (1-5)

**Outputs:**
- Risk level (High/Medium/Low)
- High-risk probability percentage
- Color-coded gauge chart

### 2. **Multi-Risk Dashboard** (4 Gauges)

Displays 4 different risk dimensions:

#### a) **Overall Risk** (0-100%)
- Composite risk score
- Combines all factors
- Primary risk indicator

#### b) **Automation Risk** (0-100%)
- Risk of job automation by AI/robots
- Based on role type and skills
- Higher for routine tasks

#### c) **Recession Risk** (0-100%)
- Vulnerability during economic downturns
- Based on industry and role stability
- Higher for non-essential sectors

#### d) **Age Discrimination Risk** (0-100%)
- Risk related to age bias
- Increases with age (especially 45+)
- Varies by industry culture

**Data Source**: Calculated by `RiskCalculatorOrchestrator` using:
- User profile characteristics
- Industry-specific factors
- Role-level analysis
- Market conditions

### 3. **Risk Projections Over Time**

Shows how risk changes over 3 time horizons:
- **1 Year**
- **3 Years**
- **5 Years**

**Two Scenarios:**
- **Without skill development**: Risk increases over time
- **With continuous learning**: Risk decreases or stabilizes

**Data Source**: `TimePredictionCalculator` using:
- Current risk profile
- Age progression
- Industry trends
- Skill obsolescence rates

### 4. **Salary Impact Analysis**

**Displays:**
- **Base Salary**: Industry/role baseline
- **Location Adjusted**: Multiplier for city tier
- **Risk Adjusted**: Penalty for high risk
- **Confidence Range**: Min-max estimate

**Data Source**: `SalaryAnalyzer` using:
- Job posting salary data (29K+ postings)
- Location multipliers (Tier-1: 1.2x, Tier-2: 1.0x, Rural: 0.8x)
- Risk penalty calculation (up to -20% for high risk)

### 5. **Peer Comparison**

**Shows:**
- Your risk percentile (0-100th)
- Distribution histogram of 100 synthetic peers
- Percentile markers (25th, 50th, 75th, 90th)
- Comparison text ("better than X% of peers")

**Data Source**: `BenchmarkEngine` generates:
- 100 synthetic peer profiles
- Same industry and role level
- Varied skills and experience
- Risk distribution analysis

### 6. **Actionable Recommendations**

**Displays:**
- Top 3-5 recommendations ranked by ROI
- Priority level (High/Medium/Low)
- Risk reduction estimate (%)
- Salary impact estimate ($)
- Time to implement
- Detailed explanation

**Data Source**: `RecommendationEngine` analyzes:
- Current risk profile
- Skill gaps
- Industry trends
- Salary potential
- ROI calculation

**Example Recommendations:**
- "Learn cloud computing (AWS/Azure)" - High priority
- "Obtain industry certification" - Medium priority
- "Develop leadership skills" - Low priority

### 7. **AI-Powered Career Path Recommendations**

**Shows:**
- 3-5 career path options
- Each path includes:
  - Target role
  - Required skills
  - Timeline (months)
  - Salary projection
  - Risk reduction potential
  - Action plan with milestones

**Data Source**: `CareerPathModeler` using:
- **Live Adzuna API data** (if available)
- Job posting analysis
- Skill demand trends
- Career progression patterns
- Historical data fallback

**API Connection Status:**
- ✅ Green: "Live market data connected"
- ℹ️ Blue: "Using historical data (API unavailable)"

### 8. **Risk Monitoring Dashboard**

**Shows:**
- Historical risk trends (line chart)
- Rate of change analysis (points/month)
- Significant changes detection (>10 point jumps)
- Assessment history timeline

**Data Source**: `RiskMonitor` stores:
- All previous assessments
- Timestamps
- Risk scores (all 4 dimensions)
- User profile snapshots

**Requires**: At least 2 assessments to show trends

### 9. **Feature Contributions**

**Displays:**
- 5 engineered feature values
- Matched high-demand keywords
- Reasons for the score (top 4 factors)
- Suggestions for improvement

**Data Source**: Linear contribution analysis
- Compares user features to training data means
- Calculates log-odds contribution per feature
- Ranks by absolute impact

### 10. **What-If Skill Simulation**

**Allows:**
- Add hypothetical skills
- Re-run risk calculation
- Compare before/after
- Show contribution shifts

**Displays:**
- Before risk %
- After risk %
- Change (delta)
- Bar chart of contribution shifts

---

## 📈 SKILL DEMAND SCORING

### How Skills Are Scored

The system maintains a **lexicon of 80+ skills** with demand weights:

#### High-Demand Skills (0.90-1.0)
```python
"machine learning": 0.98
"deep learning": 0.97
"data science": 0.96
"artificial intelligence": 0.95
"cloud computing": 0.94
"kubernetes": 0.93
"aws": 0.92
"cybersecurity": 0.93
```

#### Strong Programming Skills (0.75-0.89)
```python
"python": 0.88
"sql": 0.85
"react": 0.84
"javascript": 0.82
"java": 0.81
```

#### Moderate Skills (0.60-0.74)
```python
"product management": 0.72
"project management": 0.70
"agile": 0.68
"communication": 0.65
```

#### Low-Demand Skills (0.25-0.44)
```python
"data entry": 0.42
"excel": 0.40  # Note: Basic Excel, not advanced
"jquery": 0.35
"cobol": 0.25
```

### Skill Matching Process

1. **Parse**: Split user input by commas/semicolons
2. **Normalize**: Convert to lowercase
3. **Match**: Check against lexicon (longest phrases first)
4. **Score**: Average of matched weights
5. **Fallback**: Generic score for unrecognized skills

---

## 🏭 INDUSTRY GROWTH INDICES

Pre-defined growth scores per sector:

```python
"Technology / software": 0.92        # Highest growth
"Healthcare / biotech": 0.88
"Renewable energy / climate": 0.86
"Financial services / fintech": 0.82
"Education / edtech": 0.72
"Retail / e-commerce ops": 0.62
"Manufacturing (traditional)": 0.55
"Hospitality / tourism": 0.48       # Lowest growth
"Other / not listed": 0.60
```

---

## 📍 LOCATION RISK TIERS

```python
"Metro / Tier-1 city": 0.0          # Lowest risk
  - Bangalore, Mumbai, Delhi, Hyderabad, Chennai

"Tier-2 city": 1.0                  # Medium risk
  - Pune, Jaipur, Ahmedabad, etc.

"Smaller town / rural": 2.0         # Highest risk
  - Limited job market access
```

---

## 🔍 VALIDATION & QUALITY CHECKS

### Input Validation (ProfileValidator)

**Age Validation:**
- Must be 18-80
- Error if outside range

**Experience Validation:**
- Must be 0-40 years
- Cannot exceed (age - 16)
- Error if impossible

**Performance Rating:**
- Must be 1-5
- Error if outside range

**Required Fields:**
- Skills (at least 1)
- Industry (must be selected)
- Role level (must be selected)

---

## 📊 COMPLETE DATA FLOW

```
USER INPUT
    ↓
[Profile Validation]
    ↓
[Feature Engineering]
    ↓
[Logistic Regression Model]
    ↓
[Risk Probability (0-1)]
    ↓
[Risk Level Classification]
    ↓
┌─────────────────────────────────────┐
│ PARALLEL CALCULATIONS:              │
│ 1. Multi-Risk Dashboard             │
│ 2. Time Predictions                 │
│ 3. Salary Analysis                  │
│ 4. Peer Benchmark                   │
│ 5. Recommendations                  │
│ 6. Career Paths                     │
│ 7. Feature Contributions            │
└─────────────────────────────────────┘
    ↓
[Store in Risk Monitor]
    ↓
[Display Results + Charts]
```

---

## 🎨 UI COMPONENTS

### Gauges (4x)
- Overall Risk
- Automation Risk
- Recession Risk
- Age Discrimination Risk

**Color Coding:**
- 0-35%: Green (Low risk)
- 35-62%: Yellow (Medium risk)
- 62-100%: Red (High risk)

### Line Charts (2x)
- Risk projections over time
- Historical risk trends

### Bar Charts (2x)
- What-if contribution shifts
- Career path market comparison

### Histogram (1x)
- Peer risk distribution

### Metrics (Multiple)
- Risk percentages
- Salary estimates
- Rate of change
- Recommendation impacts

---

## 📥 EXPORT FUNCTIONALITY

**Comprehensive Risk Report (.txt)**

Includes:
- Profile summary
- Multi-dimensional risk scores
- Risk projections
- Salary analysis
- Peer comparison
- Top recommendations
- Feature values
- Reasons and suggestions

---

## ⚠️ LIMITATIONS & DISCLAIMERS

### Model Limitations

1. **Synthetic Training Data**
   - Not trained on actual unemployment outcomes
   - Silver labels are proxies, not ground truth
   - Experimental confidence level

2. **No External Validation**
   - Model has not been validated against real-world data
   - Predictions are based on market signals only
   - Should not be used for critical decisions

3. **Simplified Features**
   - Only 5 features (real-world is more complex)
   - Missing factors: company health, personal network, etc.
   - Industry growth is static (doesn't update)

4. **Skill Lexicon Limitations**
   - 80+ skills (not comprehensive)
   - Weights are manually assigned
   - May miss emerging skills
   - No context understanding (e.g., "Python" for data vs. web)

5. **Geographic Limitations**
   - Focused on Indian job market
   - Simple tier system (3 levels)
   - Doesn't account for city-specific factors

### Appropriate Use Cases

✅ **Good for:**
- Educational exploration
- Understanding risk factors
- Identifying skill gaps
- Career planning guidance
- Comparative analysis

❌ **Not suitable for:**
- Critical career decisions
- Legal/HR decisions
- Insurance underwriting
- Financial planning
- Academic research (without validation)

---

## 🔧 TECHNICAL DETAILS

### Dependencies

**Core:**
- `sklearn` - Logistic Regression, StandardScaler
- `numpy` - Numerical operations
- `pandas` - Data handling

**UI:**
- `streamlit` - Web interface
- `plotly` - Interactive charts

**Custom Modules:**
- `src.risk_calculators` - Multi-risk calculation
- `src.analytics` - Salary, benchmark, recommendations
- `src.validation` - Input validation
- `src.reporting` - Risk monitoring
- `src.ui_components` - Career path visualizer

### Model Training

**Happens at module load:**
```python
_PIPE = None  # Lazy loading

def get_pipeline():
    global _PIPE
    if _PIPE is None:
        _PIPE = _train_pipeline()  # Trains on first call
    return _PIPE
```

**Training time**: ~1-2 seconds (29K samples)

### Caching

**Streamlit session state:**
- Last risk result
- Risk profile
- Time predictions
- Salary estimate
- Benchmark result
- Recommendations
- Career paths
- User inputs

**Persistent storage:**
- Risk monitor history (JSON file)
- Career data cache (Adzuna API responses)

---

## 📊 EXAMPLE OUTPUT

### Sample Profile
```
Skills: Python, SQL, machine learning, AWS
Education: Bachelor's degree
Experience: 5 years
Industry: Technology / software
Location: Metro / Tier-1 city
Age: 30
Role Level: Mid
Company Size: 201-1000
Remote Capable: Yes
Performance: 4/5
```

### Sample Results
```
Risk Level: Low
High-Risk Probability: 18.3%

Multi-Risk Dashboard:
- Overall Risk: 18.3%
- Automation Risk: 22.5%
- Recession Risk: 15.8%
- Age Discrimination: 12.1%

Salary Analysis:
- Base: $65,000
- Location Adjusted: $78,000 (1.2x)
- Risk Adjusted: $76,500 (-2%)

Peer Comparison:
- Your Percentile: 23rd
- "You have lower risk than 77% of peers"

Top Recommendation:
- "Learn Kubernetes for container orchestration"
- Priority: High
- Risk Reduction: 3-5%
- Salary Impact: $5,000-$8,000
- Time: 2-3 months
```

---

## 🎯 SUMMARY

### What It Uses

**Primary Data Source:**
- 29,000+ job postings from Adzuna API
- Stored in `data/market_pulse/job_postings_sample.csv`

**Secondary Data:**
- Manual skill demand lexicon (80+ skills)
- Industry growth indices (9 sectors)
- Location tier mapping (3 tiers)
- Synthetic peer generation

**Model:**
- Logistic Regression (sklearn)
- 5 engineered features
- Silver-labeled training data
- Version 2.1.0

**Calculations:**
- Risk probability (0-100%)
- Multi-dimensional risks (4 types)
- Time projections (3 horizons)
- Salary estimates (3 adjustments)
- Peer benchmarking (100 synthetic peers)
- Recommendations (ROI-ranked)
- Career paths (live API + historical)

### What It Shows

1. ✅ Risk level and probability
2. ✅ Multi-risk dashboard (4 gauges)
3. ✅ Risk projections over time
4. ✅ Salary impact analysis
5. ✅ Peer comparison
6. ✅ Actionable recommendations
7. ✅ AI-powered career paths
8. ✅ Risk monitoring trends
9. ✅ Feature contributions
10. ✅ What-if skill simulation
11. ✅ Comprehensive export report

### Data Quality

⚠️ **EXPERIMENTAL MODEL**
- Training: Synthetic silver labels
- Validation: None
- Confidence: Low
- Use: Educational only

---

**Document Complete** | April 13, 2026
