"""Reusable error / evaluation metrics for forecasting and classification."""
from __future__ import annotations

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- #
# Forecasting / regression metrics
# --------------------------------------------------------------------------- #
def mae(y_true, y_pred) -> float:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred) -> float:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true, y_pred) -> float:
    """Mean Absolute Percentage Error (%). Ignores zero-valued actuals."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def forecast_scores(y_true, y_pred, model_name: str) -> dict:
    """Return a one-row dict of MAE / RMSE / MAPE for a forecast model."""
    return {
        "Model": model_name,
        "MAE": round(mae(y_true, y_pred), 2),
        "RMSE": round(rmse(y_true, y_pred), 2),
        "MAPE (%)": round(mape(y_true, y_pred), 2),
    }


def scores_table(rows: list[dict]) -> pd.DataFrame:
    """Build a sorted comparison table (best RMSE first) from score dicts."""
    return (
        pd.DataFrame(rows)
        .sort_values("RMSE")
        .reset_index(drop=True)
    )


# --------------------------------------------------------------------------- #
# Classification metrics
# --------------------------------------------------------------------------- #
def classification_scores(y_true, y_pred, y_proba, model_name: str) -> dict:
    """Accuracy / precision / recall / F1 / ROC-AUC for a churn classifier."""
    from sklearn.metrics import (
        accuracy_score, f1_score, precision_score, recall_score, roc_auc_score,
    )
    return {
        "Model": model_name,
        "Accuracy": round(accuracy_score(y_true, y_pred), 4),
        "Precision": round(precision_score(y_true, y_pred), 4),
        "Recall": round(recall_score(y_true, y_pred), 4),
        "F1": round(f1_score(y_true, y_pred), 4),
        "ROC-AUC": round(roc_auc_score(y_true, y_proba), 4),
    }
