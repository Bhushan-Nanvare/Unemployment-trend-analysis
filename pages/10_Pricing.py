"""
Pricing Page - Showcase monetization tiers
"""
import streamlit as st
from src.ui_helpers import DARK_CSS

st.set_page_config(
    page_title="Pricing - UIP",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(DARK_CSS, unsafe_allow_html=True)

# Custom CSS for pricing cards
st.markdown("""
<style>
.pricing-header {
    text-align: center;
    padding: 3rem 2rem 2rem;
}
.pricing-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #f1f5f9 0%, #818cf8 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}
.pricing-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto 3rem;
}
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem 3rem;
}
.pricing-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem;
    position: relative;
    transition: all 0.3s ease;
}
.pricing-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99,102,241,0.3);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.pricing-card.featured {
    border: 2px solid #6366f1;
    background: rgba(99,102,241,0.08);
}
.pricing-badge {
    position: absolute;
    top: -12px;
    right: 20px;
    background: linear-gradient(135deg, #6366f1, #818cf8);
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.pricing-tier {
    font-size: 1.2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.5rem;
}
.pricing-price {
    font-size: 3rem;
    font-weight: 900;
    color: #6366f1;
    margin-bottom: 0.5rem;
}
.pricing-period {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 1.5rem;
}
.pricing-description {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-bottom: 2rem;
    min-height: 60px;
}
.pricing-features {
    list-style: none;
    padding: 0;
    margin: 0 0 2rem 0;
}
.pricing-features li {
    padding: 0.6rem 0;
    color: #cbd5e1;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.pricing-features li::before {
    content: "✓";
    color: #10b981;
    font-weight: 700;
    font-size: 1.2rem;
}
.pricing-features li.disabled {
    color: #475569;
    text-decoration: line-through;
}
.pricing-features li.disabled::before {
    content: "✗";
    color: #64748b;
}
.pricing-button {
    width: 100%;
    padding: 1rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}
.pricing-button.primary {
    background: linear-gradient(135deg, #6366f1, #818cf8);
    color: white;
}
.pricing-button.secondary {
    background: rgba(255,255,255,0.08);
    color: #e2e8f0;
    border: 1px solid rgba(255,255,255,0.12);
}
.pricing-button:hover {
    transform: scale(1.02);
    box-shadow: 0 10px 30px rgba(99,102,241,0.3);
}
.faq-section {
    max-width: 800px;
    margin: 4rem auto;
    padding: 0 2rem;
}
.faq-title {
    font-size: 2rem;
    font-weight: 700;
    color: #e2e8f0;
    text-align: center;
    margin-bottom: 2rem;
}
.faq-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.faq-question {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.5rem;
}
.faq-answer {
    font-size: 0.95rem;
    color: #94a3b8;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="pricing-header">
    <div class="pricing-title">Simple, Transparent Pricing</div>
    <div class="pricing-subtitle">
        Choose the plan that fits your needs. All plans include core forecasting features.
        Upgrade anytime as you grow.
    </div>
</div>
""", unsafe_allow_html=True)

# Pricing Cards
st.markdown("""
<div class="pricing-grid">
    <!-- FREE TIER -->
    <div class="pricing-card">
        <div class="pricing-tier">Free</div>
        <div class="pricing-price">₹0</div>
        <div class="pricing-period">Forever free</div>
        <div class="pricing-description">
            Perfect for students and individuals exploring labor market trends
        </div>
        <ul class="pricing-features">
            <li>Basic unemployment forecasts</li>
            <li>5 scenario simulations/month</li>
            <li>5 job risk assessments/month</li>
            <li>Sector analysis dashboard</li>
            <li>Public data access</li>
            <li>Rule-based AI insights</li>
            <li class="disabled">Advanced simulations</li>
            <li class="disabled">Unlimited assessments</li>
            <li class="disabled">GPT-4 AI insights</li>
            <li class="disabled">Downloadable reports</li>
        </ul>
        <button class="pricing-button secondary">Current Plan</button>
    </div>
    
    <!-- PREMIUM TIER -->
    <div class="pricing-card featured">
        <div class="pricing-badge">Most Popular</div>
        <div class="pricing-tier">Premium</div>
        <div class="pricing-price">₹999</div>
        <div class="pricing-period">per month</div>
        <div class="pricing-description">
            For professionals and job seekers who want advanced career insights
        </div>
        <ul class="pricing-features">
            <li>Everything in Free, plus:</li>
            <li>Unlimited simulations (all modes)</li>
            <li>Unlimited job risk assessments</li>
            <li>GPT-4 powered AI insights</li>
            <li>Personalized career roadmaps</li>
            <li>Skill gap analysis with ROI</li>
            <li>Email alerts for market changes</li>
            <li>Downloadable reports (PDF/Excel)</li>
            <li>30+ years historical data</li>
            <li>Priority email support</li>
        </ul>
        <button class="pricing-button primary">Upgrade to Premium</button>
    </div>
    
    <!-- ENTERPRISE TIER -->
    <div class="pricing-card">
        <div class="pricing-tier">Enterprise</div>
        <div class="pricing-price">Custom</div>
        <div class="pricing-period">Contact sales</div>
        <div class="pricing-description">
            For organizations, governments, and institutions requiring custom solutions
        </div>
        <ul class="pricing-features">
            <li>Everything in Premium, plus:</li>
            <li>Custom data integration</li>
            <li>White-label deployment</li>
            <li>Multi-user access (10-100 seats)</li>
            <li>API access with custom limits</li>
            <li>Custom shock scenarios</li>
            <li>Policy impact modeling</li>
            <li>Dedicated account manager</li>
            <li>SLA guarantees</li>
            <li>On-premise deployment option</li>
        </ul>
        <button class="pricing-button secondary">Contact Sales</button>
    </div>
</div>
""", unsafe_allow_html=True)

# Add-ons section
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### 🎯 Add-Ons & Services")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">
            API Access
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1rem;">
            Integrate our forecasting engine into your applications
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #6366f1;">
            From ₹4,999/mo
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎓</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">
            Training & Workshops
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1rem;">
            Custom training for your team on labor market analysis
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #6366f1;">
            From ₹49,999
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 12px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">💼</div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;">
            Consulting Services
        </div>
        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1rem;">
            Custom analysis and policy impact assessments
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #6366f1;">
            ₹15,000/hour
        </div>
    </div>
    """, unsafe_allow_html=True)

# FAQ Section
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div class="faq-section">
    <div class="faq-title">Frequently Asked Questions</div>
    
    <div class="faq-item">
        <div class="faq-question">💳 What payment methods do you accept?</div>
        <div class="faq-answer">
            We accept all major credit/debit cards, UPI, net banking, and international cards via Stripe/Razorpay.
        </div>
    </div>
    
    <div class="faq-item">
        <div class="faq-question">🔄 Can I cancel anytime?</div>
        <div class="faq-answer">
            Yes! You can cancel your subscription anytime. You'll continue to have access until the end of your billing period.
        </div>
    </div>
    
    <div class="faq-item">
        <div class="faq-question">📈 Can I upgrade or downgrade my plan?</div>
        <div class="faq-answer">
            Absolutely! You can upgrade or downgrade at any time. Changes take effect immediately, and we'll prorate the charges.
        </div>
    </div>
    
    <div class="faq-item">
        <div class="faq-question">🎓 Do you offer student discounts?</div>
        <div class="faq-answer">
            Yes! Students get 50% off Premium plans. Contact us with your student ID for verification.
        </div>
    </div>
    
    <div class="faq-item">
        <div class="faq-question">🏢 What's included in Enterprise plans?</div>
        <div class="faq-answer">
            Enterprise plans are fully customizable. We'll work with you to create a solution that fits your organization's needs, including custom data integration, white-labeling, and dedicated support.
        </div>
    </div>
    
    <div class="faq-item">
        <div class="faq-question">📞 How do I contact sales for Enterprise?</div>
        <div class="faq-answer">
            Email us at enterprise@unemploymentintelligence.com or use the contact form on our "For Business" page.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CTA Section
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 3rem 2rem; background: rgba(99,102,241,0.08); 
            border: 1px solid rgba(99,102,241,0.2); border-radius: 20px; margin: 2rem auto; max-width: 800px;">
    <div style="font-size: 2rem; font-weight: 700; color: #e2e8f0; margin-bottom: 1rem;">
        Ready to get started?
    </div>
    <div style="font-size: 1.1rem; color: #94a3b8; margin-bottom: 2rem;">
        Join thousands of professionals making data-driven career decisions
    </div>
    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
        <button class="pricing-button primary" style="width: auto; padding: 1rem 2rem;">
            Start Free Trial
        </button>
        <button class="pricing-button secondary" style="width: auto; padding: 1rem 2rem;">
            Schedule Demo
        </button>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer note
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 2rem 0;">
    💡 <strong>Note:</strong> This is a showcase/demo page. Payment integration coming soon. 
    Contact us for early access pricing.
</div>
""", unsafe_allow_html=True)
