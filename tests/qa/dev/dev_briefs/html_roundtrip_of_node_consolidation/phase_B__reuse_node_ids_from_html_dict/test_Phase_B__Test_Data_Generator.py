# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase_B__Test_Data_Generator
# Run these tests in Phase B environment where Phase A/B classes are available
# ═══════════════════════════════════════════════════════════════════════════════

import os
import json
import tempfile
from unittest                       import TestCase
from Phase_B__Test_Data_Generator   import (HTML_SAMPLES              ,
                                            generate_test_fixture     ,
                                            generate_all_fixtures     )


class test_Phase_B__Test_Data_Generator(TestCase):

    # ═══════════════════════════════════════════════════════════════════════════
    # HTML_SAMPLES Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_html_samples__has_expected_keys(self):
        """HTML_SAMPLES should have the standard fixture names."""
        assert 'simple'            in HTML_SAMPLES
        assert 'multiple_wrappers' in HTML_SAMPLES
        assert 'nested_structure'  in HTML_SAMPLES

    def test_html_samples__values_are_strings(self):
        """All HTML samples should be strings."""
        for name, html in HTML_SAMPLES.items():
            assert type(html) is str, f"{name} should be a string"
            assert len(html) > 0, f"{name} should not be empty"

    def test_html_samples__contain_html_tags(self):
        """All samples should contain basic HTML structure."""
        for name, html in HTML_SAMPLES.items():
            assert '<html>' in html.lower() or '<body>' in html.lower(), f"{name} should have html/body tags"

    # ═══════════════════════════════════════════════════════════════════════════
    # generate_test_fixture Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_test_fixture__returns_dict(self):
        """generate_test_fixture should return a dictionary."""
        html = "<html><body><div>Test</div></body></html>"

        result = generate_test_fixture(html, 'test')

        assert type(result) is dict

    def test_generate_test_fixture__has_required_keys(self):
        """Fixture should have name, html, html_dict, body_graph_json."""
        html = "<html><body><div>Test</div></body></html>"

        result = generate_test_fixture(html, 'test_fixture')

        assert 'name'            in result
        assert 'html'            in result
        assert 'html_dict'       in result
        assert 'body_graph_json' in result

    def test_generate_test_fixture__name_matches(self):
        """Fixture name should match provided name."""
        html = "<html><body><div>Test</div></body></html>"

        result = generate_test_fixture(html, 'my_fixture')

        assert result['name'] == 'my_fixture'

    def test_generate_test_fixture__html_preserved(self):
        """Original HTML should be preserved in fixture."""
        html = "<html><body><div>Test Content</div></body></html>"

        result = generate_test_fixture(html, 'test')

        assert result['html'] == html

    def test_generate_test_fixture__html_dict_has_node_ids(self):
        """html_dict should contain node_id values (Phase A output)."""
        html = "<html><body><div>Test</div></body></html>"

        result = generate_test_fixture(html, 'test')
        html_dict = result['html_dict']

        # Root should have node_id
        assert 'node_id' in html_dict, "html_dict root should have node_id"

        # Collect all node_ids
        node_ids = _collect_node_ids(html_dict)
        assert len(node_ids) > 0, "Should have multiple node_ids"

    def test_generate_test_fixture__html_dict_has_structure(self):
        """html_dict should have proper structure."""
        html = "<html><body><div>Test</div></body></html>"

        result = generate_test_fixture(html, 'test')
        html_dict = result['html_dict']

        assert 'tag'   in html_dict
        assert 'nodes' in html_dict
        assert html_dict['tag'] == 'html'

    def test_generate_test_fixture__body_graph_json_is_dict(self):
        """body_graph_json should be a dictionary."""
        html = "<html><body><div>Test</div></body></html>"

        result = generate_test_fixture(html, 'test')

        assert type(result['body_graph_json']) is dict



    # ═══════════════════════════════════════════════════════════════════════════
    # generate_all_fixtures Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_generate_all_fixtures__returns_dict(self):
        """generate_all_fixtures should return a dictionary."""
        result = generate_all_fixtures()

        assert type(result) is dict

    def test_generate_all_fixtures__has_all_samples(self):
        """Should generate fixture for each HTML sample."""
        result = generate_all_fixtures()

        for name in HTML_SAMPLES.keys():
            assert name in result, f"Should have fixture for {name}"

    def test_generate_all_fixtures__each_fixture_complete(self):
        """Each fixture should have required keys."""
        result = generate_all_fixtures()

        for name, fixture in result.items():
            assert 'name'            in fixture, f"{name} missing 'name'"
            assert 'html'            in fixture, f"{name} missing 'html'"
            assert 'html_dict'       in fixture, f"{name} missing 'html_dict'"
            assert 'body_graph_json' in fixture, f"{name} missing 'body_graph_json'"

    def test_generate_all_fixtures__writes_json_files(self):
        """Should write JSON files when output_dir provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_all_fixtures(output_dir=tmpdir)

            for name in HTML_SAMPLES.keys():
                json_path = os.path.join(tmpdir, f'fixture__{name}.json')
                assert os.path.exists(json_path), f"Should create {json_path}"

                # Verify JSON is valid
                with open(json_path, 'r') as f:
                    loaded = json.load(f)
                assert 'name' in loaded

    def test_generate_all_fixtures__json_files_match_returned_data(self):
        """JSON files should match returned fixture data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_all_fixtures(output_dir=tmpdir)

            for name, fixture in result.items():
                json_path = os.path.join(tmpdir, f'fixture__{name}.json')
                with open(json_path, 'r') as f:
                    loaded = json.load(f)

                assert loaded['name'] == fixture['name']
                assert loaded['html'] == fixture['html']


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

def _collect_node_ids(node_dict: dict) -> set:
    """Recursively collect node_ids from dict."""
    node_ids = set()

    if 'node_id' in node_dict:
        node_ids.add(node_dict['node_id'])

    for child in node_dict.get('nodes', []):
        if isinstance(child, dict):
            node_ids.update(_collect_node_ids(child))

    return node_ids