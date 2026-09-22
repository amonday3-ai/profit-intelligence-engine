"""Inventory and working-capital analysis for the public portfolio demo."""

from __future__ import annotations

from datetime import date

import pandas as pd


def _normalize_key(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.upper()
        .str.replace(r"[^A-Z0-9]+", "", regex=True)
    )


def analyze_inventory(
    inventory: pd.DataFrame,
    sales: pd.DataFrame,
    snapshot_date: date,
    target_days: int = 180,
) -> pd.DataFrame:
    """Build model-level inventory intelligence using strict make+model matching."""

    inv = inventory.copy()
    sal = sales.copy()

    inv["key"] = (
        _normalize_key(inv["make"])
        + "|"
        + _normalize_key(inv["model"])
    )

    sal["key"] = (
        _normalize_key(sal["make"])
        + "|"
        + _normalize_key(sal["model"])
    )

    sal["sale_date"] = pd.to_datetime(
        sal["sale_date"],
        errors="coerce",
    )

    snapshot_ts = pd.Timestamp(snapshot_date)
    year_start = pd.Timestamp(
        date(snapshot_date.year, 1, 1)
    )

    sal = sal[
        sal["sale_date"].between(
            year_start,
            snapshot_ts,
            inclusive="both",
        )
    ].copy()

    elapsed_days = max(
        (snapshot_ts - year_start).days + 1,
        1,
    )

    inventory_by_model = (
        inv.groupby(
            ["key", "make", "model"],
            as_index=False,
        )
        .agg(
            on_hand_units=("stock_number", "count"),
            current_inventory_cost=("invoice_cost", "sum"),
            median_current_invoice_cost=("invoice_cost", "median"),
            stores=(
                "store",
                lambda s: " | ".join(
                    sorted(set(s))
                ),
            ),
        )
    )

    sales_by_model = (
        sal.groupby(
            "key",
            as_index=False,
        )
        .agg(
            ytd_units_sold=("key", "size"),
            ytd_sales_value=("sale_value", "sum"),
            avg_sale_value=("sale_value", "mean"),
        )
    )

    out = inventory_by_model.merge(
        sales_by_model,
        on="key",
        how="left",
    )

    for col in [
        "ytd_units_sold",
        "ytd_sales_value",
        "avg_sale_value",
    ]:
        out[col] = pd.to_numeric(
            out[col],
            errors="coerce",
        ).fillna(0)

    out["trusted_sales_evidence"] = (
        out["ytd_units_sold"] > 0
    )

    out["avg_daily_unit_sales"] = (
        out["ytd_units_sold"] / elapsed_days
    )

    out["estimated_days_supply"] = pd.NA

    has_sales = (
        out["avg_daily_unit_sales"] > 0
    )

    out.loc[
        has_sales,
        "estimated_days_supply",
    ] = (
        out.loc[
            has_sales,
            "on_hand_units",
        ]
        / out.loc[
            has_sales,
            "avg_daily_unit_sales",
        ]
    )

    out["target_units"] = (
        out["avg_daily_unit_sales"]
        * target_days
    )

    out["estimated_excess_units"] = (
        out["on_hand_units"]
        - out["target_units"]
    ).clip(lower=0)

    out[
        "evidence_backed_excess_working_capital"
    ] = 0.0

    eligible = (
        has_sales
        & out["on_hand_units"].gt(0)
    )

    out.loc[
        eligible,
        "evidence_backed_excess_working_capital",
    ] = (
        out.loc[
            eligible,
            "estimated_excess_units",
        ]
        / out.loc[
            eligible,
            "on_hand_units",
        ]
        * out.loc[
            eligible,
            "current_inventory_cost",
        ]
    )

    out[
        "unverified_inventory_cost"
    ] = 0.0

    out.loc[
        ~has_sales,
        "unverified_inventory_cost",
    ] = out.loc[
        ~has_sales,
        "current_inventory_cost",
    ]

    out["estimated_spread_per_unit"] = (
        out["avg_sale_value"]
        - out["median_current_invoice_cost"]
    )

    out.loc[
        ~has_sales,
        "estimated_spread_per_unit",
    ] = pd.NA

    def classify(row):
        if row["ytd_units_sold"] <= 0:
            if (
                row["current_inventory_cost"] >= 50000
                or row["on_hand_units"] >= 5
            ):
                return (
                    "A - VERIFY ZERO-SALES HIGH EXPOSURE"
                )

            return "B - VERIFY ZERO-SALES"

        days = row["estimated_days_supply"]

        if (
            pd.notna(days)
            and days > 365
            and row["current_inventory_cost"] >= 20000
        ):
            return (
                "A - SLOW-MOVING HIGH EXPOSURE"
            )

        if (
            pd.notna(days)
            and days > target_days
        ):
            return (
                "B - PROMOTE / PURCHASING REVIEW"
            )

        if (
            pd.notna(days)
            and days <= 60
            and row["ytd_units_sold"] >= 2
        ):
            return "B - RESTOCK REVIEW"

        return "C - BALANCED"

    out["action"] = out.apply(
        classify,
        axis=1,
    )

    out["pricing_cost_flag"] = (
        out["estimated_spread_per_unit"]
        .apply(
            lambda x: (
                "VERIFY COST / PRICING"
                if pd.notna(x) and x < 0
                else ""
            )
        )
    )

    return (
        out.sort_values(
            "evidence_backed_excess_working_capital",
            ascending=False,
        )
        .reset_index(drop=True)
    )


def scenario_table(
    model_data: pd.DataFrame,
    days_values=(90, 120, 180, 270),
) -> pd.DataFrame:
    """Recalculate exposure for several days-of-supply scenarios."""

    rows = []

    for days in days_values:
        target_units = (
            model_data["avg_daily_unit_sales"]
            * days
        )

        excess_units = (
            model_data["on_hand_units"]
            - target_units
        ).clip(lower=0)

        cost = pd.Series(
            0.0,
            index=model_data.index,
        )

        eligible = (
            model_data[
                "trusted_sales_evidence"
            ]
            & model_data[
                "on_hand_units"
            ].gt(0)
        )

        cost.loc[eligible] = (
            excess_units.loc[eligible]
            / model_data.loc[
                eligible,
                "on_hand_units",
            ]
            * model_data.loc[
                eligible,
                "current_inventory_cost",
            ]
        )

        rows.append(
            {
                "days_supply": days,
                "evidence_backed_exposure": round(
                    float(cost.sum()),
                    2,
                ),
                "models_with_exposure": int(
                    (cost > 0).sum()
                ),
            }
        )

    return pd.DataFrame(rows)
