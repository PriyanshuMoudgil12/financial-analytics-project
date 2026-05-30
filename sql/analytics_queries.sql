-- ============================================================================
-- Financial Operations Analytics — Analytical SQL
-- ----------------------------------------------------------------------------
-- Dialect: standard SQL, verified on SQLite 3. Column names contain spaces, so
-- they are wrapped in double quotes (ANSI identifier quoting).
--
-- Two tables are assumed (load the project CSVs once):
--   customers : data/processed/telco_clean.csv          (39 cleaned columns)
--   segments  : data/processed/customer_segments.csv    (K-Means value tiers)
--
-- Quick load with the sqlite3 CLI:
--   sqlite3 finops.db
--   .mode csv
--   .import data/processed/telco_clean.csv customers
--   .import data/processed/customer_segments.csv segments
--
-- (Or load the CSVs with pandas.to_sql for the same table names.)
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 1. Revenue & profit by value segment
--    Total / average monthly revenue and profit per K-Means segment, with each
--    segment's share of total monthly revenue.
-- ----------------------------------------------------------------------------
SELECT
    s."Segment"                                            AS segment,
    COUNT(*)                                               AS customers,
    ROUND(SUM(c."Monthly Charges"), 2)                     AS monthly_revenue,
    ROUND(AVG(c."Monthly Charges"), 2)                     AS avg_monthly_revenue,
    ROUND(SUM(c."MonthlyProfit"), 2)                       AS monthly_profit,
    ROUND(100.0 * SUM(c."Monthly Charges")
          / SUM(SUM(c."Monthly Charges")) OVER (), 1)      AS pct_of_revenue
FROM customers AS c
JOIN segments  AS s ON s."CustomerID" = c."CustomerID"
GROUP BY s."Segment"
ORDER BY monthly_revenue DESC;


-- ----------------------------------------------------------------------------
-- 2. Monthly revenue trend (by signup month)
--    Recurring revenue and customers acquired in each signup month — the raw
--    series behind the forecasting notebook.
-- ----------------------------------------------------------------------------
SELECT
    SUBSTR("SignupMonth", 1, 7)                            AS signup_month,
    COUNT(*)                                               AS customers_acquired,
    ROUND(SUM("Monthly Charges"), 2)                       AS monthly_revenue,
    ROUND(SUM("MonthlyProfit"), 2)                         AS monthly_profit
FROM customers
GROUP BY signup_month
ORDER BY signup_month;


-- ----------------------------------------------------------------------------
-- 3. Top 10 customers by lifetime revenue
--    Highest lifetime value accounts, with their churn status flagged.
-- ----------------------------------------------------------------------------
SELECT
    "CustomerID"                                           AS customer_id,
    "Region"                                               AS region,
    "Contract"                                             AS contract,
    "Tenure Months"                                        AS tenure_months,
    ROUND("Total Charges", 2)                              AS lifetime_revenue,
    "CLTV"                                                 AS cltv_score,
    "Churn Label"                                          AS churned
FROM customers
ORDER BY lifetime_revenue DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- 4. Churn rate by region and contract
--    Churn % for every Region x Contract combination, plus revenue exposure.
-- ----------------------------------------------------------------------------
SELECT
    "Region"                                               AS region,
    "Contract"                                             AS contract,
    COUNT(*)                                               AS customers,
    SUM("Churn Value")                                     AS churned,
    ROUND(100.0 * SUM("Churn Value") / COUNT(*), 1)        AS churn_rate_pct,
    ROUND(SUM(CASE WHEN "Churn Value" = 1
                   THEN "Monthly Charges" ELSE 0 END), 2)  AS monthly_revenue_lost
FROM customers
GROUP BY "Region", "Contract"
ORDER BY churn_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- 5. CLV by signup cohort (year)
--    Average lifetime value, tenure and churn by acquisition-year cohort.
-- ----------------------------------------------------------------------------
SELECT
    SUBSTR("SignupMonth", 1, 4)                            AS signup_year,
    COUNT(*)                                               AS customers,
    ROUND(AVG("CLTV"), 0)                                  AS avg_cltv,
    ROUND(AVG("Total Charges"), 2)                         AS avg_lifetime_revenue,
    ROUND(AVG("Tenure Months"), 1)                         AS avg_tenure_months,
    ROUND(100.0 * SUM("Churn Value") / COUNT(*), 1)        AS churn_rate_pct
FROM customers
GROUP BY signup_year
ORDER BY signup_year;


-- ----------------------------------------------------------------------------
-- 6. Plan / service margins
--    Unit economics by Internet Service x Contract: average revenue, cost to
--    serve, profit and margin %, ranked by margin.
-- ----------------------------------------------------------------------------
SELECT
    "Internet Service"                                     AS plan,
    "Contract"                                             AS contract,
    COUNT(*)                                               AS customers,
    ROUND(AVG("Monthly Charges"), 2)                       AS avg_revenue,
    ROUND(AVG("CostToServe"), 2)                           AS avg_cost_to_serve,
    ROUND(AVG("MonthlyProfit"), 2)                         AS avg_profit,
    ROUND(100.0 * AVG("MonthlyProfit") / AVG("Monthly Charges"), 1)
                                                           AS margin_pct
FROM customers
GROUP BY "Internet Service", "Contract"
ORDER BY margin_pct DESC;
