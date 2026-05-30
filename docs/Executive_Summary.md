# Executive Summary

Telco customer base in California — 7,043 customers across the North, Central, and South regions. This memo covers churn, revenue outlook, and profitability across the active book.

## Headline

The business books around $0.42M in monthly recurring revenue today and is growing. The forecast projects $5.71M over the next 12 months — an average of $476K per month, up from a $366K trailing-12 baseline. The single biggest threat to that trajectory is churn, which runs at about 31% and is heavily concentrated in low-commitment, high-bill customers.

## Findings

Revenue is predictable. A Holt-Winters model forecasts the next 12 months within 8.7% MAPE on a holdout, with a typical summer peak and a December dip. That's tight enough to plan against without burning a whole quarter on forecasting tooling.

Churn is concentrated and targetable. Month-to-month contracts, fiber-optic plans, electronic-check payers, low-tenure customers, and high monthly bills with no support add-ons drive most of the attrition. The Logistic Regression model identifies churners at 78.5% accuracy and 0.83 ROC-AUC — useful for retention prioritization, not just a number to put in a slide.

There's a 167-customer high-risk list worth acting on. These are active customers with churn probability above 70%, carrying around $12.4K of monthly revenue (about $149K annualized). It's a finite, ranked, exportable list — exactly the kind of thing a retention team can work through.

Profit is concentrated. K-Means produces five tiers. Gold and Silver are the two biggest profit pools (large segments × healthy per-customer margin). Bronze and Standard are loss-making per customer — they need either repricing or cost-to-serve cuts before anything else.

---

## Risk

Monte Carlo on next year's profit (1,000 scenarios, varying churn, growth, and per-customer margin) lands at a median of $0.83M, with a 90% range of $0.62M–$1.04M, and effectively zero probability of an annual loss. The business is structurally profitable. The upside lever is retention, not pricing.

## Recommendations

| # | Action | Why |
|---|--------|-----|
| 1 | Targeted save campaign for the 167 high-risk customers (incentivize 1- or 2-year contracts) | Protects ~$149K annualized revenue |
| 2 | Migrate month-to-month customers to annual contracts | Directly attacks the biggest churn driver |
| 3 | Reprice or cut cost-to-serve in Bronze and Standard tiers | Turns negative per-customer margins positive |
| 4 | Use the 12-month forecast for capacity and cash planning | Plan against an 8.7% MAPE baseline, not gut feel |

Full detail in [Business Insights Presentation](Business_Insights_Presentation.md), [Technical Methodology](Technical_Methodology.md), and [Model Performance Report](Model_Performance_Report.md).
