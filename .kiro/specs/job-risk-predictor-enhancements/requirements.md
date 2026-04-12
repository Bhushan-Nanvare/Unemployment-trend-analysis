# Requirements Document

## Introduction

This document specifies requirements for comprehensive enhancements to the existing Job Risk Predictor application. The enhancements add multiple risk assessment types (automation, recession, age discrimination), time-based predictions, advanced UI components, real data integration with salary analysis and industry benchmarking, advanced analytics including company risk and skills gap analysis, and professional reporting capabilities. The implementation follows a phased approach prioritizing quick wins (Phase 1) through advanced features (Phases 2-5), with future data integration (Phase 6).

## Glossary

- **Risk_Calculator**: The core component that computes risk scores and predictions
- **UI_Dashboard**: The Streamlit-based user interface displaying risk assessments
- **Risk_Type**: A category of risk assessment (Overall, Automation, Recession, Age_Discrimination)
- **Time_Horizon**: A future time period for risk prediction (6 months, 1 year, 3 years, 5 years)
- **Gauge_Chart**: A visual component displaying risk percentage as a semicircular gauge
- **Risk_Factor**: An input variable affecting risk calculation (skills, industry, role_level, company_size, age, experience, remote_capability, performance_rating)
- **Salary_Analyzer**: Component calculating location-based salary adjustments and risk impacts
- **Benchmark_Engine**: Component comparing user profile against synthetic peer data
- **Recommendation_Engine**: Component generating actionable suggestions with quantified ROI
- **Company_Assessor**: Component evaluating company-level risk factors
- **Skills_Gap_Analyzer**: Component identifying differences between current and target role requirements
- **Career_Path_Modeler**: Component showing progression paths with success probabilities
- **Report_Generator**: Component creating professional formatted reports
- **Risk_Monitor**: Component tracking risk changes over time

## Requirements

### Requirement 1: Automation Risk Assessment

**User Story:** As a user, I want to assess my automation risk based on my skills, industry, and role level, so that I can understand how likely my job is to be automated.

#### Acceptance Criteria

1. WHEN a user provides skills, industry, and role_level, THE Risk_Calculator SHALL compute an automation_risk_score between 0 and 100
2. THE Risk_Calculator SHALL assign higher automation_risk_score values to roles with repetitive tasks and lower values to roles requiring creativity or complex decision-making
3. THE Risk_Calculator SHALL reduce automation_risk_score by at least 10 percentage points when high-demand technical skills are present
4. THE Risk_Calculator SHALL increase automation_risk_score by at least 15 percentage points for industries with high automation adoption rates
5. FOR ALL valid user profiles, THE automation_risk_score SHALL be deterministic given identical inputs

### Requirement 2: Recession Vulnerability Assessment

**User Story:** As a user, I want to assess my recession vulnerability based on industry, role, company size, and experience, so that I can understand my job security during economic downturns.

#### Acceptance Criteria

1. WHEN a user provides industry, role, company_size, and experience_years, THE Risk_Calculator SHALL compute a recession_vulnerability_score between 0 and 100
2. THE Risk_Calculator SHALL assign lower recession_vulnerability_score values to essential industries (healthcare, utilities) and higher values to discretionary industries (hospitality, luxury retail)
3. THE Risk_Calculator SHALL reduce recession_vulnerability_score by at least 5 percentage points for each 5 years of experience up to 20 years
4. THE Risk_Calculator SHALL increase recession_vulnerability_score by at least 12 percentage points for company_size values indicating startups or small businesses (fewer than 50 employees)
5. THE Risk_Calculator SHALL assign lower recession_vulnerability_score values to senior roles compared to junior roles within the same industry

### Requirement 3: Age Discrimination Risk Assessment

**User Story:** As a user, I want to assess my age discrimination risk based on my age, industry, and role level, so that I can understand potential hiring or retention challenges.

#### Acceptance Criteria

1. WHEN a user provides age, industry, and role_level, THE Risk_Calculator SHALL compute an age_discrimination_risk_score between 0 and 100
2. THE Risk_Calculator SHALL assign minimal age_discrimination_risk_score values (below 15) for ages between 30 and 50
3. THE Risk_Calculator SHALL increase age_discrimination_risk_score by at least 8 percentage points for ages above 55 in technology-focused industries
4. THE Risk_Calculator SHALL reduce age_discrimination_risk_score by at least 10 percentage points when role_level indicates senior or executive positions
5. THE Risk_Calculator SHALL assign lower age_discrimination_risk_score values to industries with established age diversity practices

### Requirement 4: Time-Based Risk Predictions

**User Story:** As a user, I want to see risk predictions for multiple time horizons (6 months, 1 year, 3 years, 5 years), so that I can plan my career development strategically.

#### Acceptance Criteria

1. WHEN a user requests risk predictions, THE Risk_Calculator SHALL compute risk scores for four time_horizon values: 6 months, 1 year, 3 years, and 5 years
2. THE Risk_Calculator SHALL increase risk scores progressively for longer time_horizon values when automation trends are present
3. THE Risk_Calculator SHALL model risk score increases of at least 5 percentage points per year for roles in declining industries
4. THE Risk_Calculator SHALL model risk score decreases of at least 3 percentage points per year when continuous skill development is indicated
5. FOR ALL time_horizon predictions, THE Risk_Calculator SHALL maintain monotonic non-decreasing risk values unless skill improvement is modeled

### Requirement 5: Advanced Input Form

**User Story:** As a user, I want to provide detailed profile information including age, role level, company size, remote work capability, and performance rating, so that I receive more accurate risk assessments.

#### Acceptance Criteria

1. THE UI_Dashboard SHALL display input fields for age (numeric, 18-80), role_level (dropdown with 5 levels), company_size (dropdown with 6 categories), remote_capability (boolean), and performance_rating (scale 1-5)
2. WHEN a user submits the advanced form, THE UI_Dashboard SHALL validate that age is between 18 and 80
3. WHEN a user submits the advanced form, THE UI_Dashboard SHALL validate that all required fields contain values
4. THE UI_Dashboard SHALL provide default values for optional fields (remote_capability defaults to False, performance_rating defaults to 3)
5. WHEN validation fails, THE UI_Dashboard SHALL display specific error messages indicating which fields require correction

### Requirement 6: Multi-Risk Dashboard

**User Story:** As a user, I want to see a dashboard with four gauge charts showing Overall, Automation, Recession, and Age discrimination risks, so that I can quickly understand my risk profile across multiple dimensions.

#### Acceptance Criteria

1. THE UI_Dashboard SHALL display four gauge_chart components arranged in a 2x2 grid layout
2. WHEN risk calculations complete, THE UI_Dashboard SHALL render each gauge_chart with the corresponding risk score (Overall, Automation, Recession, Age_Discrimination)
3. THE UI_Dashboard SHALL color-code each gauge_chart using green (0-35%), yellow (35-62%), and red (62-100%) ranges
4. THE UI_Dashboard SHALL display numeric percentage values overlaid on each gauge_chart
5. THE UI_Dashboard SHALL update all four gauge_chart components simultaneously when user inputs change

### Requirement 7: Risk Breakdown Analysis

**User Story:** As a user, I want to see a horizontal bar chart showing how different risk factors contribute to my overall risk, so that I can identify which factors to address first.

#### Acceptance Criteria

1. THE UI_Dashboard SHALL display a horizontal bar chart showing contribution values for at least 8 risk_factor categories
2. THE UI_Dashboard SHALL sort risk_factor bars in descending order by absolute contribution value
3. THE UI_Dashboard SHALL color-code bars with positive contributions (increasing risk) in red and negative contributions (decreasing risk) in green
4. THE UI_Dashboard SHALL display numeric contribution values at the end of each bar
5. WHEN a user hovers over a bar, THE UI_Dashboard SHALL display a tooltip with the risk_factor name and detailed explanation

### Requirement 8: Salary Impact Analysis

**User Story:** As a user, I want to see how my location and risk profile affect my expected salary, so that I can make informed decisions about relocation or career changes.

#### Acceptance Criteria

1. WHEN a user provides location and profile data, THE Salary_Analyzer SHALL compute a base_salary_estimate based on role, industry, and experience
2. THE Salary_Analyzer SHALL apply location-based multipliers ranging from 0.70 (low cost areas) to 1.50 (high cost metro areas)
3. THE Salary_Analyzer SHALL compute a risk_adjusted_salary by reducing base_salary_estimate by 2 percentage points for each 10 points of overall risk score above 30
4. THE Salary_Analyzer SHALL display three salary values: base_estimate, location_adjusted, and risk_adjusted
5. THE Salary_Analyzer SHALL provide explanatory text describing the multipliers and adjustments applied

### Requirement 9: Industry Benchmarking

**User Story:** As a user, I want to compare my risk profile against synthetic peer data in my industry, so that I can understand how I rank relative to others.

#### Acceptance Criteria

1. WHEN a user requests benchmarking, THE Benchmark_Engine SHALL generate synthetic peer data for at least 100 profiles matching the user's industry and role_level
2. THE Benchmark_Engine SHALL compute percentile rankings (25th, 50th, 75th, 90th) for the user's risk score within the peer group
3. THE UI_Dashboard SHALL display a distribution chart showing the user's position relative to peer risk scores
4. THE UI_Dashboard SHALL display numeric percentile values indicating where the user ranks (e.g., "You are in the 35th percentile - lower risk than 65% of peers")
5. THE Benchmark_Engine SHALL ensure synthetic peer data reflects realistic variation in skills, experience, and risk factors

### Requirement 10: Actionable Recommendations with ROI

**User Story:** As a user, I want to receive specific recommendations with quantified risk reduction and salary impact, so that I can prioritize actions with the highest return on investment.

#### Acceptance Criteria

1. WHEN risk assessment completes, THE Recommendation_Engine SHALL generate at least 3 actionable recommendations ranked by estimated ROI
2. THE Recommendation_Engine SHALL quantify risk_reduction for each recommendation in percentage points (e.g., "Reduces overall risk by 8-12 points")
3. THE Recommendation_Engine SHALL estimate salary_impact for each recommendation in percentage or absolute currency values (e.g., "+$5,000 to $8,000 annually")
4. THE Recommendation_Engine SHALL estimate time_to_implement for each recommendation in weeks or months (e.g., "3-6 months")
5. THE UI_Dashboard SHALL display recommendations in a table with columns for Action, Risk_Reduction, Salary_Impact, Time_to_Implement, and ROI_Score

### Requirement 11: Company Risk Assessment

**User Story:** As a user, I want to assess the risk level of my current or prospective employer based on company size, industry, and age, so that I can evaluate job stability.

#### Acceptance Criteria

1. WHEN a user provides company_size, industry, and company_age, THE Company_Assessor SHALL compute a company_risk_score between 0 and 100
2. THE Company_Assessor SHALL assign higher company_risk_score values to companies younger than 3 years (startup phase)
3. THE Company_Assessor SHALL assign lower company_risk_score values to companies with more than 1,000 employees
4. THE Company_Assessor SHALL increase company_risk_score by at least 10 percentage points for industries experiencing contraction or disruption
5. THE UI_Dashboard SHALL display company_risk_score alongside individual risk scores with explanatory factors

### Requirement 12: Skills Gap Analysis

**User Story:** As a user, I want to identify the gap between my current skills and target role requirements, so that I can create a focused learning plan.

#### Acceptance Criteria

1. WHEN a user selects a target_role, THE Skills_Gap_Analyzer SHALL retrieve required skills for that role from a predefined skills database
2. THE Skills_Gap_Analyzer SHALL compare the user's current skills against target_role requirements and identify missing skills
3. THE Skills_Gap_Analyzer SHALL categorize missing skills into three priority levels: Critical (required for role), Important (strongly preferred), and Nice_to_Have (beneficial)
4. THE UI_Dashboard SHALL display missing skills in a table with columns for Skill_Name, Priority_Level, and Estimated_Learning_Time
5. THE Skills_Gap_Analyzer SHALL compute an overall skill_match_percentage indicating how closely the user's profile matches the target_role

### Requirement 13: Career Path Modeling

**User Story:** As a user, I want to see possible career progression paths from my current role with success probabilities, so that I can plan my career trajectory.

#### Acceptance Criteria

1. WHEN a user requests career path modeling, THE Career_Path_Modeler SHALL identify at least 3 possible progression paths based on current role and industry
2. THE Career_Path_Modeler SHALL compute a success_probability for each path based on the user's current skills, experience, and education
3. THE Career_Path_Modeler SHALL estimate time_to_transition for each path in years (e.g., "2-4 years")
4. THE UI_Dashboard SHALL display career paths in a visual tree or flowchart format with nodes representing roles and edges representing transitions
5. THE Career_Path_Modeler SHALL identify required skill acquisitions or certifications needed for each transition

### Requirement 14: Executive Summary Report

**User Story:** As a user, I want to generate a professional executive summary report with PDF-style formatting, so that I can share my risk assessment with advisors or keep for records.

#### Acceptance Criteria

1. WHEN a user requests a report, THE Report_Generator SHALL create a formatted document containing all risk scores, benchmarking data, and recommendations
2. THE Report_Generator SHALL structure the report with sections: Executive_Summary, Risk_Assessment_Details, Benchmarking_Analysis, Recommendations, and Career_Path_Options
3. THE Report_Generator SHALL format the report with professional styling including headers, tables, and charts
4. THE Report_Generator SHALL include a timestamp and unique report identifier on each generated report
5. THE UI_Dashboard SHALL provide a download button that exports the report in both TXT and HTML formats

### Requirement 15: Risk Monitoring Dashboard

**User Story:** As a user, I want to track how my risk scores change over time as I update my profile, so that I can measure the effectiveness of my career development actions.

#### Acceptance Criteria

1. WHEN a user completes a risk assessment, THE Risk_Monitor SHALL store the assessment results with a timestamp
2. THE Risk_Monitor SHALL maintain a history of at least the last 12 assessments per user
3. THE UI_Dashboard SHALL display a line chart showing risk score trends over time for each risk_type
4. THE UI_Dashboard SHALL highlight significant changes (more than 10 percentage points) between consecutive assessments
5. THE Risk_Monitor SHALL compute and display the rate_of_change in risk scores (e.g., "Risk decreased by 3 points per month over the last quarter")

### Requirement 16: Real Job Market Data Integration (Future)

**User Story:** As a user, I want the system to incorporate real-time job posting data, so that risk assessments reflect current market conditions.

#### Acceptance Criteria

1. WHERE real-time job market data integration is enabled, WHEN the system initializes, THE Risk_Calculator SHALL fetch job posting data from configured API sources
2. WHERE real-time job market data integration is enabled, THE Risk_Calculator SHALL update skill demand weights based on keyword frequency in recent job postings
3. WHERE real-time job market data integration is enabled, THE Risk_Calculator SHALL refresh job market data at least once per week
4. WHERE real-time job market data integration is enabled, THE UI_Dashboard SHALL display a data freshness indicator showing the last update timestamp
5. WHERE real-time job market data integration is enabled, IF API calls fail, THEN THE Risk_Calculator SHALL fall back to cached data and display a warning message

### Requirement 17: Economic Indicators Integration (Future)

**User Story:** As a user, I want the system to incorporate economic indicators like unemployment rate, GDP growth, and inflation, so that recession vulnerability assessments reflect macroeconomic conditions.

#### Acceptance Criteria

1. WHERE economic indicators integration is enabled, WHEN computing recession_vulnerability_score, THE Risk_Calculator SHALL incorporate current unemployment_rate data
2. WHERE economic indicators integration is enabled, THE Risk_Calculator SHALL increase recession_vulnerability_score by at least 5 percentage points when unemployment_rate exceeds 6%
3. WHERE economic indicators integration is enabled, THE Risk_Calculator SHALL adjust industry_growth factors based on GDP_growth trends for each sector
4. WHERE economic indicators integration is enabled, THE UI_Dashboard SHALL display current economic indicators in a summary panel
5. WHERE economic indicators integration is enabled, THE Risk_Calculator SHALL refresh economic indicator data at least once per month

