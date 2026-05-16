import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import OUTPUT_DIR
from common.io_utils import write_excel

BIAS_FILE = OUTPUT_DIR / "rq4_bias_input.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq4_bias_summary.xlsx"

ATTR_MAP = {
    "A": "true_residual_missing",
    "B": "boundary_or_implicit",
    "C": "granularity_mismatch",
    "D": "automation_or_labeling_miss",
}


def main() -> None:
    bias = pd.read_excel(BIAS_FILE, sheet_name="bias_input")
    rq3 = bias[bias["is_rq3_manual_sample"] == True].copy()
    n10 = bias[bias["is_n10_transition"] == True].copy()

    if len(rq3):
        attribution_summary = rq3["attribution_type"].value_counts(dropna=False).rename_axis("attribution_type").reset_index(name="count")
        attribution_summary["meaning"] = attribution_summary["attribution_type"].map(ATTR_MAP).fillna("unlabeled")
        attribution_summary["rate"] = attribution_summary["count"] / len(rq3)
    else:
        attribution_summary = pd.DataFrame(columns=["attribution_type", "count", "meaning", "rate"])

    by_field = rq3.groupby(["category", "field", "field_zh", "attribution_type"]).size().unstack(fill_value=0).reset_index() if len(rq3) else pd.DataFrame()
    if len(by_field):
        for col in ["A", "B", "C", "D"]:
            if col not in by_field.columns:
                by_field[col] = 0
        by_field["manual_n"] = by_field[["A", "B", "C", "D"]].sum(axis=1)
        by_field["E1_D_rate"] = by_field["D"] / by_field["manual_n"]
        by_field["E4_B_rate"] = by_field["B"] / by_field["manual_n"]
        by_field["E2_or_E4_C_rate"] = by_field["C"] / by_field["manual_n"]
        by_field["true_residual_A_rate"] = by_field["A"] / by_field["manual_n"]

    by_category = rq3.groupby(["category", "attribution_type"]).size().unstack(fill_value=0).reset_index() if len(rq3) else pd.DataFrame()
    if len(by_category):
        for col in ["A", "B", "C", "D"]:
            if col not in by_category.columns:
                by_category[col] = 0
        by_category["manual_n"] = by_category[["A", "B", "C", "D"]].sum(axis=1)
        by_category["E1_D_rate"] = by_category["D"] / by_category["manual_n"]
        by_category["boundary_or_granularity_BC_rate"] = (by_category["B"] + by_category["C"]) / by_category["manual_n"]
        by_category["true_residual_A_rate"] = by_category["A"] / by_category["manual_n"]

    n10_summary = pd.DataFrame([
        {"metric": "n10_transition_count", "value": len(n10)},
        {"metric": "n10_field_count", "value": n10["field"].nunique() if len(n10) else 0},
        {"metric": "n10_cve_count", "value": n10["cve_id"].nunique() if len(n10) else 0},
    ])

    summary = pd.DataFrame([
        {"metric": "rq3_manual_samples", "value": len(rq3)},
        {"metric": "rq3_D_E1_count", "value": int((rq3["attribution_type"] == "D").sum()) if len(rq3) else 0},
        {"metric": "rq3_D_E1_rate", "value": float((rq3["attribution_type"] == "D").mean()) if len(rq3) else 0},
        {"metric": "rq3_BC_boundary_granularity_count", "value": int(rq3["attribution_type"].isin(["B", "C"]).sum()) if len(rq3) else 0},
        {"metric": "rq3_BC_boundary_granularity_rate", "value": float(rq3["attribution_type"].isin(["B", "C"]).mean()) if len(rq3) else 0},
        {"metric": "rq3_A_true_residual_count", "value": int((rq3["attribution_type"] == "A").sum()) if len(rq3) else 0},
        {"metric": "rq3_A_true_residual_rate", "value": float((rq3["attribution_type"] == "A").mean()) if len(rq3) else 0},
        {"metric": "n10_transition_count", "value": len(n10)},
    ])

    write_excel(OUTPUT_FILE, {
        "summary": summary,
        "rq3_attribution_summary": attribution_summary,
        "rq3_by_field": by_field,
        "rq3_by_category": by_category,
        "n10_summary": n10_summary,
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
