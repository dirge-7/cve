import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from collections import Counter
import pandas as pd
from common.config import OUTPUT_DIR
from common.fields import FIELD_GROUPS
from common.io_utils import write_excel

INPUT_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq2_category_metrics.xlsx"


def main() -> None:
    paired = pd.read_excel(INPUT_FILE, sheet_name="paired_dataset")
    n = len(paired)
    category_rows = []
    missing_rows = []
    gain_rows = []

    for category, fields in FIELD_GROUPS.items():
        before_cols = [f"{f}_before" for f in fields]
        after_cols = [f"{f}_after" for f in fields]
        b_present = paired[before_cols].fillna(0).astype(int).sum(axis=1)
        a_present = paired[after_cols].fillna(0).astype(int).sum(axis=1)
        gain = a_present - b_present
        m = len(fields)
        b_missing = m - b_present
        a_missing = m - a_present

        category_rows.append({
            "category": category,
            "field_count": m,
            "before_avg_complete": float(paired[before_cols].mean().mean()),
            "after_avg_complete": float(paired[after_cols].mean().mean()),
            "gain": float(paired[after_cols].mean().mean() - paired[before_cols].mean().mean()),
            "avg_sample_field_gain": float(gain.mean()),
            "median_sample_field_gain": float(gain.median()),
            "improved_sample_rate": float((gain > 0).mean()),
            "unchanged_sample_rate": float((gain == 0).mean()),
            "declined_sample_rate": float((gain < 0).mean()),
        })
        for k in range(m + 1):
            missing_rows.append({
                "category": category,
                "missing_items": k,
                "before_count": int((b_missing == k).sum()),
                "before_rate": float((b_missing == k).mean()),
                "after_count": int((a_missing == k).sum()),
                "after_rate": float((a_missing == k).mean()),
            })
        for value, count in Counter(gain).items():
            gain_rows.append({
                "category": category,
                "sample_field_gain": int(value),
                "sample_count": int(count),
                "sample_rate": count / n if n else 0,
            })

    write_excel(OUTPUT_FILE, {
        "category_metrics": pd.DataFrame(category_rows).sort_values("gain", ascending=False),
        "missing_distribution": pd.DataFrame(missing_rows),
        "category_sample_gain": pd.DataFrame(gain_rows).sort_values(["category", "sample_field_gain"]),
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
