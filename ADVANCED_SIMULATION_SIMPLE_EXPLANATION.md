# Advanced Simulation - Simple Explanation

**Date**: April 14, 2026  
**Purpose**: Understand what's inside, how it calculates, and what outputs you get

---

## 🎯 WHAT'S INSIDE

Your Advanced Simulation has **4 modes**:

### 1. 🎲 Monte Carlo Simulation
**What it does**: Runs the same scenario 100-2000 times with random variations

### 2. 💥 Multi-Shock Simulation  
**What it does**: Combines multiple crises happening at the same time or overlapping

### 3. 🔬 Stress Testing
**What it does**: Tests if your system survives extreme scenarios (pass/fail tests)

### 4. 🔄 Economic Cycles
**What it does**: Models business cycles (boom → recession → recovery)

---

## 📊 MODE 1: MONTE CARLO

### Inputs You Provide:
- **Base Shock Intensity**: 0.1 to 0.6 (how strong the shock is)
- **Base Duration**: 1-5 years (how long it lasts)
- **Base Recovery Rate**: 0.1 to 0.6 (how fast recovery happens)
- **Intensity Std Dev**: 0.01 to 0.2 (how much intensity varies)
- **Recovery Std Dev**: 0.01 to 0.15 (how much recovery varies)
- **Duration Variance**: 0-3 years (how much duration varies)
- **Number of Simulations**: 100, 500, 1000, or 2000

### How It Calculates:

```python
FOR each simulation (1 to N):
    1. Add random variation to intensity:
       shock_intensity = base_intensity + random_normal(0, intensity_std)
    
    2. Add random variation to recovery:
       recovery_rate = base_recovery + random_normal(0, recovery_std)
    
    3. Add random variation to duration:
       duration = base_duration + random_normal(0, duration_variance)
    
    4. Run shock scenario with these random values
    
    5. Record:
       - Peak unemployment
       - Recovery time (years to return to baseline)
```

### Outputs You Get:

**Summary Statistics:**
- Mean peak unemployment (average across all runs)
- 95% confidence interval (5th to 95th percentile)
- Mean recovery time
- Standard deviation

**Distribution Data:**
- Percentiles: P5, P25, P75, P95
- Full distribution curve
- Probability density

**Example Output:**
```
Mean Peak UE: 8.2%
95% Confidence: 7.1% - 9.5%
Mean Recovery: 4.2 years
Std Deviation: 0.85pp
```

### ⚠️ CURRENT ISSUES:

1. **Fake Results**: Currently returns hardcoded values, not real calculations
   ```python
   # CURRENT (WRONG):
   "mean_peak_ue": round(6.5 + base_intensity * 5, 2)  # Just a formula
   
   # SHOULD BE:
   "mean_peak_ue": np.mean(all_peak_values_from_simulations)
   ```

2. **No Real Randomness**: Doesn't actually run N simulations
3. **No Correlation**: Variables are independent (should be correlated)

---

## 📊 MODE 2: MULTI-SHOCK

### Inputs You Provide:

**For Each Shock (1-4 shocks):**
- **Type**: pandemic, financial_crisis, natural_disaster, supply_chain, energy_crisis, geopolitical
- **Intensity**: 0.1 to 0.8
- **Duration**: 1-5 years
- **Start Year**: 0-5 (when shock begins)

**Optional:**
- **Policy Responses**: Which policies to apply in which years

### How It Calculates:

```python
1. Start with baseline unemployment forecast

2. FOR each shock:
   a. Calculate individual shock impact
   b. Adjust for sector-specific effects
   c. Apply shock starting from its start_year
   d. Add impact to compound scenario

3. IF policies enabled:
   FOR each policy:
       Reduce unemployment by (policy_effectiveness × 10%)

4. Calculate total compound effect
```

**Sector Adjustments:**
```python
# Example: Pandemic affects sectors differently
Services: 1.4× impact (restaurants, hotels hit hard)
Tourism: 1.8× impact (travel stops)
Healthcare: 0.6× impact (actually grows)
Technology: 0.8× impact (less affected)
```

### Outputs You Get:

**Summary:**
- Total number of shocks
- Compound peak unemployment (highest point)
- Total impact (how much worse than baseline)
- Most severe shock

**Individual Contributions:**
- Each shock's peak impact
- Shock type and intensity
- Timing information

**Interaction Effects:**
- How shocks amplify each other
- Non-linear combinations

**Example Output:**
```
Total Shocks: 2
Compound Peak: 9.8%
Total Impact: +3.3pp
Most Severe: pandemic

Shock 1 (Pandemic): +2.1pp
Shock 2 (Supply Chain): +0.9pp
Interaction Effect: +0.3pp (shocks amplified each other)
```

### ⚠️ CURRENT ISSUES:

1. **Oversimplified Combination**: Just adds shocks together
   ```python
   # CURRENT (TOO SIMPLE):
   total_impact = sum(shock.intensity for shock in shocks) * 2.5
   
   # SHOULD BE:
   # - Consider timing overlaps
   # - Model interaction effects
   # - Use time series, not just totals
   ```

2. **No Real Timing**: Doesn't properly handle overlapping shocks
3. **Policy Effect Too Weak**: Just reduces by 10%, not realistic

---

## 📊 MODE 3: STRESS TESTING

### Inputs You Provide:

**Test Configuration:**
- Use predefined scenarios (5 scenarios) OR custom
- **Pass Criteria:**
  - Max Peak UE: 8-15% (default 12%)
  - Max Years Above 8%: 1-5 years (default 3)
  - Recovery Within: 3-8 years (default 5)

**Predefined Scenarios:**
1. Severe Financial Crisis (2008-style)
2. Pandemic + Supply Chain Crisis
3. Energy Crisis + Geopolitical Tension
4. Technology Disruption
5. Natural Disaster Cascade

### How It Calculates:

```python
FOR each stress scenario:
    1. Run the scenario (single shock or multi-shock)
    
    2. Check against pass criteria:
       Test 1: Peak UE ≤ max_peak_ue?
       Test 2: Years above 8% ≤ max_duration?
       Test 3: Recovery time ≤ recovery_within?
    
    3. Overall Pass = ALL tests passed
    
4. Calculate pass rate = (passed / total) × 100%

5. Assign resilience rating:
   - HIGH: ≥80% pass rate
   - MEDIUM: 60-79% pass rate
   - LOW: <60% pass rate
```

### Outputs You Get:

**Summary:**
- Total scenarios tested
- Passed scenarios
- Failed scenarios
- Pass rate (%)
- System resilience (HIGH/MEDIUM/LOW)

**Per Scenario:**
- Peak unemployment
- Recovery time
- Pass/fail for each test
- Overall pass/fail

**Example Output:**
```
Total Scenarios: 5
Passed: 3
Failed: 2
Pass Rate: 60%
System Resilience: MEDIUM

Scenario 1 (Financial Crisis):
  Peak UE: 11.2% ✅ (< 12%)
  Years Above 8%: 4 ❌ (> 3)
  Recovery: 4 years ✅ (< 5)
  Overall: FAILED
```

### ⚠️ CURRENT ISSUES:

1. **Random Results**: Uses `np.random.randint()` instead of real tests
2. **No Actual Scenarios**: Doesn't run the predefined scenarios
3. **Vague Criteria**: Pass criteria are arbitrary, not based on real limits

---

## 📊 MODE 4: ECONOMIC CYCLES

### Inputs You Provide:

- **Cycle Length**: 4-12 years (default 8)
- **Amplitude**: 5-25% (default 15%)
- **Current Phase**: expansion, peak, contraction, or trough
- **Forecast Horizon**: 5-15 years

### How It Calculates:

```python
1. Map current phase to starting position:
   expansion → 0.0
   peak → 0.25
   contraction → 0.5
   trough → 0.75

2. FOR each year:
   a. Calculate position in cycle (0-1)
      position = (start_position + year/cycle_length) % 1.0
   
   b. Convert to sine wave:
      cycle_factor = -sin(position × 2π) × amplitude
   
   c. Apply to unemployment:
      cyclical_ue = baseline_ue × (1 + cycle_factor)
   
   d. Determine phase:
      0.00-0.25: expansion
      0.25-0.50: peak
      0.50-0.75: contraction
      0.75-1.00: trough
```

**Why Sine Wave?**
- Smooth transitions between phases
- Realistic cyclical pattern
- Inverted for unemployment (high at trough, low at peak)

### Outputs You Get:

**Summary:**
- Peak unemployment (highest in cycle)
- Trough unemployment (lowest in cycle)
- Cycle range (peak - trough)
- Volatility (standard deviation)

**Time Series:**
- Year-by-year unemployment
- Current phase for each year
- Cycle position (0-1)

**Example Output:**
```
Peak UE: 7.8%
Trough UE: 5.2%
Cycle Range: 2.6pp
Volatility: 0.82

Year 2026: 6.1% (expansion)
Year 2027: 5.8% (expansion)
Year 2028: 5.4% (peak)
Year 2029: 5.6% (peak)
Year 2030: 6.2% (contraction)
```

### ⚠️ CURRENT ISSUES:

1. **Too Simple**: Just a sine wave, real cycles are more complex
2. **No Shock Integration**: Doesn't combine with shocks
3. **Fixed Amplitude**: Real cycles have varying amplitudes

---

## 🔧 WHAT'S ACTUALLY WORKING VS FAKE

### ✅ WORKING (Real Calculations):

1. **Economic Cycles**: Actually uses sine wave math
2. **Multi-Shock Sector Adjustments**: Has real sector multipliers
3. **Policy Strength Calculation**: Converts policy scores correctly
4. **Shock Ramp-Up Logic**: Gradual increase is implemented

### ❌ FAKE (Hardcoded/Placeholder):

1. **Monte Carlo Results**: Returns formula, not real simulations
   ```python
   # Line 195-200 in pages/12_Advanced_Simulator.py
   "mean_peak_ue": round(6.5 + base_intensity * 5, 2)  # FAKE!
   ```

2. **Multi-Shock Total Impact**: Simple multiplication
   ```python
   # Line 267
   total_impact = sum(event["intensity"] for event in shock_events) * 2.5  # FAKE!
   ```

3. **Stress Test Pass/Fail**: Random number
   ```python
   # Line 349
   passed_scenarios = np.random.randint(2, total_scenarios + 1)  # FAKE!
   ```

4. **Economic Cycle Outputs**: Simplified formulas
   ```python
   # Line 391-392
   peak_ue = baseline_ue + amplitude * baseline_ue  # TOO SIMPLE!
   ```

---

## 🎯 WHAT YOU SHOULD FIX

### Priority 1: Make Monte Carlo Real

**Current (Fake):**
```python
st.session_state.mc_results = {
    "summary": {
        "mean_peak_ue": round(6.5 + base_intensity * 5, 2),  # FAKE
    }
}
```

**Should Be (Real):**
```python
# Actually call the simulation engine
from src.advanced_simulation import AdvancedSimulationEngine

engine = AdvancedSimulationEngine()
results = engine.monte_carlo_simulation(
    baseline_df=baseline_data,
    base_shock_intensity=base_intensity,
    base_shock_duration=base_duration,
    base_recovery_rate=base_recovery,
    config=MonteCarloConfig(
        num_simulations=num_simulations,
        shock_intensity_std=intensity_std,
        recovery_rate_std=recovery_std,
        duration_variance=duration_var
    )
)

st.session_state.mc_results = results  # REAL results
```

### Priority 2: Connect Multi-Shock to Real Engine

**Current (Fake):**
```python
total_impact = sum(event["intensity"] for event in shock_events) * 2.5
```

**Should Be (Real):**
```python
# Convert UI inputs to ShockEvent objects
shock_events_list = [
    ShockEvent(
        shock_type=ShockType[event["shock_type"].upper()],
        intensity=event["intensity"],
        duration=event["duration"],
        start_year=event["start_year"],
        sector_impacts={},
        description=event["description"]
    ) for event in shock_events
]

# Run real multi-shock simulation
results = engine.multi_shock_scenario(
    baseline_df=baseline_data,
    shock_events=shock_events_list,
    policy_responses=policy_responses
)

st.session_state.ms_results = results  # REAL results
```

### Priority 3: Fix Stress Testing

**Current (Fake):**
```python
passed_scenarios = np.random.randint(2, total_scenarios + 1)  # Random!
```

**Should Be (Real):**
```python
# Get predefined scenarios
from src.advanced_simulation import get_predefined_stress_scenarios

stress_scenarios = get_predefined_stress_scenarios()

# Run real stress tests
results = engine.stress_test_framework(
    baseline_df=baseline_data,
    stress_scenarios=stress_scenarios
)

st.session_state.st_results = results  # REAL results
```

### Priority 4: Improve Economic Cycles

**Current (Too Simple):**
```python
peak_ue = baseline_ue + amplitude * baseline_ue
trough_ue = baseline_ue - amplitude * baseline_ue
```

**Should Be (Real):**
```python
# Run real cycle simulation
results = engine.economic_cycle_simulation(
    baseline_df=baseline_data,
    cycle_length=cycle_length,
    amplitude=amplitude,
    current_phase=EconomicCycle[current_phase.upper()]
)

st.session_state.ec_results = results  # REAL results
```

---

## 📋 SUMMARY: WHAT TO CHANGE

### File: `pages/12_Advanced_Simulator.py`

**Lines to Replace:**

1. **Line 195-210** (Monte Carlo fake results) → Call real engine
2. **Line 267-280** (Multi-Shock fake results) → Call real engine
3. **Line 349-360** (Stress Test fake results) → Call real engine
4. **Line 391-405** (Economic Cycle fake results) → Call real engine

### What You Need:

1. **Import the engine:**
   ```python
   from src.advanced_simulation import (
       AdvancedSimulationEngine,
       MonteCarloConfig,
       ShockEvent,
       ShockType,
       EconomicCycle,
       get_predefined_stress_scenarios
   )
   ```

2. **Load baseline data:**
   ```python
   # Get baseline forecast from API or data source
   baseline_data = get_baseline_forecast()  # You need this function
   ```

3. **Replace fake results with real engine calls**

---

## 🎯 QUICK FIX CHECKLIST

- [ ] Import AdvancedSimulationEngine in page file
- [ ] Create function to load baseline forecast data
- [ ] Replace Monte Carlo fake results (line ~195)
- [ ] Replace Multi-Shock fake results (line ~267)
- [ ] Replace Stress Test fake results (line ~349)
- [ ] Replace Economic Cycle fake results (line ~391)
- [ ] Test each mode works with real data
- [ ] Verify outputs match expected format

---

**Bottom Line**: Your simulation engine (`src/advanced_simulation.py`) has good logic, but the UI page (`pages/12_Advanced_Simulator.py`) doesn't use it. It just returns fake placeholder values. Connect the two and you'll have a real simulation system!
