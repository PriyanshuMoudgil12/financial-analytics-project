"""Feature-engineering helpers: RFM scoring and Customer Lifetime Value (CLV).

These are shared by the churn (03) and profitability (04) notebooks so the
definitions stay consistent across the project.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def add_clv(df: pd.DataFrame) -> pd.DataFrame:
    """Append a model-based CLV estimate.

    CLV = expected monthly margin x expected remaining lifetime, where the
    expected lifetime is derived from a simple churn-rate assumption. This is
    independent of the dataset's own ``CLTV`` score (kept for comparison).
    """
    out = df.copy()
    monthly_margin = out["MonthlyProfit"].clip(lower=0)
    # Expected remaining tenure (months): longer for contracted customers.
    horizon = np.select(
        [out["Contract"] == "Two year", out["Contract"] == "One year"],
        [36.0, 24.0], default=12.0,
    )
    # Discount factor for likely churners (churn score -> survival weight).
    survival = 1.0 - (out["Churn Score"] / 100.0) * 0.6
    out["CLV"] = (monthly_margin * horizon * survival).round(2)
    return out


def add_rfm(df: pd.DataFrame, reference_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Append Recency / Frequency / Monetary features and an RFM score (3-15).

    For this telco panel we map:
      * Recency   -> months since last active month (lower = better)
      * Frequency -> tenure in months (longer relationship = more "purchases")
      * Monetary  -> total charges (lifetime spend)
    Each dimension is scored 1-5 via quintiles; ``RFM_Score`` is their sum and
    ``RFM_Segment`` buckets customers into named tiers.
    """
    out = df.copy()
    if reference_date is None:
        reference_date = pd.Timestamp("2021-02-01")

    signup = pd.to_datetime(out["SignupMonth"])
    last_active = signup + out["Tenure Months"].apply(lambda m: pd.DateOffset(months=int(m)))
    # Active customers were "seen" at the reference date; churned at last_active.
    last_active = np.where(out["Churn Value"] == 1, last_active, reference_date)
    last_active = pd.Series(pd.to_datetime(last_active), index=out.index)

    out["Recency"] = ((reference_date - last_active).dt.days / 30.0).round(1).clip(lower=0)
    out["Frequency"] = out["Tenure Months"]
    out["Monetary"] = pd.to_numeric(out["Total Charges"], errors="coerce").fillna(0.0)

    # Quintile scores. Recency is reverse-scored (recent = high score).
    out["R_Score"] = _quintile(out["Recency"], reverse=True)
    out["F_Score"] = _quintile(out["Frequency"])
    out["M_Score"] = _quintile(out["Monetary"])
    out["RFM_Score"] = out["R_Score"] + out["F_Score"] + out["M_Score"]
    out["RFM_Segment"] = pd.cut(
        out["RFM_Score"],
        bins=[2, 6, 9, 12, 15],
        labels=["At Risk", "Need Attention", "Loyal", "Champions"],
        include_lowest=True,
    )
    return out


def _quintile(series: pd.Series, reverse: bool = False) -> pd.Series:
    """Score a numeric series 1-5 by quintile (5 = best), robust to ties."""
    ranks = series.rank(method="first")
    try:
        q = pd.qcut(ranks, 5, labels=False) + 1
    except ValueError:  # too few distinct values
        q = pd.cut(ranks, 5, labels=False) + 1
    q = q.astype(int)
    return 6 - q if reverse else q
