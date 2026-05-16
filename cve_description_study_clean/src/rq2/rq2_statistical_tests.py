import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from scipy.stats import binomtest
from common.config import OUTPUT_DIR
from common.fields import FIELD_CN, FIELD_CATEGORY, FIELD_ORDER
from common.io_utils import write_excel

INPUT_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq2_statistical_tests.xlsx"


def main() -> None:
    paired = pd.read_excel(INPUT_FILE, sheet_name="paired_dataset")
    field_rows = []
    drop_rows = []

    for field in FIELD_ORDER:
        b = paired[f"{field}_before"].fillna(0).astype(int)
        a = paired[f"{field}_after"].fillna(0).astype(int)
        n00 = int(((b == 0) & (a == 0)).sum())
        n01 = int(((b == 0) & (a == 1)).sum())
        n10 = int(((b == 1) & (a == 0)).sum())
        n11 = int(((b == 1) & (a == 1)).sum())
        discordant = n01 + n10
        p_value = binomtest(min(n01, n10), n=discordant, p=0.5, alternative="two-sided").pvalue if discordant else 1.0
        field_rows.append({
            "field": field,
            "field_zh": FIELD_CN[field],
            "category": FIELD_CATEGORY[field],
            "n00": n00,
            "n01": n01,
            "n10": n10,
            "n11": n11,
            "before_complete": float(b.mean()),
            "after_complete": float(a.mean()),
            "gain": float(a.mean() - b.mean()),
            "fill_rate": n01 / (n00 + n01) if (n00 + n01) else None,
            "residual_miss": float((a == 0).mean()),
            "drop_rate": n10 / (n10 + n11) if (n10 + n11) else None,
            "mcnemar_p_exact": p_value,
            "significant_005": p_value < 0.05,
            "discordant": discordant,
        })
        mask = (b == 1) & (a == 0)
        for _, row in paired.loc[mask].iterrows():
            drop_rows.append({
                "cve_id": row["cve_id"],
                "field": field,
                "field_zh": FIELD_CN[field],
                "category": FIELD_CATEGORY[field],
            })

    field_df = pd.DataFrame(field_rows).sort_values("gain", ascending=False)
    summary = pd.DataFrame([
        {"metric": "paired_samples", "value": len(paired)},
        {"metric": "tested_fields", "value": len(field_df)},
        {"metric": "significant_fields_p005", "value": int(field_df["significant_005"].sum())},
        {"metric": "fields_with_n10", "value": int((field_df["n10"] > 0).sum())},
        {"metric": "total_n10", "value": int(field_df["n10"].sum())},
    ])
    write_excel(OUTPUT_FILE, {
        "summary": summary,
        "mcnemar_results": field_df,
        "abnormal_drop_fields": field_df[field_df["n10"] > 0],
        "abnormal_drop_samples": pd.DataFrame(drop_rows),
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
