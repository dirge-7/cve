# -*- coding: utf-8 -*-
"""Reusable I/O helpers."""
from __future__ import annotations

import json
import re
from json import JSONDecoder
from pathlib import Path
from typing import Iterable

import pandas as pd


def read_excel_auto(path: Path, sheet_name=0) -> pd.DataFrame:
    """Read an Excel sheet and raise a clear error if the file is missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return pd.read_excel(path, sheet_name=sheet_name)


def ensure_binary_fields(df: pd.DataFrame, fields: Iterable[str]) -> pd.DataFrame:
    """Convert field columns to clean 0/1 integers."""
    out = df.copy()
    for field in fields:
        if field not in out.columns:
            raise KeyError(f"Missing required field column: {field}")
        out[field] = pd.to_numeric(out[field], errors="coerce").fillna(0).astype(int).clip(0, 1)
    return out


def parse_mixed_json_objects(path: Path) -> list[dict]:
    """Parse a JSON file that may be a list or concatenated JSON objects."""
    path = Path(path)
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, list) else [obj]
    except json.JSONDecodeError:
        pass

    decoder = JSONDecoder()
    objects = []
    idx = 0
    while idx < len(text):
        while idx < len(text) and text[idx] in " \t\r\n,[]":
            idx += 1
        if idx >= len(text):
            break
        if text[idx] != "{":
            nxt = text.find("{", idx + 1)
            if nxt == -1:
                break
            idx = nxt
        try:
            obj, end = decoder.raw_decode(text, idx)
            if isinstance(obj, dict):
                objects.append(obj)
            elif isinstance(obj, list):
                objects.extend(x for x in obj if isinstance(x, dict))
            idx = end
        except json.JSONDecodeError:
            nxt = text.find("{", idx + 1)
            if nxt == -1:
                break
            idx = nxt
    return objects


def build_source_count_map(path: Path) -> dict[str, int]:
    """Return {cve_id: number_of_sources} from cve_description.json."""
    source_map = {}
    for item in parse_mixed_json_objects(path):
        cve_id = item.get("cve_id")
        if not cve_id:
            continue
        sources = item.get("sources") or []
        source_map[cve_id] = len(sources) if isinstance(sources, list) else 0
    return source_map


def source_count_group(value) -> str:
    if pd.isna(value):
        return ""
    try:
        value = int(value)
    except Exception:
        return ""
    if value <= 2:
        return "1-2个来源"
    if value <= 4:
        return "3-4个来源"
    return "≥5个来源"


def write_excel(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    """Write multiple dataframes to Excel using openpyxl."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            safe = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe, index=False)
