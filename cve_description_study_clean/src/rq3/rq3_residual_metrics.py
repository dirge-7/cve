import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import math
import pandas as pd
from common.config import PROCESSED_DIR, OUTPUT_DIR
from common.fields import FIELD_CN, FIELD_CATEGORY, FIELD_GROUPS, FIELD_ORDER
from common.io_utils import build_source_count_map, source_count_group, write_excel

PAIRED_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"
FIELD_METRICS_FILE = OUTPUT_DIR / "rq2_field_metrics.xlsx"
SOURCE_JSON = PROCESSED_DIR / "cve_description.json"
OUTPUT_FILE = OUTPUT_DIR / "rq3_residual_metrics.xlsx"
HIGH_RESIDUAL_THRESHOLD = 0.5


def main() -> None:
    paired = pd.read_excel(PAIRED_FILE, sheet_name="paired_dataset")
    field_metrics = pd.read_excel(FIELD_METRICS_FILE, sheet_name="field_metrics") if FIELD_METRICS_FILE.exists() else pd.DataFrame()
    source_count = build_source_count_map(SOURCE_JSON)
    n = len(paired)

    after_status = paired[["cve_id"]].copy()
    if "cwe_id" in paired.columns:
        after_status["cwe_id"] = paired["cwe_id"]
    after_status["source_count"] = after_status["cve_id"].map(source_count)
    after_status["source_count_group"] = after_status["source_count"].map(source_count_group)
    for field in FIELD_ORDER:
        after_status[field] = paired[f"{field}_after"].fillna(0).astype(int)
    after_status["after_present_count"] = after_status[FIELD_ORDER].sum(axis=1)
    after_status["after_missing_count"] = len(FIELD_ORDER) - after_status["after_present_count"]

    residual_rows = []
    for field in FIELD_ORDER:
        vals = after_status[field]
        exist = int(vals.sum())
        missing = n - exist
        base = {
            "category": FIELD_CATEGORY[field],
            "field": field,
            "field_zh": FIELD_CN[field],
            "valid_n": n,
            "after_exist_n": exist,
            "after_missing_n": missing,
            "after_complete": exist / n if n else 0,
            "residual_miss": missing / n if n else 0,
            "high_residual": (missing / n if n else 0) >= HIGH_RESIDUAL_THRESHOLD,
        }
        if not field_metrics.empty:
            match = field_metrics[field_metrics["field"] == field]
            if len(match):
                for col in ["before_complete", "gain", "fill_rate", "drop_rate"]:
                    base[f"rq2_{col}"] = match.iloc[0].get(col)
        residual_rows.append(base)
    field_residual = pd.DataFrame(residual_rows).sort_values("residual_miss", ascending=False)

    category_rows = []
    for category, fields in FIELD_GROUPS.items():
        sub = after_status[fields]
        miss_counts = len(fields) - sub.sum(axis=1)
        category_rows.append({
            "category": category,
            "field_count": len(fields),
            "after_avg_complete": float(sub.mean().mean()),
            "category_avg_residual": float(1 - sub.mean().mean()),
            "high_residual_field_n": int(field_residual[(field_residual["category"] == category) & (field_residual["high_residual"])].shape[0]),
            "avg_missing_items_per_cve": float(miss_counts.mean()),
            "full_present_rate": float((miss_counts == 0).mean()),
            "full_missing_rate": float((miss_counts == len(fields)).mean()),
            "missing_at_least_half_rate": float((miss_counts >= math.ceil(len(fields) / 2)).mean()),
        })

    source_aux = after_status.groupby("source_count_group", dropna=False).agg(
        sample_n=("cve_id", "count"),
        avg_after_present=("after_present_count", "mean"),
        avg_after_missing=("after_missing_count", "mean"),
    ).reset_index()

    write_excel(OUTPUT_FILE, {
        "after_status": after_status,
        "field_residual": field_residual,
        "high_residual_fields": field_residual[field_residual["high_residual"]].copy(),
        "category_residual": pd.DataFrame(category_rows).sort_values("category_avg_residual", ascending=False),
        "source_count_aux": source_aux,
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
