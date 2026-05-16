# -*- coding: utf-8 -*-
"""Run the non-manual parts of the analysis pipeline."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "src/rq1/rq1_field_metrics.py",
    "src/rq1/rq1_category_metrics.py",
    "src/rq1/rq1_comissing_analysis.py",
    "src/rq2/rq2_build_paired_dataset.py",
    "src/rq2/rq2_field_metrics.py",
    "src/rq2/rq2_category_metrics.py",
    "src/rq2/rq2_sample_metrics.py",
    "src/rq2/rq2_statistical_tests.py",
    "src/rq2/rq2_confidence_intervals.py",
    "src/rq3/rq3_residual_metrics.py",
    "src/rq3/rq3_sample_high_residual.py",
]

for script in SCRIPTS:
    print(f"Running {script}")
    subprocess.run([sys.executable, str(ROOT / script)], check=True)
