"""
E-Commerce Dataset Generator
Modeled after Olist Brazilian E-Commerce public dataset patterns.
Run this FIRST to generate the CSV files used by the dashboard.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# ── Config ─────────────────────────────────────────────────────
N_CUSTOMERS   = 8000
N_ORDERS      = 12000
START_DATE    = datetime(2022, 1, 1)
END_DATE      = datetime(2024, 12, 31)

CATEGORIES = {
    "Electronics":        {"avg_price": 320, "std": 180, "weight": 0.18},
    "Health & Beauty":    {"avg_price": 45,  "std": 25,  "weight": 0.14},
    "Sports & Leisure":   {"avg_price": 80,  "std": 45,  "weight": 0.12},
    "Furniture & Decor":  {"avg_price": 210, "std": 120, "weight": 0.10},
    "Computers":          {"avg_price": 780, "std": 350, "weight": 0.09},
    "Housewares":         {"avg_price": 55,  "std": 30,  "weight": 0.09},
    "Watches & Gifts":    {"avg_price": 130, "std": 90,  "weight": 0.08},
    "Auto":               {"avg_price": 95,  "std": 60,  "weight": 0.07},
    "Toys & Baby":        {"avg_price": 40,  "std": 20,  "weight": 0.07},
    "Books":              {"avg_price": 22,  "std": 10,  "weight": 0.06},
}

STATES = {
    "SP": 0.42, "RJ": 0.13, "MG": 0.11, "RS": 0.06,
    "PR": 0.06, "SC": 0.05, "BA": 0.04, "GO": 0.03,
    "ES": 0.02, "PE": 0.02, "CE": 0.02, "Other": 0.04
}

PAYMENT_TYPES = {
    "credit_card": 0.74,
    "boleto":      0.19,
    "voucher":     0.05,
    "debit_card":  0.02,
}

def random_date(start, end):
    delta = end - start
    rand_days  = np.random.randint(0, delta.days)
    rand_hours = np.random.randint(0, 24)
    # Add seasonality: Q4 boost (Black Friday / Christmas)
    base = start + timedelta(days=int(rand_days), hours=rand_hours)
    return base

def seasonal_weight(date):
    month = date.month
    # Nov-Dec spike, Jan-Feb dip
    weights = {1:0.7, 2:0.75, 3:0.9, 4:0.95, 5:1.0, 6:0.95,
               7:1.05, 8:1.0, 9:1.0, 10:1.1, 11:1.5, 12:1.4}
    return weights.get(month, 1.0)

print("Generating customers...")
customer_ids = [f"CUST_{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS+1)]
state_list   = list(STATES.keys())
state_weights = list(STATES.values())
customers = pd.DataFrame({
    "customer_id":    customer_ids,
    "customer_state": np.random.choice(state_list, N_CUSTOMERS, p=state_weights),
    "signup_date":    [START_DATE + timedelta(days=int(np.random.randint(0, 365))) for _ in range(N_CUSTOMERS)],
})
customers.to_csv("customers.csv", index=False)
print(f"  → {len(customers)} customers")

print("Generating orders...")
orders = []
cat_names    = list(CATEGORIES.keys())
cat_weights  = [CATEGORIES[c]["weight"] for c in cat_names]

# Generate dates with seasonality
all_dates = []
for _ in range(N_ORDERS * 3):
    d = random_date(START_DATE, END_DATE)
    if np.random.random() < seasonal_weight(d) / 1.5:
        all_dates.append(d)
    if len(all_dates) >= N_ORDERS:
        break
all_dates = sorted(all_dates[:N_ORDERS])

order_ids = [f"ORD_{str(i).zfill(6)}" for i in range(1, N_ORDERS+1)]
pay_types  = list(PAYMENT_TYPES.keys())
pay_weights = list(PAYMENT_TYPES.values())

for i, (oid, odate) in enumerate(zip(order_ids, all_dates)):
    cust = np.random.choice(customer_ids)
    cat  = np.random.choice(cat_names, p=cat_weights)
    info = CATEGORIES[cat]

    price    = max(5, np.random.normal(info["avg_price"], info["std"]))
    qty      = np.random.choice([1,1,1,2,2,3], p=[0.5,0.2,0.1,0.1,0.05,0.05])
    freight  = np.random.uniform(5, 45)
    revenue  = round(price * qty, 2)
    total    = round(revenue + freight, 2)

    # Delivery: 1-30 days
    delivery_days = int(np.random.exponential(8)) + 1
    delivery_date = odate + timedelta(days=delivery_days)

    # Review score (skewed positive)
    score = np.random.choice([1,2,3,4,5], p=[0.04, 0.05, 0.09, 0.25, 0.57])

    # Status
    status = np.random.choice(
        ["delivered", "delivered", "delivered", "delivered",
         "shipped", "canceled", "processing"],
        p=[0.65, 0.1, 0.1, 0.05, 0.04, 0.03, 0.03]
    )

    orders.append({
        "order_id":        oid,
        "customer_id":     cust,
        "order_date":      odate.strftime("%Y-%m-%d"),
        "delivery_date":   delivery_date.strftime("%Y-%m-%d"),
        "category":        cat,
        "product_price":   round(price, 2),
        "quantity":        qty,
        "revenue":         revenue,
        "freight_value":   round(freight, 2),
        "total_value":     total,
        "payment_type":    np.random.choice(pay_types, p=pay_weights),
        "review_score":    score,
        "delivery_days":   delivery_days,
        "order_status":    status,
        "year":            odate.year,
        "month":           odate.month,
        "quarter":         f"Q{(odate.month-1)//3+1}",
        "year_month":      odate.strftime("%Y-%m"),
    })

df_orders = pd.DataFrame(orders)
df_orders.to_csv("orders.csv", index=False)
print(f"  → {len(df_orders)} orders | Total GMV: ${df_orders['revenue'].sum():,.0f}")

print("\nAll files saved:")
print("  customers.csv")
print("  orders.csv")
print("\nNow run:  streamlit run dashboard.py")
