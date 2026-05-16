import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from common.config import OUTPUT_DIR
from common.fields import FIELD_ORDER
from common.io_utils import write_excel

INPUT_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq2_sample_metrics.xlsx"


def main() -> None:
    paired = pd.read_excel(INPUT_FILE, sheet_name="paired_dataset")
    before_cols = [f"{f}_before" for f in FIELD_ORDER]
    after_cols = [f"{f}_after" for f in FIELD_ORDER]
    n_fields = len(FIELD_ORDER)

    sample = paired[["cve_id"]].copy()
    sample["covered_before"] = paired[before_cols].sum(axis=1)
    sample["covered_after"] = paired[after_cols].sum(axis=1)
    sample["missing_before"] = n_fields - sample["covered_before"]
    sample["missing_after"] = n_fields - sample["covered_after"]
    sample["sample_gain"] = sample["covered_after"] - sample["covered_before"]
    sample["direction"] = np.where(sample["sample_gain"] > 0, "improved", np.where(sample["sample_gain"] < 0, "declined", "unchanged"))

    summary = pd.DataFrame([
        {"metric": "paired_samples", "value": len(sample)},
        {"metric": "field_count", "value": n_fields},
        {"metric": "avg_covered_before", "value": float(sample["covered_before"].mean())},
        {"metric": "avg_covered_after", "value": float(sample["covered_after"].mean())},
        {"metric": "avg_sample_gain", "value": float(sample["sample_gain"].mean())},
        {"metric": "median_sample_gain", "value": float(sample["sample_gain"].median())},
        {"metric": "improved_count", "value": int((sample["sample_gain"] > 0).sum())},
        {"metric": "unchanged_count", "value": int((sample["sample_gain"] == 0).sum())},
        {"metric": "declined_count", "value": int((sample["sample_gain"] < 0).sum())},
    ])

    gain_distribution = sample["sample_gain"].value_counts().sort_index().rename_axis("sample_gain").reset_index(name="sample_count")
    gain_distribution["sample_rate"] = gain_distribution["sample_count"] / len(sample)

    sample["before_group"] = pd.cut(
        sample["covered_before"], bins=[-0.1, 4, 8, 12, n_fields],
        labels=["low_0_4", "mid_low_5_8", "mid_high_9_12", "high_13_24"],
    )
    stratified = sample.groupby("before_group", observed=False).agg(
        sample_count=("cve_id", "count"),
        avg_covered_before=("covered_before", "mean"),
        avg_covered_after=("covered_after", "mean"),
        avg_sample_gain=("sample_gain", "mean"),
        median_sample_gain=("sample_gain", "median"),
        improved_count=("sample_gain", lambda s: int((s > 0).sum())),
        unchanged_count=("sample_gain", lambda s: int((s == 0).sum())),
        declined_count=("sample_gain", lambda s: int((s < 0).sum())),
    ).reset_index()

    write_excel(OUTPUT_FILE, {
        "summary": summary,
        "gain_distribution": gain_distribution,
        "stratified_gain": stratified,
        "sample_metrics": sample.sort_values("sample_gain", ascending=False),
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
