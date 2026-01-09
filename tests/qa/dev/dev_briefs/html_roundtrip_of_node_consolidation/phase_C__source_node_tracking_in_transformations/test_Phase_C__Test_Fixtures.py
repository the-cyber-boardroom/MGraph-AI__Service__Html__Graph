# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase_C__Test_Fixtures
# Tests JSON file loading and fixture access API
# ═══════════════════════════════════════════════════════════════════════════════

import json
import tempfile
import os
from pathlib            import Path
from unittest           import TestCase
from Phase_C__Test_Fixtures import (FIXTURES              ,
                                    FIXTURE_NAMES         ,
                                    get_fixture           ,
                                    get_html_dict         ,
                                    get_body_graph_json   ,
                                    list_fixtures         ,
                                    reload_fixtures       ,
                                    get_fixtures_dir      ,
                                    set_fixtures_dir      ,
                                    check_fixtures_status ,
                                    print_fixtures_status )


class test_Phase_C__Test_Fixtures(TestCase):        # Tests for JSON file loading functionality.

    # ═══════════════════════════════════════════════════════════════════════════
    # Module Configuration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fixture_names__is_list(self):
        """FIXTURE_NAMES should be a list."""
        assert type(FIXTURE_NAMES) is list

    def test_fixture_names__has_expected_values(self):
        """FIXTURE_NAMES should have standard names."""
        assert 'simple'            in FIXTURE_NAMES
        assert 'multiple_wrappers' in FIXTURE_NAMES
        assert 'nested_structure'  in FIXTURE_NAMES

    def test_get_fixtures_dir__returns_path(self):
        """get_fixtures_dir should return a Path."""
        result = get_fixtures_dir()
        assert isinstance(result, Path)

    def test_check_fixtures_status__returns_dict(self):
        """check_fixtures_status should return a dict."""
        result = check_fixtures_status()
        assert type(result) is dict

    def test_check_fixtures_status__has_required_keys(self):
        """check_fixtures_status should have expected keys."""
        result = check_fixtures_status()
        assert 'fixtures_dir' in result
        assert 'loaded'       in result
        assert 'missing'      in result
        assert 'files'        in result

    def test_check_fixtures_status__files_has_all_fixture_names(self):
        """check_fixtures_status files should cover all FIXTURE_NAMES."""
        result = check_fixtures_status()
        for name in FIXTURE_NAMES:
            assert name in result['files']

    def test_check_fixtures_status__file_info_structure(self):
        """Each file entry should have path and exists."""
        result = check_fixtures_status()
        for name, info in result['files'].items():
            assert 'path'   in info
            assert 'exists' in info
            assert type(info['exists']) is bool


# class test_Phase_C__Test_Fixtures__API(TestCase):
#     """Tests for the public API (require fixtures to be loaded)."""
#
#     def setUp(self):
#         """Skip tests if no fixtures loaded."""
#         if len(FIXTURES) == 0:
#             self.skipTest("No fixtures loaded - run Phase_B__Test_Data_Generator first")

    # ═══════════════════════════════════════════════════════════════════════════
    # FIXTURES Structure Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_fixtures__is_dict(self):
        """FIXTURES should be a dictionary."""
        assert type(FIXTURES) is dict

    def test_fixtures__each_has_required_keys(self):
        """Each fixture should have name, html, html_dict, body_graph_json."""
        for name, fixture in FIXTURES.items():
            assert 'name'            in fixture, f"{name} missing 'name'"
            assert 'html'            in fixture, f"{name} missing 'html'"
            assert 'html_dict'       in fixture, f"{name} missing 'html_dict'"
            assert 'body_graph_json' in fixture, f"{name} missing 'body_graph_json'"

    def test_fixtures__name_matches_key(self):
        """Fixture 'name' field should match its key."""
        for key, fixture in FIXTURES.items():
            assert fixture['name'] == key, f"Fixture {key} has mismatched name: {fixture['name']}"

    def test_fixtures__html_is_string(self):
        """html field should be a string."""
        for name, fixture in FIXTURES.items():
            assert type(fixture['html']) is str, f"{name} html should be string"
            assert len(fixture['html']) > 0, f"{name} html should not be empty"

    def test_fixtures__html_dict_is_dict(self):
        """html_dict field should be a dictionary."""
        for name, fixture in FIXTURES.items():
            assert type(fixture['html_dict']) is dict, f"{name} html_dict should be dict"

    def test_fixtures__html_dict_has_tag(self):
        """html_dict should have a tag field."""
        for name, fixture in FIXTURES.items():
            assert 'tag' in fixture['html_dict'], f"{name} html_dict missing 'tag'"

    def test_fixtures__html_dict_has_node_id(self):
        """html_dict should have node_id field."""
        for name, fixture in FIXTURES.items():
            assert 'node_id' in fixture['html_dict'], f"{name} html_dict missing 'node_id'"

    def test_fixtures__html_dict_has_nodes(self):
        """html_dict should have nodes field."""
        for name, fixture in FIXTURES.items():
            assert 'nodes' in fixture['html_dict'], f"{name} html_dict missing 'nodes'"
            assert type(fixture['html_dict']['nodes']) is list

    def test_fixtures__body_graph_json_is_dict(self):
        """body_graph_json field should be a dictionary."""
        for name, fixture in FIXTURES.items():
            assert type(fixture['body_graph_json']) is dict, f"{name} body_graph_json should be dict"


    # ═══════════════════════════════════════════════════════════════════════════
    # get_fixture Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_fixture__returns_dict_for_valid_name(self):
        """get_fixture should return dict for valid fixture name."""
        first_fixture = list_fixtures()[0] if list_fixtures() else 'simple'
        result = get_fixture(first_fixture)

        assert type(result) is dict

    def test_get_fixture__returns_none_for_invalid_name(self):
        """get_fixture should return None for invalid fixture name."""
        result = get_fixture('nonexistent_fixture')

        assert result is None

    def test_get_fixture__returns_complete_fixture(self):
        """get_fixture should return fixture with all required keys."""
        first_fixture = list_fixtures()[0]
        result = get_fixture(first_fixture)

        assert 'name'            in result
        assert 'html'            in result
        assert 'html_dict'       in result
        assert 'body_graph_json' in result

    def test_get_fixture__all_loaded_fixtures(self):
        """Should be able to get all loaded fixtures."""
        for name in list_fixtures():
            result = get_fixture(name)
            assert result is not None, f"Should get fixture '{name}'"
            assert result['name'] == name

    # ═══════════════════════════════════════════════════════════════════════════
    # get_html_dict Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_html_dict__returns_dict_for_valid_name(self):
        """get_html_dict should return dict for valid fixture name."""
        first_fixture = list_fixtures()[0]
        result = get_html_dict(first_fixture)

        assert type(result) is dict

    def test_get_html_dict__returns_none_for_invalid_name(self):
        """get_html_dict should return None for invalid fixture name."""
        result = get_html_dict('nonexistent_fixture')

        assert result is None

    def test_get_html_dict__has_tag(self):
        """Returned html_dict should have tag field."""
        first_fixture = list_fixtures()[0]
        result = get_html_dict(first_fixture)

        assert 'tag' in result

    def test_get_html_dict__has_node_id(self):
        """Returned html_dict should have node_id field."""
        first_fixture = list_fixtures()[0]
        result = get_html_dict(first_fixture)

        assert 'node_id' in result

    def test_get_html_dict__has_nodes(self):
        """Returned html_dict should have nodes field."""
        first_fixture = list_fixtures()[0]
        result = get_html_dict(first_fixture)

        assert 'nodes' in result
        assert type(result['nodes']) is list

    # ═══════════════════════════════════════════════════════════════════════════
    # get_body_graph_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_get_body_graph_json__returns_dict_for_valid_name(self):
        """get_body_graph_json should return dict for valid fixture name."""
        first_fixture = list_fixtures()[0]
        result = get_body_graph_json(first_fixture)

        assert type(result) is dict

    def test_get_body_graph_json__returns_none_for_invalid_name(self):
        """get_body_graph_json should return None for invalid fixture name."""
        result = get_body_graph_json('nonexistent_fixture')

        assert result is None



    # ═══════════════════════════════════════════════════════════════════════════
    # list_fixtures Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_list_fixtures__returns_list(self):
        """list_fixtures should return a list."""
        result = list_fixtures()

        assert type(result) is list

    def test_list_fixtures__matches_fixtures_keys(self):
        """list_fixtures should match FIXTURES.keys()."""
        result = list_fixtures()

        assert set(result) == set(FIXTURES.keys())

    def test_list_fixtures__all_items_are_strings(self):
        """All items in list_fixtures should be strings."""
        result = list_fixtures()

        for item in result:
            assert type(item) is str

    # ═══════════════════════════════════════════════════════════════════════════
    # Consistency Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_consistency__get_fixture_matches_direct_access(self):
        """get_fixture should return same data as direct FIXTURES access."""
        for name in list_fixtures():
            via_function = get_fixture(name)
            via_direct   = FIXTURES[name]

            assert via_function == via_direct

    def test_consistency__get_html_dict_matches_fixture(self):
        """get_html_dict should match fixture['html_dict']."""
        for name in list_fixtures():
            via_function = get_html_dict(name)
            via_fixture  = get_fixture(name)['html_dict']

            assert via_function == via_fixture

    def test_consistency__get_body_graph_json_matches_fixture(self):
        """get_body_graph_json should match fixture['body_graph_json']."""
        for name in list_fixtures():
            via_function = get_body_graph_json(name)
            via_fixture  = get_fixture(name)['body_graph_json']

            assert via_function == via_fixture