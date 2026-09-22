# Profit Intelligence Engine

A Python-based inventory and working-capital intelligence platform that turns operational sales and inventory data into executive decision support.

> **Portfolio edition:** this repository uses 100% synthetic data. It contains no employer, customer, inventory, pricing, or sales records.

## Why I built it

Equipment dealerships can hold millions of dollars in inventory while sales velocity varies dramatically by model, brand, and location. Raw ERP exports show what is in stock and what sold, but they do not automatically answer:

- Which current models appear overstocked relative to observed demand?
- How much current inventory cost sits above a selected days-of-supply scenario?
- Which models should management review first?
- Which inventory lacks trustworthy sales evidence and needs verification?
- How does the answer change under 90, 120, 180, or 270-day scenarios?

## What the app does

1. Aggregates current inventory by Make + Model.
2. Strictly matches YTD sales to current inventory models.
3. Calculates observed unit-sales velocity.
4. Estimates days of supply.
5. Models evidence-backed working-capital exposure above a selected supply threshold.
6. Separates unverified inventory instead of forcing weak matches.
7. Flags directional price-to-current-cost anomalies for verification.
8. Produces brand, store, scenario, and management-action views.

## Run the dashboard

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Key guardrail

The project intentionally distinguishes **evidence-backed exposure** from **unverified inventory**.

A current model with no trusted YTD sales match is not automatically labeled dead or excess inventory. It is placed into a verification population. Likewise, a negative directional spread is a **verification flag**, not a claimed loss.

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
Scenario Modeling (90 / 120 / 180 / 270)
         |
         +--> Working-Capital Opportunities
         +--> Brand Exposure
         +--> Store Exposure
         +--> Management Action Queue
         +--> Cost / Pricing Verification Flags
```

## Technology

- Python
- pandas
- Streamlit
- deterministic synthetic-data generation
- strict identifier normalization
- scenario modeling
- executive KPI design

## Project structure

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

## Data safety

The public repository deliberately does **not** contain employer data, customer information, real store inventory, proprietary pricing, real sales transactions, or internal financial figures.

All demo records are generated in `engine/demo_data.py` using fictional manufacturers, models, stores, costs, and sales.

## Portfolio focus

This project demonstrates the ability to translate messy operational data into financial opportunity identification, inventory decision support, conservative matching logic, executive dashboards, scenario analysis, and business-facing guardrails.

## Author

**Alex Monday**

Business intelligence • ERP/data administration • Python automation • operational analytics
