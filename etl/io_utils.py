from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Iterable

import pandas as pd
from slugify import slugify

from etl.config import RAW_DIR


FOREIGN_KEYWORDS = ("extranjero", "foreign", "abroad", "bext", "internacional")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def discover_source_files(root: Path = RAW_DIR) -> list[Path]:
    patterns = ("*.xls", "*.xlsx", "*.csv")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(path for path in root.rglob(pattern) if not path.name.startswith("~$")))
    return files


def infer_year_from_name(file_name: str) -> int | None:
    matches = re.findall(r"(19\d{2}|20\d{2})", file_name)
    if not matches:
        return None
    return int(matches[-1])


def infer_admin_label(file_name: str) -> str:
    lowered = file_name.lower()
    if "secihti" in lowered:
        return "Secihti"
    if "conahcyt" in lowered:
        return "Conahcyt"
    return "Conacyt/Conahcyt/Secihti"


def infer_program_hint(file_name: str) -> str:
    lowered = file_name.lower()
    if "extranj" in lowered or "bext" in lowered:
        return "becas_extranjero"
    if "posdoctor" in lowered and "extranj" in lowered:
        return "estancias_posdoctorales_extranjero"
    if "sabatic" in lowered:
        return "estancias_sabaticas"
    if "s190" in lowered:
        return "s190_mixto"
    return "desconocido"


def is_foreign_candidate(file_name: str) -> bool:
    lowered = file_name.lower()
    return any(keyword in lowered for keyword in FOREIGN_KEYWORDS) or "s190" in lowered


def infer_coverage_label(file_name: str) -> str | None:
    lowered = file_name.lower()
    if (
        "enero_a_marzo" in lowered
        or "enero-marzo" in lowered
        or "enero_marzo" in lowered
        or "ene-mar" in lowered
        or "ene_mar" in lowered
    ):
        return "Enero-Marzo"
    if (
        "enero_a_diciembre" in lowered
        or "enero-diciembre" in lowered
        or "enero_diciembre" in lowered
        or "ene-dic" in lowered
        or "ene_dic" in lowered
    ):
        return "Enero-Diciembre"
    return None


def is_partial_coverage(file_name: str) -> bool:
    coverage = infer_coverage_label(file_name)
    return coverage is not None and coverage != "Enero-Diciembre"


def build_snapshot_id(path: Path) -> str:
    stem = slugify(path.stem, separator="-")
    year = infer_year_from_name(path.name) or "na"
    return f"{year}-{stem}"


def empty_standardized_frame(columns: Iterable[str]) -> pd.DataFrame:
    return pd.DataFrame({column: pd.Series(dtype="object") for column in columns})
