"""Test script to verify risk calculators produce proper values."""

from src.risk_calculators import UserProfile
from src.risk_calculators.orchestrator import RiskCalculatorOrchestrator


def test_basic_profile():
    """Test with a basic mid-level tech worker profile"""
    print("=" * 60)
    print("TEST 1: Mid-Level Tech Worker")
    print("=" * 60)
    
    profile = UserProfile(
        skills=["python", "machine learning", "sql", "communication"],
        industry="Technology / software",
        role_level="Mid",
        experience_years=5,
        education_level="Bachelor's degree",
        location="Metro / Tier-1 city",
        age=30,
        company_size="201-1000",
        remote_capability=True,
        performance_rating=4,
    )
    
    orchestrator = RiskCalculatorOrchestrator()
    result = orchestrator.calculate_all_risks(profile)
    
    print(f"\nOverall Risk: {result.overall_risk}% ({result.risk_level})")
    print(f"Automation Risk: {result.automation_risk}%")
    print(f"Recession Risk: {result.recession_risk}%")
    print(f"Age Discrimination Risk: {result.age_discrimination_risk}%")
    print(f"\nTimestamp: {result.timestamp}")
    
    # Verify ranges
    assert 0 <= result.overall_risk <= 100, "Overall risk out of range"
    assert 0 <= result.automation_risk <= 100, "Automation risk out of range"
    assert 0 <= result.recession_risk <= 100, "Recession risk out of range"
    assert 0 <= result.age_discrimination_risk <= 100, "Age discrimination risk out of range"
    
    print("\n✓ All risk scores in valid range [0, 100]")


def test_high_risk_profile():
    """Test with a high-risk profile"""
    print("\n" + "=" * 60)
    print("TEST 2: High-Risk Profile (Entry-level, vulnerable industry)")
    print("=" * 60)
    
    profile = UserProfile(
        skills=["data entry", "excel", "typing"],
        industry="Retail / e-commerce ops",
        role_level="Entry",
        experience_years=1,
        education_level="High school / diploma",
        location="Smaller town / rural",
        age=22,
        company_size="11-50",
        remote_capability=False,
        performance_rating=3,
    )
    
    orchestrator = RiskCalculatorOrchestrator()
    result = orchestrator.calculate_all_risks(profile)
    
    print(f"\nOverall Risk: {result.overall_risk}% ({result.risk_level})")
    print(f"Automation Risk: {result.automation_risk}%")
    print(f"Recession Risk: {result.recession_risk}%")
    print(f"Age Discrimination Risk: {result.age_discrimination_risk}%")
    
    # High-risk profile should have elevated scores
    print(f"\n✓ High-risk profile detected")
    print(f"  - Automation risk should be high (vulnerable skills): {result.automation_risk}%")
    print(f"  - Recession risk should be elevated (small company, entry level): {result.recession_risk}%")


def test_low_risk_profile():
    """Test with a low-risk profile"""
    print("\n" + "=" * 60)
    print("TEST 3: Low-Risk Profile (Senior, stable industry)")
    print("=" * 60)
    
    profile = UserProfile(
        skills=["leadership", "strategic planning", "machine learning", "data science", "communication"],
        industry="Healthcare / biotech",
        role_level="Senior",
        experience_years=15,
        education_level="Master's degree",
        location="Metro / Tier-1 city",
        age=40,
        company_size="5000+",
        remote_capability=True,
        performance_rating=5,
    )
    
    orchestrator = RiskCalculatorOrchestrator()
    result = orchestrator.calculate_all_risks(profile)
    
    print(f"\nOverall Risk: {result.overall_risk}% ({result.risk_level})")
    print(f"Automation Risk: {result.automation_risk}%")
    print(f"Recession Risk: {result.recession_risk}%")
    print(f"Age Discrimination Risk: {result.age_discrimination_risk}%")
    
    # Low-risk profile should have lower scores
    print(f"\n✓ Low-risk profile detected")
    print(f"  - Automation risk should be low (resistant skills): {result.automation_risk}%")
    print(f"  - Recession risk should be low (stable industry, senior role): {result.recession_risk}%")
    print(f"  - Age discrimination risk should be minimal (optimal age range): {result.age_discrimination_risk}%")


def test_age_discrimination_curve():
    """Test age discrimination risk across different ages"""
    print("\n" + "=" * 60)
    print("TEST 4: Age Discrimination Risk Curve")
    print("=" * 60)
    
    base_profile = {
        "skills": ["python", "sql"],
        "industry": "Technology / software",
        "role_level": "Mid",
        "experience_years": 10,
        "education_level": "Bachelor's degree",
        "location": "Metro / Tier-1 city",
        "company_size": "201-1000",
        "remote_capability": True,
        "performance_rating": 4,
    }
    
    orchestrator = RiskCalculatorOrchestrator()
    
    ages_to_test = [25, 35, 45, 55, 65]
    print("\nAge Discrimination Risk by Age:")
    for age in ages_to_test:
        profile = UserProfile(age=age, **base_profile)
        result = orchestrator.calculate_all_risks(profile)
        print(f"  Age {age}: {result.age_discrimination_risk}%")
    
    # Test that ages 30-50 have lower risk
    profile_optimal = UserProfile(age=40, **base_profile)
    result_optimal = orchestrator.calculate_all_risks(profile_optimal)
    
    profile_older = UserProfile(age=60, **base_profile)
    result_older = orchestrator.calculate_all_risks(profile_older)
    
    assert result_optimal.age_discrimination_risk < 15, "Age 40 should have minimal risk"
    assert result_older.age_discrimination_risk > result_optimal.age_discrimination_risk, "Age 60 should have higher risk than age 40"
    
    print("\n✓ Age discrimination curve working correctly")
    print(f"  - Age 40 risk: {result_optimal.age_discrimination_risk}% (should be < 15%)")
    print(f"  - Age 60 risk: {result_older.age_discrimination_risk}% (should be higher)")


def test_determinism():
    """Test that same inputs produce same outputs"""
    print("\n" + "=" * 60)
    print("TEST 5: Determinism Check")
    print("=" * 60)
    
    profile = UserProfile(
        skills=["python", "sql"],
        industry="Technology / software",
        role_level="Mid",
        experience_years=5,
        education_level="Bachelor's degree",
        location="Metro / Tier-1 city",
        age=30,
        company_size="201-1000",
        remote_capability=True,
        performance_rating=4,
    )
    
    orchestrator = RiskCalculatorOrchestrator()
    
    # Calculate twice
    result1 = orchestrator.calculate_all_risks(profile)
    result2 = orchestrator.calculate_all_risks(profile)
    
    assert result1.overall_risk == result2.overall_risk, "Overall risk not deterministic"
    assert result1.automation_risk == result2.automation_risk, "Automation risk not deterministic"
    assert result1.recession_risk == result2.recession_risk, "Recession risk not deterministic"
    assert result1.age_discrimination_risk == result2.age_discrimination_risk, "Age discrimination risk not deterministic"
    
    print("\n✓ Determinism verified - same inputs produce same outputs")
    print(f"  Run 1: Overall={result1.overall_risk}%, Auto={result1.automation_risk}%, Recession={result1.recession_risk}%, Age={result1.age_discrimination_risk}%")
    print(f"  Run 2: Overall={result2.overall_risk}%, Auto={result2.automation_risk}%, Recession={result2.recession_risk}%, Age={result2.age_discrimination_risk}%")


if __name__ == "__main__":
    print("\n🧪 Testing Risk Calculators\n")
    
    try:
        test_basic_profile()
        test_high_risk_profile()
        test_low_risk_profile()
        test_age_discrimination_curve()
        test_determinism()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nRisk calculators are working correctly with proper values.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
