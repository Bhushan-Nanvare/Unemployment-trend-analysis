"""
For Business Page - B2B/Enterprise offerings
"""
import streamlit as st
from src.ui_helpers import DARK_CSS

st.set_page_config(
    page_title="For Business - UIP",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(DARK_CSS, unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
.business-hero {
    text-align: center;
    padding: 4rem 2rem 3rem;
    background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(6,182,212,0.1) 100%);
    border-radius: 20px;
    margin-bottom: 3rem;
}
.business-title {
    font-size: 3.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #f1f5f9 0%, #818cf8 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}
.business-subtitle {
    font-size: 1.3rem;
    color: #94a3b8;
    max-width: 700px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
}
.feature-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 2rem;
    transition: all 0.3s ease;
}
.feature-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99,102,241,0.3);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
.feature-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.8rem;
}
.feature-description {
    font-size: 0.95rem;
    color: #94a3b8;
    line-height: 1.6;
}
.use-case-section {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 3rem 2rem;
    margin: 3rem 0;
}
.section-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #e2e8f0;
    text-align: center;
    margin-bottom: 3rem;
}
.use-case-card {
    background: rgba(255,255,255,0.04);
    border-left: 4px solid #6366f1;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
}
.use-case-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #818cf8;
    margin-bottom: 1rem;
}
.use-case-description {
    font-size: 1rem;
    color: #cbd5e1;
    line-height: 1.7;
    margin-bottom: 1rem;
}
.use-case-benefits {
    list-style: none;
    padding: 0;
    margin: 1rem 0;
}
.use-case-benefits li {
    padding: 0.5rem 0;
    color: #94a3b8;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.use-case-benefits li::before {
    content: "→";
    color: #10b981;
    font-weight: 700;
}
.cta-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(6,182,212,0.15));
    border: 2px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 3rem;
    text-align: center;
    margin: 3rem 0;
}
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="business-hero">
    <div class="business-title">Enterprise Solutions</div>
    <div class="business-subtitle">
        Empower your organization with advanced labor market intelligence, 
        workforce planning tools, and policy impact modeling trusted by governments and Fortune 500 companies.
    </div>
</div>
""", unsafe_allow_html=True)

# Key Features
st.markdown('<div class="section-title">🚀 Enterprise Features</div>', unsafe_allow_html=True)

st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon">🎨</div>
        <div class="feature-title">White-Label Deployment</div>
        <div class="feature-description">
            Deploy the platform with your organization's branding, logo, and custom domain. 
            Fully customizable UI to match your corporate identity.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🔗</div>
        <div class="feature-title">Custom Data Integration</div>
        <div class="feature-description">
            Integrate your proprietary data sources, internal HR systems, and regional labor market data. 
            Support for CSV, API, database connections.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">👥</div>
        <div class="feature-title">Multi-User Access</div>
        <div class="feature-description">
            Manage 10-100+ user accounts with role-based permissions. 
            Team collaboration features, shared dashboards, and audit logs.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🔌</div>
        <div class="feature-title">API Access</div>
        <div class="feature-description">
            Full REST API access with custom rate limits. 
            Integrate forecasting, risk assessment, and simulation capabilities into your existing systems.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">Custom Scenarios</div>
        <div class="feature-description">
            Build custom shock scenarios based on your region's economic context. 
            Model policy interventions specific to your jurisdiction.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <div class="feature-title">Enterprise Security</div>
        <div class="feature-description">
            SOC 2 compliance, SSO/SAML integration, data encryption at rest and in transit. 
            On-premise deployment option available.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Advanced Analytics</div>
        <div class="feature-description">
            Custom dashboards, automated reporting, data export in multiple formats. 
            Integration with BI tools (Tableau, Power BI).
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🎓</div>
        <div class="feature-title">Training & Support</div>
        <div class="feature-description">
            Dedicated account manager, quarterly training sessions, 24/7 priority support. 
            Custom workshops for your team.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">SLA Guarantees</div>
        <div class="feature-description">
            99.9% uptime guarantee, dedicated infrastructure, performance monitoring. 
            Custom SLA terms available.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Use Cases
st.markdown('<div class="use-case-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💼 Use Cases by Industry</div>', unsafe_allow_html=True)

# Government
st.markdown("""
<div class="use-case-card">
    <div class="use-case-title">🏛️ Government & Policy Institutions</div>
    <div class="use-case-description">
        Labor ministries, central banks, and policy research institutes use our platform for evidence-based policymaking and economic forecasting.
    </div>
    <ul class="use-case-benefits">
        <li>Scenario-based policy evaluation (fiscal stimulus, industry support, training programs)</li>
        <li>Real-time unemployment monitoring and early warning systems</li>
        <li>Impact assessment of proposed labor market reforms</li>
        <li>Public communication tools with interactive visualizations</li>
        <li>Integration with national statistical systems</li>
    </ul>
    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99,102,241,0.1); border-radius: 8px;">
        <strong style="color: #818cf8;">Pricing:</strong> <span style="color: #e2e8f0;">₹5,00,000 - ₹50,00,000/year</span> 
        (based on country size and customization)
    </div>
</div>
""", unsafe_allow_html=True)

# Corporate
st.markdown("""
<div class="use-case-card">
    <div class="use-case-title">🏢 Corporate HR & Workforce Planning</div>
    <div class="use-case-description">
        Large enterprises and HR consulting firms leverage our platform for strategic workforce planning and talent risk management.
    </div>
    <ul class="use-case-benefits">
        <li>Workforce vulnerability assessment (which roles are at risk)</li>
        <li>Skill demand forecasting for hiring pipeline planning</li>
        <li>Salary benchmarking and compensation strategy</li>
        <li>Retention risk modeling and attrition prediction</li>
        <li>Upskilling ROI calculator for L&D investments</li>
        <li>Integration with HRIS (Workday, SAP SuccessFactors, Oracle HCM)</li>
    </ul>
    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99,102,241,0.1); border-radius: 8px;">
        <strong style="color: #818cf8;">Pricing:</strong> <span style="color: #e2e8f0;">₹10,00,000 - ₹1,00,00,000/year</span> 
        (based on employee count and features)
    </div>
</div>
""", unsafe_allow_html=True)

# Education
st.markdown("""
<div class="use-case-card">
    <div class="use-case-title">🎓 Educational Institutions</div>
    <div class="use-case-description">
        Universities, vocational schools, and online learning platforms use our platform to guide students toward high-demand careers.
    </div>
    <ul class="use-case-benefits">
        <li>Student career guidance portal (bulk access for all students)</li>
        <li>Curriculum optimization based on labor market demand</li>
        <li>Graduate employment outcome forecasting</li>
        <li>Industry partnership recommendations</li>
        <li>Alumni career tracking and success metrics</li>
        <li>Placement success prediction and improvement strategies</li>
    </ul>
    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99,102,241,0.1); border-radius: 8px;">
        <strong style="color: #818cf8;">Pricing:</strong> <span style="color: #e2e8f0;">₹2,00,000 - ₹20,00,000/year</span> 
        (based on student count)
    </div>
</div>
""", unsafe_allow_html=True)

# Financial Services
st.markdown("""
<div class="use-case-card">
    <div class="use-case-title">💰 Financial Services & Consulting</div>
    <div class="use-case-description">
        Investment firms, consulting companies, and economic research organizations use our data and models for market analysis.
    </div>
    <ul class="use-case-benefits">
        <li>Macroeconomic forecasting for investment decisions</li>
        <li>Sector vulnerability analysis for portfolio management</li>
        <li>Custom economic research reports</li>
        <li>API access for algorithmic trading strategies</li>
        <li>Data licensing for proprietary models</li>
    </ul>
    <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99,102,241,0.1); border-radius: 8px;">
        <strong style="color: #818cf8;">Pricing:</strong> <span style="color: #e2e8f0;">₹15,00,000 - ₹75,00,000/year</span> 
        (based on data access and API usage)
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Client Success Stories (Placeholder)
st.markdown('<div class="section-title">🌟 Trusted By</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.04); 
                border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏛️</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0;">
            Government Agencies
        </div>
        <div style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
            5+ countries
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.04); 
                border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏢</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0;">
            Fortune 500
        </div>
        <div style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
            20+ companies
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.04); 
                border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎓</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0;">
            Universities
        </div>
        <div style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
            50+ institutions
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.04); 
                border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">💼</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0;">
            Consulting Firms
        </div>
        <div style="font-size: 0.9rem; color: #64748b; margin-top: 0.5rem;">
            15+ partners
        </div>
    </div>
    """, unsafe_allow_html=True)

# CTA Section
st.markdown("""
<div class="cta-box">
    <div style="font-size: 2.5rem; font-weight: 700; color: #e2e8f0; margin-bottom: 1rem;">
        Ready to Transform Your Organization?
    </div>
    <div style="font-size: 1.2rem; color: #94a3b8; margin-bottom: 2rem;">
        Schedule a personalized demo and see how our platform can meet your specific needs
    </div>
</div>
""", unsafe_allow_html=True)

# Contact Form
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📧 Contact Sales")
    
    with st.form("enterprise_contact"):
        name = st.text_input("Full Name *")
        email = st.text_input("Work Email *")
        company = st.text_input("Company/Organization *")
        role = st.selectbox("Your Role", [
            "Select...",
            "Government Official",
            "HR Director/VP",
            "Chief People Officer",
            "University Administrator",
            "Consultant",
            "Researcher",
            "Other"
        ])
        employees = st.selectbox("Organization Size", [
            "Select...",
            "1-50 employees",
            "51-200 employees",
            "201-1000 employees",
            "1001-5000 employees",
            "5000+ employees",
            "Government/Public Sector"
        ])
        message = st.text_area("Tell us about your needs")
        
        submitted = st.form_submit_button("Request Demo", use_container_width=True)
        
        if submitted:
            if name and email and company:
                st.success("✅ Thank you! Our sales team will contact you within 24 hours.")
                st.balloons()
            else:
                st.error("Please fill in all required fields (*)")

with col2:
    st.markdown("### 📞 Other Ways to Reach Us")
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <div style="font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">📧 Email</div>
        <div style="color: #6366f1;">enterprise@unemploymentintelligence.com</div>
    </div>
    
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <div style="font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">📞 Phone</div>
        <div style="color: #6366f1;">+91 (800) 123-4567</div>
        <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.3rem;">Mon-Fri, 9 AM - 6 PM IST</div>
    </div>
    
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <div style="font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">💬 Schedule a Call</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">
            Book a 30-minute consultation with our solutions architect
        </div>
        <button style="margin-top: 0.8rem; padding: 0.6rem 1.2rem; background: linear-gradient(135deg, #6366f1, #818cf8); 
                       color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;">
            Book Now
        </button>
    </div>
    """, unsafe_allow_html=True)

# Footer note
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 3rem 0 1rem;">
    💡 <strong>Note:</strong> This is a showcase/demo page. All features and pricing are illustrative. 
    Contact us for actual enterprise solutions and custom pricing.
</div>
""", unsafe_allow_html=True)
