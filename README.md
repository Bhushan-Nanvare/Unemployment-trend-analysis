# Unemployment Intelligence Platform (UIP)

> Scenario-based unemployment forecasting, shock simulation, AI-powered insights, and career intelligence — built for India's labor market.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## What It Does

UIP is a full-stack analytics platform that combines real World Bank data, machine learning, and Groq LLaMA 3.1 AI to answer two questions:

- **For policymakers:** What happens to unemployment if a shock hits? Which policy response works best?
- **For job seekers:** Which skills, cities, and career paths are safest given current economic conditions?

---

## Features (11 Pages)

| Page | What It Does |
|------|-------------|
| 📊 Overview | Live KPIs, GDP growth, recession risk score, 6-year forecast |
| 🧪 Simulator | Side-by-side scenario comparison with sensitivity analysis |
| 🏭 Sector Analysis | World Bank sector data, employment/GDP share charts |
| 💼 Career Lab | Career path recommendations based on sector stress |
| 🤖 AI Insights | Groq LLaMA 3.1 economic narrative generation |
| 🔬 Model Validation | Adaptive backtesting, R², MAE, MAPE metrics |
| 🎯 Job Risk Predictor | **Enhanced Multi-Risk Assessment** - 4 risk types (Overall, Automation, Recession, Age), time-based predictions (6mo-5yr), salary analysis, peer benchmarking, ROI-ranked recommendations |
| 📡 Job Market Pulse | 29,425 real Naukri.com job postings analysis |
| 🗺️ Geo Career Advisor | 55-city map with cost of living, industry hubs, state unemployment |
| ⚡ Skill Obsolescence | Skill demand trends + 6-month forecast |
| 📉 Phillips Curve | Inflation vs unemployment correlation analysis |

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Streamlit | Rapid Python-native data app development |
| Backend | FastAPI | High-performance REST API with auto Swagger docs |
| Charts | Plotly | Interactive, exportable visualizations |
| Maps | Folium + streamlit-folium | Leaflet.js maps in Python |
| ML | Scikit-learn | Logistic regression job risk model |
| AI | Groq LLaMA 3.1 | Fast, free LLM for economic narratives |
| Data | World Bank Open API | Free, authoritative economic data |
| Data | PLFS 2022-23 (MOSPI) | Official India state-level unemployment |
| Data | Naukri.com (Kaggle) | 29,425 real job postings |

---

## Architecture

```
Browser
  └── Streamlit Frontend (port 8501)
        └── FastAPI Backend (port 8000)  ← auto-started as subprocess
              ├── World Bank API (live data)
              ├── Local CSV fallback (offline)
              ├── Groq / Gemini / OpenAI (AI insights)
              └── Naukri.com dataset (job market)
```

---

## Run Locally

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/unemployment-intelligence-platform.git
cd unemployment-intelligence-platform
pip install -r requirements.txt
```

### 2. Add API keys (optional — app works without them)

Create a `.env` file:

```
GROQ_API_KEY=your_groq_key_here
```

Get a free Groq key at [console.groq.com](https://console.groq.com) — no credit card needed.

### 3. Start the backend

```bash
uvicorn src.api:app --reload --port 8000
```

### 4. Start the frontend (new terminal)

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Deploy on Streamlit Community Cloud (Free)

**Streamlit Cloud is the recommended deployment platform.** It's free, handles Python apps natively, and the backend auto-starts via subprocess.

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository
5. Set **Main file path** to `app.py`
6. Click **"Deploy"**

### Step 3 — Add secrets (for AI features)

In Streamlit Cloud dashboard → **Settings → Secrets**, add:

```toml
GROQ_API_KEY = "your_groq_key_here"
```

That's it. The app auto-starts the FastAPI backend on first load.

---

## Deploy on Render (Alternative — also free)

Render supports running two services from one repo.

### render.yaml (already included)

```yaml
services:
  - type: web
    name: uip-api
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false

  - type: web
    name: uip-frontend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: API_BASE_URL
        value: https://uip-api.onrender.com
```

---

## Data Sources

| Source | What | Why |
|--------|------|-----|
| [World Bank Open API](https://data.worldbank.org) | Unemployment, GDP, labor indicators | Free, authoritative, no key needed |
| [PLFS 2022-23 (MOSPI)](https://mospi.gov.in) | State-level unemployment (30 states) | Only official source for state data |
| [Naukri.com / Kaggle](https://kaggle.com) | 29,425 job postings (Jul-Aug 2019) | Real job market ground truth |
| Curated CSV | 55 cities with COL index + coordinates | No free API covers Indian city COL |

---

## Key Algorithms

- **Forecasting:** Ensemble of Trend+Mean-Reversion (50%) + ARIMA-inspired (30%) + Exponential Smoothing (20%)
- **Shock Model:** Immediate full-intensity impact → exponential decay by `recovery_rate`
- **Job Risk:** Logistic Regression on 3,500 synthetic samples, 5 features
- **Sensitivity:** Tornado chart + 2D heatmap via independent parameter variation
- **Monte Carlo:** 500 simulations for confidence bands using historical volatility

---

## Project Structure

```
.
├── app.py                    # Streamlit entry point + backend auto-start
├── requirements.txt
├── packages.txt              # System packages for Streamlit Cloud
├── render.yaml               # Render deployment config
├── .streamlit/
│   └── config.toml           # Streamlit theme and server config
├── src/
│   ├── api.py                # FastAPI backend (all endpoints)
│   ├── forecasting.py        # Ensemble forecasting engine
│   ├── shock_scenario.py     # Shock + recovery model
│   ├── scenario_metrics.py   # USI, RQI, delta metrics
│   ├── sector_analysis.py    # Sector stress scoring
│   ├── job_risk_model.py     # Logistic regression risk predictor
│   ├── geo_career_advisor.py # City COL, industry LQ, state UE
│   ├── live_data.py          # World Bank API + PLFS data
│   ├── llm_insights.py       # Groq → Gemini → OpenAI → rule-based
│   ├── policy_playbook.py    # Policy configurations
│   ├── ui_helpers.py         # Shared CSS, KPI cards, Plotly theme
│   └── ...
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Simulator.py
│   ├── 3_Sector_Analysis.py
│   ├── 4_Career_Lab.py
│   ├── 5_AI_Insights.py
│   ├── 6_Model_Validation.py
│   ├── 7_Job_Risk_Predictor.py
│   ├── 8_Job_Market_Pulse.py
│   ├── 9_Geo_Career_Advisor.py
│   ├── 10_Skill_Obsolescence.py
│   └── 11_Phillips_Curve.py
└── data/
    ├── raw/india_unemployment.csv
    ├── market_pulse/job_postings_sample.csv
    └── geo/india_city_reference.csv
```

---

## Author

**Bhushan Nanavare** — Full-Stack & Analytics Developer

---

## License

MIT License — free to use, modify, and distribute.
