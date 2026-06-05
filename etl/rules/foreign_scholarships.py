from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
import unicodedata

import pandas as pd

from etl.config import COUNTRIES_CSV, DEGREES_CSV, INSTITUTIONS_CSV, STANDARD_COLUMNS
from etl.country_utils import ascii_fold, normalize_country_value
from etl.io_utils import empty_standardized_frame, infer_admin_label, utc_now_iso
from etl.normalize import normalize_text, person_key


HEADER_SCAN_ROWS = 12


def _detect_header_row(path: Path, sheet_name: str) -> int:
    preview = pd.read_excel(path, sheet_name=sheet_name, header=None, nrows=HEADER_SCAN_ROWS)
    for idx, row in preview.fillna("").astype(str).iterrows():
        cells = [ascii_fold(cell) for cell in row.tolist()]
        if any("NOMBRE BECARIO" in cell for cell in cells):
            return int(idx)
    return 0


def _clean_columns(columns: list[object]) -> dict[str, str]:
    renamed: dict[str, str] = {}
    for column in columns:
        folded = ascii_fold(column)
        folded = folded.replace(".", "").replace("-", " ")
        folded = re.sub(r"\s+", " ", folded).strip()
        renamed[str(column)] = folded
    return renamed


@lru_cache(maxsize=1)
def _load_country_catalog() -> dict[str, tuple[str, str | None]]:
    catalog = pd.read_csv(COUNTRIES_CSV).fillna("")
    return {
        ascii_fold(row.source_value): (row.canonical_value or row.source_value, row.iso3 or None)
        for row in catalog.itertuples(index=False)
        if str(row.source_value).strip()
    }


@lru_cache(maxsize=1)
def _load_institution_catalog() -> dict[str, str]:
    catalog = pd.read_csv(INSTITUTIONS_CSV).fillna("")
    return {
        ascii_fold(row.source_value): (row.canonical_value or row.source_value)
        for row in catalog.itertuples(index=False)
        if str(row.source_value).strip()
    }


@lru_cache(maxsize=1)
def _load_degree_catalog() -> dict[str, str]:
    catalog = pd.read_csv(DEGREES_CSV).fillna("")
    return {
        ascii_fold(row.source_value): (row.canonical_value or row.source_value)
        for row in catalog.itertuples(index=False)
        if str(row.source_value).strip()
    }


def _pick_first(columns: list[str], *candidates: str) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _find_amount_column(columns: list[str]) -> str | None:
    preferred_patterns = (
        "IMPORTE TOTAL PAGADO ENERO MARZO",
        "IMPORTE TOTAL PAGADO ENERO A MARZO",
        "TOTAL PAGADO ENERO MARZO",
        "TOTAL PAGADO ENERO A MARZO",
        "IMPORTE PAGADO ENERO MARZO",
        "IMPORTE PAGADO ENERO A MARZO",
        "IMPORTE TOTAL PAGADO ENERO DICIEMBRE",
        "IMPORTE TOTAL PAGADO ENERO A DICIEMBRE",
        "TOTAL PAGADO ENERO DICIEMBRE",
        "TOTAL PAGADO ENERO A DICIEMBRE",
        "IMPORTE PAGADO DE ENERO A DICIEMBRE",
        "TOTAL GENERAL",
    )
    for pattern in preferred_patterns:
        for column in columns:
            if pattern in column:
                return column
    fallback_patterns = ("IMPORTE PAGADO", "TOTAL PAGADO", "MONTO PAGADO", "IMPORTE TOTAL")
    for pattern in fallback_patterns:
        for column in columns:
            if pattern in column:
                return column
    return None


def _is_foreign_scope(row: pd.Series) -> bool:
    country = ascii_fold(row.get("country_raw"))
    modality = ascii_fold(row.get("modality_raw"))
    convocatoria = ascii_fold(row.get("convocatoria_raw"))
    if country == "MEXICO":
        return False
    if country and country != "":
        return True
    foreign_markers = ("EXT", "EXTRANJ", "FOREIGN", "CUBA")
    if modality:
        return any(marker in modality for marker in foreign_markers)
    return any(marker in convocatoria for marker in foreign_markers)


def _program_category(modality_raw: object, convocatoria_raw: object, path: Path) -> str:
    modality = ascii_fold(modality_raw)
    convocatoria = ascii_fold(convocatoria_raw)
    file_name = ascii_fold(path.name)
    combined = " ".join((modality, convocatoria, file_name))
    if "SAB" in combined:
        return "estancias_sabaticas_extranjero"
    if "TEC" in combined:
        return "estancias_tecnologicas_extranjero"
    return "becas_extranjero"


def _canonical_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    return text or None


def parse_foreign_scholarship_file(path: Path, snapshot_id: str, source_year: int | None) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return empty_standardized_frame(STANDARD_COLUMNS)

    workbook = pd.ExcelFile(path)
    sheet_name = workbook.sheet_names[0]
    header_row = _detect_header_row(path, sheet_name)
    raw = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    raw = raw.rename(columns=_clean_columns(list(raw.columns)))
    raw = raw.loc[:, ~raw.columns.str.contains(r"^UNNAMED")]

    consec_col = _pick_first(list(raw.columns), "CONSEC")
    name_col = _pick_first(list(raw.columns), "NOMBRE BECARIO")
    start_col = _pick_first(list(raw.columns), "INICIO DE BECA", "INICIO DE BECA")
    end_col = _pick_first(list(raw.columns), "FIN DE BECA", "TERMINO DE BECA")
    degree_col = _pick_first(list(raw.columns), "NIVEL DE ESTUDIOS")
    institution_col = _pick_first(list(raw.columns), "INSTITUCION")
    country_col = _pick_first(list(raw.columns), "PAIS")
    program_col = _pick_first(list(raw.columns), "PROGRAMA DE ESTUDIOS")
    area_col = _pick_first(list(raw.columns), "AREA DEL CONOCIMIENTO")
    convocatoria_col = _pick_first(list(raw.columns), "CONVOCATORIA")
    modality_col = _pick_first(list(raw.columns), "MODALIDAD")
    amount_col = _find_amount_column(list(raw.columns))

    if consec_col is None or name_col is None:
        return empty_standardized_frame(STANDARD_COLUMNS)

    parsed = pd.DataFrame(
        {
            "source_consecutive": pd.to_numeric(raw[consec_col], errors="coerce"),
            "person_name_raw": raw[name_col],
            "start_date_raw": raw[start_col] if start_col else None,
            "end_date_raw": raw[end_col] if end_col else None,
            "degree_raw": raw[degree_col] if degree_col else None,
            "institution_raw": raw[institution_col] if institution_col else None,
            "country_raw": raw[country_col] if country_col else None,
            "study_program_raw": raw[program_col] if program_col else None,
            "knowledge_area_raw": raw[area_col] if area_col else None,
            "convocatoria_raw": raw[convocatoria_col] if convocatoria_col else None,
            "modality_raw": raw[modality_col] if modality_col else None,
            "amount_nominal_mxn": pd.to_numeric(raw[amount_col], errors="coerce") if amount_col else None,
            "row_number_source": raw.index + header_row + 2,
        }
    )
    parsed = parsed[parsed["source_consecutive"].notna()].copy()
    parsed["person_name_raw"] = parsed["person_name_raw"].map(_canonical_text)
    parsed = parsed[parsed["person_name_raw"].notna()].copy()
    parsed["is_foreign_scope_confirmed"] = parsed.apply(_is_foreign_scope, axis=1)
    parsed = parsed[parsed["is_foreign_scope_confirmed"]].copy()

    country_catalog = _load_country_catalog()
    institution_catalog = _load_institution_catalog()
    degree_catalog = _load_degree_catalog()

    parsed["person_name_canonical"] = parsed["person_name_raw"].map(normalize_text)
    parsed["person_name_key"] = parsed["person_name_raw"].map(person_key)
    parsed["country_canonical"] = parsed["country_raw"].map(
        lambda value: normalize_country_value(
            value,
            country_catalog.get(ascii_fold(value), (_canonical_text(value), None))[0],
        )
    )
    parsed["country_iso3"] = parsed["country_raw"].map(
        lambda value: country_catalog.get(ascii_fold(value), (None, None))[1]
    )
    parsed["institution_canonical"] = parsed["institution_raw"].map(
        lambda value: institution_catalog.get(ascii_fold(value), _canonical_text(value))
    )
    parsed["degree_canonical"] = parsed["degree_raw"].map(
        lambda value: degree_catalog.get(ascii_fold(value), _canonical_text(value))
    )
    parsed["program_category"] = parsed.apply(
        lambda row: _program_category(row.get("modality_raw"), row.get("convocatoria_raw"), path),
        axis=1,
    )

    standardized = pd.DataFrame(
        {
            "record_id": parsed["source_consecutive"].map(
                lambda value: f"{snapshot_id}-{int(value)}" if pd.notna(value) else None
            ),
            "snapshot_id": snapshot_id,
            "source_year": source_year,
            "program_category": parsed["program_category"],
            "admin_label": infer_admin_label(path.name),
            "person_name_raw": parsed["person_name_raw"],
            "person_name_canonical": parsed["person_name_canonical"],
            "person_name_key": parsed["person_name_key"],
            "country_raw": parsed["country_raw"].map(_canonical_text),
            "country_canonical": parsed["country_canonical"],
            "country_iso3": parsed["country_iso3"],
            "institution_raw": parsed["institution_raw"].map(_canonical_text),
            "institution_canonical": parsed["institution_canonical"],
            "study_program_raw": parsed["study_program_raw"].map(_canonical_text),
            "knowledge_area_raw": parsed["knowledge_area_raw"].map(_canonical_text),
            "degree_raw": parsed["degree_raw"].map(_canonical_text),
            "degree_canonical": parsed["degree_canonical"],
            "start_date_raw": parsed["start_date_raw"].map(_canonical_text),
            "end_date_raw": parsed["end_date_raw"].map(_canonical_text),
            "amount_nominal_mxn": parsed["amount_nominal_mxn"],
            "currency_raw": "MXN",
            "deflator_base_2020": None,
            "amount_real_mxn_2020": None,
            "source_file_name": path.name,
            "source_file_path": str(path),
            "source_sheet_name": sheet_name,
            "source_url": None,
            "row_number_source": parsed["row_number_source"],
            "normalization_notes": f"header_row={header_row}; amount_column={amount_col}; filtered_foreign_scope=true",
            "duplicate_review_flag": False,
            "is_foreign_scope_confirmed": parsed["is_foreign_scope_confirmed"],
            "load_timestamp_utc": utc_now_iso(),
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in standardized.columns:
            standardized[column] = None
    return standardized[STANDARD_COLUMNS]
