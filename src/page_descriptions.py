"""
Page descriptions for the Unemployment Intelligence Platform.
Used for tooltips, help sections, and navigation guidance.
"""

PAGE_DESCRIPTIONS = {
    "Home": {
        "title": "🏠 Platform Overview",
        "short": "Welcome dashboard and navigation hub",
        "description": "Central landing page providing platform introduction, system status, and access to all analysis modules. Start here to understand the platform's capabilities.",
        "use_case": "All users - starting point for platform exploration"
    },
    
    "Overview": {
        "title": "📊 Live Dashboard", 
        "short": "Real-time unemployment forecasting and economic indicators",
        "description": "Current unemployment metrics, GDP-driven forecasts, recession risk assessment, and economic relationship analysis. Uses advanced modeling with confidence intervals.",
        "use_case": "Policymakers, economists, researchers needing current outlook"
    },
    
    "Simulator": {
        "title": "🧪 Scenario Testing",
        "short": "Interactive shock simulation and policy analysis", 
        "description": "Model economic shocks (recession, pandemic) and test policy interventions. Compare different scenarios and analyze recovery trajectories.",
        "use_case": "Policy analysts, government officials, intervention researchers"
    },
    
    "Sector Analysis": {
        "title": "🏭 Industry Insights",
        "short": "Sector-specific unemployment and employment trends",
        "description": "Analyze vulnerability across industries, employment distribution, and sector-specific forecasting. Understand cross-sector impacts.",
        "use_case": "Industry analysts, sector policymakers, business strategists"
    },
    
    "Career Lab": {
        "title": "💼 Personal Guidance", 
        "short": "Career risk assessment and skill development",
        "description": "Evaluate individual career vulnerability, identify skill gaps, get transition guidance, and upskilling recommendations based on market demand.",
        "use_case": "Job seekers, career changers, professionals, career counselors"
    },
    
    "AI Insights": {
        "title": "🤖 Smart Analysis",
        "short": "AI-powered insights and natural language explanations",
        "description": "Get human-readable analysis of unemployment trends, scenario interpretations, and policy recommendations using advanced AI.",
        "use_case": "General public, students, journalists, accessible explanations"
    },
    
    "Job Risk Predictor": {
        "title": "🎯 Risk Assessment",
        "short": "Personal unemployment risk prediction using ML",
        "description": "Predict individual unemployment probability based on skills, experience, education, location, and industry. Get improvement recommendations.",
        "use_case": "Individual professionals, job seekers, HR professionals"
    },
    
    "Job Market Pulse": {
        "title": "📡 Market Trends",
        "short": "Real-time job market analysis and posting trends", 
        "description": "Analyze 29,000+ job postings for skill demand, salary trends, hiring patterns, and market sentiment across roles and locations.",
        "use_case": "Recruiters, HR professionals, job seekers, market researchers"
    },
    
    "Geo Career Advisor": {
        "title": "🗺️ Location Intelligence",
        "short": "City-wise job opportunities and relocation guidance",
        "description": "Compare job markets across Indian cities, get relocation recommendations, analyze cost of living impacts, and skill demand by location.",
        "use_case": "Professionals considering relocation, remote workers, urban planners"
    },
    
    "Skill Demand Analysis": {
        "title": "📊 Skill Intelligence", 
        "short": "Comprehensive skill market analysis and career guidance",
        "description": "Track skill popularity, assess personal skill portfolios, understand market categories, and get targeted skill development recommendations.",
        "use_case": "Professionals planning development, students, training providers"
    },
    
    "Phillips Curve": {
        "title": "📉 Economic Theory",
        "short": "Inflation-unemployment relationship and policy analysis",
        "description": "Explore the Phillips Curve for India, analyze inflation-unemployment trade-offs, understand policy implications, and assess current economic stance for monetary policy decisions.",
        "use_case": "Economists, monetary policy analysts, academic researchers"
    }
}

def get_page_description(page_name: str, field: str = "description") -> str:
    """
    Get description for a specific page.
    
    Args:
        page_name: Name of the page (e.g., "Overview", "Simulator")
        field: Which field to return ("title", "short", "description", "use_case")
    
    Returns:
        Description string or empty string if not found
    """
    return PAGE_DESCRIPTIONS.get(page_name, {}).get(field, "")

def get_all_pages_summary() -> dict:
    """Get summary of all pages for navigation help."""
    return {
        name: {
            "title": info["title"],
            "short": info["short"]
        }
        for name, info in PAGE_DESCRIPTIONS.items()
    }

def get_recommended_journey() -> list:
    """Get recommended user journey through the platform."""
    return [
        {
            "step": 1,
            "page": "Overview", 
            "reason": "Get current unemployment status and forecasts"
        },
        {
            "step": 2,
            "page": "Simulator",
            "reason": "Understand policy impacts through scenario modeling"
        },
        {
            "step": 3, 
            "page": "Job Risk Predictor",
            "reason": "Assess personal unemployment risk"
        },
        {
            "step": 4,
            "page": "Career Lab", 
            "reason": "Get personalized career guidance"
        },
        {
            "step": 5,
            "page": "Job Market Pulse",
            "reason": "Research current market trends"
        },
        {
            "step": 6,
            "page": "Skill Demand Analysis",
            "reason": "Plan skill development strategy"
        },
        {
            "step": 7,
            "page": "Geo Career Advisor",
            "reason": "Consider location-based opportunities"
        },
        {
            "step": 8,
            "page": "AI Insights",
            "reason": "Get plain-language explanations of findings"
        }
    ]