# Implementation Plan: Job Risk Predictor Enhancements

## Overview

This implementation plan breaks down the Job Risk Predictor enhancements into discrete, testable coding tasks following the phased approach (Phase 1-5). Each task builds incrementally on previous work, with property-based tests integrated throughout to validate correctness properties. The implementation uses Python with Streamlit for the UI, building upon the existing `job_risk_model.py` foundation.

## Tasks

### Phase 1: Multi-Risk Assessment (Quick Wins)

- [x] 1. Set up project structure and data models
  - Create directory structure: `src/risk_calculators/`, `src/analytics/`, `src/reporting/`, `src/ui_components/`, `src/validation/`
  - Define core data models: `UserProfile`, `RiskProfile`, `AutomationRiskResult`, `RecessionRiskResult`, `AgeDiscriminationRiskResult` in Python dataclasses
  - Create `ProfileValidator` class with validation methods for age, experience, required fields
  - _Requirements: 5.1, 5.2, 5.3_

- [ ]* 1.1 Write property tests for input validation
  - **Property 13: Age Validation Accepts Valid Range**
  - **Validates: Requirements 5.2**
  - **Property 14: Required Field Validation**
  - **Validates: Requirements 5.3**

- [ ] 2. Implement Automation Risk Calculator
  - [x] 2.1 Create `AutomationRiskCalculator` class with industry automation rates, role level resistance, and automation-resistant skills dictionaries
    - Implement `calculate()` method: start with industry base risk, adjust for role level, reduce for automation-resistant skills, normalize to 0-100
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ]* 2.2 Write property tests for automation risk
    - **Property 1: Universal Risk Score Range** (automation risk component)
    - **Validates: Requirements 1.1**
    - **Property 3: High-Demand Skills Reduce Automation Risk**
    - **Validates: Requirements 1.3**
    - **Property 4: High-Automation Industries Increase Risk**
    - **Validates: Requirements 1.4**

- [ ] 3. Implement Recession Risk Calculator
  - [x] 3.1 Create `RecessionRiskCalculator` class with industry vulnerability, company size multipliers, and experience protection curve
    - Implement `calculate()` method: start with industry vulnerability, apply company size multiplier, reduce based on experience, adjust for role level and performance rating
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 3.2 Write property tests for recession risk
    - **Property 1: Universal Risk Score Range** (recession risk component)
    - **Validates: Requirements 2.1**
    - **Property 5: Experience Reduces Recession Vulnerability**
    - **Validates: Requirements 2.3**
    - **Property 6: Small Companies Increase Recession Risk**
    - **Validates: Requirements 2.4**

- [ ] 4. Implement Age Discrimination Risk Calculator
  - [x] 4.1 Create `AgeDiscriminationRiskCalculator` class with age risk curve, industry age diversity scores, and role level protection
    - Implement `_age_risk_curve()` method: U-shaped curve with minimum at 30-50
    - Implement `calculate()` method: compute base risk from age curve, adjust for industry diversity, apply role level protection
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 4.2 Write property tests for age discrimination risk
    - **Property 1: Universal Risk Score Range** (age discrimination component)
    - **Validates: Requirements 3.1**
    - **Property 7: Age 30-50 Has Minimal Age Discrimination Risk**
    - **Validates: Requirements 3.2**
    - **Property 8: Age 55+ in Tech Increases Discrimination Risk**
    - **Validates: Requirements 3.3**
    - **Property 9: Senior Roles Reduce Age Discrimination Risk**
    - **Validates: Requirements 3.4**

- [ ] 5. Implement Risk Calculator Orchestrator
  - [x] 5.1 Create `RiskCalculatorOrchestrator` class that coordinates all risk calculators
    - Implement `calculate_all_risks()` method: execute all calculators, aggregate results into `RiskProfile`
    - Implement `get_risk_level()` method: map risk score to "Low" (0-35), "Medium" (35-62), "High" (62-100)
    - Integrate existing `job_risk_model.py` for overall risk calculation
    - _Requirements: 1.1, 2.1, 3.1_
  
  - [ ]* 5.2 Write property tests for orchestrator
    - **Property 1: Universal Risk Score Range** (all risk types)
    - **Validates: Requirements 1.1, 2.1, 3.1**
    - **Property 2: Deterministic Risk Calculation**
    - **Validates: Requirements 1.5**

- [ ] 6. Update UI with advanced input form
  - [x] 6.1 Extend Streamlit form in `pages/7_Job_Risk_Predictor.py` to include new fields
    - Add age input (numeric, 18-80)
    - Add role_level dropdown (Entry, Mid, Senior, Lead, Executive)
    - Add company_size dropdown (1-10, 11-50, 51-200, 201-1000, 1001-5000, 5000+)
    - Add remote_capability checkbox (default False)
    - Add performance_rating slider (1-5, default 3)
    - Implement form validation with specific error messages
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Create Multi-Risk Dashboard UI
  - [x] 7.1 Implement `MultiRiskDashboard` class in `src/ui_components/multi_risk_dashboard.py`
    - Create `render()` method: display 4 gauge charts in 2x2 grid (Overall, Automation, Recession, Age Discrimination)
    - Implement `_create_gauge()` method using Plotly: color-code green (0-35%), yellow (35-62%), red (62-100%)
    - Display numeric percentage values on each gauge
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ]* 7.2 Write property tests for gauge color coding
    - **Property 15: Gauge Color Coding Consistency**
    - **Validates: Requirements 6.3**

- [ ] 8. Create Risk Breakdown Chart UI
  - [ ] 8.1 Implement `RiskBreakdownChart` class in `src/ui_components/risk_breakdown_chart.py`
    - Create `render()` method: horizontal bar chart showing factor contributions
    - Sort bars by absolute contribution (descending)
    - Color-code: positive contributions red, negative contributions green
    - Display numeric values at bar ends with tooltips
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 8.2 Write property tests for risk breakdown chart
    - **Property 16: Risk Factor Bar Sorting**
    - **Validates: Requirements 7.2**
    - **Property 17: Risk Factor Bar Color Coding**
    - **Validates: Requirements 7.3**

- [x] 9. Checkpoint - Phase 1 Complete
  - Ensure all tests pass, verify multi-risk dashboard displays correctly with all four risk types
  - Ask the user if questions arise

### Phase 2: Time-Based Predictions

- [ ] 10. Implement Time Prediction Calculator
  - [ ] 10.1 Create `TimePredictionCalculator` class with automation acceleration rates, industry trend rates, skill decay/learning rates
    - Define `TimeHorizonPrediction` dataclass
    - Implement `predict_time_horizons()` method: project risk scores for 6mo, 1yr, 3yr, 5yr
    - Apply automation acceleration for automation risk
    - Apply industry trend rates for recession risk
    - Apply age progression for age discrimination risk
    - Apply skill decay or learning benefit based on `assumes_learning` parameter
    - Ensure monotonic non-decreasing unless learning modeled
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 10.2 Write property tests for time predictions
    - **Property 10: Time Predictions Are Monotonic Without Learning**
    - **Validates: Requirements 4.2, 4.5**
    - **Property 11: Declining Industries Increase Risk Over Time**
    - **Validates: Requirements 4.3**
    - **Property 12: Continuous Learning Reduces Risk Over Time**
    - **Validates: Requirements 4.4**

- [ ] 11. Create Time Horizon Chart UI
  - [ ] 11.1 Implement `TimeHorizonChart` class in `src/ui_components/time_horizon_chart.py`
    - Create `render()` method: multi-line chart with 4 lines (Overall, Automation, Recession, Age Discrimination)
    - X-axis: time horizons (6mo, 1yr, 3yr, 5yr)
    - Y-axis: risk score (0-100)
    - Color-code by risk type with markers at each time point
    - _Requirements: 4.1_

- [ ] 12. Checkpoint - Phase 2 Complete
  - Ensure all tests pass, verify time horizon predictions display correctly
  - Ask the user if questions arise

### Phase 3: Salary and Benchmarking

- [ ] 13. Implement Salary Analyzer
  - [ ] 13.1 Create `SalaryAnalyzer` class with base salary factors, location multipliers, and risk penalty rates
    - Define `SalaryEstimate` dataclass
    - Implement `analyze()` method: compute base salary from role/industry/experience, apply location multiplier, apply risk penalty if overall_risk > 30
    - Calculate confidence interval (±15%)
    - Generate explanation text
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 13.2 Write property tests for salary analysis
    - **Property 18: Location Multiplier Application**
    - **Validates: Requirements 8.2**
    - **Property 19: Risk-Adjusted Salary Formula**
    - **Validates: Requirements 8.3**

- [ ] 14. Implement Benchmark Engine
  - [ ] 14.1 Create `BenchmarkEngine` class for peer comparison
    - Define `BenchmarkResult` dataclass
    - Implement `generate_peers()` method: create 100 synthetic profiles matching industry and role_level
    - Vary skills, experience, education with realistic distributions
    - Ensure realistic variation (std dev ~15-20 points)
    - Implement `compute_benchmark()` method: calculate percentile ranking, compute quartile markers (25th, 50th, 75th, 90th)
    - Generate comparison text
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 14.2 Write property tests for benchmarking
    - **Property 20: Benchmark Peer Generation Count**
    - **Validates: Requirements 9.1**
    - **Property 21: Percentile Calculation Correctness**
    - **Validates: Requirements 9.2**
    - **Property 22: Percentile Text Accuracy**
    - **Validates: Requirements 9.4**
    - **Property 23: Peer Data Realistic Variation**
    - **Validates: Requirements 9.5**

- [ ] 15. Create Salary and Benchmark UI Components
  - [ ] 15.1 Add salary analysis display to UI
    - Show three salary values: base_estimate, location_adjusted, risk_adjusted
    - Display explanatory text with multipliers and adjustments
    - _Requirements: 8.4, 8.5_
  
  - [ ] 15.2 Implement `BenchmarkChart` class in `src/ui_components/benchmark_chart.py`
    - Create distribution chart showing user's position relative to peer risk scores
    - Display percentile markers and comparison text
    - _Requirements: 9.3, 9.4_

- [ ] 16. Checkpoint - Phase 3 Complete
  - Ensure all tests pass, verify salary analysis and benchmarking display correctly
  - Ask the user if questions arise

### Phase 4: Recommendations and Analytics

- [ ] 17. Implement Recommendation Engine
  - [ ] 17.1 Create `RecommendationEngine` class for generating prioritized recommendations
    - Define `Recommendation` dataclass
    - Implement `generate_recommendations()` method: identify improvement opportunities, estimate risk reduction and salary impact, calculate ROI score
    - Implement `_suggest_skills()` helper: suggest high-impact skills based on gaps
    - Implement `_estimate_skill_impact()` helper: estimate risk reduction and salary impact of adding a skill
    - Rank recommendations by ROI, return top 5-7
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 17.2 Write property tests for recommendations
    - **Property 24: Minimum Recommendation Count**
    - **Validates: Requirements 10.1**
    - **Property 25: Recommendation ROI Ordering**
    - **Validates: Requirements 10.1**
    - **Property 26: Recommendation Quantification Completeness**
    - **Validates: Requirements 10.2, 10.3, 10.4**

- [ ] 18. Implement Company Assessor
  - [ ] 18.1 Create `CompanyAssessor` class for company-level risk assessment
    - Define `CompanyRiskResult` dataclass
    - Implement `assess()` method: get base risk from company age curve, adjust for company size, apply industry disruption factor
    - Identify key contributing factors
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 18.2 Write property tests for company assessment
    - **Property 1: Universal Risk Score Range** (company risk component)
    - **Validates: Requirements 11.1**
    - **Property 27: Young Companies Have Higher Risk**
    - **Validates: Requirements 11.2**
    - **Property 28: Large Companies Have Lower Risk**
    - **Validates: Requirements 11.3**
    - **Property 29: Contracting Industries Increase Company Risk**
    - **Validates: Requirements 11.4**

- [ ] 19. Implement Skills Gap Analyzer
  - [ ] 19.1 Create `SkillsGapAnalyzer` class with skills database by role
    - Define `SkillGap` and `SkillsGapResult` dataclasses
    - Implement `analyze()` method: retrieve required skills for target role, normalize and compare with current skills
    - Identify missing skills by priority (Critical, Important, Nice-to-Have)
    - Estimate learning time for each gap
    - Calculate skill match percentage
    - Generate learning roadmap
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 19.2 Write property tests for skills gap analysis
    - **Property 30: Skills Gap Set Difference**
    - **Validates: Requirements 12.2**
    - **Property 31: Skills Gap Priority Assignment**
    - **Validates: Requirements 12.3**
    - **Property 32: Skill Match Percentage Range and Monotonicity**
    - **Validates: Requirements 12.5**

- [ ] 20. Implement Career Path Modeler
  - [ ] 20.1 Create `CareerPathModeler` class with career progression graph and transition requirements
    - Define `CareerTransition` and `CareerPath` dataclasses
    - Implement `model_paths()` method: use BFS to explore career graph, calculate success probability, estimate time to transition
    - Implement `_calculate_transition_probability()` helper: compute success probability based on skills, experience, education, performance
    - Return top 3-5 most viable paths
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 20.2 Write property tests for career path modeling
    - **Property 33: Minimum Career Path Count**
    - **Validates: Requirements 13.1**
    - **Property 34: Career Path Success Probability Range**
    - **Validates: Requirements 13.2**
    - **Property 35: Career Path Requirements Completeness**
    - **Validates: Requirements 13.5**

- [ ] 21. Create Analytics UI Components
  - [ ] 21.1 Add recommendations table to UI
    - Display table with columns: Action, Risk_Reduction, Salary_Impact, Time_to_Implement, ROI_Score
    - _Requirements: 10.5_
  
  - [ ] 21.2 Add company risk assessment display to UI
    - Show company_risk_score with explanatory factors
    - _Requirements: 11.5_
  
  - [ ] 21.3 Add skills gap analysis display to UI
    - Display missing skills table with Skill_Name, Priority_Level, Estimated_Learning_Time
    - Show skill_match_percentage and learning roadmap
    - _Requirements: 12.4_
  
  - [ ] 21.4 Add career path visualization to UI
    - Display career paths in visual tree or flowchart format
    - Show success probabilities and required skills for each transition
    - _Requirements: 13.4_

- [ ] 22. Checkpoint - Phase 4 Complete
  - Ensure all tests pass, verify all analytics components display correctly
  - Ask the user if questions arise

### Phase 5: Reporting and Monitoring

- [ ] 23. Implement Report Generator
  - [ ] 23.1 Create `ReportGenerator` class for creating formatted reports
    - Implement `generate_report()` method: aggregate data from all components
    - Structure report with sections: Executive_Summary, Risk_Assessment_Details, Benchmarking_Analysis, Recommendations, Career_Path_Options
    - Format with professional styling (headers, tables, charts)
    - Include timestamp and unique report identifier
    - Support TXT and HTML export formats
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [ ]* 23.2 Write property tests for report generation
    - **Property 36: Report Section Completeness**
    - **Validates: Requirements 14.1, 14.2**
    - **Property 37: Report Metadata Presence and Uniqueness**
    - **Validates: Requirements 14.4**

- [ ] 24. Implement Risk Monitor
  - [ ] 24.1 Create `RiskMonitor` class for tracking risk changes over time
    - Implement storage mechanism for historical assessments with timestamps
    - Implement history size constraint: retain only last 12 assessments
    - Implement `compute_rate_of_change()` method: calculate slope of linear regression through risk scores
    - Identify significant changes (>10 percentage points between consecutive assessments)
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ]* 24.2 Write property tests for risk monitoring
    - **Property 38: Risk History Size Constraint**
    - **Validates: Requirements 15.2**
    - **Property 39: Significant Change Detection**
    - **Validates: Requirements 15.4**
    - **Property 40: Rate of Change Calculation**
    - **Validates: Requirements 15.5**

- [ ] 25. Create Reporting and Monitoring UI Components
  - [ ] 25.1 Add report download functionality to UI
    - Provide download button for TXT and HTML formats
    - _Requirements: 14.5_
  
  - [ ] 25.2 Add risk monitoring dashboard to UI
    - Display line chart showing risk score trends over time for each risk_type
    - Highlight significant changes
    - Display rate_of_change metrics
    - _Requirements: 15.3, 15.4, 15.5_

- [ ] 26. Checkpoint - Phase 5 Complete
  - Ensure all tests pass, verify report generation and risk monitoring work correctly
  - Ask the user if questions arise

### Future Phase 6: Real Data Integration (Preparation)

- [ ] 27. Implement Data Provider Interfaces
  - [ ] 27.1 Create abstract provider interfaces in `src/data_providers/interfaces.py`
    - Define `JobMarketDataProvider` abstract class with methods: `fetch_job_postings()`, `get_skill_demand_trends()`, `get_last_update_timestamp()`
    - Define `EconomicIndicatorProvider` abstract class with methods: `get_unemployment_rate()`, `get_gdp_growth()`, `get_industry_gdp_growth()`, `get_inflation_rate()`
    - _Requirements: 16.1, 17.1_
  
  - [ ] 27.2 Implement synthetic/static providers
    - Create `SyntheticJobMarketProvider` using existing CSV data
    - Create `StaticEconomicProvider` with baseline values
    - _Requirements: 16.1, 17.1_
  
  - [ ] 27.3 Implement caching layer
    - Create `DataCache` class with TTL support
    - Implement fallback logic for API failures
    - _Requirements: 16.5_
  
  - [ ] 27.4 Create `DataProviderFactory` for provider instantiation
    - Implement factory methods based on configuration
    - _Requirements: 16.1, 17.1_
  
  - [ ]* 27.5 Write property tests for data integration
    - **Property 41: Skill Demand Weight Update from Job Postings**
    - **Validates: Requirements 16.2**
    - **Property 42: Unemployment Rate Threshold Effect**
    - **Validates: Requirements 17.2**
    - **Property 43: GDP Growth Industry Adjustment**
    - **Validates: Requirements 17.3**

- [ ] 28. Update Risk Calculators for Data Integration
  - [ ] 28.1 Modify `RecessionRiskCalculator` to accept `EconomicIndicatorProvider`
    - Adjust risk based on current unemployment rate (>6% adds 5+ points)
    - Adjust for industry-specific GDP growth
    - _Requirements: 17.2, 17.3_
  
  - [ ] 28.2 Modify `AutomationRiskCalculator` to accept `JobMarketDataProvider`
    - Update skill demand weights from job posting data
    - _Requirements: 16.2_
  
  - [ ] 28.3 Add data freshness indicators to UI
    - Display last update timestamp
    - Show warning if using cached/fallback data
    - _Requirements: 16.4, 16.5_

- [ ] 29. Final Integration and Testing
  - [ ] 29.1 Wire all components together in main Streamlit page
    - Integrate all calculators, analytics, reporting, and monitoring
    - Ensure smooth data flow from input form through all components
    - Add loading states and progress indicators
  
  - [ ]* 29.2 Run comprehensive integration tests
    - Test end-to-end flow with various user profiles
    - Verify all risk scores, analytics, and reports generate correctly
    - Test error handling and validation
  
  - [ ]* 29.3 Run all property-based tests
    - Execute full property test suite (43 properties)
    - Verify all correctness properties hold across generated test cases
    - Fix any property violations discovered

- [ ] 30. Final Checkpoint - Implementation Complete
  - Ensure all tests pass (unit, integration, property-based)
  - Verify all features work as specified in requirements
  - Ask the user if questions arise or if any adjustments are needed

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at the end of each phase
- Property tests validate universal correctness properties from the design document
- The implementation follows a phased approach allowing for incremental delivery
- Phase 6 (Real Data Integration) is prepared but not fully implemented in this plan
- All code should include type hints and docstrings for maintainability
- Use `@st.cache_data` decorator for expensive computations in Streamlit
- Ensure backward compatibility with existing `job_risk_model.py`
