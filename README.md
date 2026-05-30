# 📈 Financial Operations Analytics — Revenue, Churn & Profitability

> 7,043 telco customers, ~31% churn. One question: which 167 of them are about to walk out the door, how much money goes with them, and which customer segments are actually making us money?

🔗 **[Live interactive dashboard →](https://raw.githack.com/PriyanshuMoudgil12/financial-analytics-project/main/dashboard/financial_ops_dashboard.html)**

[![Revenue forecast](https://github.com/PriyanshuMoudgil12/financial-analytics-project/raw/main/reports/02_forecast_12m.png)](/PriyanshuMoudgil12/financial-analytics-project/blob/main/reports/02_forecast_12m.png)

---

## The problem

A telco running a California customer base has the same three questions every Monday morning: where is revenue heading next year, who is about to churn, and which customers actually make us money once you net out cost-to-serve and marketing spend.

Most portfolio projects answer one of those in isolation. I wanted to build the whole pipeline on a single 7,043-customer base — forecasting, classification, segmentation, simulation, dashboard, SQL, business memo — so the methodology is consistent end-to-end and the recommendations actually trace back to numbers a finance team could defend.

---

## What it does

- Loads a **7,043-customer telco base** (39 fields: 33 IBM Telco columns + 6 financial extensions)
- Cleans, profiles, and outputs a **39-field data dictionary** in Notebook 01
- Benchmarks **3 forecasters** (SARIMA, Prophet, Holt-Winters) on a 12-month holdout
- Benchmarks **3 churn classifiers** (Logistic Regression, Random Forest, XGBoost) with leakage control
- Segments the base into **5 value tiers** (K-Means, silhouette-selected)
- Runs **Monte Carlo (1,000 iterations)** on next year's profit under uncertain churn / growth / margin
- Ships a **standalone interactive HTML dashboard** with Region + Segment dropdown filters
- Writes **6 SQL queries** answering the same questions in SQLite
- Packages findings into an **Executive Summary**, **slide-by-slide Business Insights deck**, **Technical Methodology**, and **Model Performance Report**

---

## Tech stack

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![SQL](https://img.shields.io/badge/SQL-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/) [![Pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/) [![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/) [![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/) [![XGBoost](https://img.shields.io/badge/XGBoost-EC7211?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/) [![statsmodels](https://img.shields.io/badge/statsmodels-3E73A8?style=for-the-badge&logoColor=white)](https://www.statsmodels.org/) [![Prophet](https://img.shields.io/badge/Prophet-1877F2?style=for-the-badge&logo=meta&logoColor=white)](https://facebook.github.io/prophet/) [![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/) [![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/) [![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

---

## How to run it locally

```bash
git clone https://github.com/PriyanshuMoudgil12/financial-analytics-project.git
cd financial-analytics-project
pip install -r requirements.txt
```

Then:

1. **Generate the dataset** (writes `data/raw/telco_financial_raw.csv`, seeded for reproducibility):

  ```bash
  python src/data_generation.py
  ```

2. **Run the notebooks in order** — each is self-contained and feeds the next:

  ```bash
  jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda_cleaning.ipynb
  jupyter nbconvert --to notebook --execute --inplace notebooks/02_revenue_forecasting.ipynb
  jupyter nbconvert --to notebook --execute --inplace notebooks/03_churn_prediction.ipynb
  jupyter nbconvert --to notebook --execute --inplace notebooks/04_profitability_segmentation.ipynb
  jupyter nbconvert --to notebook --execute --inplace dashboard/05_dashboard.ipynb
  ```

3. **Run any of the 6 SQL queries** against the cleaned data:

  ```bash
  sqlite3 :memory: ".mode csv" ".import data/processed/telco_clean.csv telco" < sql/analytics_queries.sql
  ```

4. **Open the interactive HTML dashboard** — double-click `dashboard/financial_ops_dashboard.html` in your file browser. Works offline.

5. **Live dashboard online:** [raw.githack link](https://raw.githack.com/PriyanshuMoudgil12/financial-analytics-project/main/dashboard/financial_ops_dashboard.html)

---

## Key findings

1. **A 167-customer high-risk list is worth ~$149K annualized.** Active customers with churn probability above 70% carry $12.4K of monthly recurring revenue (~$149K/year). It's a finite, ranked list — exactly the kind of target a retention team can work through, not a vague "reduce churn" mandate.

2. **Contract length is the single biggest churn driver.** Month-to-month customers churn far more aggressively than one-year and two-year contract holders. The top-10 driver list from Random Forest agrees with the OLS correlations: contract type swamps pricing, services, and demographics.

3. **Holt-Winters beats Prophet and SARIMA on the holdout — at 8.72% MAPE.** All three forecasters are within 3pp of each other, so the choice is mostly about confidence-band tightness and explainability. The 12-month projection is **$5.71M** total revenue (~$476K/month, up from a $366K trailing baseline).

4. **Logistic Regression wins on churn AUC — 0.827, 78.5% accuracy.** Expected XGBoost to dominate. It didn't. The relationships here are mostly linear, so the boosted trees aren't extracting extra signal. All three classifiers clear the 75% accuracy target; LogReg ships because it's the easiest to retrain and explain.

5. **Bronze and Standard tiers are loss-making per customer.** K-Means produces 5 value tiers. Per-customer profit by tier: Platinum +$23.65, Gold +$19.46, Silver +$18.58, **Bronze −$2.23, Standard −$3.03**. These two tiers (~1,800 customers combined) need repricing or cost-to-serve cuts before anything else.

6. **Monte Carlo on next year's profit gives effectively zero probability of an annual loss.** 1,000 iterations under varying churn, growth, and per-customer margin: median $0.83M, 90% range $0.62M–$1.04M. The business is structurally profitable. Upside lever is retention, not pricing.

[![Profit by segment](https://github.com/PriyanshuMoudgil12/financial-analytics-project/raw/main/reports/04_profit_by_segment.png)](/PriyanshuMoudgil12/financial-analytics-project/blob/main/reports/04_profit_by_segment.png)

The full business narrative lives in [`docs/Executive_Summary.md`](docs/Executive_Summary.md); the slide-by-slide deck in [`docs/Business_Insights_Presentation.md`](docs/Business_Insights_Presentation.md); the technical methodology in [`docs/Technical_Methodology.md`](docs/Technical_Methodology.md); the full metrics tables in [`docs/Model_Performance_Report.md`](docs/Model_Performance_Report.md).

---

## What I learned

- **Linear models can beat XGBoost when the structure is linear.** I went into the churn modeling expecting boosted trees to win on AUC. They didn't — Logistic Regression edged them out by 0.008 AUC. The lesson isn't "use LogReg always," it's that picking the most sophisticated model by default is lazy. If the data's relationships are mostly linear, the trees won't find anything extra and you've given up interpretability for nothing.

- **A 4.38% MAPE is a red flag, not a brag.** My first build produced a Holt-Winters MAPE of 4.38%, which sounded great until I realised the synthetic data had collapsed too many customers into a single signup month — making the time series unrealistically smooth. After smoothing the signup distribution, MAPE landed at 8.72%, which is in the realistic range for monthly revenue forecasts. Honest numbers beat impressive numbers in an interview.

- **Per-customer profit beats total profit as a segment metric.** The first version of the profit-by-segment chart used total contribution and flagged Platinum (high-margin, small segment) as a "loss-maker" because the total was small. Switching to average profit per customer surfaced the real story: Bronze and Standard tiers are individually unprofitable. The metric you choose changes the recommendation.

- **Class balancing is a tool, not a rule.** I started with `class_weight="balanced"` on the classifiers. It dropped LogReg accuracy below the 75% target with no corresponding AUC benefit. Removing it pushed all three models above 77% accuracy. Defaults exist for a reason, but you have to actually check whether they're earning their keep.

---

## What I'd add next

- **SHAP analysis on the churn model.** The current top-10 drivers are based on coefficients (LogReg) and feature importances (RF). SHAP values would catch interaction effects the linear model misses — for example, "month-to-month + fiber + high charges" might be more predictive than the three features summed individually.

- **Threshold tuning with a cost matrix.** The current model uses the default 0.5 decision threshold. In production, the threshold should depend on the cost of outreach vs the value of the customer being retained. Add a precision-recall curve at the deployment step and let the business pick the operating point.

- **Real cost-to-serve and marketing attribution.** The six financial columns are synthetic. The methodology, segmentation, and recommendations would all hold against real GL data, but the absolute dollar amounts would shift. Worth running the pipeline against actual finance numbers before committing to retention budgets.

- **Survival analysis instead of binary churn.** Modeling churn as a single event throws away timing information. A Cox proportional hazards model (via `lifelines`) would estimate *when* a customer is likely to churn, not just *whether*. That's the version a real retention team would prefer.

---

**Priyanshu Moudgil** · BBA, 5th Semester · open to Summer / Winter 2026 analyst internships

- GitHub: [@PriyanshuMoudgil12](https://github.com/PriyanshuMoudgil12)
- LinkedIn: [linkedin.com/in/priyanshu-moudgil](https://linkedin.com/in/priyanshu-moudgil)
- Email: priyanshumoudgil12@gmail.com
