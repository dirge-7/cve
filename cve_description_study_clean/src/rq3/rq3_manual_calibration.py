import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from collections import Counter
import pandas as pd
from common.config import OUTPUT_DIR
from common.io_utils import write_excel

MANUAL_FILE = OUTPUT_DIR / "rq3_high_residual_samples_reviewed.xlsx"
RESIDUAL_FILE = OUTPUT_DIR / "rq3_residual_metrics.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq3_manual_calibration.xlsx"
ATTR_LABELS = {
    "A": "true_residual_missing",
    "B": "implicit_or_boundary",
    "C": "granularity_mismatch",
    "D": "automation_or_labeling_miss",
}


def main() -> None:
    if not MANUAL_FILE.exists():
        raise FileNotFoundError(
            f"Manual review file not found: {MANUAL_FILE}. "
            "Copy rq3_high_residual_samples.xlsx to this name after filling manual columns."
        )
    manual = pd.read_excel(MANUAL_FILE, sheet_name="manual_review_samples")
    field_residual = pd.read_excel(RESIDUAL_FILE, sheet_name="field_residual")
    manual["attribution_type"] = manual["attribution_type"].astype(str).str.strip().str.upper()
    valid = manual[manual["attribution_type"].isin(ATTR_LABELS)].copy()

    overall = valid["attribution_type"].value_counts().rename_axis("attribution_type").reset_index(name="count")
    overall["meaning"] = overall["attribution_type"].map(ATTR_LABELS)
    overall["rate"] = overall["count"] / len(valid) if len(valid) else 0

    by_field = valid.groupby(["category", "field", "field_zh", "attribution_type"]).size().unstack(fill_value=0).reset_index()
    for col in ["A", "B", "C", "D"]:
        if col not in by_field.columns:
            by_field[col] = 0
    by_field["manual_n"] = by_field[["A", "B", "C", "D"]].sum(axis=1)
    by_field["strict_residual_share_A_B_C"] = (by_field["A"] + by_field["B"] + by_field["C"]) / by_field["manual_n"]
    by_field["clear_true_residual_share_A"] = by_field["A"] / by_field["manual_n"]
    by_field["overestimate_share_D"] = by_field["D"] / by_field["manual_n"]
    by_field = by_field.merge(field_residual[["field", "residual_miss"]], on="field", how="left")
    by_field["calibrated_strict_residual"] = by_field["residual_miss"] * by_field["strict_residual_share_A_B_C"]
    by_field["calibrated_clear_residual"] = by_field["residual_miss"] * by_field["clear_true_residual_share_A"]
    by_field["overestimated_residual_part"] = by_field["residual_miss"] * by_field["overestimate_share_D"]

    by_category = valid.groupby(["category", "attribution_type"]).size().unstack(fill_value=0).reset_index()
    for col in ["A", "B", "C", "D"]:
        if col not in by_category.columns:
            by_category[col] = 0
    by_category["manual_n"] = by_category[["A", "B", "C", "D"]].sum(axis=1)
    by_category["strict_residual_share_A_B_C"] = (by_category["A"] + by_category["B"] + by_category["C"]) / by_category["manual_n"]
    by_category["overestimate_share_D"] = by_category["D"] / by_category["manual_n"]

    write_excel(OUTPUT_FILE, {
        "overall_attribution": overall,
        "by_field": by_field.sort_values("residual_miss", ascending=False),
        "by_category": by_category,
        "manual_samples": valid,
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
