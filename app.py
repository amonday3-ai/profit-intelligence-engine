from __future__ import annotations

from datetime import date
import pandas as pd
import streamlit as st

from engine import analyze_inventory, build_demo_data, scenario_table

st.set_page_config(page_title="Profit Intelligence Engine", page_icon="📊", layout="wide")
SNAPSHOT_DATE = date(2026, 9, 14)

st.title("Profit Intelligence Engine")
st.caption("Public portfolio demo using 100% synthetic equipment-dealership data. No employer, customer, pricing, inventory, or sales data is included.")

with st.sidebar:
    st.header("Scenario")
    target_days = st.select_slider("Target days of supply", options=[90, 120, 180, 270], value=180)
    st.markdown("**Interpretation**\n\nThis is a decision-support scenario, not an accounting reserve. Models without trusted sales evidence are kept separate from evidence-backed exposure.")

inventory, sales = build_demo_data(snapshot_date=SNAPSHOT_DATE)
model = analyze_inventory(inventory, sales, snapshot_date=SNAPSHOT_DATE, target_days=target_days)

current_cost = model["current_inventory_cost"].sum()
trusted_cost = model.loc[model["trusted_sales_evidence"], "current_inventory_cost"].sum()
coverage = trusted_cost / current_cost if current_cost else 0
exposure = model["evidence_backed_excess_working_capital"].sum()
unverified = model["unverified_inventory_cost"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Inventory Cost", f"${current_cost:,.0f}")
c2.metric(f"{target_days}-Day Evidence-Backed Exposure", f"${exposure:,.0f}")
c3.metric("Trusted Inventory-Cost Coverage", f"{coverage:.1%}")
c4.metric("Unverified Inventory Cost", f"${unverified:,.0f}")

st.info("Evidence-backed exposure uses only current models with strict Make + Model YTD sales evidence. Unverified inventory is deliberately excluded.")

left, right = st.columns([1.15, 1])

with left:
    st.subheader("Top Working-Capital Opportunities")
    top = model[model["evidence_backed_excess_working_capital"] > 0].head(10).copy()
    top["Exposure"] = top["evidence_backed_excess_working_capital"].map(lambda x: f"${x:,.0f}")
    top["Inventory Cost"] = top["current_inventory_cost"].map(lambda x: f"${x:,.0f}")
    top["Days Supply"] = pd.to_numeric(top["estimated_days_supply"], errors="coerce").round(0)
    st.dataframe(
        top[["make","model","on_hand_units","ytd_units_sold","Days Supply","Inventory Cost","Exposure","pricing_cost_flag"]]
        .rename(columns={"make":"Make","model":"Model","on_hand_units":"On Hand","ytd_units_sold":"YTD Sold","pricing_cost_flag":"Verification"}),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("Scenario Sensitivity")
    scenarios = scenario_table(model)
    st.line_chart(scenarios.set_index("days_supply")["evidence_backed_exposure"])
    st.dataframe(
        scenarios.rename(columns={"days_supply":"Days Supply","evidence_backed_exposure":"Exposure","models_with_exposure":"Models"}),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
brand_col, store_col = st.columns(2)

with brand_col:
    st.subheader("Brand Exposure")
    brand = model.groupby("make", as_index=False).agg(
        inventory_cost=("current_inventory_cost","sum"),
        evidence_backed_exposure=("evidence_backed_excess_working_capital","sum"),
    ).sort_values("evidence_backed_exposure", ascending=False)
    st.bar_chart(brand.set_index("make")["evidence_backed_exposure"])

with store_col:
    st.subheader("Current Inventory by Store")
    store = inventory.groupby("store", as_index=False).agg(
        units=("stock_number","count"),
        inventory_cost=("invoice_cost","sum"),
    ).sort_values("inventory_cost", ascending=False)
    st.bar_chart(store.set_index("store")["inventory_cost"])

st.divider()
st.subheader("Management Action Queue")
action_counts = model.groupby("action", as_index=False).agg(
    models=("model","count"),
    inventory_cost=("current_inventory_cost","sum"),
    evidence_backed_exposure=("evidence_backed_excess_working_capital","sum"),
).sort_values("evidence_backed_exposure", ascending=False)
st.dataframe(action_counts, use_container_width=True, hide_index=True)

with st.expander("Methodology and guardrails"):
    st.markdown("""
### What the model does
1. Aggregates current inventory by Make + Model.
2. Strictly matches YTD sales using normalized Make + Model identifiers.
3. Calculates observed unit velocity from January 1 through the snapshot date.
4. Converts that velocity into estimated days of supply.
5. Estimates the portion of current inventory cost above the selected days-of-supply scenario.
6. Keeps models without trusted sales evidence in a separate verification bucket.

### What the model does not claim
- Exposure is **not** a guaranteed saving or accounting reserve.
- Zero matched sales does **not** prove inventory is dead.
- Estimated price-to-current-cost spread is **not** realized gross profit.
- Management should combine these signals with seasonality, OEM programs, incoming purchase orders, commitments, promotions, and local demand.

### Data
Every record in this public demo is synthetic and generated deterministically in `engine/demo_data.py`.
""")

st.caption("Portfolio project: Python • pandas • Streamlit • inventory analytics • scenario modeling • executive decision support")
