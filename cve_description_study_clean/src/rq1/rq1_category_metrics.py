import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import PROCESSED_DIR, OUTPUT_DIR
from common.fields import FIELD_GROUPS, FIELD_CN, FIELD_ORDER
from common.io_utils import ensure_binary_fields, read_excel_auto, write_excel

INPUT_FILE = PROCESSED_DIR / "5000cve_before.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq1_category_metrics.xlsx"


def main() -> None:
    df = read_excel_auto(INPUT_FILE, sheet_name=0)
    df = df.drop_duplicates(subset=["cve_id"], keep="first").copy()
    df = ensure_binary_fields(df, FIELD_ORDER)
    n = len(df)

    category_rows = []
    dist_rows = []
    per_cve_rows = []

    for category, fields in FIELD_GROUPS.items():
        sub = df[fields]
        m = len(fields)
        present_counts = sub.sum(axis=1)
        missing_counts = m - present_counts

        category_rows.append({
            "category": category,
            "field_count": m,
            "avg_present_rate": float(sub.to_numpy().mean()),
            "avg_missing_rate": 1 - float(sub.to_numpy().mean()),
            "full_present_n": int((missing_counts == 0).sum()),
            "full_present_rate": float((missing_counts == 0).mean()),
            "full_missing_n": int((missing_counts == m).sum()),
            "full_missing_rate": float((missing_counts == m).mean()),
            "missing_at_least_half_n": int((missing_counts >= math.ceil(m / 2)).sum()),
            "missing_at_least_half_rate": float((missing_counts >= math.ceil(m / 2)).mean()),
            "avg_missing_items": float(missing_counts.mean()),
            "median_missing_items": float(missing_counts.median()),
        })

        counts = missing_counts.value_counts().sort_index()
        for k in range(m + 1):
            count = int(counts.get(k, 0))
            dist_rows.append({
                "category": category,
                "field_count": m,
                "missing_items": k,
                "sample_n": count,
                "sample_rate": count / n if n else 0,
            })

        tmp = pd.DataFrame({
            "cve_id": df["cve_id"],
            "category": category,
            "field_count": m,
            "present_items": present_counts.astype(int),
            "missing_items": missing_counts.astype(int),
            "category_complete_rate": present_counts / m,
        })
        per_cve_rows.append(tmp)

    field_mapping = pd.DataFrame([
        {"category": cat, "field_key": f, "field_zh": FIELD_CN[f], "order_in_category": i + 1}
        for cat, fields in FIELD_GROUPS.items()
        for i, f in enumerate(fields)
    ])

    write_excel(OUTPUT_FILE, {
        "category_metrics": pd.DataFrame(category_rows).sort_values("avg_present_rate", ascending=False),
        "missing_distribution": pd.DataFrame(dist_rows),
        "per_cve_category": pd.concat(per_cve_rows, ignore_index=True),
        "field_mapping": field_mapping,
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
