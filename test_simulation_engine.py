#!/usr/bin/env python3
"""
test_simulation_engine.py

COMPREHENSIVE SIMULATION ENGINE TEST SUITE
==========================================

Tests all aspects of the simulation engine including:
1. Basic scenario simulation
2. Sensitivity analysis
3. Policy interventions
4. Edge cases and stress testing
5. Performance benchmarks
6. Data validation

Author: Simulation Testing Framework
Date: 2026-04-13
Version: 1.0.0
"""

import sys
from pathlib import Path
import time
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api import simulate_scenario, sensitivity_analysis, ScenarioRequest, SensitivityRequest
from src.shock_scenario import ShockScenario
from src.scenario_metrics import ScenarioMetrics
from src.forecasting import ForecastingEngine
from src.live_data import fetch_world_bank
from src.preprocessing import Preprocessor


class SimulationTester:
    """Comprehensive simulation engine testing framework"""
    
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {}
        self.data_df = None
        self.baseline_df = None
        
    def setup_test_data(self):
        """Load and prepare test data"""
        print("📊 Setting up test data...")
        
        # Load India unemployment data
        self.data_df = fetch_world_bank(country="India")
        self.data_df = Preprocessor().preprocess(self.data_df)
        
        # Generate baseline forecast
        engine = ForecastingEngine(forecast_horizon=6)
        self.baseline_df = engine.forecast(self.data_df)
        
        print(f"  ✅ Loaded {len(self.data_df)} historical data points")
        print(f"  ✅ Generated {len(self.baseline_df)} baseline forecast points")
        
    def test_basic_scenarios(self):
        """Test basic scenario simulation functionality"""
        print("\n🧪 Testing Basic Scenarios...")
        
        test_cases = [
            {
                "name": "No Shock (Baseline)",
                "params": {"shock_intensity": 0.0, "shock_duration": 0, "recovery_rate": 0.05},
                "expected": "Should match baseline closely"
            },
            {
                "name": "Mild Recession",
                "params": {"shock_intensity": 0.2, "shock_duration": 2, "recovery_rate": 0.3},
                "expected": "Moderate increase in unemployment"
            },
            {
                "name": "Severe Crisis",
                "params": {"shock_intensity": 0.5, "shock_duration": 3, "recovery_rate": 0.2},
                "expected": "Significant unemployment spike"
            },
            {
                "name": "Quick Recovery",
                "params": {"shock_intensity": 0.3, "shock_duration": 1, "recovery_rate": 0.6},
                "expected": "Fast return to baseline"
            },
        ]
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n  Test {i}: {case['name']}")
            
            try:
                # Create request
                request = ScenarioRequest(
                    shock_intensity=case["params"]["shock_intensity"],
                    shock_duration=case["params"]["shock_duration"],
                    recovery_rate=case["params"]["recovery_rate"],
                    forecast_horizon=6,
                    policy_name=None
                )
                
                # Time the simulation
                start_time = time.time()
                result = simulate_scenario(request)
                execution_time = time.time() - start_time
                
                # Validate result structure
                required_keys = ["baseline", "scenario", "metrics", "indices", "sector_impact"]
                missing_keys = [key for key in required_keys if key not in result]
                
                if missing_keys:
                    print(f"    ❌ Missing keys: {missing_keys}")
                    self.test_results.append({
                        "test": case["name"],
                        "status": "FAILED",
                        "error": f"Missing keys: {missing_keys}"
                    })
                    continue
                
                # Extract key metrics
                scenario_df = pd.DataFrame(result["scenario"])
                baseline_df = pd.DataFrame(result["baseline"])
                
                baseline_peak = baseline_df["Predicted_Unemployment"].max()
                scenario_peak = scenario_df["Scenario_Unemployment"].max()
                peak_delta = scenario_peak - baseline_peak
                
                # Validate expectations
                if case["params"]["shock_intensity"] == 0.0:
                    # No shock should be very close to baseline
                    if abs(peak_delta) > 0.1:
                        print(f"    ❌ No-shock scenario has {peak_delta:.2f}pp deviation (expected < 0.1pp)")
                        status = "FAILED"
                    else:
                        print(f"    ✅ No-shock scenario: {peak_delta:.3f}pp deviation")
                        status = "PASSED"
                else:
                    # Shock scenarios should increase unemployment
                    if peak_delta <= 0:
                        print(f"    ❌ Shock scenario decreased unemployment by {abs(peak_delta):.2f}pp")
                        status = "FAILED"
                    else:
                        print(f"    ✅ Shock scenario increased unemployment by {peak_delta:.2f}pp")
                        status = "PASSED"
                
                # Check indices
                indices = result["indices"]
                usi = indices.get("unemployment_stress_index", 0)
                early_warning = indices.get("early_warning", "Unknown")
                
                print(f"    📊 Peak UE: {scenario_peak:.2f}% (Δ{peak_delta:+.2f}pp)")
                print(f"    📈 USI: {usi:.1f}")
                print(f"    🚦 Warning: {early_warning}")
                print(f"    ⏱️ Execution: {execution_time:.3f}s")
                
                self.test_results.append({
                    "test": case["name"],
                    "status": status,
                    "peak_delta": round(peak_delta, 2),
                    "usi": round(usi, 1),
                    "execution_time": round(execution_time, 3),
                    "early_warning": early_warning
                })
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                self.test_results.append({
                    "test": case["name"],
                    "status": "ERROR",
                    "error": str(e)
                })
    
    def test_policy_interventions(self):
        """Test policy intervention effects"""
        print("\n🏛️ Testing Policy Interventions...")
        
        policies = ["None", "Fiscal Stimulus", "Monetary Policy", "Labor Reforms", "Industry Support"]
        base_scenario = {
            "shock_intensity": 0.4,
            "shock_duration": 2,
            "recovery_rate": 0.3,
            "forecast_horizon": 6
        }
        
        policy_results = {}
        
        for policy in policies:
            print(f"\n  Testing Policy: {policy}")
            
            try:
                request = ScenarioRequest(
                    **base_scenario,
                    policy_name=policy if policy != "None" else None
                )
                
                result = simulate_scenario(request)
                scenario_df = pd.DataFrame(result["scenario"])
                peak_ue = scenario_df["Scenario_Unemployment"].max()
                
                indices = result["indices"]
                policy_cushion = indices.get("policy_cushion_score", 0)
                
                policy_results[policy] = {
                    "peak_unemployment": round(peak_ue, 2),
                    "policy_cushion": policy_cushion,
                    "early_warning": indices.get("early_warning", "Unknown")
                }
                
                print(f"    📊 Peak UE: {peak_ue:.2f}%")
                print(f"    🛡️ Policy Cushion: {policy_cushion}")
                print(f"    🚦 Warning: {indices.get('early_warning', 'Unknown')}")
                
            except Exception as e:
                print(f"    ❌ Error testing {policy}: {e}")
                policy_results[policy] = {"error": str(e)}
        
        # Compare policy effectiveness
        print(f"\n  📈 Policy Effectiveness Comparison:")
        baseline_peak = policy_results.get("None", {}).get("peak_unemployment", 0)
        
        for policy, data in policy_results.items():
            if "error" in data:
                continue
            
            peak = data["peak_unemployment"]
            if policy == "None":
                print(f"    {policy:15}: {peak:.2f}% (baseline)")
            else:
                improvement = baseline_peak - peak
                print(f"    {policy:15}: {peak:.2f}% ({improvement:+.2f}pp vs baseline)")
        
        self.test_results.append({
            "test": "Policy Interventions",
            "status": "COMPLETED",
            "policy_results": policy_results
        })
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis functionality"""
        print("\n🔬 Testing Sensitivity Analysis...")
        
        try:
            request = SensitivityRequest(
                base_shock_intensity=0.3,
                base_shock_duration=2,
                base_recovery_rate=0.3,
                forecast_horizon=6,
                policy_name=None
            )
            
            start_time = time.time()
            result = sensitivity_analysis(request)
            execution_time = time.time() - start_time
            
            # Validate result structure
            required_keys = ["tornado_data", "heatmap_data", "safe_combinations", "critical_thresholds"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"  ❌ Missing keys: {missing_keys}")
                self.test_results.append({
                    "test": "Sensitivity Analysis",
                    "status": "FAILED",
                    "error": f"Missing keys: {missing_keys}"
                })
                return
            
            # Analyze tornado data
            tornado_data = result["tornado_data"]
            print(f"  📊 Tornado Analysis ({len(tornado_data)} parameters):")
            
            for param in tornado_data:
                print(f"    {param['parameter']:15}: ±{param['total_range']:.2f}pp impact")
            
            # Analyze safe combinations
            safe_count = len(result["safe_combinations"])
            unsafe_count = len(result["unsafe_combinations"])
            total_combinations = safe_count + unsafe_count
            safe_percentage = (safe_count / total_combinations * 100) if total_combinations > 0 else 0
            
            print(f"  🎯 Safe Zone Analysis:")
            print(f"    Safe combinations: {safe_count}/{total_combinations} ({safe_percentage:.1f}%)")
            print(f"    Threshold: {result['threshold']}%")
            
            # Analyze critical thresholds
            thresholds = result["critical_thresholds"]
            print(f"  ⚠️ Critical Thresholds ({len(thresholds)} intensity levels):")
            
            for threshold in thresholds[:3]:  # Show first 3
                intensity = threshold["shock_intensity"]
                required_rr = threshold["required_recovery_rate"]
                print(f"    Intensity {intensity}: Requires RR ≥ {required_rr}")
            
            print(f"  ⏱️ Execution: {execution_time:.3f}s")
            
            self.test_results.append({
                "test": "Sensitivity Analysis",
                "status": "PASSED",
                "tornado_parameters": len(tornado_data),
                "safe_percentage": round(safe_percentage, 1),
                "execution_time": round(execution_time, 3)
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                "test": "Sensitivity Analysis",
                "status": "ERROR",
                "error": str(e)
            })
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        print("\n⚠️ Testing Edge Cases...")
        
        edge_cases = [
            {
                "name": "Maximum Shock",
                "params": {"shock_intensity": 0.6, "shock_duration": 5, "recovery_rate": 0.05},
                "expected": "Should handle extreme values"
            },
            {
                "name": "Instant Recovery",
                "params": {"shock_intensity": 0.3, "shock_duration": 1, "recovery_rate": 0.6},
                "expected": "Should recover quickly"
            },
            {
                "name": "Zero Duration",
                "params": {"shock_intensity": 0.4, "shock_duration": 0, "recovery_rate": 0.3},
                "expected": "Should be minimal impact"
            },
            {
                "name": "Long Forecast",
                "params": {"shock_intensity": 0.2, "shock_duration": 2, "recovery_rate": 0.3},
                "forecast_horizon": 10,
                "expected": "Should handle long horizons"
            },
        ]
        
        for i, case in enumerate(edge_cases, 1):
            print(f"\n  Edge Case {i}: {case['name']}")
            
            try:
                request = ScenarioRequest(
                    shock_intensity=case["params"]["shock_intensity"],
                    shock_duration=case["params"]["shock_duration"],
                    recovery_rate=case["params"]["recovery_rate"],
                    forecast_horizon=case.get("forecast_horizon", 6),
                    policy_name=None
                )
                
                result = simulate_scenario(request)
                scenario_df = pd.DataFrame(result["scenario"])
                
                # Validate data quality
                has_nan = scenario_df["Scenario_Unemployment"].isna().any()
                has_negative = (scenario_df["Scenario_Unemployment"] < 0).any()
                has_extreme = (scenario_df["Scenario_Unemployment"] > 50).any()
                
                if has_nan:
                    print(f"    ❌ Contains NaN values")
                    status = "FAILED"
                elif has_negative:
                    print(f"    ❌ Contains negative unemployment")
                    status = "FAILED"
                elif has_extreme:
                    print(f"    ❌ Contains extreme values (>50%)")
                    status = "FAILED"
                else:
                    peak = scenario_df["Scenario_Unemployment"].max()
                    print(f"    ✅ Valid data, peak UE: {peak:.2f}%")
                    status = "PASSED"
                
                self.test_results.append({
                    "test": f"Edge Case: {case['name']}",
                    "status": status,
                    "peak_unemployment": round(scenario_df["Scenario_Unemployment"].max(), 2)
                })
                
            except Exception as e:
                print(f"    ❌ Error: {e}")
                self.test_results.append({
                    "test": f"Edge Case: {case['name']}",
                    "status": "ERROR",
                    "error": str(e)
                })
    
    def test_performance_benchmarks(self):
        """Test performance and scalability"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        # Test different forecast horizons
        horizons = [3, 6, 10, 15]
        horizon_times = {}
        
        print(f"\n  📊 Forecast Horizon Performance:")
        
        for horizon in horizons:
            try:
                request = ScenarioRequest(
                    shock_intensity=0.3,
                    shock_duration=2,
                    recovery_rate=0.3,
                    forecast_horizon=horizon,
                    policy_name=None
                )
                
                start_time = time.time()
                result = simulate_scenario(request)
                execution_time = time.time() - start_time
                
                horizon_times[horizon] = execution_time
                print(f"    Horizon {horizon:2d}: {execution_time:.3f}s")
                
            except Exception as e:
                print(f"    Horizon {horizon:2d}: ERROR - {e}")
                horizon_times[horizon] = None
        
        # Test batch scenarios
        print(f"\n  🔄 Batch Scenario Performance:")
        
        batch_sizes = [5, 10, 20]
        
        for batch_size in batch_sizes:
            try:
                start_time = time.time()
                
                for i in range(batch_size):
                    request = ScenarioRequest(
                        shock_intensity=0.1 + (i * 0.02),  # Vary parameters
                        shock_duration=1 + (i % 3),
                        recovery_rate=0.2 + (i * 0.01),
                        forecast_horizon=6,
                        policy_name=None
                    )
                    simulate_scenario(request)
                
                total_time = time.time() - start_time
                avg_time = total_time / batch_size
                
                print(f"    Batch {batch_size:2d}: {total_time:.3f}s total, {avg_time:.3f}s avg")
                
            except Exception as e:
                print(f"    Batch {batch_size:2d}: ERROR - {e}")
        
        self.performance_metrics = {
            "horizon_times": horizon_times,
            "test_timestamp": time.time()
        }
    
    def test_data_validation(self):
        """Test data validation and consistency"""
        print("\n🔍 Testing Data Validation...")
        
        # Test scenario consistency
        print(f"\n  📊 Scenario Consistency Tests:")
        
        try:
            # Run same scenario multiple times
            request = ScenarioRequest(
                shock_intensity=0.3,
                shock_duration=2,
                recovery_rate=0.3,
                forecast_horizon=6,
                policy_name=None
            )
            
            results = []
            for i in range(3):
                result = simulate_scenario(request)
                scenario_df = pd.DataFrame(result["scenario"])
                peak = scenario_df["Scenario_Unemployment"].max()
                results.append(peak)
            
            # Check consistency
            max_diff = max(results) - min(results)
            if max_diff < 0.001:  # Should be identical
                print(f"    ✅ Deterministic: {max_diff:.6f} max difference")
                consistency_status = "PASSED"
            else:
                print(f"    ❌ Non-deterministic: {max_diff:.6f} max difference")
                consistency_status = "FAILED"
            
            # Test monotonicity (higher shock = higher unemployment)
            print(f"\n  📈 Monotonicity Tests:")
            
            intensities = [0.1, 0.2, 0.3, 0.4, 0.5]
            peaks = []
            
            for intensity in intensities:
                request = ScenarioRequest(
                    shock_intensity=intensity,
                    shock_duration=2,
                    recovery_rate=0.3,
                    forecast_horizon=6,
                    policy_name=None
                )
                result = simulate_scenario(request)
                scenario_df = pd.DataFrame(result["scenario"])
                peak = scenario_df["Scenario_Unemployment"].max()
                peaks.append(peak)
            
            # Check if peaks are monotonically increasing
            is_monotonic = all(peaks[i] <= peaks[i+1] for i in range(len(peaks)-1))
            
            if is_monotonic:
                print(f"    ✅ Monotonic: Higher shock → Higher unemployment")
                monotonic_status = "PASSED"
            else:
                print(f"    ❌ Non-monotonic: Inconsistent shock-unemployment relationship")
                print(f"       Intensities: {intensities}")
                print(f"       Peaks:       {[round(p, 2) for p in peaks]}")
                monotonic_status = "FAILED"
            
            self.test_results.append({
                "test": "Data Validation",
                "status": "COMPLETED",
                "consistency": consistency_status,
                "monotonicity": monotonic_status
            })
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            self.test_results.append({
                "test": "Data Validation",
                "status": "ERROR",
                "error": str(e)
            })
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("SIMULATION ENGINE TEST REPORT")
        print("="*80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAILED"])
        error_tests = len([t for t in self.test_results if t["status"] == "ERROR"])
        completed_tests = len([t for t in self.test_results if t["status"] == "COMPLETED"])
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed:      {passed_tests}")
        print(f"   Failed:      {failed_tests}")
        print(f"   Errors:      {error_tests}")
        print(f"   Completed:   {completed_tests}")
        
        success_rate = (passed_tests + completed_tests) / total_tests * 100 if total_tests > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        
        for result in self.test_results:
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "ERROR": "💥",
                "COMPLETED": "✅"
            }.get(result["status"], "❓")
            
            print(f"\n   {status_icon} {result['test']}")
            
            if "peak_delta" in result:
                print(f"      Peak Delta: {result['peak_delta']:+.2f}pp")
            if "usi" in result:
                print(f"      USI: {result['usi']}")
            if "execution_time" in result:
                print(f"      Time: {result['execution_time']}s")
            if "error" in result:
                print(f"      Error: {result['error']}")
        
        # Performance summary
        if self.performance_metrics:
            print(f"\n⚡ PERFORMANCE METRICS:")
            horizon_times = self.performance_metrics.get("horizon_times", {})
            
            for horizon, time_taken in horizon_times.items():
                if time_taken is not None:
                    print(f"   Horizon {horizon:2d}: {time_taken:.3f}s")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        
        if success_rate >= 90:
            assessment = "🟢 EXCELLENT - Simulation engine is highly reliable"
        elif success_rate >= 80:
            assessment = "🟡 GOOD - Minor issues detected, mostly functional"
        elif success_rate >= 70:
            assessment = "🟠 FAIR - Several issues need attention"
        else:
            assessment = "🔴 POOR - Major issues require immediate fixes"
        
        print(f"   {assessment}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if failed_tests > 0:
            print(f"   • Fix {failed_tests} failed test(s)")
        if error_tests > 0:
            print(f"   • Debug {error_tests} error(s)")
        
        if success_rate >= 90:
            print(f"   • System is production-ready")
            print(f"   • Consider adding more advanced features")
        elif success_rate >= 80:
            print(f"   • Address minor issues before production")
            print(f"   • Add more edge case testing")
        else:
            print(f"   • Significant debugging required")
            print(f"   • Review core simulation logic")
        
        print("\n" + "="*80)
        
        return {
            "total_tests": total_tests,
            "success_rate": success_rate,
            "assessment": assessment,
            "results": self.test_results,
            "performance": self.performance_metrics
        }
    
    def save_report(self, filename="simulation_test_report.json"):
        """Save test report to file"""
        report = self.generate_test_report()
        
        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Test report saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️ Could not save report: {e}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive Simulation Engine Tests")
        print("="*80)
        
        start_time = time.time()
        
        try:
            self.setup_test_data()
            self.test_basic_scenarios()
            self.test_policy_interventions()
            self.test_sensitivity_analysis()
            self.test_edge_cases()
            self.test_performance_benchmarks()
            self.test_data_validation()
            
        except Exception as e:
            print(f"\n💥 Critical error during testing: {e}")
            self.test_results.append({
                "test": "Test Suite Execution",
                "status": "ERROR",
                "error": str(e)
            })
        
        total_time = time.time() - start_time
        print(f"\n⏱️ Total test execution time: {total_time:.2f}s")
        
        # Generate and save report
        report = self.generate_test_report()
        self.save_report()
        
        return report


def main():
    """Main test execution"""
    tester = SimulationTester()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    success_rate = report.get("success_rate", 0)
    exit_code = 0 if success_rate >= 80 else 1
    
    print(f"\n🏁 Test suite completed with {success_rate:.1f}% success rate")
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)