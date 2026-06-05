import unittest


def deflate_to_2020(nominal: float, deflator: float) -> float:
    return nominal * (100.0 / deflator)


class TestDeflatorFormula(unittest.TestCase):
    def test_identity_for_2020(self) -> None:
        self.assertEqual(deflate_to_2020(1000.0, 100.0), 1000.0)

    def test_2019_to_2020(self) -> None:
        self.assertAlmostEqual(deflate_to_2020(956.12049638, 95.612049638), 1000.0, places=6)


if __name__ == "__main__":
    unittest.main()
