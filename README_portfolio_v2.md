# 📊 Profit Intelligence Engine

**Inventory working-capital intelligence for equipment dealerships**

[🚀 Launch the Live Demo](https://profit-intelligence-engine-jf5ufd3ezkdtotarikappmy.streamlit.app/)

A Python and Streamlit portfolio project that converts current inventory and YTD sales velocity into management-ready working-capital signals.

> **Portfolio edition:** This repository uses 100% synthetic data. It contains no employer, customer, pricing, inventory, or proprietary sales records.

---

## The Business Problem

ERP and dealership-management-system exports can tell a company:

- what inventory is currently on hand,
- what each unit costs,
- and what has sold.

But those exports do not automatically answer:

- Which models appear overstocked relative to observed demand?
- Where is working capital concentrated?
- Which models should management review first?
- Which inventory lacks trustworthy sales evidence?
- How does the opportunity change under different days-of-supply thresholds?

The Profit Intelligence Engine turns those raw operational questions into a repeatable analytical workflow.

---

## What the Engine Does

The application:

1. Aggregates current inventory by **Make + Model**.
2. Strictly matches YTD sales to current inventory.
3. Calculates observed unit-sales velocity.
4. Estimates days of supply.
5. Models current inventory cost above a selected supply threshold.
6. Separates unverified inventory instead of forcing weak matches.
7. Flags directional price-to-current-cost anomalies for verification.
8. Produces executive views for:
   - working-capital opportunities,
   - scenario sensitivity,
   - brand exposure,
   - store exposure,
   - and management action queues.

---

## 🚀 Live Demo

### [Launch the Profit Intelligence Engine →](https://profit-intelligence-engine-jf5ufd3ezkdtotarikappmy.streamlit.app/)

The demo includes interactive **90 / 120 / 180 / 270-day supply scenarios**.

Users can explore:

- Executive KPIs
- Top working-capital opportunities
- A-tier concentration
- Scenario sensitivity
- Brand-level exposure
- Store-level inventory
- Management action queues
- Cost / pricing verification flags
- Downloadable opportunity data

---

## Executive Logic

The central calculation asks:

> **Based on observed YTD unit velocity, how much of the current inventory cost sits above a selected days-of-supply scenario?**

For example, if a model has:

- 8 units currently on hand
- 1 unit sold over approximately 257 YTD days

then observed unit velocity is approximately:

```text
1 unit / 257 days = 0.00389 units per day
```

A 180-day supply scenario would support approximately:

```text
0.00389 × 180 = 0.70 units
```

The engine then estimates the proportional current inventory cost represented by inventory above that scenario.

This creates an **evidence-backed working-capital review signal**.

It does **not** automatically recommend liquidation or discounting.

---

## Key Analytical Guardrail

The engine intentionally distinguishes:

### Evidence-Backed Exposure

Current inventory where the model has trusted YTD Make + Model sales evidence.

### Unverified Inventory

Current models where the application cannot establish trusted YTD sales evidence.

Unverified inventory is kept separate and is **not automatically labeled dead or excess inventory**.

This design prevents weak matching from artificially inflating the financial opportunity.

Likewise, a negative directional spread is treated as a:

```text
VERIFY COST / PRICING
```

flag rather than a claimed financial loss.

---

## Architecture

```text
Synthetic Inventory + YTD Sales
              |
              v
       Data Validation
              |
              v
     Make + Model Normalization
              |
              v
      Strict Trusted Matching
          /             \
         v               v
 Sales Evidence      Unverified
         |
         v
   Unit Sales Velocity
         |
         v
  Estimated Days Supply
         |
         v
Scenario Modeling
(90 / 120 / 180 / 270)
         |
         +--> Working-Capital Opportunities
         +--> A-Tier Prioritization
         +--> Brand Exposure
         +--> Store Exposure
         +--> Management Action Queue
         +--> Cost / Pricing Verification
```

---

## Technology

- **Python**
- **pandas**
- **Streamlit**
- Synthetic-data generation
- Data normalization
- Strict identifier matching
- Scenario modeling
- Executive KPI design
- Operational decision-support logic

---

## Repository Structure

```text
profit-intelligence-engine/
├── app.py
├── engine/
│   ├── __init__.py
│   ├── analysis.py
│   └── demo_data.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Run Locally

Clone the repository:

```bash
git clone https://github.com/amonday3-ai/profit-intelligence-engine.git
cd profit-intelligence-engine
```

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run app.py
```

---

## Data Safety

This public portfolio repository deliberately contains **no real employer data**.

It does not include:

- customer records,
- real store inventory,
- proprietary pricing,
- actual sales transactions,
- internal financial results,
- or confidential company information.

All demonstration records are generated deterministically in:

```text
engine/demo_data.py
```

using fictional:

- manufacturers,
- models,
- locations,
- costs,
- and sales activity.

---

## What This Project Demonstrates

This project is designed to show more than Python syntax.

It demonstrates the ability to:

- translate operational data into business questions,
- create conservative data-matching rules,
- connect inventory velocity to working-capital analysis,
- distinguish verified evidence from uncertain records,
- create scenario-based financial models,
- build management action queues,
- communicate analytical limitations,
- and present results through an executive-facing application.

---

## Potential Production Enhancements

A production implementation could add:

- seasonality by product category,
- incoming purchase orders,
- manufacturer programs and commitments,
- historical sold-unit cost,
- true gross-margin analysis,
- inter-store transfer recommendations,
- automated weekly refreshes,
- demand forecasting,
- and purchasing / reorder recommendations.

---

## Author

### Alex Monday

**Business Intelligence • ERP/Data Administration • Python Automation • Operational Analytics**

[Live Demo](https://profit-intelligence-engine-jf5ufd3ezkdtotarikappmy.streamlit.app/)  
[GitHub Repository](https://github.com/amonday3-ai/profit-intelligence-engine)
