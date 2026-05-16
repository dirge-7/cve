# -*- coding: utf-8 -*-
"""Path utilities. All scripts use project-relative paths by default."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = ROOT_DIR / "outputs"

for _path in (RAW_DIR, PROCESSED_DIR, OUTPUT_DIR):
    _path.mkdir(parents=True, exist_ok=True)
