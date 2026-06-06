from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "snapshots"
STAGING_DIR = DATA_DIR / "staging"
STANDARDIZED_DIR = DATA_DIR / "standardized"
ANALYSIS_DIR = DATA_DIR / "analysis"
CATALOGS_DIR = DATA_DIR / "catalogs"
SITE_DATA_DIR = ROOT / "site" / "assets" / "data"
DB_DIR = ROOT / "db"
SITE_SUMMARY_JSON = SITE_DATA_DIR / "summary.json"
SITE_SUMMARY_JS = SITE_DATA_DIR / "summary.js"
SITE_SUMMARY_NATIONAL_JSON = SITE_DATA_DIR / "summary_national.json"
SITE_SUMMARY_NATIONAL_JS = SITE_DATA_DIR / "summary_national.js"

INVENTORY_CSV = STAGING_DIR / "file_inventory.csv"
INVENTORY_PARQUET = STAGING_DIR / "file_inventory.parquet"
STANDARDIZED_CSV = STANDARDIZED_DIR / "scholarships_foreign.csv"
STANDARDIZED_PARQUET = STANDARDIZED_DIR / "scholarships_foreign.parquet"
STANDARDIZED_NATIONAL_CSV = STANDARDIZED_DIR / "scholarships_national.csv"
STANDARDIZED_NATIONAL_PARQUET = STANDARDIZED_DIR / "scholarships_national.parquet"
ANALYSIS_YEARLY_CSV = ANALYSIS_DIR / "yearly_summary.csv"
ANALYSIS_COUNTRY_CSV = ANALYSIS_DIR / "country_summary.csv"
ANALYSIS_INSTITUTION_CSV = ANALYSIS_DIR / "institution_summary.csv"
ANALYSIS_COUNTRY_YEAR_CSV = ANALYSIS_DIR / "country_year_summary.csv"
ANALYSIS_INSTITUTION_YEAR_CSV = ANALYSIS_DIR / "institution_year_summary.csv"
ANALYSIS_KNOWLEDGE_AREA_YEAR_CSV = ANALYSIS_DIR / "knowledge_area_year_summary.csv"
ANALYSIS_DEGREE_YEAR_CSV = ANALYSIS_DIR / "degree_year_summary.csv"
ANALYSIS_YEAR_METADATA_CSV = ANALYSIS_DIR / "year_metadata.csv"
ANALYSIS_NATIONAL_YEARLY_CSV = ANALYSIS_DIR / "national_yearly_summary.csv"
ANALYSIS_NATIONAL_ENTITY_CSV = ANALYSIS_DIR / "national_entity_summary.csv"
ANALYSIS_NATIONAL_INSTITUTION_CSV = ANALYSIS_DIR / "national_institution_summary.csv"
ANALYSIS_NATIONAL_ENTITY_YEAR_CSV = ANALYSIS_DIR / "national_entity_year_summary.csv"
ANALYSIS_NATIONAL_INSTITUTION_YEAR_CSV = ANALYSIS_DIR / "national_institution_year_summary.csv"
ANALYSIS_NATIONAL_KNOWLEDGE_AREA_YEAR_CSV = ANALYSIS_DIR / "national_knowledge_area_year_summary.csv"
ANALYSIS_NATIONAL_DEGREE_YEAR_CSV = ANALYSIS_DIR / "national_degree_year_summary.csv"
ANALYSIS_NATIONAL_YEAR_METADATA_CSV = ANALYSIS_DIR / "national_year_metadata.csv"
DEFLATORS_CSV = CATALOGS_DIR / "deflactors_base_2020.csv"
COUNTRIES_CSV = CATALOGS_DIR / "countries_manual.csv"
INSTITUTIONS_CSV = CATALOGS_DIR / "institutions_manual.csv"
DEGREES_CSV = CATALOGS_DIR / "degrees_manual.csv"
PROGRAM_RULES_CSV = CATALOGS_DIR / "program_rules.csv"

STANDARD_COLUMNS = [
    "record_id",
    "snapshot_id",
    "source_year",
    "program_category",
    "admin_label",
    "person_name_raw",
    "person_name_canonical",
    "person_name_key",
    "country_raw",
    "country_canonical",
    "country_iso3",
    "entity_raw",
    "entity_canonical",
    "institution_raw",
    "institution_canonical",
    "study_program_raw",
    "knowledge_area_raw",
    "degree_raw",
    "degree_canonical",
    "start_date_raw",
    "end_date_raw",
    "amount_nominal_mxn",
    "currency_raw",
    "deflator_base_2020",
    "amount_real_mxn_2020",
    "source_file_name",
    "source_file_path",
    "source_sheet_name",
    "source_url",
    "row_number_source",
    "normalization_notes",
    "duplicate_review_flag",
    "is_foreign_scope_confirmed",
    "load_timestamp_utc",
]


@dataclass(frozen=True)
class ProjectPaths:
    root: Path = ROOT
    raw_dir: Path = RAW_DIR
    staging_dir: Path = STAGING_DIR
    standardized_dir: Path = STANDARDIZED_DIR
    analysis_dir: Path = ANALYSIS_DIR
    catalogs_dir: Path = CATALOGS_DIR
    site_data_dir: Path = SITE_DATA_DIR
    db_dir: Path = DB_DIR


def ensure_directories() -> None:
    for path in (
        RAW_DIR,
        STAGING_DIR,
        STANDARDIZED_DIR,
        ANALYSIS_DIR,
        CATALOGS_DIR,
        SITE_DATA_DIR,
        DB_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
