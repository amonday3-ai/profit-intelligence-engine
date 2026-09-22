from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from engine import analyze_inventory, build_demo_data, scenario_table


st.set_page_config(
    page_title="Profit Intelligence Engine",
    page_icon="📊",
    layout="wide",
)

SNAPSHOT_DATE = date(2026, 9, 14)


def money(value: float) -> str:
    return f"${value:,.0f}"


def percent(value: float) -> str:
    return f"{value:.1%}"


# ---------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------
st.title("📊 Profit Intelligence Engine")
st.markdown(
    """
    **Inventory working-capital intelligence for equipment dealerships**

    This public portfolio demo shows how sales velocity and current inventory
    can be converted into management-ready opportunity signals.
    """
)

st.caption(
    "Portfolio edition • 100% synthetic data • No employer, customer, pricing, "
    "inventory, or proprietary sales records are included."
)


# ---------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("Scenario Controls")

    target_days = st.select_slider(
        "Target days of supply",
        options=[90, 120, 180, 270],
        value=180,
        help=(
            "Select the inventory-duration scenario used to estimate "
            "evidence-backed working-capital exposure."
        ),
    )

    st.divider()

    st.subheader("About this demo")
    st.markdown(
        """
        **Data:** Synthetic dealership inventory + YTD sales

        **Matching:** Strict Make + Model

        **Primary goal:** Identify where current inventory cost may be
        out of alignment with observed sales velocity.
        """
    )

    st.warning(
        "Exposure is a decision-support estimate, not a booked saving, "
        "accounting reserve, or liquidation recommendation."
    )


# ---------------------------------------------------------------------
# DATA + ANALYSIS
# ---------------------------------------------------------------------
inventory, sales = build_demo_data(snapshot_date=SNAPSHOT_DATE)

model = analyze_inventory(
    inventory,
    sales,
    snapshot_date=SNAPSHOT_DATE,
    target_days=target_days,
)

scenarios = scenario_table(model)

current_cost = float(model["current_inventory_cost"].sum())

trusted_cost = float(
    model.loc[
        model["trusted_sales_evidence"],
        "current_inventory_cost",
    ].sum()
)

coverage = trusted_cost / current_cost if current_cost else 0

exposure = float(
    model["evidence_backed_excess_working_capital"].sum()
)

unverified = float(
    model["unverified_inventory_cost"].sum()
)

a_tier = model[
    model["action"] == "A - SLOW-MOVING HIGH EXPOSURE"
].copy()

a_tier_exposure = float(
    a_tier["evidence_backed_excess_working_capital"].sum()
)

a_tier_share = (
    a_tier_exposure / exposure
    if exposure
    else 0
)

pricing_flags = int(
    model["pricing_cost_flag"]
    .astype(str)
    .str.len()
    .gt(0)
    .sum()
)


# ---------------------------------------------------------------------
# BUSINESS CONTEXT
# ---------------------------------------------------------------------
with st.expander("💼 Business Problem & Approach", expanded=False):
    left, right = st.columns(2)

    with left:
        st.markdown(
            """
            ### Business problem

            ERP exports can show what is currently in stock and what has sold,
            but they do not automatically show:

            - which models appear overstocked relative to demand,
            - where working capital is concentrated,
            - which records need verification,
            - or how the answer changes under different inventory thresholds.
            """
        )

    with right:
        st.markdown(
            """
            ### Analytical approach

            1. Aggregate current inventory by Make + Model.
            2. Strictly match YTD sales to current inventory.
            3. Calculate observed unit velocity.
            4. Estimate days of supply.
            5. Model current inventory cost above the selected scenario.
            6. Keep unmatched inventory in a separate verification bucket.
            """
        )


# ---------------------------------------------------------------------
# KPI ROW
# ---------------------------------------------------------------------
st.subheader("Executive Snapshot")

k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Current Inventory Cost",
    money(current_cost),
)

k2.metric(
    f"{target_days}-Day Evidence-Backed Exposure",
    money(exposure),
)

k3.metric(
    "Trusted Inventory-Cost Coverage",
    percent(coverage),
)

k4.metric(
    "Unverified Inventory Cost",
    money(unverified),
)

k5, k6, k7 = st.columns(3)

k5.metric(
    "A-Tier Exposure",
    money(a_tier_exposure),
)

k6.metric(
    "A-Tier Share of Exposure",
    percent(a_tier_share),
)

k7.metric(
    "Cost / Pricing Verification Flags",
    f"{pricing_flags:,}",
)

st.info(
    "Evidence-backed exposure includes only current models with trusted YTD "
    "sales evidence. Unverified inventory remains separate so weak matches "
    "cannot inflate the opportunity."
)


# ---------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Top Opportunities",
        "Scenario Sensitivity",
        "Brand & Store Exposure",
        "Management Queue",
    ]
)


# ---------------------------------------------------------------------
# TOP OPPORTUNITIES
# ---------------------------------------------------------------------
with tab1:
    st.subheader("Top Working-Capital Opportunities")

    top = model[
        model["evidence_backed_excess_working_capital"] > 0
    ].copy()

    top = top.sort_values(
        "evidence_backed_excess_working_capital",
        ascending=False,
    ).head(10)

    top["Days Supply"] = pd.to_numeric(
        top["estimated_days_supply"],
        errors="coerce",
    ).round(0)

    display_top = top[
        [
            "make",
            "model",
            "on_hand_units",
            "ytd_units_sold",
            "Days Supply",
            "current_inventory_cost",
            "evidence_backed_excess_working_capital",
            "pricing_cost_flag",
        ]
    ].rename(
        columns={
            "make": "Make",
            "model": "Model",
            "on_hand_units": "On Hand",
            "ytd_units_sold": "YTD Sold",
            "current_inventory_cost": "Inventory Cost",
            "evidence_backed_excess_working_capital": "Exposure",
            "pricing_cost_flag": "Verification",
        }
    )

    st.dataframe(
        display_top,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Inventory Cost": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Exposure": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Days Supply": st.column_config.NumberColumn(
                format="%.0f",
            ),
        },
    )

    top10_total = float(
        top["evidence_backed_excess_working_capital"].sum()
    )

    st.caption(
        f"Top 10 opportunity concentration: {money(top10_total)} "
        f"({percent(top10_total / exposure if exposure else 0)} of current scenario exposure)."
    )


# ---------------------------------------------------------------------
# SCENARIO SENSITIVITY
# ---------------------------------------------------------------------
with tab2:
    st.subheader("Scenario Sensitivity")

    left, right = st.columns([1.3, 1])

    with left:
        chart_data = scenarios.set_index(
            "days_supply"
        )["evidence_backed_exposure"]

        st.line_chart(chart_data)

    with right:
        scenario_display = scenarios.rename(
            columns={
                "days_supply": "Days Supply",
                "evidence_backed_exposure": "Exposure",
                "models_with_exposure": "Models",
            }
        )

        st.dataframe(
            scenario_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Exposure": st.column_config.NumberColumn(
                    format="$%d",
                ),
            },
        )

    st.caption(
        "Lower supply thresholds create a more aggressive working-capital view. "
        "Higher thresholds are more conservative. These are analytical scenarios, "
        "not company policy."
    )


# ---------------------------------------------------------------------
# BRAND / STORE
# ---------------------------------------------------------------------
with tab3:
    brand_col, store_col = st.columns(2)

    with brand_col:
        st.subheader("Brand Exposure")

        brand = (
            model.groupby(
                "make",
                as_index=False,
            )
            .agg(
                inventory_cost=(
                    "current_inventory_cost",
                    "sum",
                ),
                evidence_backed_exposure=(
                    "evidence_backed_excess_working_capital",
                    "sum",
                ),
            )
            .sort_values(
                "evidence_backed_exposure",
                ascending=False,
            )
        )

        st.bar_chart(
            brand.set_index(
                "make"
            )["evidence_backed_exposure"]
        )

        st.dataframe(
            brand.rename(
                columns={
                    "make": "Brand",
                    "inventory_cost": "Inventory Cost",
                    "evidence_backed_exposure": "Exposure",
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Inventory Cost": st.column_config.NumberColumn(
                    format="$%d",
                ),
                "Exposure": st.column_config.NumberColumn(
                    format="$%d",
                ),
            },
        )

    with store_col:
        st.subheader("Current Inventory by Store")

        store = (
            inventory.groupby(
                "store",
                as_index=False,
            )
            .agg(
                units=("stock_number", "count"),
                inventory_cost=("invoice_cost", "sum"),
            )
            .sort_values(
                "inventory_cost",
                ascending=False,
            )
        )

        st.bar_chart(
            store.set_index(
                "store"
            )["inventory_cost"]
        )

        st.dataframe(
            store.rename(
                columns={
                    "store": "Store",
                    "units": "Units",
                    "inventory_cost": "Inventory Cost",
                }
            ),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Inventory Cost": st.column_config.NumberColumn(
                    format="$%d",
                ),
            },
        )


# ---------------------------------------------------------------------
# MANAGEMENT QUEUE
# ---------------------------------------------------------------------
with tab4:
    st.subheader("Management Action Queue")

    action_counts = (
        model.groupby(
            "action",
            as_index=False,
        )
        .agg(
            models=("model", "count"),
            inventory_cost=(
                "current_inventory_cost",
                "sum",
            ),
            evidence_backed_exposure=(
                "evidence_backed_excess_working_capital",
                "sum",
            ),
        )
        .sort_values(
            "evidence_backed_exposure",
            ascending=False,
        )
    )

    st.dataframe(
        action_counts.rename(
            columns={
                "action": "Action",
                "models": "Models",
                "inventory_cost": "Inventory Cost",
                "evidence_backed_exposure": "Exposure",
            }
        ),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Inventory Cost": st.column_config.NumberColumn(
                format="$%d",
            ),
            "Exposure": st.column_config.NumberColumn(
                format="$%d",
            ),
        },
    )

    st.markdown(
        """
        **Suggested interpretation**

        - **A - Slow-Moving High Exposure:** review first.
        - **B - Promote / Purchasing Review:** assess promotion, transfer, or future purchasing.
        - **B - Restock Review:** demand appears strong relative to current stock.
        - **Verify Zero-Sales:** confirm model identity and historical sales before escalation.
        """
    )


# ---------------------------------------------------------------------
# DOWNLOAD
# ---------------------------------------------------------------------
st.divider()
st.subheader("Download Demo Opportunity Data")

download_cols = [
    "make",
    "model",
    "on_hand_units",
    "current_inventory_cost",
    "ytd_units_sold",
    "estimated_days_supply",
    "evidence_backed_excess_working_capital",
    "unverified_inventory_cost",
    "action",
    "pricing_cost_flag",
    "stores",
]

download_df = model[download_cols].copy()

csv_data = download_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Opportunity Queue as CSV",
    data=csv_data,
    file_name="profit_intelligence_demo_opportunity_queue.csv",
    mime="text/csv",
)


# ---------------------------------------------------------------------
# METHODOLOGY
# ---------------------------------------------------------------------
with st.expander("Methodology & Guardrails"):
    st.markdown(
        """
        ### What the model does

        1. Aggregates current inventory by Make + Model.
        2. Strictly matches YTD sales using normalized Make + Model identifiers.
        3. Calculates observed unit velocity from January 1 through the snapshot date.
        4. Converts that velocity into estimated days of supply.
        5. Estimates the portion of current inventory cost above the selected
           days-of-supply scenario.
        6. Keeps models without trusted sales evidence in a separate verification bucket.

        ### What the model does not claim

        - Exposure is **not** a guaranteed saving or accounting reserve.
        - Zero matched sales does **not** prove inventory is dead.
        - Estimated price-to-current-cost spread is **not** realized gross profit.
        - Management should combine these signals with seasonality, OEM programs,
          incoming purchase orders, commitments, promotions, and local demand.

        ### Data safety

        Every record in this public demo is synthetic and generated deterministically
        in `engine/demo_data.py`.
        """
    )


st.caption(
    "Portfolio project by Alex Monday • Python • pandas • Streamlit • "
    "inventory analytics • scenario modeling • executive decision support"
)
