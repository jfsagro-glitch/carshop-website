import unittest

from tools.import_from_oem_gaps import GapTargetedImporter
from tools.oem_validation import is_plausible_oem, split_oem_candidates


class OemGapImporterTest(unittest.TestCase):
    def setUp(self):
        self.importer = GapTargetedImporter(lookup_pairs=set())

    def test_parse_suggested_sources_accepts_plain_and_url_domains(self):
        sources = self.importer.parse_suggested_sources(
            "https://www.realoem.com/bmw/enUS/select?q=x(product); partsale.eu; www.exist.ru(price)"
        )

        self.assertEqual(
            sources,
            [
                ("realoem.com", "product"),
                ("partsale.eu", ""),
                ("exist.ru", "price"),
            ],
        )

    def test_oem_filter_rejects_html_and_date_tokens(self):
        self.assertFalse(self.importer._is_plausible_oem("20JULI2024", "VW"))
        self.assertFalse(self.importer._is_plausible_oem("2024-07-19T12", "BM"))
        self.assertFalse(self.importer._is_plausible_oem("WP-ABCD123456", "TY"))
        self.assertFalse(self.importer._is_plausible_oem("UA-36928549-1", "AC"))
        self.assertTrue(self.importer._is_plausible_oem("04152-YZZA6", "TY"))

    def test_partsale_vag_filter_rejects_non_vag_looking_tokens(self):
        self.assertFalse(self.importer._is_domain_allowed_oem("www.partsale.eu", "BUTTON-ICON-123456", "VW"))
        self.assertTrue(self.importer._is_domain_allowed_oem("https://partsale.eu/search", "5Q0129620B", "VW"))

    def test_page_context_requires_query_or_brand_plus_part_name(self):
        self.assertFalse(
            self.importer._page_has_search_context(
                "Random page with 04152-YZZA6 and no requested context",
                query="Toyota OF oil filter",
                part_code="OF",
                brand_prefix="TY",
                part_name="oil filter",
            )
        )

    def test_shared_validator_rejects_synthetic_brand_formats(self):
        self.assertFalse(is_plausible_oem("FI", "FI-54192-AB-ACA0", strict_brand=True))
        self.assertFalse(is_plausible_oem("VW", "G-3Z0088RGKJ", strict_brand=True))
        self.assertFalse(is_plausible_oem("AU", "4538740448", strict_brand=True))
        self.assertTrue(is_plausible_oem("FI", "71765450", strict_brand=True))
        self.assertTrue(is_plausible_oem("TY", "04152-YZZA6", strict_brand=True))
        self.assertTrue(
            self.importer._page_has_search_context(
                "Toyota genuine oil filter 04152-YZZA6",
                query="Toyota OF oil filter",
                part_code="OF",
                brand_prefix="TY",
                part_name="oil filter",
            )
        )

    def test_split_supplier_oem_alternates(self):
        self.assertEqual(
            split_oem_candidates("1F1Z-6C315-DB, 1F1Z6C315DB"),
            ["1F1Z-6C315-DB", "1F1Z6C315DB"],
        )


if __name__ == "__main__":
    unittest.main()
