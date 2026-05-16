import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import OUTPUT_DIR
from common.io_utils import write_excel

BIAS_SUMMARY_FILE = OUTPUT_DIR / "rq4_bias_summary.xlsx"
RQ2_STATS_FILE = OUTPUT_DIR / "rq2_statistical_tests.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq4_bias_metrics.xlsx"


def get_count(summary: pd.DataFrame, key: str) -> float:
    row = summary[summary["metric"] == key]
    return float(row.iloc[0]["value"]) if len(row) else 0.0


def safe_div(x: float, y: float) -> float:
    return x / y if y else 0.0


def main() -> None:
    summary = pd.read_excel(BIAS_SUMMARY_FILE, sheet_name="summary")
    stats = pd.read_excel(RQ2_STATS_FILE, sheet_name="summary") if RQ2_STATS_FILE.exists() else pd.DataFrame(columns=["metric", "value"])

    rq3_total = get_count(summary, "rq3_manual_samples")
    d_count = get_count(summary, "rq3_D_E1_count")
    bc_count = get_count(summary, "rq3_BC_boundary_granularity_count")
    a_count = get_count(summary, "rq3_A_true_residual_count")
    n10_count = get_count(summary, "n10_transition_count")
    total_n10 = get_count(stats, "total_n10") if len(stats) else n10_count

    metrics = pd.DataFrame([
        {
            "metric": "E1_rate_RQ3_field_existence_false_negative",
            "formula": "D / (A+B+C+D)",
            "value": safe_div(d_count, rq3_total),
            "numerator": d_count,
            "denominator": rq3_total,
        },
        {
            "metric": "E4_extended_boundary_granularity_rate",
            "formula": "(B+C) / (A+B+C+D)",
            "value": safe_div(bc_count, rq3_total),
            "numerator": bc_count,
            "denominator": rq3_total,
        },
        {
            "metric": "TrueResidual_rate",
            "formula": "A / (A+B+C+D)",
            "value": safe_div(a_count, rq3_total),
            "numerator": a_count,
            "denominator": rq3_total,
        },
        {
            "metric": "Residual_overestimate_rate",
            "formula": "D / (A+B+C+D)",
            "value": safe_div(d_count, rq3_total),
            "numerator": d_count,
            "denominator": rq3_total,
        },
        {
            "metric": "N10_remaining_rate_after_rework",
            "formula": "remaining_n10 / total_n10",
            "value": safe_div(n10_count, total_n10),
            "numerator": n10_count,
            "denominator": total_n10,
        },
    ])

    write_excel(OUTPUT_FILE, {"bias_metrics": metrics})
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
