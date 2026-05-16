import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import OUTPUT_DIR, PROCESSED_DIR
from common.fields import FIELD_CATEGORY, FIELD_CN, FIELD_ORDER
from common.io_utils import build_source_count_map, source_count_group, write_excel

PAIRED_FILE = OUTPUT_DIR / "rq2_paired_dataset.xlsx"
RQ2_STATS_FILE = OUTPUT_DIR / "rq2_statistical_tests.xlsx"
RQ3_CALIBRATION_FILE = OUTPUT_DIR / "rq3_manual_calibration.xlsx"
SOURCE_JSON = PROCESSED_DIR / "cve_description.json"
OUTPUT_FILE = OUTPUT_DIR / "rq4_bias_input.xlsx"


def main() -> None:
    paired = pd.read_excel(PAIRED_FILE, sheet_name="paired_dataset")
    mcnemar = pd.read_excel(RQ2_STATS_FILE, sheet_name="mcnemar_results") if RQ2_STATS_FILE.exists() else pd.DataFrame()
    rq3_samples = pd.read_excel(RQ3_CALIBRATION_FILE, sheet_name="manual_samples") if RQ3_CALIBRATION_FILE.exists() else pd.DataFrame()
    rq3_field = pd.read_excel(RQ3_CALIBRATION_FILE, sheet_name="by_field") if RQ3_CALIBRATION_FILE.exists() else pd.DataFrame()
    source_map = build_source_count_map(SOURCE_JSON)

    mcnemar_map = mcnemar.set_index("field").to_dict("index") if not mcnemar.empty else {}
    manual_map = rq3_samples.set_index(["cve_id", "field"]).to_dict("index") if not rq3_samples.empty else {}
    field_cal_map = rq3_field.set_index("field").to_dict("index") if not rq3_field.empty else {}

    rows = []
    for _, r in paired.iterrows():
        cve_id = r["cve_id"]
        sc = source_map.get(cve_id)
        for field in FIELD_ORDER:
            before_status = int(r[f"{field}_before"])
            after_status = int(r[f"{field}_after"])
            transition = f"{before_status}→{after_status}"
            manual = manual_map.get((cve_id, field), {})
            attribution = manual.get("attribution_type", "")
            if attribution == "D":
                error_type = "E1_field_existence_false_negative"
                error_source = "rq3_manual_review"
            elif attribution == "C":
                error_type = "E2_or_E4_granularity_mismatch"
                error_source = "rq3_manual_review"
            elif attribution == "B":
                error_type = "E4_boundary_uncertainty"
                error_source = "rq3_manual_review"
            elif attribution == "A":
                error_type = "true_residual_not_method_error"
                error_source = "rq3_manual_review"
            elif transition == "1→0":
                error_type = "E5_abnormal_drop_to_review"
                error_source = "rq2_transition"
            else:
                error_type = ""
                error_source = ""
            stats = mcnemar_map.get(field, {})
            cal = field_cal_map.get(field, {})
            rows.append({
                "cve_id": cve_id,
                "field": field,
                "field_zh": FIELD_CN[field],
                "category": FIELD_CATEGORY[field],
                "before_status": before_status,
                "after_status": after_status,
                "transition": transition,
                "source_count": sc,
                "source_count_group": source_count_group(sc),
                "is_n10_transition": transition == "1→0",
                "is_rq3_manual_sample": bool(manual),
                "manual_after_status": manual.get("manual_after_status", ""),
                "attribution_type": attribution,
                "rq4_error_type": error_type,
                "error_source": error_source,
                "field_auto_residual": cal.get("residual_miss", ""),
                "field_calibrated_strict_residual": cal.get("calibrated_strict_residual", ""),
                "gain": stats.get("gain", ""),
                "drop_rate": stats.get("drop_rate", ""),
                "mcnemar_p_exact": stats.get("mcnemar_p_exact", ""),
            })

    bias = pd.DataFrame(rows)
    summary = pd.DataFrame([
        {"metric": "paired_cve", "value": paired["cve_id"].nunique()},
        {"metric": "field_count", "value": len(FIELD_ORDER)},
        {"metric": "bias_table_rows", "value": len(bias)},
        {"metric": "transition_0_to_0", "value": int((bias["transition"] == "0→0").sum())},
        {"metric": "transition_0_to_1", "value": int((bias["transition"] == "0→1").sum())},
        {"metric": "transition_1_to_0", "value": int((bias["transition"] == "1→0").sum())},
        {"metric": "transition_1_to_1", "value": int((bias["transition"] == "1→1").sum())},
        {"metric": "rq3_manual_samples_linked", "value": int(bias["is_rq3_manual_sample"].sum())},
    ])

    meta = pd.DataFrame([{"field": f, "field_zh": FIELD_CN[f], "category": FIELD_CATEGORY[f]} for f in FIELD_ORDER])
    write_excel(OUTPUT_FILE, {"summary": summary, "bias_input": bias, "field_metadata": meta})
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
