"""Deterministic synthetic equipment-dealership data.

No employer, customer, inventory, pricing, or sales data is included here.
"""

from __future__ import annotations

from datetime import date, timedelta
import random

import pandas as pd


BRANDS = {
    "Apex Motors": [
        "Ranger 900",
        "Ranger 1000",
        "Trail 570",
        "Trail 850",
        "WorkPro 1000",
    ],
    "FieldPro": [
        "ZT 42",
        "ZT 54",
        "ZT 60",
        "ProTurn 52",
        "ProTurn 60",
    ],
    "IronPeak": [
        "MX 26",
        "MX 30",
        "RX 48",
        "RX 60",
        "Utility 24",
    ],
    "TrailWorks": [
        "Defender 700",
        "Defender 1000",
        "Scout 500",
        "Scout 800",
        "Summit 1000",
    ],
    "Northland": [
        "Lawn 42",
        "Lawn 46",
        "Lawn 54",
        "Snow 24",
        "Snow 30",
    ],
}

STORES = [
    "Grand River",
    "Lakeview",
    "Northfield",
    "Pine Ridge",
]


def build_demo_data(
    seed: int = 4712,
    snapshot_date: date = date(2026, 9, 14),
):
    """Return synthetic inventory and sales DataFrames."""

    rng = random.Random(seed)

    inventory_rows = []
    sales_rows = []

    stock_counter = 10000

    start = date(
        snapshot_date.year,
        1,
        1,
    )

    elapsed_days = (
        snapshot_date - start
    ).days + 1

    for brand_idx, (
        brand,
        models,
    ) in enumerate(BRANDS.items()):

        for model_idx, model in enumerate(models):

            tier = (
                brand_idx * len(models)
                + model_idx
            ) % 7

            if tier == 0:
                on_hand = 8
                sold = 1

            elif tier == 1:
                on_hand = 6
                sold = 2

            elif tier == 2:
                on_hand = 5
                sold = 4

            elif tier == 3:
                on_hand = 3
                sold = 8

            elif tier == 4:
                on_hand = 2
                sold = 13

            elif tier == 5:
                on_hand = 4
                sold = 0

            else:
                on_hand = 7
                sold = 3

            base_cost = (
                3500
                + brand_idx * 4200
                + model_idx * 1850
            )

            unit_cost = round(
                base_cost
                * rng.uniform(
                    0.90,
                    1.12,
                ),
                2,
            )

            for unit_no in range(
                on_hand
            ):
                store = STORES[
                    (
                        brand_idx
                        + model_idx
                        + unit_no
                    )
                    % len(STORES)
                ]

                stock_counter += 1

                inventory_rows.append(
                    {
                        "stock_number": (
                            f"DEMO-{stock_counter}"
                        ),
                        "store": store,
                        "make": brand,
                        "model": model,
                        "condition": (
                            "New"
                            if unit_no % 5
                            else "Used"
                        ),
                        "invoice_cost": round(
                            unit_cost
                            * rng.uniform(
                                0.97,
                                1.04,
                            ),
                            2,
                        ),
                    }
                )

            price_multiplier = 1.23

            if (
                tier == 1
                and model_idx % 2 == 0
            ):
                price_multiplier = 0.96

            sale_value = (
                unit_cost
                * price_multiplier
            )

            for sale_no in range(sold):

                offset = int(
                    (
                        sale_no + 1
                    )
                    * elapsed_days
                    / (
                        sold + 1
                    )
                )

                sale_date = (
                    start
                    + timedelta(
                        days=min(
                            offset,
                            elapsed_days - 1,
                        )
                    )
                )

                store = STORES[
                    (
                        brand_idx
                        + model_idx
                        + sale_no
                        + 1
                    )
                    % len(STORES)
                ]

                sales_rows.append(
                    {
                        "sale_date": (
                            sale_date.isoformat()
                        ),
                        "store": store,
                        "make": brand,
                        "model": model,
                        "sale_value": round(
                            sale_value
                            * rng.uniform(
                                0.97,
                                1.05,
                            ),
                            2,
                        ),
                    }
                )

    inventory = pd.DataFrame(
        inventory_rows
    )

    sales = pd.DataFrame(
        sales_rows
    )

    return inventory, sales
