"""
Synthetic data generator for the Financial Operations Analytics project.

Reproduces the schema of the IBM Telco Customer Churn dataset
(yeanzc/telco-customer-churn-ibm-dataset): 7,043 rows x 33 columns, all
customers located in California. Six financial columns are appended:

    MonthlyProfit, CostToServe, MarketingSpend, Discount, Region, SignupMonth

The generator is fully deterministic (seeded) so every notebook and report in
the repo is reproducible. Churn is driven by an explicit logit of tenure,
contract type, charges and support features so the relationship is *learnable*
by the models in notebook 03 (target test accuracy > 75%).

Run as a script to (re)create ``data/raw/telco_financial_raw.csv``:

    python src/data_generation.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
N_ROWS = 7_043
SEED = 42
# IBM data snapshot reference (signup month = reference - tenure months).
REFERENCE_DATE = pd.Timestamp("2021-02-01")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "telco_financial_raw.csv"

# California city pool: (city, zip, lat, long, region)
CA_CITIES = [
    # North California
    ("San Francisco", "94109", 37.7749, -122.4194, "North California"),
    ("Sacramento", "95814", 38.5816, -121.4944, "North California"),
    ("Oakland", "94601", 37.8044, -122.2712, "North California"),
    ("Berkeley", "94704", 37.8715, -122.2730, "North California"),
    ("Santa Rosa", "95401", 38.4404, -122.7141, "North California"),
    # Central California
    ("San Jose", "95112", 37.3382, -121.8863, "Central California"),
    ("Fresno", "93701", 36.7378, -119.7871, "Central California"),
    ("Bakersfield", "93301", 35.3733, -119.0187, "Central California"),
    ("Stockton", "95202", 37.9577, -121.2908, "Central California"),
    ("Modesto", "95354", 37.6391, -120.9969, "Central California"),
    # South California
    ("Los Angeles", "90001", 34.0522, -118.2437, "South California"),
    ("San Diego", "92101", 32.7157, -117.1611, "South California"),
    ("Long Beach", "90802", 33.7701, -118.1937, "South California"),
    ("Anaheim", "92805", 33.8366, -117.9143, "South California"),
    ("Riverside", "92501", 33.9806, -117.3755, "South California"),
]


def _yes_no(rng: np.random.Generator, n: int, p_yes: float) -> np.ndarray:
    return np.where(rng.random(n) < p_yes, "Yes", "No")


def generate(n: int = N_ROWS, seed: int = SEED) -> pd.DataFrame:
    """Build the full synthetic Telco + financial dataframe."""
    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------------- geo ---
    city_idx = rng.integers(0, len(CA_CITIES), n)
    cities = np.array([CA_CITIES[i][0] for i in city_idx])
    zips = np.array([CA_CITIES[i][1] for i in city_idx])
    base_lat = np.array([CA_CITIES[i][2] for i in city_idx])
    base_lon = np.array([CA_CITIES[i][3] for i in city_idx])
    regions = np.array([CA_CITIES[i][4] for i in city_idx])
    # jitter coordinates slightly around each city centre
    lat = np.round(base_lat + rng.normal(0, 0.05, n), 4)
    lon = np.round(base_lon + rng.normal(0, 0.05, n), 4)
    lat_long = [f"{a}, {b}" for a, b in zip(lat, lon)]

    customer_id = [f"{rng.integers(1000, 9999)}-{''.join(rng.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 5))}"
                   for _ in range(n)]

    # ------------------------------------------------------- demographics ---
    gender = rng.choice(["Male", "Female"], n)
    senior = rng.choice([0, 1], n, p=[0.84, 0.16])
    partner = _yes_no(rng, n, 0.48)
    dependents = np.where(partner == "Yes",
                          _yes_no(rng, n, 0.45),
                          _yes_no(rng, n, 0.15))

    # ------------------------------------------------------------ tenure ---
    # Bimodal-ish: many newish customers, a loyal long-tenure cluster.
    # Bimodal tenure without a pile-up at the 72-month cap. The loyal cohort is
    # drawn as 72 - gamma so it tapers smoothly down from the cap (gamma's shape>1
    # gives ~zero density at 0, so almost nobody lands exactly on 72). This spreads
    # long-tenure customers across many signup months instead of one spike.
    new_cohort = rng.gamma(2.0, 6.0, n)              # newer customers, skewed low
    loyal_cohort = 72.0 - rng.gamma(2.0, 7.0, n)     # loyal customers, tapering down
    tenure = np.where(rng.random(n) < 0.45, new_cohort, loyal_cohort)
    tenure = np.clip(tenure, 0, 72).round().astype(int)

    # ----------------------------------------------------------- services ---
    phone_service = _yes_no(rng, n, 0.90)
    multiple_lines = np.where(
        phone_service == "No", "No phone service",
        _yes_no(rng, n, 0.42),
    )
    internet_service = rng.choice(
        ["DSL", "Fiber optic", "No"], n, p=[0.34, 0.44, 0.22]
    )
    no_net = internet_service == "No"

    def net_addon(p_yes: float) -> np.ndarray:
        return np.where(no_net, "No internet service", _yes_no(rng, n, p_yes))

    online_security = net_addon(0.33)
    online_backup = net_addon(0.38)
    device_protection = net_addon(0.36)
    tech_support = net_addon(0.33)
    streaming_tv = net_addon(0.40)
    streaming_movies = net_addon(0.40)

    contract = rng.choice(
        ["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.21, 0.24]
    )
    paperless = _yes_no(rng, n, 0.59)
    payment_method = rng.choice(
        ["Electronic check", "Mailed check",
         "Bank transfer (automatic)", "Credit card (automatic)"],
        n, p=[0.34, 0.23, 0.22, 0.21],
    )

    # ----------------------------------------------------------- charges ---
    monthly = np.full(n, 18.0)  # base line/phone charge
    monthly += np.where(phone_service == "Yes", 2.0, 0.0)
    monthly += np.where(multiple_lines == "Yes", 5.0, 0.0)
    monthly += np.select(
        [internet_service == "DSL", internet_service == "Fiber optic"],
        [25.0, 45.0], default=0.0,
    )
    for addon in (online_security, online_backup, device_protection,
                  tech_support, streaming_tv, streaming_movies):
        monthly += np.where(addon == "Yes", rng.uniform(4, 7, n), 0.0)
    monthly = np.round(monthly + rng.normal(0, 1.5, n), 2)
    monthly = np.clip(monthly, 18.25, 120.0)

    total_charges = np.round(monthly * tenure + rng.normal(0, 25, n), 2)
    total_charges = np.clip(total_charges, 0, None)
    # New customers (tenure 0) sometimes have a blank Total Charges in the real
    # IBM file -> emulate as empty string for the cleaning step in notebook 01.
    total_charges_str = total_charges.astype(object)
    total_charges_str[tenure == 0] = " "

    # --------------------------------------------------------- churn logit ---
    z = (
        -1.1
        + 1.7 * (contract == "Month-to-month")
        - 0.9 * (contract == "Two year")
        + 0.9 * (internet_service == "Fiber optic")
        + 0.7 * (payment_method == "Electronic check")
        - 0.035 * tenure
        + 0.012 * (monthly - 65)
        + 0.45 * (senior == 1)
        - 0.6 * (tech_support == "Yes")
        - 0.5 * (online_security == "Yes")
        + 0.25 * (paperless == "Yes")
        - 0.2 * (partner == "Yes")
    )
    churn_prob = 1.0 / (1.0 + np.exp(-z))
    churn_value = (rng.random(n) < churn_prob).astype(int)
    churn_label = np.where(churn_value == 1, "Yes", "No")
    # Churn score: 0-100, correlated with probability + noise.
    churn_score = np.clip(
        np.round(churn_prob * 100 + rng.normal(0, 8, n)), 5, 100
    ).astype(int)

    churn_reasons = [
        "Competitor offered higher download speeds",
        "Competitor made better offer",
        "Attitude of support person",
        "Competitor had better devices",
        "Price too high",
        "Product dissatisfaction",
        "Network reliability",
        "Long wait times",
        "Moved",
        "Don't know",
    ]
    churn_reason = np.full(n, np.nan, dtype=object)
    churned_mask = churn_value == 1
    churn_reason[churned_mask] = rng.choice(churn_reasons, churned_mask.sum())

    # CLTV: lifetime value score (IBM range ~2000-7000), higher for loyal /
    # high-value, lower for likely churners.
    cltv = np.round(
        2500
        + 30 * tenure
        + 18 * monthly
        - 900 * churn_value
        + rng.normal(0, 350, n)
    )
    cltv = np.clip(cltv, 2000, 7000).astype(int)

    # ----------------------------------------------- financial extensions ---
    signup_month = [
        (REFERENCE_DATE - pd.DateOffset(months=int(t))).strftime("%Y-%m-01")
        for t in tenure
    ]

    discount = np.round(
        np.where(contract == "Two year", rng.uniform(0.10, 0.30, n),
                 np.where(contract == "One year", rng.uniform(0.05, 0.20, n),
                          rng.uniform(0.0, 0.10, n))),
        3,
    )
    # Acquisition spend, higher in competitive South California metros.
    region_premium = np.select(
        [regions == "South California", regions == "North California"],
        [1.25, 1.10], default=1.0,
    )
    marketing_spend = np.round(
        rng.uniform(80, 400, n) * region_premium
        + 60 * (internet_service == "Fiber optic"),
        2,
    )
    # Monthly cost to serve: variable share of charges + support overhead.
    cost_to_serve = np.round(
        monthly * rng.uniform(0.30, 0.45, n)
        + np.where(tech_support == "Yes", rng.uniform(3, 7, n), 0.0)
        + rng.uniform(2, 6, n),
        2,
    )
    monthly_profit = np.round(
        monthly * (1 - discount) - cost_to_serve - marketing_spend / 24.0,
        2,
    )

    df = pd.DataFrame({
        "CustomerID": customer_id,
        "Count": 1,
        "Country": "United States",
        "State": "California",
        "City": cities,
        "Zip Code": zips,
        "Lat Long": lat_long,
        "Latitude": lat,
        "Longitude": lon,
        "Gender": gender,
        "Senior Citizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "Tenure Months": tenure,
        "Phone Service": phone_service,
        "Multiple Lines": multiple_lines,
        "Internet Service": internet_service,
        "Online Security": online_security,
        "Online Backup": online_backup,
        "Device Protection": device_protection,
        "Tech Support": tech_support,
        "Streaming TV": streaming_tv,
        "Streaming Movies": streaming_movies,
        "Contract": contract,
        "Paperless Billing": paperless,
        "Payment Method": payment_method,
        "Monthly Charges": monthly,
        "Total Charges": total_charges_str,
        "Churn Label": churn_label,
        "Churn Value": churn_value,
        "Churn Score": churn_score,
        "CLTV": cltv,
        "Churn Reason": churn_reason,
        # --- six financial extension columns ---
        "MonthlyProfit": monthly_profit,
        "CostToServe": cost_to_serve,
        "MarketingSpend": marketing_spend,
        "Discount": discount,
        "Region": regions,
        "SignupMonth": signup_month,
    })
    return df


def main() -> None:
    df = generate()
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_PATH, index=False)

    # ---- validation ----
    assert df.shape == (N_ROWS, 39), f"unexpected shape {df.shape}"
    assert (df["State"] == "California").all()
    assert set(df["Region"].unique()) == {
        "North California", "Central California", "South California"
    }
    print(f"Wrote {RAW_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Churn rate: {df['Churn Value'].mean():.1%}")
    print(f"Regions: {df['Region'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
