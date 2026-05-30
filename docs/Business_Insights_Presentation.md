# Business Insights Presentation
### Financial Operations Analytics — slide-by-slide deck

> Each section below is a slide. Figures referenced live in `reports/`.

---

## Slide 1 — Title

**Financial Operations Analytics**
Turning a 7,043-customer telco base into revenue, churn, and profit decisions.

California customer base. Revenue forecasting, churn prediction, profitability segmentation.

By Priyanshu Moudgil

---

## Slide 2 — The business question

> *"Where is revenue heading, who is about to leave, and which customers actually make
> us money?"*

Three linked problems:
- **Forecast** the next 12 months of revenue
- **Predict** which customers will churn
- **Segment** the base by profitability and act on the extremes

---

## Slide 3 — The data

- **7,043 customers**, all in California (North / Central / South)
- **39 fields**: demographics, services, contract, billing, churn — plus six financial
  columns (monthly profit, cost to serve, marketing spend, discount, region, signup month)
- Cleaned and validated: types fixed, missing values resolved, outliers IQR-capped
- *Synthetic but schema-faithful to IBM Telco; fully reproducible*

---

## Slide 4 — Churn at a glance

- **~31% overall churn** — roughly 1 in 3 customers has left
- Churn is **not random**: it clusters in specific contract / service / payment profiles
- *Figure:* `reports/01_churn_distribution.png`, `reports/01_churn_by_segment.png`

**So what:** churn is the dominant risk to revenue — and it's targetable.

---

## Slide 5 — What drives churn

Top drivers (model + correlation agree):
1. **Month-to-month contract** (biggest single factor)
2. **Fiber-optic** internet
3. **Electronic-check** payment
4. **Low tenure** (new customers leave fastest)
5. **High monthly charges** with **no tech support / security**

*Figure:* `reports/03_top_drivers.png`, `reports/01_correlation_heatmap.png`

---

## Slide 6 — Revenue is forecastable

- Reconstructed monthly recurring revenue shows a clear **upward trend + 12-month
  seasonality** (summer peak, December dip)
- Benchmarked three models; **Holt-Winters wins** at **8.72% MAPE**

| Model | MAE | RMSE | MAPE |
|-------|----:|-----:|-----:|
| **Holt-Winters** | **33,060** | **38,663** | **8.72%** |
| Prophet | 41,689 | 44,532 | 11.18% |
| SARIMA | 43,832 | 48,134 | 11.70% |

*Figure:* `reports/02_forecast_12m.png`, `reports/02_decomposition.png`

---

## Slide 7 — The 12-month outlook

- **$5.71M** projected revenue over the next 12 months
- **~$476K/month** average vs. a **$366K/month** trailing baseline → continued growth
- Forecast ships with a **90% confidence band** for downside planning

*Figure:* `reports/02_forecast_12m.png`

---

## Slide 8 — Predicting who leaves

- Three classifiers benchmarked; all clear the **75% accuracy** bar (>77%)
- **Logistic Regression** selected (best ROC-AUC **0.827**, accuracy **78.5%**)
- Balanced churn detection — **precision 0.69**, recall 0.55 on churners

*Figure:* `reports/03_roc_curves.png`, `reports/03_confusion_matrix.png`

---

## Slide 9 — The at-risk list

- **167 active customers** with churn probability **> 70%**
- **~$12.4K monthly** recurring revenue at stake (~$149K annualized)
- Ranked, exportable list handed to retention: `reports/at_risk_customers.csv`

**So what:** a finite, high-value target list — not a vague "reduce churn" mandate.

---

## Slide 10 — Who actually makes us money

- K-Means splits the base into **5 value tiers** (Platinum → Standard)
- **Gold and Silver are the largest total profit pools** (big segments × healthy margin)
- **Bottom 3 by per-customer profit (Silver, Bronze, Standard)** flagged red; **Bronze
  and Standard are loss-making per customer**

*Figure:* `reports/04_profit_by_segment.png` (bottom 3 in red), `reports/04_rfm_segments.png`

---

## Slide 11 — Retention by cohort

- Cohort retention decays with months-since-signup, as expected
- **Recent, contracted cohorts retain better** — the contract lever works
- *Figure:* `reports/04_cohort_retention.png`

---

## Slide 12 — How risky is next year's profit?

- Monte Carlo, **1,000 scenarios**, varying churn, growth and per-customer margin
- **Median annual profit $0.83M**; 90% range **$0.62M–$1.04M**
- **P(annual loss) ≈ 0%** — structurally profitable

*Figure:* `reports/04_monte_carlo.png`

---

## Slide 13 — What moves profit (OLS)

Drivers of monthly profit (R² = 0.73):
- **Fiber optic** customers: **+$7.9/mo** (but higher cost to serve)
- **More add-on services**: **+$2.1** per add-on
- **Longer contracts**: lower headline monthly profit but far better retention
- **No internet**: **−$13/mo** (low-value segment)

*Figure:* `reports/04_profit_drivers_ols.png`

---

## Slide 14 — Recommendations

1. **Save campaign** for the 167 high-risk customers → protect ~$149K/yr
2. **Convert month-to-month → annual** contracts → attack the #1 churn driver
3. **Reprice / cut cost-to-serve** in the Bronze & Standard tiers → fix negative margins
4. **Plan on the forecast** (8.7% error) for cash & capacity

---

## Slide 15 — The dashboard

One interactive view ties it together — revenue + forecast, churn gauge, profit by
segment (bottom 3 red), at-risk table, with **Region + Segment filters**.

➡ `dashboard/financial_ops_dashboard.html` (standalone, opens in any browser)

---

## Slide 16 — Appendix

- Methods and validation: `docs/Technical_Methodology.md`
- Full metrics: `docs/Model_Performance_Report.md`
- Queries: `sql/analytics_queries.sql`
- Contact: priyanshumoudgil12@gmail.com
