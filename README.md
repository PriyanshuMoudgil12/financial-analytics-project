# Financial Operations Analytics

Portfolio project. One repo, three questions a business analyst usually has to answer at the same time: where revenue is going, who's about to churn, and which customers actually make us money.

Built on the IBM Telco Customer Churn schema (7,043 California customers, 33 columns) plus six financial columns I added on top so the profitability analysis is actually possible. The base file from Kaggle has no cost, marketing, or discount data — so I generated those, deterministically, with the assumptions documented in `src/data_generation.py`.

---

## Results in one paragraph

Best forecast: Holt-Winters at 8.72% MAPE, projecting $5.71M over 12 months. Best churn model: Logistic Regression at 78.5% accuracy / 0.827 AUC, clearing the 75% target (XGBoost and Random Forest also pass at 78.0% and 77.8%). K-Means produces 5 value tiers — Platinum, Gold, Silver, Bronze, Standard — with Bronze and Standard genuinely loss-making per customer. The model surfaces a 167-customer high-risk list (probability > 0.7) worth ~$12.4K of monthly revenue and ~$149K annualized. Monte Carlo on next year's profit (1,000 iterations) lands at a median of $0.83M with a 90% confidence range of $0.62M–$1.04M and effectively zero probability of an annual loss.

---

## Project structure

```
financial-analytics-v2/
├── data/
│   ├── raw/            # generated raw dataset
│   └── processed/      # cleaned data, revenue series, forecast, segments
├── notebooks/
│   ├── 01_eda_cleaning.ipynb              # EDA, cleaning, data dictionary
│   ├── 02_revenue_forecasting.ipynb       # SARIMA · Prophet · Holt-Winters
│   ├── 03_churn_prediction.ipynb          # LogReg · RF · XGBoost
│   └── 04_profitability_segmentation.ipynb# K-Means · cohorts · Monte Carlo · OLS
├── dashboard/
│   ├── 05_dashboard.ipynb                 # builds the view
│   └── financial_ops_dashboard.html       # standalone interactive dashboard
├── src/
│   ├── data_generation.py   # synthetic IBM-schema generator (seeded)
│   ├── features.py          # RFM + CLV feature engineering
│   ├── metrics.py           # MAE/RMSE/MAPE + classification metrics
│   └── viz.py               # shared plotting style
├── sql/
│   └── analytics_queries.sql# 6 analytical queries (SQLite-verified)
├── docs/
│   ├── Executive_Summary.md
│   ├── Business_Insights_Presentation.md
│   ├── Technical_Methodology.md
│   └── Model_Performance_Report.md
├── reports/                 # exported figures + at_risk_customers.csv
├── requirements.txt
└── README.md
```

---

## Tech stack

Python with pandas, NumPy, scikit-learn, XGBoost, statsmodels (SARIMA / Holt-Winters), Prophet, matplotlib, seaborn, Plotly. SQL is plain SQLite. Versions pinned in `requirements.txt`.

---

## How to run

```bash
# 1. Install dependencies (Python 3.13)
pip install -r requirements.txt

# 2. Generate the dataset (writes data/raw/telco_financial_raw.csv)
python src/data_generation.py

# 3. Run the notebooks in order (01 → 04). Each is self-contained and will
#    regenerate the raw data if missing.
jupyter notebook            # or: jupyter nbconvert --to notebook --execute notebooks/01_eda_cleaning.ipynb

# 4. Build the dashboard
jupyter nbconvert --to notebook --execute dashboard/05_dashboard.ipynb
#    then open dashboard/financial_ops_dashboard.html in any browser
```

The pipeline is sequential: **01** writes `data/processed/telco_clean.csv`, which feeds
**02–04**; **03** exports the at-risk list and per-customer churn scores; **04** exports
the segment table; **05** assembles everything into the dashboard.

---

## The dashboard

`dashboard/financial_ops_dashboard.html` is one standalone view — opens in any browser, no server needed. Four panels: revenue trend with 12-month forecast and 90% confidence band, churn-rate gauge, profit-by-segment bar with the bottom three highlighted red, and the at-risk customers table. Two dropdowns at the top filter the gauge, bar, and table by Region and Segment, all client-side via embedded JavaScript.

## Documentation

- [Executive Summary](docs/Executive_Summary.md) — one-page business overview
- [Business Insights Presentation](docs/Business_Insights_Presentation.md) — slide-by-slide deck
- [Technical Methodology](docs/Technical_Methodology.md) — data, methods, validation
- [Model Performance Report](docs/Model_Performance_Report.md) — full metrics tables

Contact: priyanshumoudgil12@gmail.com
