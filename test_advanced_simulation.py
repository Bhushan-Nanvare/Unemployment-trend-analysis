#!/usr/bin/env python3
"""
test_advanced_simulation.py

ADVANCED SIMULATION FEATURES TEST SUITE
=======================================

Tests the enhanced simulation capabilities including:
1. Monte Carlo simulations
2. Multi-shock scenarios
3. Stress testing framework
4. Economic cycle modeling
5. API endpoint integration

Author: Advanced Simulation Testing
Date: 2026-04-13
Version: 1.0.0
"""

import sys
from pathlib import Path
import time
import json
import requests
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.advanced_simulation import (
    AdvancedSimulationEngine, 
    MonteCarloConfig, 
    ShockEvent, 
    ShockType, 
    EconomicCycle,
    get_predefined_stress_scenarios
)
from src.forecasting import ForecastingEngine
from src.live_data import fetch_world_bank
from src.preprocessing import Preprocessor


class AdvancedSimulationTester:
    """Test suite for advanced simulation features"""
    
    def __init__(self):
        self.test_results = []
        self.engine = AdvancedSimulationEngine()
        self.baseline_df = None
        
    def setup_test_data(self):
        """Setup test data"""
        print("📊 Setting up advanced simulation test data...")
        
        # Load and prepare data
        df = fetch_world_bank(country="India")
        df = Preprocessor().preprocess(df)
        
        # Generate baseline
        forecast_engine = ForecastingEngine(forecast_horizon=8)
        self.baseline_df = forecast_engine.forecast(df)
        
        print(f"  ✅ Baseline forecast ready: {len(self.baseline_df)} years")
    
    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation with uncertainty"""
        print("\n🎲 Testing Monte Carlo Simulation...")
        
        try:
            config = MonteCarloConfig(
                num_simulations=100,  # Reduced for testing speed
                shock_intensity_std=0.05,
                recovery_rate_std=0.03,
                duration_variance=1
            )
            
            start_time = time.time()
            result = self.engine.monte_carlo_simulation(
                baseline_df=self.baseline_df,
                base_shock_intensity=0.3,
                base_shock_duration=2,
                base_recovery_rate=0.3,
                config=config
            )
            execution_time = time.time() - start_time
            
            # Validate results
            required_keys = ["peak_unemployment_stats", "confidence_bands", "summary"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"  ❌ Missing keys: {missing_keys}")
                status = "FAILED"
            else:
                stats = result["peak_unemployment_stats"]
                summary = result["summary"]
                
                print(f"  📊 Simulations: {summary['total_simulations']}")
                print(f"  📈 Mean Peak UE: {summary['mean_peak_ue']}%")
                print(f"  📉 95% CI: {summary['ue_95_confidence'][0]}% - {summary['ue_95_confidence'][1]}%")
                print(f"  🔄 Mean Recovery: {summary['mean_recovery_time']} years")
                print(f"  ⏱️ Execution: {execution_time:.3f}s")
                
                # Validate statistical properties
                if stats["std"] > 0 and len(result["confidence_bands"]["Year"]) > 0:
                    status = "PASSED"
                else:
                    status = "FAILED"
            
            self.test_results.append({
                "test": "Monte Carlo Simulation",
                "status": status,
                "execution_time": round(execution_time, 3),
                "simulations": config.num_simulations
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                "test": "Monte Carlo Simulation",
                "status": "ERROR",
                "error": str(e)
            })
    
    def test_multi_shock_scenarios(self):
        """Test multi-shock compound crisis scenarios"""
        print("\n💥 Testing Multi-Shock Scenarios...")
        
        try:
            # Create compound crisis scenario
            shock_events = [
                ShockEvent(
                    shock_type=ShockType.PANDEMIC,
                    intensity=0.4,
                    duration=2,
                    start_year=0,
                    sector_impacts={"Services": 1.5, "Tourism": 2.0},
                    description="COVID-19 style pandemic"
                ),
                ShockEvent(
                    shock_type=ShockType.SUPPLY_CHAIN,
                    intensity=0.25,
                    duration=3,
                    start_year=1,
                    sector_impacts={"Manufacturing": 1.3},
                    description="Supply chain disruption"
                )
            ]
            
            policy_responses = {1: "Fiscal Stimulus", 2: "Industry Support"}
            
            start_time = time.time()
            result = self.engine.multi_shock_scenario(
                baseline_df=self.baseline_df,
                shock_events=shock_events,
                policy_responses=policy_responses
            )
            execution_time = time.time() - start_time
            
            # Validate results
            required_keys = ["compound_scenario", "shock_contributions", "summary"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"  ❌ Missing keys: {missing_keys}")
                status = "FAILED"
            else:
                summary = result["summary"]
                contributions = result["shock_contributions"]
                
                print(f"  💥 Total Shocks: {summary['total_shocks']}")
                print(f"  📊 Compound Peak UE: {summary['compound_peak_ue']}%")
                print(f"  📈 Total Impact: {summary['total_impact']:+.2f}pp")
                print(f"  🎯 Most Severe: {summary['most_severe_shock']}")
                print(f"  ⏱️ Execution: {execution_time:.3f}s")
                
                # Validate compound effects
                if summary["total_impact"] > 0 and len(contributions) == 2:
                    status = "PASSED"
                else:
                    status = "FAILED"
            
            self.test_results.append({
                "test": "Multi-Shock Scenarios",
                "status": status,
                "execution_time": round(execution_time, 3),
                "shock_count": len(shock_events)
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                "test": "Multi-Shock Scenarios",
                "status": "ERROR",
                "error": str(e)
            })
    
    def test_stress_testing_framework(self):
        """Test comprehensive stress testing"""
        print("\n🔬 Testing Stress Testing Framework...")
        
        try:
            # Get predefined stress scenarios
            stress_scenarios = get_predefined_stress_scenarios()
            
            start_time = time.time()
            result = self.engine.stress_test_framework(
                baseline_df=self.baseline_df,
                stress_scenarios=stress_scenarios[:3]  # Test first 3 scenarios
            )
            execution_time = time.time() - start_time
            
            # Validate results
            required_keys = ["stress_results", "pass_criteria", "summary"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"  ❌ Missing keys: {missing_keys}")
                status = "FAILED"
            else:
                summary = result["summary"]
                
                print(f"  🧪 Total Scenarios: {summary['total_scenarios']}")
                print(f"  ✅ Passed: {summary['passed_scenarios']}")
                print(f"  ❌ Failed: {summary['failed_scenarios']}")
                print(f"  📊 Pass Rate: {summary['pass_rate']}%")
                print(f"  🛡️ System Resilience: {summary['system_resilience']}")
                print(f"  ⏱️ Execution: {execution_time:.3f}s")
                
                # Validate stress test execution
                if summary["total_scenarios"] > 0:
                    status = "PASSED"
                else:
                    status = "FAILED"
            
            self.test_results.append({
                "test": "Stress Testing Framework",
                "status": status,
                "execution_time": round(execution_time, 3),
                "scenarios_tested": len(stress_scenarios[:3])
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                "test": "Stress Testing Framework",
                "status": "ERROR",
                "error": str(e)
            })
    
    def test_economic_cycle_simulation(self):
        """Test economic cycle modeling"""
        print("\n🔄 Testing Economic Cycle Simulation...")
        
        try:
            start_time = time.time()
            result = self.engine.economic_cycle_simulation(
                baseline_df=self.baseline_df,
                cycle_length=6,
                amplitude=0.12,
                current_phase=EconomicCycle.EXPANSION
            )
            execution_time = time.time() - start_time
            
            # Validate results
            required_keys = ["cyclical_scenario", "cycle_metrics", "summary"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if missing_keys:
                print(f"  ❌ Missing keys: {missing_keys}")
                status = "FAILED"
            else:
                summary = result["summary"]
                metrics = result["cycle_metrics"]
                
                print(f"  📊 Peak UE: {summary['peak_ue']}%")
                print(f"  📉 Trough UE: {summary['trough_ue']}%")
                print(f"  📈 Cycle Range: {summary['cycle_range']}pp")
                print(f"  📊 Volatility: {summary['volatility']:.2f}")
                print(f"  🔄 Phases: {', '.join(metrics['phases_covered'])}")
                print(f"  ⏱️ Execution: {execution_time:.3f}s")
                
                # Validate cycle properties
                if summary["cycle_range"] > 0 and len(metrics["phases_covered"]) > 1:
                    status = "PASSED"
                else:
                    status = "FAILED"
            
            self.test_results.append({
                "test": "Economic Cycle Simulation",
                "status": status,
                "execution_time": round(execution_time, 3),
                "cycle_length": 6
            })
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                "test": "Economic Cycle Simulation",
                "status": "ERROR",
                "error": str(e)
            })
    
    def test_api_integration(self):
        """Test API endpoint integration (if server is running)"""
        print("\n🌐 Testing API Integration...")
        
        # Test if API server is running
        try:
            response = requests.get("http://localhost:8000/data-status", timeout=2)
            if response.status_code != 200:
                print("  ⚠️ API server not running - skipping API tests")
                self.test_results.append({
                    "test": "API Integration",
                    "status": "SKIPPED",
                    "reason": "API server not available"
                })
                return
        except:
            print("  ⚠️ API server not running - skipping API tests")
            self.test_results.append({
                "test": "API Integration",
                "status": "SKIPPED",
                "reason": "API server not available"
            })
            return
        
        # Test predefined scenarios endpoint
        try:
            response = requests.get("http://localhost:8000/predefined_stress_scenarios")
            if response.status_code == 200:
                data = response.json()
                scenarios = data.get("scenarios", [])
                print(f"  ✅ Predefined scenarios: {len(scenarios)} available")
                api_status = "PASSED"
            else:
                print(f"  ❌ API error: {response.status_code}")
                api_status = "FAILED"
                
        except Exception as e:
            print(f"  ❌ API test error: {e}")
            api_status = "ERROR"
        
        self.test_results.append({
            "test": "API Integration",
            "status": api_status
        })
    
    def test_performance_benchmarks(self):
        """Test performance of advanced features"""
        print("\n⚡ Testing Advanced Performance...")
        
        performance_results = {}
        
        # Test Monte Carlo scaling
        print("  🎲 Monte Carlo Scaling:")
        for num_sims in [50, 100, 200]:
            try:
                config = MonteCarloConfig(num_simulations=num_sims)
                
                start_time = time.time()
                self.engine.monte_carlo_simulation(
                    baseline_df=self.baseline_df,
                    base_shock_intensity=0.3,
                    base_shock_duration=2,
                    base_recovery_rate=0.3,
                    config=config
                )
                execution_time = time.time() - start_time
                
                performance_results[f"monte_carlo_{num_sims}"] = execution_time
                print(f"    {num_sims:3d} sims: {execution_time:.3f}s")
                
            except Exception as e:
                print(f"    {num_sims:3d} sims: ERROR - {e}")
        
        # Test multi-shock complexity
        print("  💥 Multi-Shock Scaling:")
        for num_shocks in [1, 2, 3]:
            try:
                shock_events = []
                for i in range(num_shocks):
                    shock_events.append(ShockEvent(
                        shock_type=ShockType.FINANCIAL_CRISIS,
                        intensity=0.2 + (i * 0.1),
                        duration=2,
                        start_year=i,
                        sector_impacts={},
                        description=f"Shock {i+1}"
                    ))
                
                start_time = time.time()
                self.engine.multi_shock_scenario(
                    baseline_df=self.baseline_df,
                    shock_events=shock_events
                )
                execution_time = time.time() - start_time
                
                performance_results[f"multi_shock_{num_shocks}"] = execution_time
                print(f"    {num_shocks} shocks: {execution_time:.3f}s")
                
            except Exception as e:
                print(f"    {num_shocks} shocks: ERROR - {e}")
        
        self.test_results.append({
            "test": "Performance Benchmarks",
            "status": "COMPLETED",
            "performance_data": performance_results
        })
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("ADVANCED SIMULATION TEST REPORT")
        print("="*80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAILED"])
        error_tests = len([t for t in self.test_results if t["status"] == "ERROR"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIPPED"])
        completed_tests = len([t for t in self.test_results if t["status"] == "COMPLETED"])
        
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed:      {passed_tests}")
        print(f"   Failed:      {failed_tests}")
        print(f"   Errors:      {error_tests}")
        print(f"   Skipped:     {skipped_tests}")
        print(f"   Completed:   {completed_tests}")
        
        success_rate = (passed_tests + completed_tests) / (total_tests - skipped_tests) * 100 if (total_tests - skipped_tests) > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Feature assessment
        print(f"\n🎯 FEATURE ASSESSMENT:")
        
        feature_status = {}
        for result in self.test_results:
            test_name = result["test"]
            status = result["status"]
            
            if "Monte Carlo" in test_name:
                feature_status["Monte Carlo"] = status
            elif "Multi-Shock" in test_name:
                feature_status["Multi-Shock"] = status
            elif "Stress Testing" in test_name:
                feature_status["Stress Testing"] = status
            elif "Economic Cycle" in test_name:
                feature_status["Economic Cycle"] = status
            elif "API Integration" in test_name:
                feature_status["API Integration"] = status
        
        for feature, status in feature_status.items():
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌",
                "ERROR": "💥",
                "SKIPPED": "⏭️",
                "COMPLETED": "✅"
            }.get(status, "❓")
            
            print(f"   {status_icon} {feature:20}: {status}")
        
        # Overall assessment
        print(f"\n🏆 OVERALL ASSESSMENT:")
        
        if success_rate >= 90:
            assessment = "🟢 EXCELLENT - Advanced features are production-ready"
        elif success_rate >= 80:
            assessment = "🟡 GOOD - Minor issues with advanced features"
        elif success_rate >= 70:
            assessment = "🟠 FAIR - Some advanced features need work"
        else:
            assessment = "🔴 POOR - Advanced features require significant fixes"
        
        print(f"   {assessment}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if success_rate >= 90:
            print("   • Advanced simulation system is ready for production")
            print("   • Consider adding more sophisticated modeling features")
            print("   • Integrate with main simulation UI")
        elif success_rate >= 80:
            print("   • Address minor issues before production deployment")
            print("   • Add more comprehensive error handling")
        else:
            print("   • Significant debugging required for advanced features")
            print("   • Review implementation of failed components")
        
        print("\n" + "="*80)
        
        return {
            "total_tests": total_tests,
            "success_rate": success_rate,
            "assessment": assessment,
            "feature_status": feature_status,
            "results": self.test_results
        }
    
    def run_all_tests(self):
        """Run complete advanced simulation test suite"""
        print("🚀 Starting Advanced Simulation Feature Tests")
        print("="*80)
        
        start_time = time.time()
        
        try:
            self.setup_test_data()
            self.test_monte_carlo_simulation()
            self.test_multi_shock_scenarios()
            self.test_stress_testing_framework()
            self.test_economic_cycle_simulation()
            self.test_api_integration()
            self.test_performance_benchmarks()
            
        except Exception as e:
            print(f"\n💥 Critical error during testing: {e}")
            self.test_results.append({
                "test": "Test Suite Execution",
                "status": "ERROR",
                "error": str(e)
            })
        
        total_time = time.time() - start_time
        print(f"\n⏱️ Total test execution time: {total_time:.2f}s")
        
        # Generate report
        report = self.generate_test_report()
        
        # Save report
        try:
            with open("advanced_simulation_test_report.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Test report saved to: advanced_simulation_test_report.json")
        except Exception as e:
            print(f"\n⚠️ Could not save report: {e}")
        
        return report


def main():
    """Main test execution"""
    tester = AdvancedSimulationTester()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    success_rate = report.get("success_rate", 0)
    exit_code = 0 if success_rate >= 80 else 1
    
    print(f"\n🏁 Advanced simulation tests completed with {success_rate:.1f}% success rate")
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)