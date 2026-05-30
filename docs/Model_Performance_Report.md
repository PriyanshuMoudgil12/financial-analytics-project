# Model Performance Report
### Financial Operations Analytics

All figures below are produced by the executed notebooks (seed = 42) and the figures in
`reports/`. Metrics are reported on held-out data.

---

## 1. Revenue forecasting (Notebook 02)

**Setup:** monthly recurring revenue series, last **12 months** held out for model
selection. Metrics on the hold-out:

| Model | MAE | RMSE | MAPE (%) |
|-------|----:|-----:|---------:|
| **Holt-Winters** ✅ | **33,060.10** | **38,663.24** | **8.72** |
| Prophet | 41,689.33 | 44,532.32 | 11.18 |
| SARIMA | 43,832.34 | 48,134.21 | 11.70 |

- **Selected model:** Holt-Winters (additive trend + additive seasonality, period 12),
  lowest RMSE and MAPE.
- **12-month forward forecast:** **$5,713,047** total; **$476,087/month** average vs. a
  **$365,722/month** trailing-12 actual average (continued growth).
- Forecast and 90% confidence band saved to `data/processed/revenue_forecast.csv`.

*Figures:* `02_mrr_series.png`, `02_decomposition.png`, `02_holdout_forecasts.png`,
`02_forecast_12m.png`.

---

## 2. Churn prediction (Notebook 03)

**Setup:** stratified 75/25 train/test split, leakage-controlled features. Test metrics:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|---------:|----------:|-------:|---:|--------:|
| **Logistic Regression** ✅ | **0.7853** | 0.6866 | 0.5519 | 0.6119 | **0.8268** |
| XGBoost | 0.7802 | 0.6624 | 0.5778 | 0.6172 | 0.8195 |
| Random Forest | 0.7785 | 0.6829 | 0.5185 | 0.5895 | 0.8190 |

- **Selection criterion:** ROC-AUC → **Logistic Regression** (0.8268), which also has the
  highest accuracy. **All three models clear the >75% accuracy target.**
- **Classification report (best model):**

  | Class | Precision | Recall | F1 | Support |
  |-------|----------:|-------:|---:|--------:|
  | Stay | 0.82 | 0.89 | 0.85 | 1,221 |
  | Churn | 0.69 | 0.55 | 0.61 | 540 |
  | **Accuracy** | | | **0.79** | 1,761 |

- **Top churn drivers:** month-to-month contract, fiber-optic internet, electronic-check
  payment, low tenure, high monthly charges (absence of tech support / online security).

**At-risk export:**
- **167** active customers with churn probability **> 0.70**
- **$12,434** monthly recurring revenue at risk (~$149K annualized)
- Ranked top-200 at-risk list: `reports/at_risk_customers.csv`

*Figures:* `03_roc_curves.png`, `03_confusion_matrix.png`, `03_top_drivers.png`.

---

## 3. Segmentation & profitability (Notebook 04)

### 3.1 K-Means value tiers
- **k = 5** chosen by silhouette (k=5: 0.392, k=6: 0.339, k=7: 0.369).
- Segment profile (per-customer means + totals):

| Segment | Customers | Avg Monthly Profit | Avg CLV | Avg Tenure | Churn Rate | Total Monthly Profit |
|---------|----------:|-------------------:|--------:|-----------:|-----------:|---------------------:|
| Platinum | 677 | 23.65 | 620.39 | 52.73 | 0.10 | 16,012.38 |
| Gold | 2,197 | 19.46 | 236.68 | 11.65 | 0.52 | 42,756.15 |
| Silver | 2,326 | 18.58 | 234.45 | 58.87 | 0.25 | 43,223.92 |
| Bronze | 868 | −2.23 | 16.35 | 11.57 | 0.33 | −1,939.34 |
| Standard | 975 | −3.03 | 14.82 | 58.18 | 0.10 | −2,958.37 |

- **Bottom 3 by avg profit per customer (flagged red):** Silver, Bronze, Standard.
  **Bronze and Standard are loss-making per customer** — repricing / cost-to-serve
  targets. By *total* contribution, **Gold and Silver** are the two largest profit pools
  (large segments × healthy per-customer profit), while Platinum is high-margin but small.

### 3.2 Monte Carlo — annual profit (1,000 iterations)
- **Median:** $0.83M
- **90% interval:** [$0.62M, $1.04M]
- **P(annual loss):** ≈ 0%

### 3.3 OLS — drivers of monthly profit
- **R² = 0.731.** Key coefficients (all p < 0.001 unless noted):

| Driver | Coefficient ($/mo) |
|--------|-------------------:|
| Fiber optic (vs DSL) | +7.87 |
| Each additional add-on | +2.10 |
| One-year contract | −4.34 |
| Two-year contract | −8.90 |
| No internet (vs DSL) | −13.11 |
| South California | −2.68 |
| North California | −1.10 |
| Tenure / Senior / Paperless | not significant |

*Figures:* `04_kmeans_selection.png`, `04_profit_by_segment.png`, `04_rfm_segments.png`,
`04_cohort_retention.png`, `04_monte_carlo.png`, `04_profit_drivers_ols.png`.

---

## 4. Summary scorecard

| Deliverable | Target | Result | Status |
|-------------|--------|--------|--------|
| Revenue forecast accuracy | usable | MAPE 8.72% (Holt-Winters) | ✅ |
| Churn model accuracy | > 75% | 78.5% (all 3 models > 77%) | ✅ |
| Churn discrimination | strong | ROC-AUC 0.827 | ✅ |
| Segmentation | 5–7 tiers | 5 tiers (silhouette-selected) | ✅ |
| Monte Carlo | 1,000 iters | 1,000 iters, P(loss) ≈ 0% | ✅ |
| At-risk customer list | exportable | 167 high-risk, CSV exported | ✅ |
