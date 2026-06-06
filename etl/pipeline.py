from __future__ import annotations

import json
from pathlib import Path
import re

import pandas as pd

from etl.config import (
    ANALYSIS_COUNTRY_YEAR_CSV,
    ANALYSIS_COUNTRY_CSV,
    ANALYSIS_DEGREE_YEAR_CSV,
    ANALYSIS_INSTITUTION_CSV,
    ANALYSIS_INSTITUTION_YEAR_CSV,
    ANALYSIS_KNOWLEDGE_AREA_YEAR_CSV,
    ANALYSIS_NATIONAL_DEGREE_YEAR_CSV,
    ANALYSIS_NATIONAL_ENTITY_CSV,
    ANALYSIS_NATIONAL_ENTITY_YEAR_CSV,
    ANALYSIS_NATIONAL_INSTITUTION_CSV,
    ANALYSIS_NATIONAL_INSTITUTION_YEAR_CSV,
    ANALYSIS_NATIONAL_KNOWLEDGE_AREA_YEAR_CSV,
    ANALYSIS_NATIONAL_YEARLY_CSV,
    ANALYSIS_NATIONAL_YEAR_METADATA_CSV,
    ANALYSIS_YEAR_METADATA_CSV,
    ANALYSIS_YEARLY_CSV,
    DEFLATORS_CSV,
    INVENTORY_CSV,
    INVENTORY_PARQUET,
    SITE_DATA_DIR,
    SITE_SUMMARY_JSON,
    SITE_SUMMARY_JS,
    SITE_SUMMARY_NATIONAL_JSON,
    SITE_SUMMARY_NATIONAL_JS,
    STANDARD_COLUMNS,
    STANDARDIZED_CSV,
    STANDARDIZED_NATIONAL_CSV,
    STANDARDIZED_NATIONAL_PARQUET,
    STANDARDIZED_PARQUET,
    ensure_directories,
)
from etl.country_utils import ascii_fold, get_country_map_code
from etl.io_utils import (
    build_snapshot_id,
    discover_source_files,
    infer_admin_label,
    infer_coverage_label,
    infer_program_hint,
    infer_year_from_name,
    is_foreign_candidate,
    is_national_candidate,
    is_partial_coverage,
    utc_now_iso,
)
from etl.normalize import conservative_duplicate_flag
from etl.rules.foreign_scholarships import parse_foreign_scholarship_file
from etl.rules.national_scholarships import parse_national_scholarship_file

INVENTORY_COLUMNS = [
    "snapshot_id",
    "source_file_name",
    "source_file_path",
    "file_extension",
    "source_year",
    "program_hint",
    "admin_label",
    "is_foreign_candidate",
    "is_national_candidate",
    "coverage_label",
    "is_partial_period",
    "ingestion_notes",
    "load_timestamp_utc",
]


def log_status(message: str) -> None:
    print(f"[pipeline] {message}", flush=True)


def _format_int(value: int) -> str:
    return f"{value:,}"


def _format_money(value: float) -> str:
    return f"{value:,.2f}"


def normalize_knowledge_area_label(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    if not text or text.lower() == "nan":
        return None
    folded = ascii_fold(text)
    folded = re.sub(r"^[IVXLCM]+\.\s*", "", folded)
    area_map = {
        "INGENIERIAS": "Ingenierías",
        "CIENCIAS SOCIALES": "Ciencias sociales",
        "MEDICINA Y CS. DE LA SALUD": "Medicina y salud",
        "HUMANIDADES Y CS. DE LA CONDUCTA": "Humanidades y conducta",
        "BIOLOGIA Y QUIMICA": "Biología y química",
        "FISICO MATEMATICAS Y CS. DE LA TIERRA": "Físico-matemáticas y ciencias de la Tierra",
        "BIOTECNOLOGIA Y CS. AGROPECUARIAS": "Biotecnología y agropecuarias",
        "HUMANIDADES": "Humanidades",
        "CIENCIAS DE AGRICULTURA, AGROPECUARIAS, FORESTALES Y DE ECOSISTEMAS": "Agropecuarias y ecosistemas",
        "CIENCIAS DE LA CONDUCTA Y LA EDUCACION": "Conducta y educación",
    }
    return area_map.get(folded, text)


def normalize_degree_series_label(value: object) -> str | None:
    text = str(value).strip() if value is not None else ""
    if not text or text.lower() == "nan":
        return None
    folded = ascii_fold(text)
    if "DOC" in folded or "DOCTOR" in folded:
        return "Doctorado"
    if "MAE" in folded or "MAESTR" in folded:
        return "Maestría"
    if "ESP" in folded or "ESPECIAL" in folded:
        return "Especialidad"
    if "SABAT" in folded:
        return "Sabática"
    if "TECNIC" in folded or "EST TEC" in folded:
        return "Estancia técnica"
    if "POSDOC" in folded:
        return "Posdoctoral"
    if "LIC" in folded:
        return "Licenciatura"
    return text


def build_inventory(source_files: list[Path]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in source_files:
        rows.append(
            {
                "snapshot_id": build_snapshot_id(path),
                "source_file_name": path.name,
                "source_file_path": str(path),
                "file_extension": path.suffix.lower(),
                "source_year": infer_year_from_name(path.name),
                "program_hint": infer_program_hint(path.name),
                "admin_label": infer_admin_label(path.name),
                "is_foreign_candidate": is_foreign_candidate(path.name),
                "is_national_candidate": is_national_candidate(path.name),
                "coverage_label": infer_coverage_label(path.name),
                "is_partial_period": is_partial_coverage(path.name),
                "ingestion_notes": "",
                "load_timestamp_utc": utc_now_iso(),
            }
        )
    return pd.DataFrame(rows, columns=INVENTORY_COLUMNS)


def compute_real_amounts(frame: pd.DataFrame, deflators: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    merged = frame.merge(deflators, left_on="source_year", right_on="year", how="left")
    existing_deflator = (
        merged["deflator_base_2020_x"]
        if "deflator_base_2020_x" in merged.columns
        else pd.Series(index=merged.index, dtype="float64")
    )
    merged["deflator_base_2020"] = merged["deflator_base_2020_y"].combine_first(existing_deflator)
    merged["amount_real_mxn_2020"] = (
        pd.to_numeric(merged["amount_nominal_mxn"], errors="coerce")
        * 100.0
        / pd.to_numeric(merged["deflator_base_2020"], errors="coerce")
    )
    drop_columns = [column for column in ("year", "deflator_base_2020_x", "deflator_base_2020_y") if column in merged]
    return merged.drop(columns=drop_columns)


def standardize_foreign_scholarships(inventory: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    candidates = inventory[inventory["is_foreign_candidate"]].copy()
    log_status(
        f"Processing { _format_int(len(candidates)) } foreign-scholarship candidate file(s)."
    )
    for idx, row in enumerate(candidates.itertuples(index=False), start=1):
        path = Path(row.source_file_path)
        log_status(f"[{idx}/{len(candidates)}] Reading {path.name}")
        try:
            parsed = parse_foreign_scholarship_file(path, row.snapshot_id, row.source_year)
        except Exception as exc:  # pragma: no cover - keeps the pipeline audit-friendly
            log_status(f"[{idx}/{len(candidates)}] Failed to parse {path.name}: {exc}")
            parsed = pd.DataFrame(
                [
                    {
                        "record_id": None,
                        "snapshot_id": row.snapshot_id,
                        "source_year": row.source_year,
                        "program_category": row.program_hint,
                        "admin_label": row.admin_label,
                        "source_file_name": path.name,
                        "source_file_path": str(path),
                        "normalization_notes": f"Lectura fallida: {exc}",
                        "is_foreign_scope_confirmed": False,
                        "load_timestamp_utc": utc_now_iso(),
                    }
                ]
            )
        if not parsed.empty:
            log_status(f"[{idx}/{len(candidates)}] Extracted { _format_int(len(parsed)) } row(s)")
            frames.append(parsed)
        else:
            log_status(f"[{idx}/{len(candidates)}] No usable rows extracted")
    if not frames:
        return pd.DataFrame(columns=STANDARD_COLUMNS)
    standardized = pd.concat(frames, ignore_index=True)
    for column in STANDARD_COLUMNS:
        if column not in standardized.columns:
            standardized[column] = None
    standardized = standardized[STANDARD_COLUMNS]
    standardized["duplicate_review_flag"] = conservative_duplicate_flag(standardized)
    return standardized


def standardize_national_scholarships(inventory: pd.DataFrame) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    candidates = inventory[inventory["is_national_candidate"]].copy()
    log_status(
        f"Processing { _format_int(len(candidates)) } national-scholarship candidate file(s)."
    )
    for idx, row in enumerate(candidates.itertuples(index=False), start=1):
        path = Path(row.source_file_path)
        log_status(f"[N {idx}/{len(candidates)}] Reading {path.name}")
        try:
            parsed = parse_national_scholarship_file(path, row.snapshot_id, row.source_year)
        except Exception as exc:  # pragma: no cover - keeps the pipeline audit-friendly
            log_status(f"[N {idx}/{len(candidates)}] Failed to parse {path.name}: {exc}")
            parsed = pd.DataFrame(
                [
                    {
                        "record_id": None,
                        "snapshot_id": row.snapshot_id,
                        "source_year": row.source_year,
                        "program_category": row.program_hint,
                        "admin_label": row.admin_label,
                        "source_file_name": path.name,
                        "source_file_path": str(path),
                        "normalization_notes": f"Lectura fallida: {exc}",
                        "is_foreign_scope_confirmed": False,
                        "load_timestamp_utc": utc_now_iso(),
                    }
                ]
            )
        if not parsed.empty:
            log_status(f"[N {idx}/{len(candidates)}] Extracted { _format_int(len(parsed)) } row(s)")
            frames.append(parsed)
        else:
            log_status(f"[N {idx}/{len(candidates)}] No usable rows extracted")
    if not frames:
        return pd.DataFrame(columns=STANDARD_COLUMNS)
    standardized = pd.concat(frames, ignore_index=True)
    for column in STANDARD_COLUMNS:
        if column not in standardized.columns:
            standardized[column] = None
    standardized = standardized[STANDARD_COLUMNS]
    standardized["duplicate_review_flag"] = conservative_duplicate_flag(standardized)
    return standardized


def build_analysis_tables(
    standardized: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if standardized.empty:
        yearly = pd.DataFrame(columns=["source_year", "scholarship_count", "amount_nominal_mxn", "amount_real_mxn_2020"])
        country = pd.DataFrame(columns=["country_canonical", "scholarship_count", "amount_real_mxn_2020"])
        institution = pd.DataFrame(columns=["institution_canonical", "scholarship_count", "amount_real_mxn_2020"])
        country_year = pd.DataFrame(
            columns=["source_year", "country_canonical", "map_code", "scholarship_count", "amount_real_mxn_2020"]
        )
        institution_year = pd.DataFrame(
            columns=[
                "source_year",
                "institution_canonical",
                "scholarship_count",
                "amount_nominal_mxn",
                "amount_real_mxn_2020",
                "amount_visual_mxn",
                "amount_visual_basis",
            ]
        )
        knowledge_area_year = pd.DataFrame(columns=["source_year", "knowledge_area_label", "scholarship_count"])
        degree_year = pd.DataFrame(columns=["source_year", "degree_label", "scholarship_count"])
        return yearly, country, institution, country_year, institution_year, knowledge_area_year, degree_year

    yearly = (
        standardized.groupby("source_year", dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_nominal_mxn=("amount_nominal_mxn", lambda series: series.sum(min_count=1)),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values("source_year")
    )

    country = (
        standardized.groupby("country_canonical", dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["scholarship_count", "amount_real_mxn_2020"], ascending=[False, False])
    )

    institution_source = standardized[
        standardized["institution_canonical"].fillna("").astype(str).str.strip() != ""
    ].copy()

    institution = (
        institution_source.groupby("institution_canonical", dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["scholarship_count", "amount_real_mxn_2020"], ascending=[False, False])
    )

    country_year = (
        standardized.groupby(["source_year", "country_canonical"], dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )
    country_year["map_code"] = country_year["country_canonical"].map(get_country_map_code)
    institution_year = (
        institution_source.groupby(["source_year", "institution_canonical"], dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_nominal_mxn=("amount_nominal_mxn", lambda series: series.sum(min_count=1)),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )
    institution_year["amount_visual_mxn"] = institution_year["amount_real_mxn_2020"].combine_first(
        institution_year["amount_nominal_mxn"]
    )
    institution_year["amount_visual_basis"] = institution_year["amount_real_mxn_2020"].map(
        lambda value: "real_2020" if pd.notna(value) else "nominal"
    )
    knowledge_area_frame = standardized.copy()
    knowledge_area_frame["knowledge_area_label"] = knowledge_area_frame["knowledge_area_raw"].map(
        normalize_knowledge_area_label
    )
    knowledge_area_year = (
        knowledge_area_frame[knowledge_area_frame["knowledge_area_label"].notna()]
        .groupby(["source_year", "knowledge_area_label"], dropna=False)
        .agg(scholarship_count=("snapshot_id", "count"))
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )

    degree_frame = standardized.copy()
    degree_frame["degree_label"] = degree_frame["degree_canonical"].map(normalize_degree_series_label)
    degree_year = (
        degree_frame[degree_frame["degree_label"].notna()]
        .groupby(["source_year", "degree_label"], dropna=False)
        .agg(scholarship_count=("snapshot_id", "count"))
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )

    return yearly, country, institution, country_year, institution_year, knowledge_area_year, degree_year


def build_year_metadata(inventory: pd.DataFrame) -> pd.DataFrame:
    candidates = inventory[inventory["is_foreign_candidate"]].copy()
    if candidates.empty:
        return pd.DataFrame(columns=["source_year", "coverage_label", "is_partial_period"])

    year_meta = (
        candidates.groupby("source_year", dropna=False)
        .agg(
            coverage_label=("coverage_label", "first"),
            is_partial_period=("is_partial_period", "max"),
        )
        .reset_index()
        .sort_values("source_year")
    )
    return year_meta


def build_national_year_metadata(inventory: pd.DataFrame) -> pd.DataFrame:
    candidates = inventory[inventory["is_national_candidate"]].copy()
    if candidates.empty:
        return pd.DataFrame(columns=["source_year", "coverage_label", "is_partial_period"])

    year_meta = (
        candidates.groupby("source_year", dropna=False)
        .agg(
            coverage_label=("coverage_label", "first"),
            is_partial_period=("is_partial_period", "max"),
        )
        .reset_index()
        .sort_values("source_year")
    )
    return year_meta


def build_national_analysis_tables(
    standardized: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if standardized.empty:
        yearly = pd.DataFrame(columns=["source_year", "scholarship_count", "amount_nominal_mxn", "amount_real_mxn_2020"])
        entity = pd.DataFrame(columns=["entity_canonical", "scholarship_count", "amount_real_mxn_2020"])
        institution = pd.DataFrame(columns=["institution_canonical", "scholarship_count", "amount_real_mxn_2020"])
        entity_year = pd.DataFrame(columns=["source_year", "entity_canonical", "scholarship_count", "amount_real_mxn_2020"])
        institution_year = pd.DataFrame(
            columns=[
                "source_year",
                "institution_canonical",
                "scholarship_count",
                "amount_nominal_mxn",
                "amount_real_mxn_2020",
                "amount_visual_mxn",
                "amount_visual_basis",
            ]
        )
        knowledge_area_year = pd.DataFrame(columns=["source_year", "knowledge_area_label", "scholarship_count"])
        degree_year = pd.DataFrame(columns=["source_year", "degree_label", "scholarship_count"])
        return yearly, entity, institution, entity_year, institution_year, knowledge_area_year, degree_year

    yearly = (
        standardized.groupby("source_year", dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_nominal_mxn=("amount_nominal_mxn", lambda series: series.sum(min_count=1)),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values("source_year")
    )

    entity_source = standardized[
        standardized["entity_canonical"].fillna("").astype(str).str.strip() != ""
    ].copy()
    institution_source = standardized[
        standardized["institution_canonical"].fillna("").astype(str).str.strip() != ""
    ].copy()

    entity = (
        entity_source.groupby("entity_canonical", dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["scholarship_count", "amount_real_mxn_2020"], ascending=[False, False])
    )

    institution = (
        institution_source.groupby("institution_canonical", dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["scholarship_count", "amount_real_mxn_2020"], ascending=[False, False])
    )

    entity_year = (
        entity_source.groupby(["source_year", "entity_canonical"], dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )

    institution_year = (
        institution_source.groupby(["source_year", "institution_canonical"], dropna=False)
        .agg(
            scholarship_count=("snapshot_id", "count"),
            amount_nominal_mxn=("amount_nominal_mxn", lambda series: series.sum(min_count=1)),
            amount_real_mxn_2020=("amount_real_mxn_2020", lambda series: series.sum(min_count=1)),
        )
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )
    institution_year["amount_visual_mxn"] = institution_year["amount_real_mxn_2020"].combine_first(
        institution_year["amount_nominal_mxn"]
    )
    institution_year["amount_visual_basis"] = institution_year["amount_real_mxn_2020"].map(
        lambda value: "real_2020" if pd.notna(value) else "nominal"
    )

    knowledge_area_frame = standardized.copy()
    knowledge_area_frame["knowledge_area_label"] = knowledge_area_frame["knowledge_area_raw"].map(
        normalize_knowledge_area_label
    )
    knowledge_area_year = (
        knowledge_area_frame[knowledge_area_frame["knowledge_area_label"].notna()]
        .groupby(["source_year", "knowledge_area_label"], dropna=False)
        .agg(scholarship_count=("snapshot_id", "count"))
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )

    degree_frame = standardized.copy()
    degree_frame["degree_label"] = degree_frame["degree_canonical"].map(normalize_degree_series_label)
    degree_year = (
        degree_frame[degree_frame["degree_label"].notna()]
        .groupby(["source_year", "degree_label"], dropna=False)
        .agg(scholarship_count=("snapshot_id", "count"))
        .reset_index()
        .sort_values(["source_year", "scholarship_count"], ascending=[True, False])
    )

    return yearly, entity, institution, entity_year, institution_year, knowledge_area_year, degree_year


def _write_site_payload(payload: dict[str, object], json_output: Path, js_output: Path, js_variable: str) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)
    json_output.write_text(serialized, encoding="utf-8")
    js_output.write_text(f"window.{js_variable} = {serialized};\n", encoding="utf-8")
    log_status(f"Site data written to {json_output} and {js_output}")


def write_site_seed(
    yearly: pd.DataFrame,
    country: pd.DataFrame,
    institution: pd.DataFrame,
    country_year: pd.DataFrame,
    institution_year: pd.DataFrame,
    knowledge_area_year: pd.DataFrame,
    degree_year: pd.DataFrame,
    year_metadata: pd.DataFrame,
) -> None:
    year_meta_lookup = {
        int(row.source_year): {
            "coverage_label": row.coverage_label,
            "is_partial_period": bool(row.is_partial_period),
        }
        for row in year_metadata.itertuples(index=False)
        if pd.notna(row.source_year)
    }
    yearly_records = yearly.fillna("").to_dict(orient="records")
    for record in yearly_records:
        year = int(record["source_year"])
        record.update(year_meta_lookup.get(year, {"coverage_label": None, "is_partial_period": False}))

    payload = {
        "updated_at_utc": utc_now_iso(),
        "kpis": {
            "scholarship_count": int(yearly["scholarship_count"].sum()) if not yearly.empty else 0,
            "amount_real_mxn_2020": float(yearly["amount_real_mxn_2020"].sum()) if not yearly.empty else 0.0,
            "years_covered": int(yearly["source_year"].nunique()) if "source_year" in yearly else 0,
        },
        "yearly": yearly_records,
        "available_years": [int(value) for value in sorted(year_meta_lookup.keys())],
        "year_metadata": year_metadata.fillna("").to_dict(orient="records"),
        "country_yearly": country_year.fillna("").to_dict(orient="records"),
        "institution_yearly": institution_year.fillna("").to_dict(orient="records"),
        "knowledge_area_yearly": knowledge_area_year.fillna("").to_dict(orient="records"),
        "degree_yearly": degree_year.fillna("").to_dict(orient="records"),
        "top_countries": country.head(10).fillna("").to_dict(orient="records"),
        "top_institutions": institution.head(10).fillna("").to_dict(orient="records"),
    }
    _write_site_payload(payload, SITE_SUMMARY_JSON, SITE_SUMMARY_JS, "__SITE_SUMMARY__")


def write_national_site_seed(
    yearly: pd.DataFrame,
    entity: pd.DataFrame,
    institution: pd.DataFrame,
    entity_year: pd.DataFrame,
    institution_year: pd.DataFrame,
    knowledge_area_year: pd.DataFrame,
    degree_year: pd.DataFrame,
    year_metadata: pd.DataFrame,
) -> None:
    year_meta_lookup = {
        int(row.source_year): {
            "coverage_label": row.coverage_label,
            "is_partial_period": bool(row.is_partial_period),
        }
        for row in year_metadata.itertuples(index=False)
        if pd.notna(row.source_year)
    }
    yearly_records = yearly.fillna("").to_dict(orient="records")
    for record in yearly_records:
        year = int(record["source_year"])
        record.update(year_meta_lookup.get(year, {"coverage_label": None, "is_partial_period": False}))

    payload = {
        "updated_at_utc": utc_now_iso(),
        "kpis": {
            "scholarship_count": int(yearly["scholarship_count"].sum()) if not yearly.empty else 0,
            "amount_real_mxn_2020": float(yearly["amount_real_mxn_2020"].sum()) if not yearly.empty else 0.0,
            "years_covered": int(yearly["source_year"].nunique()) if "source_year" in yearly else 0,
        },
        "yearly": yearly_records,
        "available_years": [int(value) for value in sorted(year_meta_lookup.keys())],
        "year_metadata": year_metadata.fillna("").to_dict(orient="records"),
        "entity_yearly": entity_year.fillna("").to_dict(orient="records"),
        "institution_yearly": institution_year.fillna("").to_dict(orient="records"),
        "knowledge_area_yearly": knowledge_area_year.fillna("").to_dict(orient="records"),
        "degree_yearly": degree_year.fillna("").to_dict(orient="records"),
        "top_entities": entity.head(10).fillna("").to_dict(orient="records"),
        "top_institutions": institution.head(10).fillna("").to_dict(orient="records"),
    }
    _write_site_payload(
        payload,
        SITE_SUMMARY_NATIONAL_JSON,
        SITE_SUMMARY_NATIONAL_JS,
        "__SITE_SUMMARY_NATIONAL__",
    )


def run() -> None:
    log_status("Starting pipeline run")
    ensure_directories()
    log_status("Directories verified")
    source_files = discover_source_files()
    log_status(f"Discovered { _format_int(len(source_files)) } source file(s)")
    inventory = build_inventory(source_files)
    inventory.to_csv(INVENTORY_CSV, index=False)
    inventory.to_parquet(INVENTORY_PARQUET, index=False)
    log_status(f"Inventory written to {INVENTORY_CSV} and {INVENTORY_PARQUET}")

    standardized = standardize_foreign_scholarships(inventory)
    log_status(f"Standardized { _format_int(len(standardized)) } row(s)")
    deflators = pd.read_csv(DEFLATORS_CSV)
    log_status(f"Loaded { _format_int(len(deflators)) } deflator row(s)")
    standardized = compute_real_amounts(standardized, deflators)
    standardized.to_csv(STANDARDIZED_CSV, index=False)
    standardized.to_parquet(STANDARDIZED_PARQUET, index=False)
    log_status(f"Standardized outputs written to {STANDARDIZED_CSV} and {STANDARDIZED_PARQUET}")

    national_standardized = standardize_national_scholarships(inventory)
    log_status(f"National standardized { _format_int(len(national_standardized)) } row(s)")
    national_standardized = compute_real_amounts(national_standardized, deflators)
    national_standardized.to_csv(STANDARDIZED_NATIONAL_CSV, index=False)
    national_standardized.to_parquet(STANDARDIZED_NATIONAL_PARQUET, index=False)
    log_status(
        f"National standardized outputs written to {STANDARDIZED_NATIONAL_CSV} and {STANDARDIZED_NATIONAL_PARQUET}"
    )

    yearly, country, institution, country_year, institution_year, knowledge_area_year, degree_year = build_analysis_tables(standardized)
    year_metadata = build_year_metadata(inventory)
    yearly.to_csv(ANALYSIS_YEARLY_CSV, index=False)
    country.to_csv(ANALYSIS_COUNTRY_CSV, index=False)
    institution.to_csv(ANALYSIS_INSTITUTION_CSV, index=False)
    country_year.to_csv(ANALYSIS_COUNTRY_YEAR_CSV, index=False)
    institution_year.to_csv(ANALYSIS_INSTITUTION_YEAR_CSV, index=False)
    knowledge_area_year.to_csv(ANALYSIS_KNOWLEDGE_AREA_YEAR_CSV, index=False)
    degree_year.to_csv(ANALYSIS_DEGREE_YEAR_CSV, index=False)
    year_metadata.to_csv(ANALYSIS_YEAR_METADATA_CSV, index=False)
    log_status(
        "Analysis outputs written: "
        f"{ANALYSIS_YEARLY_CSV.name}, {ANALYSIS_COUNTRY_CSV.name}, "
        f"{ANALYSIS_INSTITUTION_CSV.name}, {ANALYSIS_COUNTRY_YEAR_CSV.name}, "
        f"{ANALYSIS_INSTITUTION_YEAR_CSV.name}, {ANALYSIS_KNOWLEDGE_AREA_YEAR_CSV.name}, "
        f"{ANALYSIS_DEGREE_YEAR_CSV.name}, "
        f"{ANALYSIS_YEAR_METADATA_CSV.name}"
    )

    (
        national_yearly,
        national_entity,
        national_institution,
        national_entity_year,
        national_institution_year,
        national_knowledge_area_year,
        national_degree_year,
    ) = build_national_analysis_tables(national_standardized)
    national_year_metadata = build_national_year_metadata(inventory)
    national_yearly.to_csv(ANALYSIS_NATIONAL_YEARLY_CSV, index=False)
    national_entity.to_csv(ANALYSIS_NATIONAL_ENTITY_CSV, index=False)
    national_institution.to_csv(ANALYSIS_NATIONAL_INSTITUTION_CSV, index=False)
    national_entity_year.to_csv(ANALYSIS_NATIONAL_ENTITY_YEAR_CSV, index=False)
    national_institution_year.to_csv(ANALYSIS_NATIONAL_INSTITUTION_YEAR_CSV, index=False)
    national_knowledge_area_year.to_csv(ANALYSIS_NATIONAL_KNOWLEDGE_AREA_YEAR_CSV, index=False)
    national_degree_year.to_csv(ANALYSIS_NATIONAL_DEGREE_YEAR_CSV, index=False)
    national_year_metadata.to_csv(ANALYSIS_NATIONAL_YEAR_METADATA_CSV, index=False)
    log_status(
        "National analysis outputs written: "
        f"{ANALYSIS_NATIONAL_YEARLY_CSV.name}, {ANALYSIS_NATIONAL_ENTITY_CSV.name}, "
        f"{ANALYSIS_NATIONAL_INSTITUTION_CSV.name}, {ANALYSIS_NATIONAL_ENTITY_YEAR_CSV.name}, "
        f"{ANALYSIS_NATIONAL_INSTITUTION_YEAR_CSV.name}, {ANALYSIS_NATIONAL_KNOWLEDGE_AREA_YEAR_CSV.name}, "
        f"{ANALYSIS_NATIONAL_DEGREE_YEAR_CSV.name}, {ANALYSIS_NATIONAL_YEAR_METADATA_CSV.name}"
    )

    write_site_seed(
        yearly,
        country,
        institution,
        country_year,
        institution_year,
        knowledge_area_year,
        degree_year,
        year_metadata,
    )
    write_national_site_seed(
        national_yearly,
        national_entity,
        national_institution,
        national_entity_year,
        national_institution_year,
        national_knowledge_area_year,
        national_degree_year,
        national_year_metadata,
    )
    total_real = float(yearly["amount_real_mxn_2020"].sum()) if not yearly.empty else 0.0
    years_covered = int(yearly["source_year"].nunique()) if not yearly.empty else 0
    national_total_real = float(national_yearly["amount_real_mxn_2020"].sum()) if not national_yearly.empty else 0.0
    national_years_covered = int(national_yearly["source_year"].nunique()) if not national_yearly.empty else 0
    log_status(
        "Completed pipeline run: "
        f"{_format_int(len(standardized))} row(s), "
        f"{_format_int(years_covered)} year(s), "
        f"MXN real 2020 total {_format_money(total_real)}; "
        f"national {_format_int(len(national_standardized))} row(s), "
        f"{_format_int(national_years_covered)} year(s), MXN real 2020 total {_format_money(national_total_real)}"
    )


if __name__ == "__main__":
    run()
