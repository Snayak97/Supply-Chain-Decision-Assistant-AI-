# Supply Chain Decision & Planning Assistant - Scenario Simulation MVP

**Version:** 1.0  
**Focus:** Demand Forecasting Scenario Assistant  
**Date:** May 2026

---

## Executive Summary

This MVP implements a conversational AI assistant focused on demand forecasting scenario simulation. The assistant allows any business user to ask forward-looking 'what-if' questions in plain language — for example, 'What does the forecast look like if we increase the topline by 25%?' — and receive an immediate, quantified, visual answer with downstream impact across inventory, stockout risk, and open-to-buy position.

### Key Features

- **Natural Language Queries:** Ask questions like "What if we increase topline by 25%?" or "Show impact if DTC drops 15%"
- **Multi-turn Scenarios:** Perturbations accumulate across turns (e.g., "Now add a 10% demand uplift")
- **Quantified Impact:** See baseline vs scenario comparison with confidence intervals
- **Stockout Risk Analysis:** Identify SKUs at risk with revenue-at-risk quantification
- **OTB Position Evaluation:** Re-evaluate budget commitment under scenario demand
- **Actionable Recommendations:** Ranked mitigation actions with cost/benefit analysis
- **Full Transparency:** 'Show your work' panel exposing all tool calls and raw outputs

---

## Architecture Overview

The system is composed of **seven layers**, each with a distinct responsibility:

| Layer | Role | Technology |
|-------|------|------------|
| **1. Interaction Layer** | Chat UI & streaming | FastAPI + Plotly |
| **2. Orchestration Layer** | LLM planner & state machine | LangGraph + Ollama |
| **3. Tool/Capability Layer** | Domain analytics functions | Python + Pydantic |
| **4. Recommendation Layer** | Action proposals & tradeoffs | LangGraph node |
| **5. Memory & Caching Layer** | Session & result reuse | SQLite (MVP) |
| **6. Data Layer** | Curated warehouse views | SQLite dbt-like models |
| **7. Observability Layer** | Tracing, evals & audit | Loguru structured logging |

### Layer-by-Layer Explanation


#### Layer 1: Interaction Layer (FastAPI)
- **Purpose:** Surface the user touches
- **Components:**
  - REST API endpoints for scenario simulation
  - Automatic API documentation (Swagger/OpenAPI)
  - Response formatting for UI rendering
- **Key Files:** `apps/api/main.py`, `apps/api/routes/scenario_routes.py`

#### Layer 2: Orchestration Layer (LangGraph)
- **Purpose:** LLM-driven planner that parses intent and sequences tool calls
- **Components:**
  - Perturbation parser (topline, channel, category, shipment delay)
  - LangGraph state machine for workflow orchestration
  - Multi-turn scenario state persistence
- **Key Files:** `agents/orchestrator/`
- **How It Works:**
  1. Parses user query to extract perturbations
  2. Sequences tool calls: forecast → adjust → risk → OTB → recommendations
  3. Maintains state across conversation turns

#### Layer 3: Tool/Capability Layer (Python Functions)
- **Purpose:** Deterministic, Pydantic-typed functions that perform actual calculations
- **Components:**
  - `get_demand_forecast`: Retrieve baseline forecast with CI bands
  - `apply_topline_adjustment`: Apply perturbations to forecast
  - `calculate_stockout_risk`: Monte Carlo simulation for stockout probability
  - `evaluate_otb_position`: Re-evaluate OTB commitment under scenario
- **Key Files:** `tools/forecast/`, `tools/inventory/`, `tools/risk/`, `tools/otb/`
- **Design Principle:** All numeric outputs originate here, not from the LLM

#### Layer 4: Recommendation Layer
- **Purpose:** Convert scenario delta into ranked mitigation actions
- **Components:**
  - Action space: buy, hold, cancel, delay, expedite, reallocate
  - Cost/benefit quantification per action
  - Confidence caveats and tradeoff presentation
- **Key Files:** `tools/recommendation/recommendation_engine.py`

#### Layer 5: Memory & Caching Layer
- **Purpose:** Session persistence and result caching for responsive follow-up queries
- **Components:**
  - Scenario session state (perturbations accumulate across turns)
  - Tool result cache (TTL-aligned to warehouse refresh)
  - SQLite-based for MVP simplicity
- **Key Files:** `core/cache/cache_manager.py`

#### Layer 6: Data Layer
- **Purpose:** Curated data views that tools read from
- **Components:**
  - `sku_master`: SKU attributes (category, channel, margin, MOQ)
  - `forecast`: Demand forecast with 80/95% CI bands
  - `inventory`: Net available-to-sell per SKU/warehouse/channel
  - `purchase_order`: Open POs with cancelability flags
  - `lead_time`: Supplier lead-time distributions
  - `otb_plan`: Budget vs committed spend by category/period
- **Key Files:** `core/database/models.py`

#### Layer 7: Observability Layer
- **Purpose:** Full traceability for inspection and improvement
- **Components:**
  - Structured JSON logging (Loguru)
  - Tool call tracing with arguments and results
  - Error logging with context
  - Separate error log file
- **Key Files:** `core/logging/logger.py`

---

## Technology Stack

### Core Technologies (All Free & Open-Source)

| Technology | Purpose | Why It's Needed |
|------------|---------|-----------------|
| **Python 3.13** | Programming language | Modern, enterprise-standard with rich ecosystem |
| **uv** | Package manager | Fast, reliable dependency management (faster than pip) |
| **FastAPI** | Web framework | High-performance API with automatic docs |
| **LangGraph** | Orchestration framework | State machine for LLM workflow orchestration |
| **Ollama** | Local LLM runtime | Run LLMs locally without cloud APIs (free) |
| **SQLAlchemy** | ORM | Database abstraction layer |
| **SQLite** | Database | Zero-config, file-based database (perfect for local MVP) |
| **Pydantic** | Data validation | Type-safe data models with validation |
| **Loguru** | Logging | Structured, easy-to-use logging with rotation |
| **Plotly** | Visualization | Interactive charts for scenario comparison |

### Why These Tools?

- **No Cloud APIs Required:** Ollama runs LLMs locally on your machine
- **No Paid Services:** All tools are free and open-source
- **Local Execution:** Everything runs on your laptop, no external dependencies
- **Enterprise-Grade:** FastAPI, LangGraph, and Pydantic are industry standards
- **Beginner-Friendly:** Clear documentation and large community support

---

## Project Structure

```
sc-ai-assistant-mvp/
├── apps/
│   └── api/                    # FastAPI application
│       ├── main.py            # API entry point
│       └── routes/            # API endpoints
│           └── scenario_routes.py  # Scenario simulation endpoint
├── agents/
│   └── orchestrator/          # LangGraph orchestration
│       ├── state.py           # Typed state definition
│       ├── graph/             # LangGraph workflow
│       └── nodes/             # Workflow nodes
├── tools/                     # Layer 3: Business logic
│   ├── forecast/              # Forecast tools
│   ├── inventory/             # Inventory tools
│   ├── risk/                  # Risk analysis tools
│   ├── otb/                   # OTB evaluation tools
│   └── recommendation/        # Recommendation engine
├── schemas/                   # Pydantic data models
│   ├── perturbation_schema.py
│   ├── forecast_schema.py
│   ├── risk_schema.py
│   ├── otb_schema.py
│   └── recommendation_schema.py
├── core/
│   ├── config/                # Configuration
│   ├── database/              # Database models & session
│   ├── cache/                 # Memory & caching layer
│   └── logging/               # Observability layer
├── scripts/                   # Utility scripts
│   ├── setup.sh / setup.bat   # Setup scripts
│   ├── init_db.py             # Database initialization
│   └── generate_mock_data.py  # Sample data generation
├── pyproject.toml             # Dependencies (uv)
├── .env                       # Environment variables
└── README.md                  # This file
```

---

## Setup Instructions

### Prerequisites

- **Python 3.13+** (or use uv to manage Python versions)
- **Ollama** (for local LLM)
- **Git** (optional, for version control)

### Step 1: Install Ollama

1. Download Ollama from https://ollama.com
2. Install Ollama for your OS (Windows, Mac, or Linux)
3. Pull the Llama3 model:
   ```bash
   ollama pull llama3
   ```

### Step 2: Clone the Repository

```bash
cd d:/windserve/sc-ai-assistant-mvp
```

### Step 3: Run Setup Script

**Windows:**
```bash
cd scripts
setup.bat
```

**Linux/Mac:**
```bash
cd scripts
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install Python dependencies with uv
- Create `.env` file from `.env.example`
- Initialize the SQLite database
- Generate sample business data
- Verify Ollama installation

### Step 4: Configure Environment

Edit `.env` file with your settings:

```env
APP_NAME=SC AI Assistant
APP_ENV=development

API_HOST=0.0.0.0
API_PORT=8000

OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

DATABASE_URL=sqlite:///./sc_ai.db

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### Step 5: Start the API Server

```bash
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 6: Access the API

Open your browser to:
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## Usage Examples

### Example 1: Topline Adjustment

**Query:** "What does the forecast look like if we increase the topline by 25%?"

**API Call:**
```bash
curl -X POST "http://localhost:8000/scenario/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What does the forecast look like if we increase the topline by 25%?",
    "scope": {}
  }'
```

**Response:**
```json
{
  "session_id": "session_123",
  "query": "What does the forecast look like if we increase the topline by 25%?",
  "perturbations": [
    {"type": "topline", "multiplier": 1.25, "scope": "all"}
  ],
  "perturbation_summary": "+25% topline",
  "adjusted_forecast": {
    "original_total_qty": 150000,
    "adjusted_total_qty": 187500,
    "total_change_pct": 25.0
  },
  "stockout_risk": {
    "sku_count_at_risk": 14,
    "total_revenue_at_risk": 380000,
    "core_sku_count_at_risk": 8
  },
  "otb_position": {
    "overcommitted_categories": ["Apparel"],
    "total_overcommit_amount": 120000
  },
  "recommendations": {
    "recommendations": [
      {
        "action_type": "expedite",
        "description": "Expedite PO-4821",
        "cost": 8000,
        "revenue_protected": 180000
      }
    ]
  }
}
```

### Example 2: Channel-Specific Adjustment

**Query:** "Show me the impact if DTC demand drops 15% while wholesale stays flat"

**API Call:**
```bash
curl -X POST "http://localhost:8000/scenario/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me the impact if DTC demand drops 15% while wholesale stays flat",
    "scope": {}
  }'
```

### Example 3: Multi-Turn Scenario

**First Query:** "What happens to stockout risk if apparel demand is up 30%?"

**Follow-up Query:** "Now add a 10% demand uplift to all channels"

**Reset Scenario:**
```bash
curl -X POST "http://localhost:8000/scenario/reset?session_id=session_123"
```

---

## Data Flow Explanation

### End-to-End Workflow

1. **User submits query** → FastAPI receives HTTP request
2. **LangGraph parses intent** → Extracts perturbations from natural language
3. **Retrieve baseline forecast** → Reads from `forecast` table with CI bands
4. **Apply perturbations** → Multiplies forecast by scalar(s)
5. **Calculate stockout risk** → Monte Carlo simulation over adjusted demand
6. **Evaluate OTB position** → Re-calculates budget commitment
7. **Generate recommendations** → Ranks mitigation actions
8. **Return response** → JSON with all results and tool trace

### Sample Data

The system generates realistic business data:

- **100 SKUs** across 3 categories (Apparel, Shoes, Accessories)
- **2 channels** (DTC, Wholesale)
- **3 warehouses** (MUM_WH1, DEL_WH1, BLR_WH1)
- **4 suppliers** with varying lead times
- **90-day forecast horizon** with daily forecasts
- **50 open purchase orders** with cancelability flags
- **OTB budgets** by category and quarter

### Data Volume

- Forecast records: 9,000 (100 SKUs × 90 days)
- Inventory records: 600 (100 SKUs × 3 warehouses × 2 channels)
- Sales actuals: 3,000 (100 SKUs × 30 days historical)
- Purchase orders: 50
- Lead time records: 12 (4 suppliers × 3 categories)

---

## Beginner's Guide to Components

### What is a Perturbation?

A **perturbation** is a change you want to apply to the forecast. Think of it as a "what-if" scenario:

- **Topline:** Change everything by X% (e.g., +25% topline)
- **Channel:** Change a specific channel (e.g., DTC down 15%)
- **Category:** Change a specific category (e.g., Apparel up 30%)
- **Shipment Delay:** Delay shipments by X days

### What is CI (Confidence Interval)?

**CI** stands for Confidence Interval. It shows the range of possible outcomes:

- **80% CI:** There's an 80% chance the actual value falls in this range
- **95% CI:** There's a 95% chance the actual value falls in this range

Wider CI = more uncertainty. Narrower CI = more confidence.

### What is Stockout Risk?

**Stockout risk** is the probability that you'll run out of inventory:

- **Low risk:** < 30% probability
- **Medium risk:** 30-50% probability
- **High risk:** 50-70% probability
- **Critical risk:** > 70% probability

### What is OTB?

**OTB** stands for Open-to-Buy. It's your budget for purchasing inventory:

- **Budget:** Total amount you can spend
- **Committed:** Amount already spent on open POs
- **Available:** Budget - Committed
- **Overcommitted:** Committed > Budget (bad!)

### What is a Recommendation?

A **recommendation** is an action you can take to mitigate risk:

- **Buy:** Purchase more inventory
- **Expedite:** Speed up existing shipments
- **Delay:** Postpone shipments to free cash
- **Cancel:** Cancel purchase orders
- **Reallocate:** Move inventory between channels

Each recommendation includes:
- Cost to implement
- Revenue protected
- Confidence level
- Caveats and tradeoffs

---

## Common Issues & Solutions

### Issue 1: Ollama Not Found

**Error:** `Connection refused to Ollama`

**Solution:**
1. Ensure Ollama is installed: https://ollama.com
2. Start Ollama: `ollama serve`
3. Pull the model: `ollama pull llama3`
4. Check Ollama is running: `curl http://localhost:11434`

### Issue 2: Database Lock Error

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
- Close any other processes accessing the database
- Delete the `sc_ai.db` file and re-run `python scripts/init_db.py`

### Issue 3: Import Errors

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
- Run `uv sync` to install dependencies
- Ensure you're in the project root directory
- Check Python version: `python --version` (should be 3.13+)

### Issue 4: Port Already in Use

**Error:** `Address already in use: port 8000`

**Solution:**
- Use a different port: `uvicorn apps.api.main:app --port 8001`
- Or kill the process using port 8000:
  - Windows: `netstat -ano | findstr :8000` then `taskkill /PID <pid>`
  - Linux/Mac: `lsof -ti:8000 | xargs kill`

### Issue 5: Slow Performance

**Symptom:** API responses take > 10 seconds

**Solution:**
- Check if Ollama model is loaded: `ollama list`
- Reduce forecast horizon in query
- Use category/channel filters to limit data volume

---

## Enterprise Design Practices

### Separation of Concerns

Each layer has a single, well-defined responsibility. This makes the system:
- **Testable:** Each layer can be unit-tested independently
- **Maintainable:** Changes to one layer don't break others
- **Scalable:** Layers can be optimized or replaced independently

### Type Safety

All data structures use Pydantic models for:
- **Validation:** Catch data errors at runtime
- **Documentation:** Self-documenting code
- **IDE Support:** Autocomplete and type hints

### Observability

Every operation is logged with:
- **Timestamp:** When it happened
- **Session ID:** Which conversation
- **Arguments:** What was passed
- **Result:** What was returned
- **Duration:** How long it took

### Deterministic Arithmetic

- **LLM** orchestrates and synthesizes
- **Python tools** do the math
- This ensures reproducible, auditable results

### Advisory, Not Autonomous

- The system **recommends**, humans decide
- Clear caveats and confidence levels
- Tradeoffs are explicitly presented

---

## Next Steps for Production

This MVP is designed to be a foundation for production deployment. Future enhancements could include:

1. **Real Database:** Replace SQLite with PostgreSQL
2. **Redis Cache:** Replace SQLite cache with Redis
3. **Streamlit UI:** Add a modern web UI
4. **Authentication:** Add user authentication and authorization
5. **Multi-tenant:** Support multiple companies/organizations
6. **Advanced LLM:** Use more sophisticated models via Ollama
7. **Probabilistic Scenarios:** Monte Carlo over scenario space
8. **Forecast Improvement:** ML-based forecast model
9. **Real-time Data:** Streaming data ingestion
10. **Langfuse Integration:** Advanced LLM tracing and evaluation

---

## Support & Documentation

- **API Documentation:** http://localhost:8000/docs (when running)
- **Logs:** Check `logs/app.log` and `logs/error.log`
- **Database:** SQLite file at `sc_ai.db` (can open with DB Browser for SQLite)

---

## License

This project is provided as an MVP for educational and prototyping purposes.

---

**Built with enterprise-level standards using only free and open-source tools.**


<!-- Full End-to-End Flow -->
User query
    ↓
LLM parses perturbation (llama3.2:3b)
    ↓
Validation removes hallucinated perturbations
    ↓
get_demand_forecast → reads 9,000 forecast rows
    ↓
apply_topline_adjustment → multiplies adjusted_forecast_qty
    ↓
calculate_stockout_risk → Monte Carlo per SKU
    ↓
evaluate_otb_position → budget vs committed spend
    ↓
generate_recommendations → ranked action plan
    ↓
Response stripped to summary + top 10 SKUs
    ↓
Streamlit renders charts + tables