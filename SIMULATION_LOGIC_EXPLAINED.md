# Simulation Logic - How It Actually Works

**Date**: April 14, 2026  
**Purpose**: Explain the mathematical and economic logic behind each simulation

---

## 🧮 CORE CONCEPT: SHOCK MODEL

Everything starts with this basic idea:

```
Future Unemployment = Baseline + Shock Effect - Policy Effect + Recovery
```

### Base Shock Logic (Foundation for All Modes)

**From `src/shock_scenario.py`:**

```python
# PHASE 1: RAMP-UP (shock builds gradually)
if year < shock_duration:
    ramp_progress = (year + 1) / shock_duration
    shock_effect = shock_intensity × ramp_progress
    
    # Example: 3-year shock with 2pp intensity
    # Year 1: 2pp × (1/3) = 0.67pp
    # Year 2: 2pp × (2/3) = 1.33pp
    # Year 3: 2pp × (3/3) = 2.00pp (full impact)

# PHASE 2: RECOVERY (exponential decay)
else:
    years_since_peak = year - shock_duration
    shock_effect = shock_intensity × e^(-recovery_rate × years_since_peak)
    
    # Example: recovery_rate = 0.3
    # Year 4: 2pp × e^(-0.3×1) = 2pp × 0.74 = 1.48pp
    # Year 5: 2pp × e^(-0.3×2) = 2pp × 0.55 = 1.10pp
    # Year 6: 2pp × e^(-0.3×3) = 2pp × 0.41 = 0.82pp
```

**Why Exponential Decay?**
- Real economies don't recover linearly
- Initial recovery is fast (stimulus, pent-up demand)
- Later recovery is slower (structural issues remain)
- Matches real-world data (2008 crisis, COVID recovery)

---

## 🎲 MODE 1: MONTE CARLO LOGIC

### Economic Concept:
**"We don't know the exact future, but we can model uncertainty"**

### Mathematical Approach: **Stochastic Simulation**

```python
# Run N simulations (e.g., 1000 times)
FOR i = 1 to N:
    # Add random variation to each parameter
    shock_intensity = base_intensity + random_normal(0, std_dev)
    recovery_rate = base_recovery + random_normal(0, std_dev)
    duration = base_duration + random_normal(0, variance)
    
    # Run shock scenario with these random values
    result[i] = simulate_shock(intensity, recovery, duration)
    
    # Record outcomes
    peak_unemployment[i] = max(result[i])
    recovery_time[i] = time_to_baseline(result[i])
```

### Statistical Logic:

**1. Normal Distribution (Gaussian)**
```
Why? Most economic shocks cluster around average with some variation
Formula: f(x) = (1/σ√2π) × e^(-(x-μ)²/2σ²)

Where:
- μ = mean (your base value)
- σ = standard deviation (how much it varies)
- x = random value generated
```

**2. Confidence Intervals**
```python
# After N simulations, sort all peak unemployment values
sorted_peaks = sort(peak_unemployment)

# Calculate percentiles
P5  = sorted_peaks[0.05 × N]  # 5th percentile (worst 5%)
P25 = sorted_peaks[0.25 × N]  # 25th percentile
P50 = sorted_peaks[0.50 × N]  # Median
P75 = sorted_peaks[0.75 × N]  # 75th percentile
P95 = sorted_peaks[0.95 × N]  # 95th percentile (best 95%)

# 95% Confidence Interval = [P5, P95]
# Meaning: "We're 95% confident the outcome will be between P5 and P95"
```

**3. Risk Metrics**
```python
# Mean (expected value)
mean = sum(peak_unemployment) / N

# Standard Deviation (volatility/risk)
std = sqrt(sum((x - mean)² for x in peak_unemployment) / N)

# Interpretation:
# - High std = high uncertainty/risk
# - Low std = predictable outcome
```

### Real-World Example:

```
Base shock intensity: 0.3 (expect +1.8pp unemployment)
Intensity std dev: 0.05

Run 1000 simulations:
- 50 simulations: intensity = 0.25 (mild shock)
- 680 simulations: intensity = 0.28-0.32 (near expected)
- 50 simulations: intensity = 0.35 (severe shock)

Results:
- Mean peak: 8.2%
- 95% CI: [7.1%, 9.5%]
- Interpretation: "Most likely 8.2%, but could be as low as 7.1% or as high as 9.5%"
```

---

## 💥 MODE 2: MULTI-SHOCK LOGIC

### Economic Concept:
**"Multiple crises can overlap and amplify each other"**

### Mathematical Approach: **Superposition + Interaction Effects**

```python
# Start with baseline
compound_unemployment = baseline_unemployment

# Add each shock with timing
FOR each shock:
    # Calculate individual shock trajectory
    shock_trajectory = calculate_shock(
        intensity=shock.intensity,
        duration=shock.duration,
        start_year=shock.start_year
    )
    
    # Adjust for sector-specific impacts
    adjusted_shock = shock_trajectory × sector_multiplier
    
    # Add to compound scenario (ADDITIVE model)
    compound_unemployment += adjusted_shock

# Add interaction effects (non-linear)
interaction_effect = calculate_interaction(all_shocks)
compound_unemployment += interaction_effect
```

### Sector Sensitivity Logic:

**Why Different Sectors React Differently?**

```python
# Example: Pandemic shock
sector_multipliers = {
    "Tourism": 1.8,      # Hit hardest (travel stops)
    "Services": 1.4,     # Restaurants, retail close
    "Manufacturing": 1.0, # Moderate impact
    "Technology": 0.8,   # Less affected (remote work)
    "Healthcare": 0.6    # Actually grows (demand increases)
}

# Adjusted shock intensity
adjusted_intensity = base_intensity × sector_multiplier

# Example:
# Base pandemic shock: 0.4 (2.4pp unemployment)
# Tourism: 0.4 × 1.8 = 0.72 (4.3pp) - much worse
# Healthcare: 0.4 × 0.6 = 0.24 (1.4pp) - less severe
```

### Interaction Effects Logic:

**Why Shocks Amplify Each Other?**

```python
# LINEAR (wrong): Just add shocks
total_impact = shock1 + shock2
# Example: 2pp + 1.5pp = 3.5pp

# NON-LINEAR (correct): Shocks interact
total_impact = shock1 + shock2 + interaction_effect

# Interaction effect calculation:
interaction_effect = (shock1 × shock2) × overlap_factor

# Example:
# Shock 1 (Pandemic): 2pp
# Shock 2 (Supply Chain): 1.5pp
# Overlap: Both hit manufacturing
# Interaction: (2 × 1.5) × 0.15 = 0.45pp
# Total: 2 + 1.5 + 0.45 = 3.95pp (worse than simple sum)
```

### Timing Logic:

```python
# Shock 1 starts at year 0, duration 2 years
# Shock 2 starts at year 1, duration 3 years

Year 0: Only Shock 1 active
Year 1: Both shocks active (OVERLAP - amplification)
Year 2: Both shocks active (OVERLAP - amplification)
Year 3: Only Shock 2 active
Year 4: Both recovering

# Overlapping years have higher impact due to:
# 1. Combined direct effects
# 2. Interaction effects
# 3. Reduced policy effectiveness (resources spread thin)
```

### Policy Response Logic:

```python
# Policy reduces shock impact
policy_strength = policy_cushion_score / 100
# Example: Fiscal Stimulus = 35/100 = 0.35

# Apply policy effect
adjusted_shock = raw_shock × (1 - policy_strength)

# Example:
# Raw shock: 2.5pp unemployment increase
# Policy strength: 0.35 (35% effective)
# Adjusted shock: 2.5 × (1 - 0.35) = 2.5 × 0.65 = 1.625pp
# Policy saved: 2.5 - 1.625 = 0.875pp
```

---

## 🔬 MODE 3: STRESS TESTING LOGIC

### Economic Concept:
**"Test if the system survives extreme but plausible scenarios"**

### Mathematical Approach: **Threshold Testing + Pass/Fail Criteria**

```python
# Define system limits (regulatory/practical)
pass_criteria = {
    "max_peak_unemployment": 12.0,    # System breaks above 12%
    "max_duration_above_8": 3,        # Can't sustain >8% for >3 years
    "recovery_within_years": 5        # Must recover within 5 years
}

# Test each scenario
FOR each stress_scenario:
    # Run simulation
    result = simulate(stress_scenario)
    
    # Test 1: Peak unemployment
    peak_ue = max(result.unemployment)
    test1_pass = (peak_ue <= 12.0)
    
    # Test 2: Duration above threshold
    years_above_8 = count(result.unemployment > 8.0)
    test2_pass = (years_above_8 <= 3)
    
    # Test 3: Recovery time
    recovery_time = time_to_return_to_baseline(result)
    test3_pass = (recovery_time <= 5)
    
    # Overall pass: ALL tests must pass
    overall_pass = test1_pass AND test2_pass AND test3_pass

# System resilience rating
pass_rate = (passed_scenarios / total_scenarios) × 100%

IF pass_rate >= 80%: resilience = "HIGH"
ELIF pass_rate >= 60%: resilience = "MEDIUM"
ELSE: resilience = "LOW"
```

### Stress Scenario Design Logic:

**Predefined Scenarios Based on Historical Events:**

```python
# Scenario 1: Severe Financial Crisis (2008-style)
{
    "shock_intensity": 0.6,    # Very high (6% → 9.6%)
    "shock_duration": 4,       # Long-lasting
    "recovery_rate": 0.15      # Slow recovery
}
# Logic: Financial crises have deep, lasting impacts

# Scenario 2: Pandemic + Supply Chain (COVID-style)
{
    "shocks": [
        {"type": "pandemic", "intensity": 0.4, "start": 0},
        {"type": "supply_chain", "intensity": 0.3, "start": 1}
    ]
}
# Logic: Modern crises often compound

# Scenario 3: Energy Crisis + Geopolitical
{
    "shocks": [
        {"type": "energy", "intensity": 0.35, "start": 0},
        {"type": "geopolitical", "intensity": 0.25, "start": 1}
    ]
}
# Logic: Energy shocks often trigger geopolitical tensions
```

### Why These Thresholds?

```
12% Peak Unemployment:
- Historical: US peaked at 10% (2009), 14.7% (COVID)
- India: Rarely exceeds 10% officially
- 12% = severe but survivable

3 Years Above 8%:
- Prolonged high unemployment causes:
  * Skill erosion
  * Social unrest
  * Permanent job losses
- 3 years = maximum sustainable period

5 Years Recovery:
- Historical recoveries: 3-7 years
- 5 years = reasonable expectation
- Longer = structural damage
```

---

## 🔄 MODE 4: ECONOMIC CYCLES LOGIC

### Economic Concept:
**"Economies naturally cycle between growth and recession"**

### Mathematical Approach: **Sinusoidal Wave Function**

```python
# Business cycle as sine wave
FOR each year:
    # Calculate position in cycle (0 to 1)
    cycle_position = (start_position + year/cycle_length) % 1.0
    
    # Convert to radians (0 to 2π)
    radians = cycle_position × 2π
    
    # Calculate cyclical factor (inverted for unemployment)
    cyclical_factor = -sin(radians) × amplitude
    
    # Apply to unemployment
    cyclical_unemployment = baseline × (1 + cyclical_factor)
```

### Why Sine Wave?

**Mathematical Properties:**
```
sin(0°) = 0      → Neutral (baseline)
sin(90°) = 1     → Peak (lowest unemployment)
sin(180°) = 0    → Neutral (baseline)
sin(270°) = -1   → Trough (highest unemployment)
sin(360°) = 0    → Back to start

# Inverted for unemployment:
-sin(0°) = 0     → Expansion starts
-sin(90°) = -1   → Peak (economy hot, unemployment low)
-sin(180°) = 0   → Contraction starts
-sin(270°) = 1   → Trough (recession, unemployment high)
```

**Economic Justification:**
- Smooth transitions (no sudden jumps)
- Symmetric (expansion ≈ contraction duration)
- Periodic (cycles repeat)
- Matches empirical data

### Phase Logic:

```python
# Map cycle position to economic phase
IF 0.00 <= position < 0.25:
    phase = "EXPANSION"
    # Economy growing, unemployment falling
    # Businesses hiring, consumer confidence high
    
ELIF 0.25 <= position < 0.50:
    phase = "PEAK"
    # Maximum growth, lowest unemployment
    # Inflation risk, tight labor market
    # Central banks may raise rates
    
ELIF 0.50 <= position < 0.75:
    phase = "CONTRACTION"
    # Economy slowing, unemployment rising
    # Businesses cutting costs, layoffs begin
    # Consumer spending decreases
    
ELSE:  # 0.75 <= position < 1.00
    phase = "TROUGH"
    # Recession bottom, highest unemployment
    # Economic activity at minimum
    # Stimulus policies activated
```

### Amplitude Logic:

```python
# Amplitude = maximum deviation from baseline
amplitude = 0.15  # 15%

# Example with 6% baseline unemployment:
peak_unemployment = 6% × (1 - 0.15) = 5.1%  # Economy hot
trough_unemployment = 6% × (1 + 0.15) = 6.9%  # Recession

# Cycle range = 6.9% - 5.1% = 1.8pp

# Historical context:
# - Mild cycles: 10% amplitude (±0.6pp)
# - Normal cycles: 15% amplitude (±0.9pp)
# - Severe cycles: 25% amplitude (±1.5pp)
```

### Cycle Length Logic:

```python
# Historical business cycles:
# - Short cycles: 4-6 years (inventory cycles)
# - Normal cycles: 7-10 years (investment cycles)
# - Long cycles: 15-20 years (Kondratiev waves)

# Default: 8 years
# - Matches average post-WWII US cycle
# - 4 years expansion + 4 years contraction
# - Realistic for modern economies
```

---

## 🧮 MATHEMATICAL FORMULAS SUMMARY

### 1. Shock Effect (Exponential Decay)
```
S(t) = I × e^(-r×t)

Where:
- S(t) = shock effect at time t
- I = initial shock intensity
- r = recovery rate
- t = time since shock peak
- e = Euler's number (2.71828...)
```

### 2. Monte Carlo Mean & Variance
```
Mean: μ = (1/N) × Σ(xi)
Variance: σ² = (1/N) × Σ(xi - μ)²
Standard Deviation: σ = √σ²

Where:
- N = number of simulations
- xi = outcome of simulation i
- Σ = sum over all simulations
```

### 3. Confidence Interval
```
CI = [P(α/2), P(1-α/2)]

For 95% CI: α = 0.05
CI = [P(0.025), P(0.975)]
≈ [P5, P95] for large N
```

### 4. Multi-Shock Compound Effect
```
C(t) = B(t) + Σ[Si(t-ti) × Mi] + I(t)

Where:
- C(t) = compound unemployment at time t
- B(t) = baseline unemployment
- Si(t-ti) = shock i effect (delayed by ti)
- Mi = sector multiplier for shock i
- I(t) = interaction effect
- Σ = sum over all shocks
```

### 5. Economic Cycle
```
U(t) = B × [1 + A × sin(2π × (t/L + φ))]

Where:
- U(t) = cyclical unemployment at time t
- B = baseline unemployment
- A = amplitude (fraction)
- L = cycle length (years)
- φ = phase offset (starting position)
- Inverted: use -sin for unemployment
```

### 6. Policy Effect
```
Uadjusted = Uraw × (1 - P)

Where:
- Uadjusted = unemployment after policy
- Uraw = unemployment without policy
- P = policy strength (0 to 1)
```

---

## 🎯 LOGIC QUALITY ASSESSMENT

### ✅ GOOD LOGIC (Realistic):

1. **Exponential Recovery**: Matches real-world data
2. **Sector Multipliers**: Based on economic theory
3. **Sine Wave Cycles**: Standard macroeconomic model
4. **Additive Shocks**: Correct for percentage points
5. **Policy Cushioning**: Reasonable effectiveness model

### ⚠️ SIMPLIFIED LOGIC (Approximate):

1. **Independent Variables**: Monte Carlo assumes no correlation
2. **Linear Interaction**: Real interactions are more complex
3. **Fixed Sector Weights**: Should vary by shock type
4. **Symmetric Cycles**: Real cycles are asymmetric
5. **Constant Recovery Rate**: Should vary by shock severity

### ❌ MISSING LOGIC (Needs Addition):

1. **Correlation Matrix**: Variables should be correlated
2. **Time-Varying Uncertainty**: Uncertainty changes over time
3. **Regime Switching**: Different rules for different states
4. **Feedback Loops**: Unemployment affects growth affects unemployment
5. **Structural Breaks**: Long-term changes in relationships

---

## 📚 ECONOMIC THEORY BEHIND THIS

### 1. **Okun's Law** (GDP-Unemployment)
```
ΔU = -β × (ΔY - Y*)

Where:
- ΔU = change in unemployment
- ΔY = GDP growth
- Y* = potential GDP growth
- β = Okun coefficient (~0.5 for US)
```

### 2. **Phillips Curve** (Inflation-Unemployment)
```
π = πe - α(U - U*)

Where:
- π = inflation
- πe = expected inflation
- U = unemployment rate
- U* = natural rate
- α = sensitivity parameter
```

### 3. **NAIRU** (Non-Accelerating Inflation Rate of Unemployment)
```
Natural unemployment rate where inflation is stable
- Below NAIRU: inflation rises
- Above NAIRU: inflation falls
- Typical range: 4-6%
```

### 4. **Real Business Cycle Theory**
```
Cycles driven by:
- Technology shocks
- Productivity changes
- Supply-side factors
- Rational expectations
```

---

**Bottom Line**: The logic is based on real economic theory and mathematical models. The implementation is mostly correct, but the UI doesn't use it properly. Fix the connections and you'll have a solid simulation system!
