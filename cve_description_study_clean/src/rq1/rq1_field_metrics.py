import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import PROCESSED_DIR, OUTPUT_DIR
from common.fields import FIELD_CATEGORY, FIELD_CN, FIELD_ORDER
from common.io_utils import ensure_binary_fields, read_excel_auto, write_excel

INPUT_FILE = PROCESSED_DIR / "5000cve_before.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq1_field_metrics.xlsx"
SHEET_NAME = 0


def main() -> None:
    df = read_excel_auto(INPUT_FILE, sheet_name=SHEET_NAME)
    df = df.drop_duplicates(subset=["cve_id"], keep="first").copy()
    df = ensure_binary_fields(df, FIELD_ORDER)
    n = len(df)

    rows = []
    for field in FIELD_ORDER:
        present = int(df[field].sum())
        rows.append({
            "category": FIELD_CATEGORY[field],
            "field_key": field,
            "field_zh": FIELD_CN[field],
            "valid_n": n,
            "present_n": present,
            "present_rate": present / n if n else 0,
            "missing_n": n - present,
            "missing_rate": 1 - present / n if n else 0,
        })

    result = pd.DataFrame(rows).sort_values("present_rate", ascending=False)
    write_excel(OUTPUT_FILE, {"field_metrics": result})
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
