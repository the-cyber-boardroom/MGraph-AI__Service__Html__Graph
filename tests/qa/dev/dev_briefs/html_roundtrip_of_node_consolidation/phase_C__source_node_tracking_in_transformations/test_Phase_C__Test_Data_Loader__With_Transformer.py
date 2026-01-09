from unittest                          import TestCase
from Phase_C__Test_Data_Loader         import load_fixture_for_transform
from Phase_C__Test_Fixtures            import get_fixture
from Html_Use_Case__3__Source_Tracking import Html_Use_Case__3__Source_Tracking

class test_Phase_C__Test_Data_Loader__With_Transformer(TestCase):
    """Tests that verify loader output works with transformer."""

    def setUp(self):
        """Skip tests if no fixtures loaded."""
        from Phase_C__Test_Fixtures import FIXTURES
        if len(FIXTURES) == 0:
            self.skipTest("No fixtures loaded - copy fixture__*.json files from Phase B first")

    def test_transformer_accepts_loaded_mgraph(self):
        """Html_Use_Case__3__Source_Tracking should accept loaded MGraph."""
        from Html_Use_Case__3__Source_Tracking import Html_Use_Case__3__Source_Tracking

        fixture = get_fixture('simple')
        html_dict, mgraph = load_fixture_for_transform(fixture)

        transformer = Html_Use_Case__3__Source_Tracking()

        # Should not raise an exception
        result = transformer.transform_mgraph(mgraph)

        assert result is not None

    def test_transformer_produces_mappings(self):
        """Transformer should produce mapping data from loaded fixture."""
        from Html_Use_Case__3__Source_Tracking import Html_Use_Case__3__Source_Tracking

        fixture = get_fixture('simple')
        html_dict, mgraph = load_fixture_for_transform(fixture)

        transformer = Html_Use_Case__3__Source_Tracking()
        transformer.transform_mgraph(mgraph)

        # Mappings should be initialized (may be empty depending on fixture content)
        assert transformer.source_mapping  is not None
        assert transformer.wrapper_mapping is not None
        assert type(transformer.source_mapping)  is dict
        assert type(transformer.wrapper_mapping) is dict