import math
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from common.config import OUTPUT_DIR
from common.io_utils import write_excel

FIELD_FILE = OUTPUT_DIR / "rq2_field_metrics.xlsx"
CATEGORY_FILE = OUTPUT_DIR / "rq2_category_metrics.xlsx"
SAMPLE_FILE = OUTPUT_DIR / "rq2_sample_metrics.xlsx"
OUTPUT_FILE = OUTPUT_DIR / "rq2_confidence_intervals.xlsx"
BOOTSTRAP_N = 5000
RANDOM_SEED = 20260424


def wilson_ci(x: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = x / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return center - half, center + half


def main() -> None:
    rng = np.random.default_rng(RANDOM_SEED)
    field = pd.read_excel(FIELD_FILE, sheet_name="field_metrics")
    cat = pd.read_excel(CATEGORY_FILE, sheet_name="category_metrics")
    cat_gain_dist = pd.read_excel(CATEGORY_FILE, sheet_name="category_sample_gain")
    sample = pd.read_excel(SAMPLE_FILE, sheet_name="sample_metrics")

    field_rows = []
    for _, r in field.iterrows():
        n00, n01, n10, n11 = map(int, [r["n00"], r["n01"], r["n10"], r["n11"]])
        n = int(r["paired_n"])
        diff = np.array([-1] * n10 + [0] * (n00 + n11) + [1] * n01)
        boot = rng.choice(diff, size=(BOOTSTRAP_N, n), replace=True).mean(axis=1)
        gain_lo, gain_hi = np.quantile(boot, [0.025, 0.975])
        fill_lo, fill_hi = wilson_ci(n01, n00 + n01)
        residual_lo, residual_hi = wilson_ci(n00 + n10, n)
        drop_lo, drop_hi = wilson_ci(n10, n10 + n11)
        field_rows.append({
            "field": r["field"],
            "field_zh": r["field_zh"],
            "gain": r["gain"],
            "gain_ci95_low": gain_lo,
            "gain_ci95_high": gain_hi,
            "fill_rate": r["fill_rate"],
            "fill_rate_ci95_low": fill_lo,
            "fill_rate_ci95_high": fill_hi,
            "residual_miss": r["residual_miss"],
            "residual_miss_ci95_low": residual_lo,
            "residual_miss_ci95_high": residual_hi,
            "drop_rate": r["drop_rate"],
            "drop_rate_ci95_low": drop_lo,
            "drop_rate_ci95_high": drop_hi,
        })

    cat_rows = []
    for _, r in cat.iterrows():
        dist = cat_gain_dist[cat_gain_dist["category"] == r["category"]]
        gains = np.repeat(dist["sample_field_gain"].to_numpy(), dist["sample_count"].to_numpy().astype(int))
        boot = rng.choice(gains, size=(BOOTSTRAP_N, len(gains)), replace=True).mean(axis=1) / int(r["field_count"])
        lo, hi = np.quantile(boot, [0.025, 0.975])
        cat_rows.append({
            "category": r["category"],
            "gain": r["gain"],
            "gain_ci95_low": lo,
            "gain_ci95_high": hi,
            "avg_sample_field_gain": r["avg_sample_field_gain"],
        })

    sample_gain = sample["sample_gain"].to_numpy()
    boot = rng.choice(sample_gain, size=(BOOTSTRAP_N, len(sample_gain)), replace=True).mean(axis=1)
    sample_ci = pd.DataFrame([{
        "paired_samples": len(sample_gain),
        "mean_sample_gain": float(sample_gain.mean()),
        "mean_sample_gain_ci95_low": float(np.quantile(boot, 0.025)),
        "mean_sample_gain_ci95_high": float(np.quantile(boot, 0.975)),
        "median_sample_gain": float(np.median(sample_gain)),
    }])

    write_excel(OUTPUT_FILE, {
        "field_ci": pd.DataFrame(field_rows),
        "category_ci": pd.DataFrame(cat_rows),
        "sample_ci": sample_ci,
    })
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
