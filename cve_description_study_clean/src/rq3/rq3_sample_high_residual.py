import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import OUTPUT_DIR
from common.fields import FIELD_CN, FIELD_CATEGORY
from common.io_utils import write_excel

RESIDUAL_FILE = OUTPUT_DIR / "rq3_residual_metrics.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq3_high_residual_samples.xlsx"
RANDOM_SEED = 20260508
SAMPLES_PER_FIELD = 10


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    after_status = pd.read_excel(RESIDUAL_FILE, sheet_name="after_status")
    high_fields = pd.read_excel(RESIDUAL_FILE, sheet_name="high_residual_fields")

    selected_rows = []
    summary_rows = []
    used_pairs = set()

    for _, row in high_fields.iterrows():
        field = row["field"]
        candidates = after_status[after_status[field].fillna(0).astype(int) == 0].copy()
        candidate_indices = list(candidates.index)
        rng.shuffle(candidate_indices)
        chosen = candidate_indices[:SAMPLES_PER_FIELD]
        summary_rows.append({
            "field": field,
            "field_zh": FIELD_CN.get(field, field),
            "category": FIELD_CATEGORY.get(field, ""),
            "candidate_after0_n": len(candidates),
            "sample_n": len(chosen),
        })
        for idx in chosen:
            rec = after_status.loc[idx]
            pair = (rec["cve_id"], field)
            if pair in used_pairs:
                continue
            used_pairs.add(pair)
            selected_rows.append({
                "category": FIELD_CATEGORY.get(field, ""),
                "field": field,
                "field_zh": FIELD_CN.get(field, field),
                "cve_id": rec["cve_id"],
                "cwe_id": rec.get("cwe_id", ""),
                "source_count": rec.get("source_count", ""),
                "source_count_group": rec.get("source_count_group", ""),
                "auto_after_status": 0,
                "manual_after_status": "",
                "attribution_type": "",
                "evidence_text": "",
                "comment": "",
            })

    write_excel(OUTPUT_FILE, {
        "sample_summary": pd.DataFrame(summary_rows),
        "manual_review_samples": pd.DataFrame(selected_rows),
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
