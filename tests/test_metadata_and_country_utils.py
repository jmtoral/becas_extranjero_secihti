import unittest

from etl.config import STANDARD_COLUMNS
from etl.country_utils import get_country_map_code, normalize_country_value
from etl.io_utils import infer_coverage_label, is_national_candidate, is_partial_coverage
from etl.pipeline import normalize_degree_series_label, normalize_knowledge_area_label
from etl.rules.foreign_scholarships import _find_amount_column


class TestMetadataAndCountryUtils(unittest.TestCase):
    def test_partial_coverage_detection_for_2026_file(self) -> None:
        file_name = "S190_Becas_de_Posgrado_y_Apoyos_a_la_Calidad_de_Enero_a_Marzo_2026.xlsx"
        self.assertEqual(infer_coverage_label(file_name), "Enero-Marzo")
        self.assertTrue(is_partial_coverage(file_name))
        self.assertEqual(infer_coverage_label("Becas_Extranjero_Ene_Dic_2018.xlsx"), "Enero-Diciembre")

    def test_country_normalization_and_map_code(self) -> None:
        self.assertEqual(normalize_country_value("TORAL CRUZ"), "Toral Cruz")
        self.assertEqual(normalize_country_value("ESPANA"), "España")
        self.assertEqual(normalize_country_value("CANAD"), "Canadá")
        self.assertEqual(get_country_map_code("Estados Unidos"), "us")

    def test_amount_column_supports_partial_year_files(self) -> None:
        columns = [
            "CONSEC",
            "NOMBRE BECARIO",
            "IMPORTE PAGADO ENERO MARZO",
        ]
        self.assertEqual(_find_amount_column(columns), "IMPORTE PAGADO ENERO MARZO")

    def test_standard_columns_include_requested_source_fields(self) -> None:
        for column in ("study_program_raw", "knowledge_area_raw", "start_date_raw", "end_date_raw", "entity_raw", "entity_canonical"):
            self.assertIn(column, STANDARD_COLUMNS)

    def test_national_candidate_detection(self) -> None:
        self.assertTrue(is_national_candidate("Becas_Nacionales_Ene-Dic_2019.xlsx"))
        self.assertTrue(is_national_candidate("S190_Becas_de_Posgrado_y_Apoyos_a_la_Calidad_de_Enero_a_Diciembre_2025.xlsx"))
        self.assertFalse(is_national_candidate("Sabaticas_Nacionales_Ene-Dic_2019.xlsx"))

    def test_series_label_normalization(self) -> None:
        self.assertEqual(normalize_degree_series_label("1. DOC"), "Doctorado")
        self.assertEqual(normalize_degree_series_label("MAESTRÍA"), "Maestría")
        self.assertEqual(normalize_degree_series_label("4. EST TEC"), "Estancia técnica")
        self.assertEqual(
            normalize_knowledge_area_label("I. FISICO MATEMATICAS Y CS. DE LA TIERRA"),
            "Físico-matemáticas y ciencias de la Tierra",
        )


if __name__ == "__main__":
    unittest.main()
