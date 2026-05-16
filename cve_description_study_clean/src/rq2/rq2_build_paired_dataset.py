import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import PROCESSED_DIR, OUTPUT_DIR
from common.fields import FIELD_ORDER
from common.io_utils import ensure_binary_fields, read_excel_auto, write_excel

BEFORE_FILE = PROCESSED_DIR / "5000cve_before.xlsx"
AFTER_FILE = PROCESSED_DIR / "cve_after.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"


def main() -> None:
    before = read_excel_auto(BEFORE_FILE, sheet_name=0)
    after = read_excel_auto(AFTER_FILE, sheet_name=0)
    before = before.drop_duplicates(subset=["cve_id"], keep="first").copy()
    after = after.drop_duplicates(subset=["cve_id"], keep="first").copy()
    before = ensure_binary_fields(before, FIELD_ORDER)
    after = ensure_binary_fields(after, FIELD_ORDER)

    keep_cols = ["cve_id"]
    if "cwe_id" in before.columns:
        keep_cols.append("cwe_id")
    if "description" in before.columns:
        keep_cols.append("description")
    before_part = before[keep_cols + FIELD_ORDER].copy()

    after_cols = ["cve_id"] + (["description"] if "description" in after.columns else []) + FIELD_ORDER
    after_part = after[after_cols].copy()

    paired = before_part.merge(after_part, on="cve_id", how="inner", suffixes=("_before", "_after"))

    summary = pd.DataFrame([
        {"metric": "before_unique_cve", "value": before["cve_id"].nunique()},
        {"metric": "after_unique_cve", "value": after["cve_id"].nunique()},
        {"metric": "paired_cve", "value": paired["cve_id"].nunique()},
        {"metric": "field_count", "value": len(FIELD_ORDER)},
    ])

    write_excel(OUTPUT_FILE, {"summary": summary, "paired_dataset": paired})
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
