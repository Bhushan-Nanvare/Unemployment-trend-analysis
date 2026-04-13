# 🔧 NAMING ISSUE FIX PROPOSAL

**Issue Identified By User:** The `recession_risk.py` module is misnamed.

---

## 🎯 THE PROBLEM

### Current Naming (WRONG):
```
Module: recession_risk.py
Class: RecessionRiskCalculator
Output: "Recession Risk Score"
```

**Problem:** This suggests the system predicts if a recession will happen (macroeconomic), but it actually calculates individual job vulnerability during a recession (microeconomic).

---

## ✅ PROPOSED FIX

### Option 1: Recession Vulnerability (RECOMMENDED)
```
Module: recession_vulnerability.py
Class: RecessionVulnerabilityCalculator
Output: "Recession Vulnerability Score"
Description: "How vulnerable is your job during an economic downturn?"
```

### Option 2: Layoff Risk
```
Module: layoff_risk.py
Class: LayoffRiskCalculator
Output: "Layoff Risk Score"
Description: "Risk of job loss during economic recession"
```

### Option 3: Job Security (Recession)
```
Module: job_security_recession.py
Class: JobSecurityRecessionCalculator
Output: "Job Security Score (Recession)"
Description: "Job security during economic downturns"
```

---

## 📊 COMPARISON: WHAT EACH TERM MEANS

| Term | What It Implies | Correct Usage? |
|------|----------------|----------------|
| **Recession Risk** | Probability of recession happening | ❌ Wrong for this module |
| **Recession Vulnerability** | Individual vulnerability during recession | ✅ Correct |
| **Layoff Risk** | Risk of being laid off | ✅ Correct |
| **Job Security (Recession)** | How secure your job is during recession | ✅ Correct |

---

## 🔄 WHAT NEEDS TO BE CHANGED

### Files to Rename/Update:
1. `src/risk_calculators/recession_risk.py` → `recession_vulnerability.py`
2. Class name: `RecessionRiskCalculator` → `RecessionVulnerabilityCalculator`
3. Dataclass: `RecessionRiskResult` → `RecessionVulnerabilityResult`
4. Variable names throughout codebase
5. UI labels in Streamlit pages
6. Documentation

### Estimated Changes:
- 1 file rename
- ~10 class/variable renames
- ~5 UI label updates
- ~3 documentation updates

---

## 💡 RECOMMENDED APPROACH

### Phase 1: Add Alias (Backward Compatible)
```python
# In recession_vulnerability.py
class RecessionVulnerabilityCalculator:
    """Calculates job vulnerability during economic recessions"""
    pass

# Backward compatibility alias
RecessionRiskCalculator = RecessionVulnerabilityCalculator
```

### Phase 2: Update UI Labels
```python
# In Streamlit pages
st.metric("Recession Vulnerability", f"{score}%")
st.caption("How vulnerable is your job during an economic downturn?")
```

### Phase 3: Update Documentation
- Change all references from "Recession Risk" to "Recession Vulnerability"
- Add clarification: "This measures individual job security, not recession probability"

### Phase 4: Deprecate Old Names (Future)
- Add deprecation warnings
- Remove aliases in next major version

---

## 🎯 CORRECT TERMINOLOGY

### What This Module ACTUALLY Calculates:

**Individual Job Vulnerability During Recession**

Factors:
- ✅ Industry vulnerability (some industries hit harder)
- ✅ Company size (small companies more vulnerable)
- ✅ Experience (more experience = more protection)
- ✅ Role level (senior roles more protected)
- ✅ Performance (high performers retained)
- ✅ Remote capability (more flexibility)

**Output:** Score 0-100 indicating how likely you are to lose your job IF a recession happens.

---

## 🔍 WHAT "RECESSION RISK" SHOULD MEAN

If we wanted to calculate actual "Recession Risk" (macroeconomic), we would use:

### Macroeconomic Indicators:
- GDP growth rate (declining = higher risk)
- Unemployment rate (rising = higher risk)
- Inflation rate (extreme values = higher risk)
- Yield curve inversion (inverted = higher risk)
- Consumer confidence index (falling = higher risk)
- Stock market volatility (high = higher risk)

**Output:** Probability that a recession will occur in next 6-12 months.

**This is NOT what the current module does!**

---

## ✅ RECOMMENDATION

**Rename to "Recession Vulnerability" because:**

1. ✅ Accurately describes what it calculates
2. ✅ Avoids confusion with macroeconomic recession prediction
3. ✅ Aligns with user's mental model
4. ✅ More intuitive for end users
5. ✅ Consistent with other risk calculators (automation, age discrimination)

---

## 🎯 SUMMARY

**User is correct:** The module is misnamed.

**Current:** "Recession Risk" (implies macro prediction)  
**Should Be:** "Recession Vulnerability" (individual job security)

**Impact:** Medium (naming confusion, but functionality is correct)  
**Priority:** High (affects user understanding)  
**Effort:** Low (mostly renaming, no logic changes)

---

**Next Steps:**
1. Get user confirmation on preferred naming
2. Create rename script
3. Update all references
4. Update UI labels
5. Update documentation
6. Test thoroughly

---

**User Feedback:** ✅ Correct identification of naming issue  
**Status:** Awaiting decision on preferred terminology
