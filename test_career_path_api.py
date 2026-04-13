"""Test script for Career Path Modeler API connection."""

import os
from src.data_providers.adzuna_client import AdzunaClient
from src.data_providers.career_data_manager import CareerDataManager
from src.analytics.career_path_modeler import CareerPathModeler
from src.risk_calculators import UserProfile

def test_adzuna_api():
    """Test Adzuna API connection"""
    print("🔍 Testing Adzuna API connection...")
    
    client = AdzunaClient()
    
    # Test connection
    if client.test_connection():
        print("✅ Adzuna API connection successful!")
        
        # Test search
        result = client.search_jobs("software engineer", "india", max_results=5)
        
        if result.get("success"):
            print(f"✅ Found {result['total_jobs']} software engineer jobs")
            print(f"✅ Average salary: ${result.get('avg_salary', 0):,.0f}")
            print(f"✅ Top skills: {', '.join(result.get('top_skills', [])[:5])}")
            print(f"✅ Remote percentage: {result.get('remote_percentage', 0):.1f}%")
        else:
            print(f"❌ Search failed: {result.get('error')}")
    else:
        print("❌ Adzuna API connection failed")

def test_career_data_manager():
    """Test Career Data Manager"""
    print("\n🔍 Testing Career Data Manager...")
    
    manager = CareerDataManager()
    
    # Test market data retrieval
    data = manager.get_role_market_data("Senior Software Engineer", "india")
    
    if data.get("success"):
        print("✅ Career Data Manager working!")
        print(f"✅ Data source: {data.get('source')}")
        print(f"✅ Total jobs: {data.get('total_jobs', 0)}")
        print(f"✅ Market health: {data.get('market_health')}")
        print(f"✅ Demand level: {data.get('demand_level')}")
        print(f"✅ Confidence score: {data.get('confidence_score', 0):.2f}")
    else:
        print("❌ Career Data Manager failed")

def test_career_path_modeler():
    """Test Career Path Modeler"""
    print("\n🔍 Testing Career Path Modeler...")
    
    # Create test user profile
    profile = UserProfile(
        skills=["python", "javascript", "react", "sql"],
        industry="Technology / software",
        role_level="Mid",
        experience_years=4,
        education_level="Bachelor's degree",
        location="Metro / Tier-1 city",
        age=28,
        company_size="201-1000",
        remote_capability=True,
        performance_rating=4
    )
    
    modeler = CareerPathModeler()
    
    try:
        paths = modeler.generate_paths(profile)
        
        if paths:
            print(f"✅ Generated {len(paths)} career paths!")
            
            for i, path in enumerate(paths[:2], 1):
                print(f"\n📈 Path {i}: {path.path_name}")
                print(f"   Success: {path.overall_success_probability:.0f}%")
                print(f"   Timeline: {path.total_timeline}")
                print(f"   Salary Growth: {path.total_salary_growth}")
                print(f"   Market Viability: {path.market_viability}")
                
                if path.transitions:
                    transition = path.transitions[0]
                    print(f"   Market Insights: {len(transition.market_insights)} insights")
                    print(f"   Skills to Learn: {len(transition.skill_gaps)} skills")
        else:
            print("❌ No career paths generated")
            
    except Exception as e:
        print(f"❌ Career Path Modeler failed: {e}")

def main():
    """Run all tests"""
    print("🚀 Career Path Modeler - API Test Suite")
    print("=" * 50)
    
    # Check environment variables
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    
    if not app_id or not app_key:
        print("⚠️ Warning: ADZUNA_APP_ID or ADZUNA_APP_KEY not found in environment")
        print("   Using hardcoded values from .env file")
    
    # Run tests
    test_adzuna_api()
    test_career_data_manager()
    test_career_path_modeler()
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()