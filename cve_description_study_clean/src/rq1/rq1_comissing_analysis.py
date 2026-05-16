import itertools
import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.config import PROCESSED_DIR, OUTPUT_DIR
from common.fields import FIELD_CATEGORY, FIELD_CN, FIELD_ORDER
from common.io_utils import ensure_binary_fields, read_excel_auto, write_excel

INPUT_FILE = PROCESSED_DIR / "5000cve_before.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq1_comissing_analysis.xlsx"


def main() -> None:
    df = read_excel_auto(INPUT_FILE, sheet_name=0)
    df = df.drop_duplicates(subset=["cve_id"], keep="first").copy()
    df = ensure_binary_fields(df, FIELD_ORDER)
    n = len(df)
    missing = 1 - df[FIELD_ORDER]

    rows = []
    for f1, f2 in itertools.combinations(FIELD_ORDER, 2):
        a = missing[f1].to_numpy()
        b = missing[f2].to_numpy()
        n11 = int(((a == 1) & (b == 1)).sum())
        n10 = int(((a == 1) & (b == 0)).sum())
        n01 = int(((a == 0) & (b == 1)).sum())
        n00 = int(((a == 0) & (b == 0)).sum())
        denom = math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
        phi = (n11 * n00 - n10 * n01) / denom if denom else 0
        jaccard = n11 / (n11 + n10 + n01) if (n11 + n10 + n01) else 0
        rows.append({
            "field1": f1,
            "field1_zh": FIELD_CN[f1],
            "category1": FIELD_CATEGORY[f1],
            "field2": f2,
            "field2_zh": FIELD_CN[f2],
            "category2": FIELD_CATEGORY[f2],
            "comissing_n": n11,
            "comissing_rate": n11 / n if n else 0,
            "comissing_jaccard": jaccard,
            "comissing_phi": phi,
            "n11_comissing": n11,
            "n10_field1_missing_field2_present": n10,
            "n01_field1_present_field2_missing": n01,
            "n00_copresent": n00,
        })

    pair_df = pd.DataFrame(rows).sort_values("comissing_phi", ascending=False)
    labels = [FIELD_CN[f] for f in FIELD_ORDER]
    phi_matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
    rate_matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
    lookup = {(r.field1, r.field2): r for r in pair_df.itertuples(index=False)}
    lookup.update({(r.field2, r.field1): r for r in pair_df.itertuples(index=False)})
    for f1 in FIELD_ORDER:
        for f2 in FIELD_ORDER:
            if f1 == f2:
                phi_matrix.loc[FIELD_CN[f1], FIELD_CN[f2]] = 1.0
                rate_matrix.loc[FIELD_CN[f1], FIELD_CN[f2]] = float(missing[f1].mean())
            else:
                r = lookup[(f1, f2)]
                phi_matrix.loc[FIELD_CN[f1], FIELD_CN[f2]] = r.comissing_phi
                rate_matrix.loc[FIELD_CN[f1], FIELD_CN[f2]] = r.comissing_rate

    write_excel(OUTPUT_FILE, {
        "top_phi_pairs": pair_df.head(50),
        "all_field_pairs": pair_df,
        "phi_matrix": phi_matrix.reset_index(names="field"),
        "comissing_rate_matrix": rate_matrix.reset_index(names="field"),
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
