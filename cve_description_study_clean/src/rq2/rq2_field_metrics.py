import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import OUTPUT_DIR
from common.fields import FIELD_CN, FIELD_CATEGORY, FIELD_ORDER
from common.io_utils import write_excel

INPUT_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq2_field_metrics.xlsx"


def main() -> None:
    paired = pd.read_excel(INPUT_FILE, sheet_name="paired_dataset")
    rows = []
    transitions = []
    n = len(paired)

    for field in FIELD_ORDER:
        b = paired[f"{field}_before"].fillna(0).astype(int)
        a = paired[f"{field}_after"].fillna(0).astype(int)
        n00 = int(((b == 0) & (a == 0)).sum())
        n01 = int(((b == 0) & (a == 1)).sum())
        n10 = int(((b == 1) & (a == 0)).sum())
        n11 = int(((b == 1) & (a == 1)).sum())
        before_complete = float(b.mean())
        after_complete = float(a.mean())
        rows.append({
            "field": field,
            "field_zh": FIELD_CN[field],
            "category": FIELD_CATEGORY[field],
            "paired_n": n,
            "before_exist_n": int(b.sum()),
            "before_complete": before_complete,
            "after_exist_n": int(a.sum()),
            "after_complete": after_complete,
            "gain": after_complete - before_complete,
            "n00": n00,
            "n01": n01,
            "n10": n10,
            "n11": n11,
            "fill_rate": n01 / (n00 + n01) if (n00 + n01) else None,
            "residual_miss": float((a == 0).mean()),
            "drop_rate": n10 / (n10 + n11) if (n10 + n11) else None,
        })
        transitions.append({"field": field, "field_zh": FIELD_CN[field], "transition": "0→0", "count": n00})
        transitions.append({"field": field, "field_zh": FIELD_CN[field], "transition": "0→1", "count": n01})
        transitions.append({"field": field, "field_zh": FIELD_CN[field], "transition": "1→0", "count": n10})
        transitions.append({"field": field, "field_zh": FIELD_CN[field], "transition": "1→1", "count": n11})

    metrics = pd.DataFrame(rows).sort_values("gain", ascending=False)
    abnormal = metrics[(metrics["n10"] > 0) | (metrics["gain"] < 0)].copy()
    write_excel(OUTPUT_FILE, {
        "field_metrics": metrics,
        "transition_long": pd.DataFrame(transitions),
        "abnormal_drop_fields": abnormal,
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
