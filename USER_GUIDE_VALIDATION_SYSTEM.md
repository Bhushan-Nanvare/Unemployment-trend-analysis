# User Guide: Data Quality Validation System

**For**: End Users of Unemployment Intelligence Platform  
**Date**: 2026-04-13  
**Version**: 1.0

---

## 🎯 What is the Validation System?

The **Data Quality Validation System** automatically checks all data used in the platform and shows you how reliable it is. You'll see quality scores, data sources, and any warnings about the data.

---

## 📊 What You'll See

### **1. Data Quality Dashboard**

At the top of the Overview page, you'll see a quality dashboard:

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔍 Data Quality Dashboard                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Unemployment Data       Inflation Data       System Health     │
│  🟢 Excellent (100/100)  🟢 Excellent (98/100)  ✅ HEALTHY      │
│  India Unemployment      India Inflation                        │
│  (Realistic)             (Corrected)                            │
│                                                                  │
│  All data automatically validated on load                       │
└──────────────────────────────────────────────────────────────────┘
```

**What This Means**:
- **Quality Score**: 0-100 scale showing data reliability
- **Data Source**: Where the data comes from
- **System Health**: Overall system status

### **2. Quality Indicators**

You'll see colored indicators throughout the platform:

- 🟢 **Green (90-100)**: Excellent quality - highly reliable
- 🟡 **Yellow (70-89)**: Good quality - generally reliable
- 🔴 **Red (0-69)**: Poor quality - use with caution

### **3. Sidebar Quality Summary**

In the sidebar (left side), you'll always see a compact quality summary:

```
┌──────────────────────────┐
│ 🔍 Data Quality          │
├──────────────────────────┤
│ Unemployment:  🟢 100/100│
│ Inflation:     🟢 98/100 │
│ System:        ✅ HEALTHY│
└──────────────────────────┘
```

This stays visible as you navigate, so you always know the data quality.

### **4. Validation Warnings**

If there are any issues with the data, you'll see a warning panel:

```
┌──────────────────────────────────────────────────────────────────┐
│ ⚠️ Validation Warnings                                           │
├──────────────────────────────────────────────────────────────────┤
│ • ⚠️ WARNING: 3 missing values (10.0%)                           │
│ • ℹ️ INFO: 2 statistical outliers detected                      │
└──────────────────────────────────────────────────────────────────┘
```

**Types of Warnings**:
- ⚠️ **WARNING**: Something to be aware of, but not critical
- ℹ️ **INFO**: Informational message, no action needed
- ❌ **ERROR**: Critical issue, data may be unreliable

---

## 🔍 Understanding Quality Scores

### **What the Scores Mean**

**100/100 - Perfect**:
- All data present and validated
- No errors or issues
- Highly reliable

**90-99 - Excellent**:
- Minor issues (e.g., 1-2 outliers)
- Still very reliable
- Safe to use

**80-89 - Good**:
- Some minor issues
- Generally reliable
- Use with awareness

**70-79 - Fair**:
- Several issues present
- Use with caution
- Check warnings

**Below 70 - Poor**:
- Significant issues
- Use with extreme caution
- Review warnings carefully

### **Current Platform Scores**

**Unemployment Data**: 100/100 🟢
- Source: Curated PLFS/CMIE data
- 34 years of data (1991-2024)
- No missing values
- All values validated

**Inflation Data**: 98.2/100 🟢
- Source: Corrected RBI CPI data
- 34 years of data (1991-2024)
- No missing values
- 3 minor YoY volatility warnings (expected)

**System Health**: ✅ HEALTHY
- All systems operational
- All quality checks passing
- No critical issues

---

## 📋 Data Sources

### **Unemployment Data**
- **Source**: India Unemployment (Realistic)
- **Authority**: PLFS/CMIE (curated)
- **Quality Level**: HIGH
- **Last Updated**: 2024
- **Notes**: COVID peak corrected to 7.1% annual average (not 23.5% monthly)

### **Inflation Data**
- **Source**: India Inflation (Corrected)
- **Authority**: RBI CPI Data (curated)
- **Quality Level**: HIGH
- **Last Updated**: 2024
- **Notes**: Realistic ranges 3.4-13.9%, not 20%+

---

## ❓ Frequently Asked Questions

### **Q: What does "HEALTHY" system health mean?**
A: It means all data quality checks are passing, scores are above 70%, and there are no critical errors. The system is operating normally.

### **Q: Should I trust data with a score of 75?**
A: Yes, but be aware of the warnings. A score of 75 means the data is generally reliable but has some issues. Check the validation warnings to understand what they are.

### **Q: What if I see a red indicator (🔴)?**
A: Red indicators mean the data quality is poor (below 70%). You should review the validation warnings carefully and use the data with caution. Consider the limitations when interpreting results.

### **Q: Why do I see warnings about "YoY violations"?**
A: YoY (Year-over-Year) violations mean the data changed more than expected from one year to the next. This can happen during economic shocks (like COVID-19) and is sometimes expected. Check if the warning explains why.

### **Q: Can I hide the quality indicators?**
A: No, the quality indicators are always visible to ensure transparency. This helps you make informed decisions about the data you're using.

### **Q: What does "automatically validated on load" mean?**
A: Every time data is loaded, the system automatically checks it for errors, missing values, outliers, and other issues. You don't need to do anything - it happens automatically.

### **Q: How often are quality scores updated?**
A: Quality scores are calculated every time data is loaded. If the underlying data changes, the scores will update automatically.

---

## 🎓 Best Practices

### **When Using the Platform**

1. **Check Quality Scores First**
   - Always look at the quality dashboard before using insights
   - Understand the data quality before making decisions

2. **Read Validation Warnings**
   - If warnings are present, read them carefully
   - Understand what they mean for your use case

3. **Consider Data Sources**
   - Know where the data comes from
   - Understand the authority and quality level

4. **Use Appropriate Caution**
   - High scores (90+): Use confidently
   - Medium scores (70-89): Use with awareness
   - Low scores (<70): Use with extreme caution

5. **Report Issues**
   - If you see unexpected quality scores, report them
   - Help improve the system by providing feedback

---

## 🔧 Technical Details (For Advanced Users)

### **Validation Rules**

**Unemployment Data**:
- Range: 2.0% - 10.0%
- Realistic range: 3.0% - 8.0%
- Max YoY change: 3.0 percentage points
- COVID year max: 8.0% (annual average)

**Inflation Data**:
- Range: 2.0% - 15.0%
- Realistic range: 3.0% - 14.0%
- Max YoY change: 5.0 percentage points

**Quality Scoring**:
- Base score: 100
- Missing values: -0.5 per % missing
- Invalid values: -30 for all invalid
- YoY violations: -20 for all violations
- Minimum score: 0
- Maximum score: 100

### **System Health Criteria**

**HEALTHY**:
- All quality scores ≥ 70%
- No critical errors
- All validation checks passing

**DEGRADED**:
- Some quality scores 50-69%
- Minor errors present
- Most validation checks passing

**CRITICAL**:
- Quality scores < 50%
- Critical errors present
- Validation checks failing

---

## 📞 Support

### **Need Help?**

If you have questions about the validation system:
1. Check this guide first
2. Review the validation warnings
3. Contact support with specific questions

### **Reporting Issues**

If you notice:
- Incorrect quality scores
- Missing validation warnings
- System health issues
- Other data quality concerns

Please report them with:
- Page you were on
- Quality scores shown
- What you expected vs. what you saw
- Screenshots if possible

---

## 🎉 Summary

The Data Quality Validation System helps you:
- ✅ See data quality immediately
- ✅ Understand data reliability
- ✅ Make informed decisions
- ✅ Trust the platform more
- ✅ Use data appropriately

**Current Status**: ✅ All systems operational, quality scores excellent (100/100, 98.2/100)

---

**Last Updated**: 2026-04-13  
**Version**: 1.0  
**For Questions**: Contact platform support
