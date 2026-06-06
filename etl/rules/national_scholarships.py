from __future__ import annotations

from pathlib import Path

import pandas as pd

from etl.config import COUNTRIES_CSV, DEGREES_CSV, INSTITUTIONS_CSV, STANDARD_COLUMNS
from etl.country_utils import ascii_fold, normalize_country_value
from etl.io_utils import empty_standardized_frame, infer_admin_label, utc_now_iso
from etl.normalize import normalize_text, person_key
from etl.rules.foreign_scholarships import (
    _canonical_text,
    _clean_columns,
    _detect_header_row,
    _find_amount_column,
    _load_degree_catalog,
    _load_institution_catalog,
    _pick_first,
)


def _normalize_entity_value(value: object) -> str | None:
    text = _canonical_text(value)
    if text is None:
        return None
    folded = ascii_fold(text)
    aliases = {
        "AGUASCALIENTES": "Aguascalientes",
        "BAJA CALIFORNIA": "Baja California",
        "BAJA CALIFORNIA SUR": "Baja California Sur",
        "CAMPECHE": "Campeche",
        "CHIAPAS": "Chiapas",
        "CHIHUAHUA": "Chihuahua",
        "CIUDAD DE MEXICO": "Ciudad de México",
        "CDMX": "Ciudad de México",
        "COAHUILA": "Coahuila",
        "COLIMA": "Colima",
        "DISTRITO FEDERAL": "Ciudad de México",
        "DURANGO": "Durango",
        "ESTADO DE MEXICO": "Estado de México",
        "GUANAJUATO": "Guanajuato",
        "GUERRERO": "Guerrero",
        "HIDALGO": "Hidalgo",
        "JALISCO": "Jalisco",
        "MEXICO": "Estado de México",
        "MICHOACAN": "Michoacán",
        "MORELOS": "Morelos",
        "NAYARIT": "Nayarit",
        "NUEVO LEON": "Nuevo León",
        "OAXACA": "Oaxaca",
        "PUEBLA": "Puebla",
        "QUERETARO": "Querétaro",
        "QUINTANA ROO": "Quintana Roo",
        "SAN LUIS POTOSI": "San Luis Potosí",
        "SINALOA": "Sinaloa",
        "SONORA": "Sonora",
        "TABASCO": "Tabasco",
        "TAMAULIPAS": "Tamaulipas",
        "TLAXCALA": "Tlaxcala",
        "VERACRUZ": "Veracruz",
        "YUCATAN": "Yucatán",
        "ZACATECAS": "Zacatecas",
    }
    return aliases.get(folded, text.title())


def _is_excluded_national_type(row: pd.Series, path: Path) -> bool:
    modality = ascii_fold(row.get("modality_raw"))
    convocatoria = ascii_fold(row.get("convocatoria_raw"))
    file_name = ascii_fold(path.name)
    combined = " ".join((modality, convocatoria, file_name))
    return any(marker in combined for marker in ("POSDOC", "POSDOCTOR", "SABAT", "REPATRIA"))


def _is_national_scope(row: pd.Series, path: Path) -> bool:
    if _is_excluded_national_type(row, path):
        return False

    country = ascii_fold(row.get("country_raw"))
    modality = ascii_fold(row.get("modality_raw"))
    convocatoria = ascii_fold(row.get("convocatoria_raw"))
    file_name = ascii_fold(path.name)

    if country == "MEXICO":
        return True
    if country and country != "":
        return False

    if "NACIONAL" in file_name or "BNAC" in file_name:
        return True

    national_markers = ("NAC", "NACIONAL", "MEXICO")
    if modality:
        return any(marker in modality for marker in national_markers)
    return any(marker in convocatoria for marker in national_markers)


def parse_national_scholarship_file(path: Path, snapshot_id: str, source_year: int | None) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return empty_standardized_frame(STANDARD_COLUMNS)

    workbook = pd.ExcelFile(path)
    sheet_name = workbook.sheet_names[0]
    header_row = _detect_header_row(path, sheet_name)
    raw = pd.read_excel(path, sheet_name=sheet_name, header=header_row)
    raw = raw.rename(columns=_clean_columns(list(raw.columns)))
    raw = raw.loc[:, ~raw.columns.str.contains(r"^UNNAMED")]

    consec_col = _pick_first(list(raw.columns), "CONSEC", "CONSEC.")
    name_col = _pick_first(list(raw.columns), "NOMBRE BECARIO", "NOMBRE")
    start_col = _pick_first(list(raw.columns), "INICIO DE BECA", "INICIO BECA")
    end_col = _pick_first(list(raw.columns), "FIN DE BECA", "FIN BECA", "TERMINO DE BECA")
    degree_col = _pick_first(list(raw.columns), "NIVEL DE ESTUDIOS")
    institution_col = _pick_first(list(raw.columns), "INSTITUCION")
    country_col = _pick_first(list(raw.columns), "PAIS")
    entity_col = _pick_first(list(raw.columns), "ENTIDAD")
    program_col = _pick_first(list(raw.columns), "PROGRAMA DE ESTUDIOS", "PROGRAMA")
    area_col = _pick_first(list(raw.columns), "AREA DEL CONOCIMIENTO", "AREA S N I", "AREA SNI")
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
            "country_raw": raw[country_col] if country_col else "MEXICO",
            "entity_raw": raw[entity_col] if entity_col else None,
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
    parsed["is_national_scope_confirmed"] = parsed.apply(lambda row: _is_national_scope(row, path), axis=1)
    parsed = parsed[parsed["is_national_scope_confirmed"]].copy()

    institution_catalog = _load_institution_catalog()
    degree_catalog = _load_degree_catalog()

    parsed["person_name_canonical"] = parsed["person_name_raw"].map(normalize_text)
    parsed["person_name_key"] = parsed["person_name_raw"].map(person_key)
    parsed["country_canonical"] = parsed["country_raw"].map(
        lambda value: normalize_country_value(value, "México")
    )
    parsed["country_iso3"] = "MEX"
    parsed["entity_canonical"] = parsed["entity_raw"].map(_normalize_entity_value)
    parsed["institution_canonical"] = parsed["institution_raw"].map(
        lambda value: institution_catalog.get(ascii_fold(value), _canonical_text(value))
    )
    parsed["degree_canonical"] = parsed["degree_raw"].map(
        lambda value: degree_catalog.get(ascii_fold(value), _canonical_text(value))
    )

    standardized = pd.DataFrame(
        {
            "record_id": parsed["source_consecutive"].map(
                lambda value: f"{snapshot_id}-{int(value)}" if pd.notna(value) else None
            ),
            "snapshot_id": snapshot_id,
            "source_year": source_year,
            "program_category": "becas_nacionales",
            "admin_label": infer_admin_label(path.name),
            "person_name_raw": parsed["person_name_raw"],
            "person_name_canonical": parsed["person_name_canonical"],
            "person_name_key": parsed["person_name_key"],
            "country_raw": parsed["country_raw"].map(_canonical_text),
            "country_canonical": parsed["country_canonical"],
            "country_iso3": parsed["country_iso3"],
            "entity_raw": parsed["entity_raw"].map(_canonical_text),
            "entity_canonical": parsed["entity_canonical"],
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
            "normalization_notes": f"header_row={header_row}; amount_column={amount_col}; filtered_national_scope=true",
            "duplicate_review_flag": False,
            "is_foreign_scope_confirmed": False,
            "load_timestamp_utc": utc_now_iso(),
        }
    )

    for column in STANDARD_COLUMNS:
        if column not in standardized.columns:
            standardized[column] = None
    return standardized[STANDARD_COLUMNS]
