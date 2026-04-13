# 📊 RECESSION RISK CALCULATION - COMPLETE EXPLANATION

**Module:** `src/risk_calculators/recession_risk.py`  
**Purpose:** Calculate how vulnerable a job/person is during economic recessions  
**Output:** Risk score (0-100) with detailed breakdown

---

## 🎯 WHAT IS RECESSION RISK?

Recession risk measures how likely someone is to:
- Lose their job during an economic downturn
- Face salary cuts or reduced hours
- Experience career setbacks

**Higher score = Higher vulnerability during recession**

---

## 📐 THE FORMULA

```
Recession Risk Score = (Base Risk × Company_Multiplier) 
                       - Experience_Protection 
                       - Role_Protection 
                       + Performance_Adjustment 
                       - Remote_Benefit

Final Score = clip(0, 100)
```

---

## 🔢 CALCULATION FACTORS (6 TOTAL)

### 1️⃣ **INDUSTRY VULNERABILITY** (Base Risk)
**Weight:** Primary factor (0-90 points)  
**Logic:** Some industries are hit harder during recessions

| Industry | Vulnerability | Why? |
|----------|--------------|------|
| **Hospitality / Tourism** | 90% | Discretionary spending, first to cut |
| **Retail / E-commerce Ops** | 75% | Consumer spending drops |
| **Manufacturing (Traditional)** | 70% | Production cuts, inventory reduction |
| **Technology / Software** | 50% | Mixed - some essential, some discretionary |
| **Financial Services / Fintech** | 55% | Affected by market volatility |
| **Healthcare / Biotech** | 25% | Essential services, recession-resistant |
| **Education / Edtech** | 40% | Relatively stable, government-backed |
| **Renewable Energy / Climate** | 45% | Growing sector, some government support |
| **Other / Not Listed** | 60% | Default moderate risk |

**Example:**
- Healthcare worker: Base risk = 25 points (low)
- Hospitality worker: Base risk = 90 points (high)

---

### 2️⃣ **COMPANY SIZE** (Multiplier)
**Weight:** ±35% adjustment  
**Logic:** Larger companies have more resources to weather downturns

| Company Size | Multiplier | Effect |
|--------------|-----------|--------|
| **1-10 employees** | 1.35× | +35% risk (startups vulnerable) |
| **11-50 employees** | 1.25× | +25% risk (small companies) |
| **51-200 employees** | 1.10× | +10% risk (mid-size) |
| **201-1000 employees** | 1.00× | Baseline (no adjustment) |
| **1001-5000 employees** | 0.90× | -10% risk (large companies) |
| **5000+ employees** | 0.85× | -15% risk (enterprise, most stable) |

**Example:**
- Base risk: 60 points
- Company size: 1-10 employees (1.35×)
- Adjusted risk: 60 × 1.35 = 81 points

---

### 3️⃣ **EXPERIENCE PROTECTION**
**Weight:** Up to -20 points  
**Logic:** More experienced workers are harder to replace

**Formula:** `min(Experience_Years / 5 × 5, 20)`

| Experience | Protection | Explanation |
|------------|-----------|-------------|
| 0-4 years | 0 points | Entry level, easily replaced |
| 5-9 years | -5 points | Some protection |
| 10-14 years | -10 points | Moderate protection |
| 15-19 years | -15 points | Strong protection |
| 20+ years | -20 points | Maximum protection |

**Example:**
- 12 years experience: -10 points protection
- 25 years experience: -20 points protection (capped)

---

### 4️⃣ **ROLE LEVEL PROTECTION**
**Weight:** Up to -30 points  
**Logic:** Senior roles are more strategic and harder to eliminate

| Role Level | Protection | Why? |
|------------|-----------|------|
| **Entry** | 0 points | First to be cut |
| **Mid** | -10 points | Some strategic value |
| **Senior** | -20 points | Key contributor |
| **Lead** | -25 points | Team leadership |
| **Executive** | -30 points | Strategic decision-maker |

**Example:**
- Entry level: 0 points protection
- Executive: -30 points protection

---

### 5️⃣ **PERFORMANCE RATING**
**Weight:** ±10 points  
**Logic:** High performers are retained, low performers are cut first

**Formula:** `(Performance_Rating - 3) × -5`

| Rating | Adjustment | Explanation |
|--------|-----------|-------------|
| **1 (Poor)** | +10 points | First to be laid off |
| **2 (Below Average)** | +5 points | At risk |
| **3 (Average)** | 0 points | Baseline |
| **4 (Above Average)** | -5 points | Protected |
| **5 (Excellent)** | -10 points | Highly protected |

**Example:**
- Rating 5: -10 points (protected)
- Rating 2: +5 points (at risk)

---

### 6️⃣ **REMOTE CAPABILITY**
**Weight:** -5 points  
**Logic:** Remote workers have access to broader job markets

| Remote Capability | Benefit |
|-------------------|---------|
| **Yes** | -5 points (more flexible) |
| **No** | 0 points (location-dependent) |

---

## 📊 COMPLETE EXAMPLE CALCULATION

### Example 1: High-Risk Profile
```
Profile:
- Industry: Hospitality / Tourism
- Company Size: 1-10 employees
- Experience: 3 years
- Role Level: Entry
- Performance Rating: 3 (Average)
- Remote Capability: No

Calculation:
1. Base Risk (Industry): 90 points
2. Company Multiplier: 90 × 1.35 = 121.5 points
3. Experience Protection: -0 points (< 5 years)
4. Role Protection: -0 points (Entry level)
5. Performance Adjustment: 0 points (Average)
6. Remote Benefit: -0 points (No remote)

Final Score: 121.5 → capped at 100 points
Risk Level: HIGH (>62)
```

### Example 2: Low-Risk Profile
```
Profile:
- Industry: Healthcare / Biotech
- Company Size: 5000+ employees
- Experience: 15 years
- Role Level: Senior
- Performance Rating: 5 (Excellent)
- Remote Capability: Yes

Calculation:
1. Base Risk (Industry): 25 points
2. Company Multiplier: 25 × 0.85 = 21.25 points
3. Experience Protection: -15 points (15 years)
4. Role Protection: -20 points (Senior)
5. Performance Adjustment: -10 points (Rating 5)
6. Remote Benefit: -5 points (Remote capable)

Final Score: 21.25 - 15 - 20 - 10 - 5 = -28.75 → capped at 0 points
Risk Level: LOW (<35)
```

### Example 3: Medium-Risk Profile
```
Profile:
- Industry: Technology / Software
- Company Size: 201-1000 employees
- Experience: 8 years
- Role Level: Mid
- Performance Rating: 4 (Above Average)
- Remote Capability: Yes

Calculation:
1. Base Risk (Industry): 50 points
2. Company Multiplier: 50 × 1.00 = 50 points
3. Experience Protection: -5 points (5-9 years)
4. Role Protection: -10 points (Mid level)
5. Performance Adjustment: -5 points (Rating 4)
6. Remote Benefit: -5 points (Remote capable)

Final Score: 50 - 5 - 10 - 5 - 5 = 25 points
Risk Level: LOW (but close to MEDIUM at 35)
```

---

## 🎯 RISK LEVEL THRESHOLDS

| Score Range | Risk Level | Meaning |
|-------------|-----------|---------|
| **0-34** | 🟢 LOW | Relatively safe during recession |
| **35-61** | 🟡 MEDIUM | Moderate vulnerability |
| **62-100** | 🔴 HIGH | High risk of job loss |

---

## 💡 RECOMMENDATIONS GENERATED

The system provides personalized recommendations based on risk score:

### For HIGH Risk (≥50 points):

1. **If Experience < 10 years:**
   - "Build experience depth. Each 5 years reduces vulnerability by 5%."

2. **If Small Company (multiplier > 1.15):**
   - "Consider larger, more established companies for greater stability."

3. **If Vulnerable Industry (>65%):**
   - "Explore recession-resistant industries like healthcare or education."

4. **If Entry/Mid Level:**
   - "Aim for senior roles with strategic responsibilities."

5. **If No Remote Capability:**
   - "Develop remote work capabilities for broader job markets."

### For LOW/MEDIUM Risk (<50 points):
- "Your recession vulnerability is relatively low. Maintain your experience and build an emergency fund."

---

## ✅ VALIDATION & QUALITY

### Input Validation
- ✅ All inputs validated before calculation
- ✅ Invalid inputs trigger clear error messages
- ✅ Default values for missing data

### Calculation Properties
- ✅ **Deterministic:** Same inputs = same output
- ✅ **Explainable:** Every factor is tracked
- ✅ **Bounded:** Score always 0-100
- ✅ **Realistic:** Based on economic research

### Contributing Factors Tracked
```json
{
  "industry_vulnerability": 50.0,
  "company_size_factor": 0.0,
  "experience_protection": -5.0,
  "role_level_protection": -10.0,
  "performance_adjustment": -5.0,
  "remote_capability_benefit": -5.0
}
```

---

## 📚 ECONOMIC RATIONALE

### Why These Factors?

1. **Industry Vulnerability**
   - Historical data shows certain industries are hit harder
   - Discretionary spending drops first (hospitality, retail)
   - Essential services remain stable (healthcare, utilities)

2. **Company Size**
   - Larger companies have more cash reserves
   - Can weather downturns longer
   - Smaller companies often cut staff quickly

3. **Experience**
   - Experienced workers have institutional knowledge
   - Harder to replace
   - More expensive to rehire after recovery

4. **Role Level**
   - Strategic roles are protected
   - Entry-level positions are easier to eliminate
   - Executives make decisions, less likely to cut themselves

5. **Performance**
   - High performers are retained
   - Low performers are cut first
   - Clear correlation in layoff data

6. **Remote Capability**
   - Access to broader job markets
   - More flexibility during crisis
   - Can relocate without moving

---

## 🔍 DATA SOURCES

The vulnerability scores are based on:
- Historical recession data (2008, 2020)
- Industry employment statistics
- Labor market research
- Economic studies on layoff patterns

**Note:** This is a model-based estimate, not a guarantee. Individual circumstances vary.

---

## 🎓 HOW TO USE THIS INFORMATION

### For Job Seekers:
1. Calculate your current recession risk
2. Identify which factors you can improve
3. Focus on controllable factors (skills, role level, performance)
4. Consider industry/company changes if risk is high

### For Career Planning:
1. Understand which factors matter most
2. Build experience in recession-resistant areas
3. Develop remote work capabilities
4. Aim for senior roles in stable industries

### For Employers:
1. Understand employee vulnerability
2. Provide training to reduce risk
3. Support career development
4. Build recession-resilient teams

---

## 📊 SUMMARY

**Recession Risk is calculated using 6 factors:**

1. 🏢 **Industry Vulnerability** (0-90 points) - Primary factor
2. 🏭 **Company Size** (±35% adjustment) - Stability multiplier
3. 📅 **Experience** (up to -20 points) - Protection from experience
4. 👔 **Role Level** (up to -30 points) - Strategic importance
5. ⭐ **Performance** (±10 points) - Individual contribution
6. 🌐 **Remote Capability** (-5 points) - Flexibility bonus

**Final Score:** 0-100 (lower is better)  
**Risk Levels:** Low (0-34), Medium (35-61), High (62-100)

**All calculations are:**
- ✅ Deterministic (reproducible)
- ✅ Explainable (every factor tracked)
- ✅ Validated (input checking)
- ✅ Realistic (based on economic data)

---

**File Location:** `src/risk_calculators/recession_risk.py`  
**Last Updated:** 2026-04-13  
**Status:** ✅ Production-Ready
