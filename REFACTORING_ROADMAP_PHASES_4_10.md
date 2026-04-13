# System Refactoring Roadmap: Phases 4-10

**Current Status**: Phases 1-3 Complete ✅  
**Remaining**: Phases 4-10  
**Estimated Effort**: 4-6 hours of development

---

## 📋 PHASE 4: FORECASTING MODULE FIX

**Status**: 📋 PLANNED  
**Estimated Time**: 30 minutes  
**Priority**: MEDIUM

### **Current State**
The forecasting module (`src/forecasting.py`) is already well-designed:
- ✅ Uses ensemble method (trend + mean reversion + ARIMA + exp smoothing)
- ✅ Has realistic constraints (max ±1.5% annual change)
- ✅ Provides Monte Carlo confidence bands
- ✅ No randomness in base forecast

### **Actions Required**
1. Add data quality check before forecasting
2. Validate forecast outputs stay within realistic bounds
3. Add warning if input data quality is low
4. Update to use `central_data.load_unemployment()`

### **Code Changes**
```python
# Add to forecasting.py
from central_data import load_unemployment, get_data_quality_report

def forecast_with_validation(df: pd.DataFrame) -> pd.DataFrame:
    # Check data quality
    report = get_data_quality_report()
    if report['unemployment']['data_quality_score'] < 70:
        print("⚠️  WARNING: Input data quality is low")
    
    # Run forecast
    forecast_df = self.forecast(df)
    
    # Validate outputs
    if forecast_df['Predicted_Unemployment'].max() > 10.0:
        print("⚠️  WARNING: Forecast exceeds realistic bounds")
    
    return forecast_df
```

---

## 📋 PHASE 5: RISK MODEL REBUILD

**Status**: 📋 PLANNED  
**Estimated Time**: 45 minutes  
**Priority**: HIGH

### **Target Files**
- `src/risk_calculators/orchestrator.py`
- `src/risk_calculators/automation_risk.py`
- `src/risk_calculators/recession_risk.py`
- `src/risk_calculators/age_discrimination_risk.py`
- `src/risk_calculators/time_prediction.py`

### **Current State**
Risk calculators are already deterministic with clear formulas.

### **Actions Required**
1. Add input validation for all risk calculators
2. Add "INSUFFICIENT DATA" flags when needed
3. Document all formulas explicitly in docstrings
4. Add validation for input ranges
5. Add data quality metadata to results

### **Code Changes**
```python
# Add to each risk calculator
def validate_inputs(self, profile: UserProfile) -> Tuple[bool, str]:
    """Validate input profile has sufficient data."""
    if not profile.skills:
        return False, "INSUFFICIENT DATA: No skills provided"
    if profile.experience_years < 0:
        return False, "INVALID DATA: Negative experience"
    return True, "Valid"

def calculate_risk(self, profile: UserProfile) -> RiskResult:
    # Validate inputs
    is_valid, message = self.validate_inputs(profile)
    if not is_valid:
        return RiskResult(
            risk_score=0.0,
            confidence="NONE",
            warning=message
        )
    
    # Calculate risk (existing logic)
    ...
```

---

## 📋 PHASE 6: SIMULATION ENGINE FIX

**Status**: 📋 PLANNED  
**Estimated Time**: 20 minutes  
**Priority**: MEDIUM

### **Target File**
- `src/shock_scenario.py`

### **Current State**
Already well-designed with exponential decay and bounded outputs.

### **Actions Required**
1. Add validation after simulation
2. Ensure values stay within realistic bounds (2%-10%)
3. Add data quality checks

### **Code Changes**
```python
# Add to shock_scenario.py
def apply_with_validation(self, baseline_df: pd.DataFrame) -> pd.DataFrame:
    # Apply shock
    scenario_df = self.apply(baseline_df)
    
    # Validate outputs
    max_val = scenario_df['Scenario_Unemployment'].max()
    if max_val > 10.0:
        print(f"⚠️  WARNING: Scenario exceeds realistic bounds ({max_val:.1f}%)")
        # Cap at realistic maximum
        scenario_df['Scenario_Unemployment'] = scenario_df['Scenario_Unemployment'].clip(upper=10.0)
    
    return scenario_df
```

---

## 📋 PHASE 7: GRAPH VALIDATION LAYER

**Status**: 📋 PLANNED  
**Estimated Time**: 1 hour  
**Priority**: HIGH

### **New File to Create**
- `src/graph_validator.py`

### **Actions Required**
1. Create graph validation module
2. Validate data before plotting
3. Add data source labels to all graphs
4. Clearly separate historical vs forecast (solid vs dashed lines)
5. Add quality indicators to graphs

### **Code Structure**
```python
# src/graph_validator.py

class GraphValidator:
    """Validates data before plotting and adds quality indicators."""
    
    def validate_before_plot(self, df: pd.DataFrame, metric: str) -> Tuple[bool, str]:
        """Validate data is suitable for plotting."""
        if df.empty:
            return False, "No data to plot"
        if df[metric].isna().all():
            return False, "All values are missing"
        return True, "Valid"
    
    def add_data_source_label(self, fig, source: str, quality_score: float):
        """Add data source and quality indicator to graph."""
        label = f"Source: {source} | Quality: {quality_score:.0f}/100"
        fig.add_annotation(
            text=label,
            xref="paper", yref="paper",
            x=0.5, y=-0.15,
            showarrow=False,
            font=dict(size=10, color="gray")
        )
        return fig
    
    def style_historical_vs_forecast(self, fig, historical_years, forecast_years):
        """Style historical data as solid, forecast as dashed."""
        # Historical: solid line
        # Forecast: dashed line with different color
        ...
```

---

## 📋 PHASE 8: MODULE CLEANUP

**Status**: 📋 PLANNED  
**Estimated Time**: 1 hour  
**Priority**: MEDIUM

### **Target Files**
- `src/skill_obsolescence.py`
- `src/job_market_pulse.py`
- `src/geo_career_advisor.py`
- `src/llm_insights.py`

### **Actions Required**

#### **skill_obsolescence.py**
```python
# Add at top of file
"""
⚠️  DATA AGE WARNING ⚠️

This module uses job posting data from July-August 2019.
The data is 5+ years old and may not reflect current market conditions.

Data Quality Status:
- Source: Naukri.com job postings
- Date Range: July 1 - August 30, 2019
- Age: 5+ years old
- Recommended Use: Historical baseline only
"""
```

#### **job_market_pulse.py**
```python
# Add data age warning
def load_job_postings() -> pd.DataFrame:
    """
    Load job postings data.
    
    ⚠️  WARNING: Data is from 2019 (5+ years old)
    """
    df = pd.read_csv("marketing_sample_for_naukri_com-jobs__20190701_20190830__30k_data.csv")
    print("⚠️  Using historical job data from 2019")
    return df
```

#### **geo_career_advisor.py**
```python
# Add estimation disclaimer
"""
⚠️  ESTIMATION DISCLAIMER ⚠️

Geographic unemployment estimates are based on:
- PLFS 2022-23 state-level data (official)
- City-level estimates (ESTIMATED, not official)

Data Quality Status:
- State-level: HIGH (official PLFS data)
- City-level: ESTIMATED (derived from state data)
"""
```

#### **llm_insights.py**
```python
# Restrict to data-based explanations
def generate_insight(data: Dict) -> str:
    """
    Generate AI insight based ONLY on provided data.
    
    ⚠️  IMPORTANT: This function should only explain the data,
    not make predictions or recommendations beyond what the data shows.
    """
    ...
```

---

## 📋 PHASE 9: SYSTEM-WIDE VALIDATION REPORT

**Status**: 📋 PLANNED  
**Estimated Time**: 1 hour  
**Priority**: HIGH

### **New File to Create**
- `src/system_audit.py`

### **Actions Required**
1. Create system audit module
2. Check all data sources
3. Report errors and corrections
4. Calculate confidence levels
5. Generate comprehensive report

### **Code Structure**
```python
# src/system_audit.py

class SystemAuditor:
    """Performs system-wide data quality audit."""
    
    def audit_all_data_sources(self) -> Dict:
        """Audit all data sources in the system."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "modules": {},
            "overall_health": "UNKNOWN"
        }
        
        # Check unemployment data
        report["data_sources"]["unemployment"] = self._audit_unemployment()
        
        # Check inflation data
        report["data_sources"]["inflation"] = self._audit_inflation()
        
        # Check job market data
        report["data_sources"]["job_market"] = self._audit_job_market()
        
        # Check all modules
        report["modules"]["forecasting"] = self._audit_forecasting()
        report["modules"]["risk_calculators"] = self._audit_risk_calculators()
        report["modules"]["simulation"] = self._audit_simulation()
        
        # Calculate overall health
        report["overall_health"] = self._calculate_overall_health(report)
        
        return report
    
    def generate_audit_report(self) -> str:
        """Generate human-readable audit report."""
        report = self.audit_all_data_sources()
        
        output = []
        output.append("="*80)
        output.append("SYSTEM AUDIT REPORT")
        output.append("="*80)
        output.append(f"Timestamp: {report['timestamp']}")
        output.append(f"Overall Health: {report['overall_health']}")
        output.append("")
        
        # Data sources
        output.append("DATA SOURCES:")
        for source, status in report["data_sources"].items():
            output.append(f"  {source}: {status['status']} ({status['quality_score']}/100)")
        
        # Modules
        output.append("")
        output.append("MODULES:")
        for module, status in report["modules"].items():
            output.append(f"  {module}: {status['status']}")
        
        output.append("="*80)
        
        return "\n".join(output)
```

---

## 📋 PHASE 10: ENFORCE STRICT RULES

**Status**: 📋 PLANNED  
**Estimated Time**: 1.5 hours  
**Priority**: HIGH

### **Actions Required**

#### **1. Add Import Guards**
```python
# Create src/import_guard.py

import sys
import warnings

class ImportGuard:
    """Prevents direct CSV access, enforces central_data usage."""
    
    FORBIDDEN_PATTERNS = [
        "pd.read_csv",
        "pandas.read_csv",
        "open('data/",
        'open("data/',
    ]
    
    def check_module(self, module_path: str) -> List[str]:
        """Check module for forbidden patterns."""
        violations = []
        with open(module_path, 'r') as f:
            content = f.read()
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern in content:
                    violations.append(f"Found forbidden pattern: {pattern}")
        return violations
```

#### **2. Add Runtime Validation**
```python
# Add to central_data.py

def enforce_single_source():
    """Ensure no other module is reading CSV files directly."""
    import inspect
    import sys
    
    # Check call stack
    stack = inspect.stack()
    for frame in stack[2:]:  # Skip this function and caller
        if "pd.read_csv" in frame.code_context[0]:
            warnings.warn(
                f"⚠️  VIOLATION: Direct CSV access detected in {frame.filename}:{frame.lineno}\n"
                f"   Use central_data.load_unemployment() or load_inflation() instead"
            )
```

#### **3. Add Error Logging**
```python
# Create src/error_logger.py

import logging
from datetime import datetime

class DataQualityLogger:
    """Logs all data quality issues."""
    
    def __init__(self):
        self.logger = logging.getLogger("data_quality")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler("data_quality.log")
        fh.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
    
    def log_validation_issue(self, issue: ValidationIssue):
        """Log a validation issue."""
        self.logger.warning(
            f"Year {issue.year}: {issue.issue_type} - {issue.message}"
        )
    
    def log_correction(self, correction: ValidationIssue):
        """Log a correction."""
        self.logger.info(
            f"Year {correction.year}: Corrected {correction.original_value} → {correction.corrected_value}"
        )
```

#### **4. Create Enforcement Tests**
```python
# Create test_enforcement.py

def test_no_direct_csv_access():
    """Test that no module directly accesses CSV files."""
    import os
    import re
    
    violations = []
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                    if re.search(r'pd\.read_csv\(["\']data/', content):
                        violations.append(path)
    
    assert len(violations) == 0, f"Found direct CSV access in: {violations}"

def test_all_modules_use_central_data():
    """Test that all modules import from central_data."""
    # Check that forecasting, risk calculators, etc. use central_data
    ...
```

---

## 📊 IMPLEMENTATION PRIORITY

### **High Priority** (Do First)
1. ✅ Phase 1: Central Data Layer - COMPLETE
2. ✅ Phase 2: Validation Engine - COMPLETE
3. ✅ Phase 3: Remove Invalid Logic - COMPLETE
4. 📋 Phase 5: Risk Model Rebuild - PLANNED
5. 📋 Phase 7: Graph Validation Layer - PLANNED
6. 📋 Phase 9: System-Wide Validation Report - PLANNED
7. 📋 Phase 10: Enforce Strict Rules - PLANNED

### **Medium Priority** (Do Second)
4. 📋 Phase 4: Forecasting Module Fix - PLANNED
6. 📋 Phase 6: Simulation Engine Fix - PLANNED
8. 📋 Phase 8: Module Cleanup - PLANNED

---

## 🎯 ESTIMATED TIMELINE

### **Already Complete** (3 hours)
- ✅ Phase 1: Central Data Layer (1.5 hours)
- ✅ Phase 2: Validation Engine (1 hour)
- ✅ Phase 3: Remove Invalid Logic (0.5 hours)

### **Remaining Work** (4-6 hours)
- Phase 4: Forecasting Module Fix (0.5 hours)
- Phase 5: Risk Model Rebuild (1 hour)
- Phase 6: Simulation Engine Fix (0.5 hours)
- Phase 7: Graph Validation Layer (1 hour)
- Phase 8: Module Cleanup (1 hour)
- Phase 9: System-Wide Validation Report (1 hour)
- Phase 10: Enforce Strict Rules (1.5 hours)

**Total Project**: 7-9 hours  
**Progress**: 33% complete (3/9 hours)

---

## 📝 NEXT SESSION PLAN

### **Recommended Order**
1. **Phase 5**: Risk Model Rebuild (1 hour)
   - High impact, high priority
   - Adds validation to core risk calculations

2. **Phase 7**: Graph Validation Layer (1 hour)
   - High impact, visible to users
   - Adds quality indicators to all graphs

3. **Phase 9**: System-Wide Validation Report (1 hour)
   - High impact, provides comprehensive overview
   - Useful for debugging and monitoring

4. **Phase 10**: Enforce Strict Rules (1.5 hours)
   - Prevents future violations
   - Ensures system integrity

5. **Phases 4, 6, 8**: Remaining cleanup (2 hours)
   - Lower priority, incremental improvements

---

## ✅ SUCCESS CRITERIA

### **Phase 4-10 Complete When**:
- ✅ All modules use `central_data.py`
- ✅ No direct CSV access anywhere
- ✅ All graphs have quality indicators
- ✅ All modules have data quality checks
- ✅ System audit report available
- ✅ Enforcement tests passing
- ✅ All synthetic data clearly marked
- ✅ All estimates clearly labeled

---

**Status**: Phases 1-3 Complete, Phases 4-10 Planned  
**Next**: Implement Phases 5, 7, 9, 10 (high priority)  
**Estimated Time**: 4-6 hours remaining
