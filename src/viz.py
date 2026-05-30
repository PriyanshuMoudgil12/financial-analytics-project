"""Shared plotting style and a small save-figure helper.

Importing :func:`set_style` at the top of each notebook gives every chart a
consistent, presentation-ready look.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"

# Brand palette used across notebooks and the dashboard.
PALETTE = ["#2E5A88", "#4C9A8E", "#E6A23C", "#C0504D", "#8064A2", "#9BBB59", "#4BACC6"]
ACCENT = "#2E5A88"
DANGER = "#C0504D"


def set_style() -> None:
    """Apply the project's matplotlib/seaborn theme."""
    sns.set_theme(style="whitegrid", palette=PALETTE)
    plt.rcParams.update({
        "figure.figsize": (10, 5.5),
        "figure.dpi": 110,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.edgecolor": "#cccccc",
        "font.family": "DejaVu Sans",
        "savefig.bbox": "tight",
        "savefig.dpi": 130,
    })


def save_fig(fig, name: str) -> Path:
    """Save a matplotlib figure to ``reports/<name>.png`` and return the path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / (name if name.endswith(".png") else f"{name}.png")
    fig.savefig(path)
    return path


# Plotly template name (built-in) used by the dashboard.
PLOTLY_TEMPLATE = "plotly_white"
