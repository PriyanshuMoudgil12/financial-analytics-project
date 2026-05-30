# Technical Methodology
### Financial Operations Analytics

This document describes the data, methods, modeling choices and validation behind the
project. It is the technical companion to the
[Model Performance Report](Model_Performance_Report.md).

---

## 1. Data

### 1.1 Source & generation
The project targets the **IBM Telco Customer Churn** schema (Kaggle:
`yeanzc/telco-customer-churn-ibm-dataset`) — 7,043 customers, 33 columns, all located
in California. Because the Kaggle file could not be downloaded in the build
environment, the dataset is **generated synthetically** by `src/data_generation.py`
to match the schema exactly, then extended with six financial columns.

Generation is **fully deterministic** (`numpy.random.default_rng(42)`), so every figure
and metric in the repo reproduces exactly.

### 1.2 Schema (39 columns)
- **33 IBM columns**: IDs/geo (CustomerID, Count, Country, State, City, Zip, Lat/Long),
  demographics (Gender, Senior Citizen, Partner, Dependents), services (Phone, Multiple
  Lines, Internet, six add-ons), account (Tenure, Contract, Paperless Billing, Payment
  Method, Monthly/Total Charges) and outcome fields (Churn Label/Value/Score, CLTV,
  Churn Reason).
- **6 financial extensions**: `MonthlyProfit`, `CostToServe`, `MarketingSpend`,
  `Discount`, `Region` (North/Central/South California), `SignupMonth`.

Full field-by-field definitions are in the data dictionary inside
`notebooks/01_eda_cleaning.ipynb`.

### 1.3 Realism & learnable signal
Churn is generated from an explicit **logit** of tenure, contract, internet type,
payment method, monthly charges, senior status and support add-ons. This guarantees a
genuine — but noisy — signal, so models perform realistically (mid-to-high 70s
accuracy) rather than trivially. `MonthlyProfit` is derived as
`MonthlyCharges × (1 − Discount) − CostToServe − MarketingSpend/24`.

---

## 2. EDA & cleaning (Notebook 01)
- **Type fixing:** `Total Charges` arrives as text (blank for tenure-0 customers, as in
  the real IBM export) → coerced to numeric; blanks set to 0 (un-billed first month).
- **Missing values:** `Churn Reason` is missing-by-design for non-churners → filled
  with `"Not Churned"`. No other nulls remain.
- **Outliers:** continuous financial fields winsorised at **1.5×IQR** fences (capped,
  not dropped, to preserve the 7,043-row panel).
- **Profiling:** churn / tenure / revenue / profit distributions, churn by contract and
  region, and a numeric **correlation heatmap** (categoricals encoded).
- **Output:** `data/processed/telco_clean.csv`.

---

## 3. Revenue forecasting (Notebook 02)

### 3.1 Building the series
Monthly recurring revenue (MRR) is reconstructed from the panel: each customer
contributes `Monthly Charges` for every month they are active
(`SignupMonth ≤ m < SignupMonth + Tenure`). A documented multiplicative seasonal
factor (summer peak, December dip) and light noise are layered on so the series has
realistic trend + seasonal structure. The reference (snapshot) month is excluded
because every customer's tenure window closes there.

### 3.2 Models
A **12-month hold-out** is used for model selection:
- **SARIMA** — `SARIMAX(1,1,1)(1,1,1,12)` (statsmodels)
- **Holt-Winters** — additive trend + additive seasonality, period 12
- **Prophet** — yearly seasonality, 90% interval

### 3.3 Selection & forecast
Models are scored with **MAE, RMSE, MAPE**; the lowest-RMSE model is **refit on the
full series** and projected 12 months forward with a confidence band. Outputs:
`data/processed/monthly_revenue.csv`, `data/processed/revenue_forecast.csv`.

> Prophet is imported defensively — if unavailable, the notebook falls back to
> SARIMA + Holt-Winters with a clear note.

---

## 4. Churn prediction (Notebook 03)

### 4.1 Leakage control
Outcome-derived fields (`Churn Score`, `CLTV`, `Churn Reason`) and IDs/geo are
**excluded** from the feature set. CLV/RFM-style features are rebuilt from **spend and
tenure only** (no churn signal): `AvgMonthlySpend`, `CLV_est`, `NumAddons`, and
quintile-scored Frequency/Monetary.

### 4.2 Pipeline & models
A `ColumnTransformer` applies `StandardScaler` to numerics and `OneHotEncoder` to
categoricals inside an sklearn `Pipeline`. Three classifiers on a stratified 75/25
split (`random_state=42`):
- **Logistic Regression** (L2, `max_iter=1000`)
- **Random Forest** (400 trees, depth 10, `min_samples_leaf=5`)
- **XGBoost** (350 trees, depth 4, lr 0.05, subsample/colsample 0.9)

The best model is selected by **ROC-AUC**; all three clear the >75% accuracy target.

### 4.3 Evaluation & outputs
Accuracy / precision / recall / F1 / ROC-AUC, ROC curves, confusion matrix,
classification report, and **top-10 drivers** (importances or |coefficients| over the
one-hot feature space). The fitted model scores the full base; the highest-risk
**active** customers are exported to `reports/at_risk_customers.csv`, and per-customer
scores to `data/processed/churn_scored.csv`.

---

## 5. Profitability & segmentation (Notebook 04)
- **K-Means** on standardized value signals (lifetime spend, tenure, monthly charges,
  monthly profit, CLV). `k` swept over **5–7**; chosen by **silhouette** (with an elbow
  diagnostic). Clusters named into tiers by descending mean monthly profit; the
  **bottom 3 tiers by average profit per customer** are flagged.
- **RFM** scoring via `src/features.py` (quintile R/F/M → named segments).
- **Cohort retention heatmap** by signup quarter × months-since-signup.
- **Monte Carlo** (1,000 iterations) of annual profit under uncertain per-customer
  margin, churn and base growth → median + 90% interval + P(loss).
- **OLS** (`statsmodels`) of monthly profit on customer attributes (not its own cost
  inputs) to read off profitability drivers.
- **Output:** `data/processed/customer_segments.csv`.

---

## 6. Dashboard (Notebook 05)
A single Plotly figure (`make_subplots`): revenue + forecast line with CI band, a churn
**gauge** indicator, a profit-by-segment **bar** (bottom 3 red), and an at-risk
**table**. All Region × Segment aggregates are **pre-computed** and serialized into the
page; two HTML dropdowns wired with an embedded `post_script` call `Plotly.restyle` to
filter the gauge, bar and table **client-side**. Exported with
`include_plotlyjs="cdn"` so the HTML is standalone and needs no server.

---

## 7. SQL (`sql/analytics_queries.sql`)
Six analytical queries (revenue by segment, monthly trend, top-10 customers, churn by
region+contract, CLV by cohort, plan margins), written in SQLite-compatible standard
SQL and **verified** by loading `telco_clean.csv` and `customer_segments.csv` into
SQLite tables.

---

## 8. Reproducibility & environment
- **Python 3.13**, dependencies pinned in `requirements.txt`.
- Single global seed (`42`) across data generation and all models.
- Notebooks are executed top-to-bottom (`nbconvert`) and committed **with outputs**.
- Shared utilities in `src/` (`data_generation`, `features`, `metrics`, `viz`) keep
  definitions consistent across notebooks.
