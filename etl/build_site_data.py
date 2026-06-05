from __future__ import annotations

import pandas as pd

from etl.config import ANALYSIS_COUNTRY_CSV, ANALYSIS_INSTITUTION_CSV, ANALYSIS_YEARLY_CSV
from etl.pipeline import write_site_seed


def run() -> None:
    yearly = pd.read_csv(ANALYSIS_YEARLY_CSV) if ANALYSIS_YEARLY_CSV.exists() else pd.DataFrame()
    country = pd.read_csv(ANALYSIS_COUNTRY_CSV) if ANALYSIS_COUNTRY_CSV.exists() else pd.DataFrame()
    institution = (
        pd.read_csv(ANALYSIS_INSTITUTION_CSV) if ANALYSIS_INSTITUTION_CSV.exists() else pd.DataFrame()
    )
    write_site_seed(yearly, country, institution)


if __name__ == "__main__":
    run()
