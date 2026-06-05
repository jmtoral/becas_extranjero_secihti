from __future__ import annotations

import re
import unicodedata

import pandas as pd


def normalize_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text.upper()


def person_key(name: object) -> str | None:
    normalized = normalize_text(name)
    if normalized is None:
        return None
    normalized = re.sub(r"[^A-Z0-9 ]", "", normalized)
    return normalized


def conservative_duplicate_flag(frame: pd.DataFrame) -> pd.Series:
    keys = (
        frame["source_year"].astype("string").fillna("")
        + "|"
        + frame["person_name_key"].astype("string").fillna("")
        + "|"
        + frame["program_category"].astype("string").fillna("")
    )
    return keys.duplicated(keep=False)
