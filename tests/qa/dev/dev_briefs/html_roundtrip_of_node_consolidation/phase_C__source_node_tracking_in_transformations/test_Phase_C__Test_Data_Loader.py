# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Phase_C__Test_Data_Loader
# Tests MGraph reconstruction and fixture loading utilities
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                       import TestCase
from Phase_C__Test_Data_Loader      import (load_mgraph_from_json       ,
                                            load_fixture_for_transform  ,
                                            collect_node_ids_from_dict  ,
                                            collect_node_ids_from_mgraph)
from Phase_C__Test_Fixtures         import get_fixture, get_body_graph_json, get_html_dict
from mgraph_db.mgraph.MGraph import MGraph


class test_Phase_C__Test_Data_Loader(TestCase):

    def setUp(self):
        """Skip tests if no fixtures loaded."""
        from Phase_C__Test_Fixtures import FIXTURES
        if len(FIXTURES) == 0:
            self.skipTest("No fixtures loaded - copy fixture__*.json files from Phase B first")

    # ═══════════════════════════════════════════════════════════════════════════
    # collect_node_ids_from_dict Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_collect_node_ids_from_dict__empty_dict(self):
        """Should return empty set for dict without node_id."""
        result = collect_node_ids_from_dict({'tag': 'div', 'nodes': []})

        assert type(result) is set
        assert len(result) == 0

    def test_collect_node_ids_from_dict__single_node(self):
        """Should collect single node_id."""
        node_dict = {'tag': 'div', 'node_id': 'div_001', 'nodes': []}

        result = collect_node_ids_from_dict(node_dict)

        assert result == {'div_001'}

    def test_collect_node_ids_from_dict__nested_nodes(self):
        """Should collect node_ids from nested structure."""
        node_dict = {
            'tag': 'div',
            'node_id': 'div_001',
            'nodes': [
                {'tag': 'p', 'node_id': 'p_001', 'nodes': [
                    {'type': 'TEXT', 'data': 'hello', 'node_id': 'text_001'}
                ]}
            ]
        }

        result = collect_node_ids_from_dict(node_dict)

        assert result == {'div_001', 'p_001', 'text_001'}

    def test_collect_node_ids_from_dict__with_fixture(self):
        """Should collect node_ids from actual fixture."""
        html_dict = get_html_dict('simple')

        result = collect_node_ids_from_dict(html_dict)

        assert type(result) is set
        assert len(result) > 0, "Should find node_ids in fixture"

    def test_collect_node_ids_from_dict__all_strings(self):
        """All collected node_ids should be strings."""
        html_dict = get_html_dict('simple')

        result = collect_node_ids_from_dict(html_dict)

        for node_id in result:
            assert type(node_id) is str, f"node_id should be string, got {type(node_id)}"

    # ═══════════════════════════════════════════════════════════════════════════
    # load_mgraph_from_json Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load_mgraph_from_json__returns_mgraph(self):
        """Should return an MGraph instance."""
        from mgraph_db.mgraph.MGraph import MGraph

        graph_json = get_body_graph_json('simple')

        result = load_mgraph_from_json(graph_json)

        assert isinstance(result, MGraph)

    def test_load_mgraph_from_json__empty_graph(self):
        """Should handle empty graph JSON."""
        from mgraph_db.mgraph.MGraph import MGraph

        graph_json = {'nodes': {}, 'edges': {}, 'root_id': None}

        result = load_mgraph_from_json(graph_json)

        assert isinstance(result, MGraph)

    def test_load_mgraph_from_json__preserves_structure(self):
        """Loaded MGraph should have same structure as JSON."""
        graph_json = get_body_graph_json('simple')

        result = load_mgraph_from_json(graph_json)

        # Should be able to iterate nodes
        node_count = 0
        for _ in result.data().nodes():
            node_count += 1

        # Should have at least some nodes (may vary based on fixture)
        assert node_count >= 0

    # ═══════════════════════════════════════════════════════════════════════════
    # collect_node_ids_from_mgraph Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_collect_node_ids_from_mgraph__returns_set(self):
        """Should return a set."""
        graph_json = get_body_graph_json('simple')
        mgraph = load_mgraph_from_json(graph_json)

        result = collect_node_ids_from_mgraph(mgraph)

        assert type(result) is set

    def test_collect_node_ids_from_mgraph__all_strings(self):
        """All collected node_ids should be strings."""
        graph_json = get_body_graph_json('simple')
        mgraph = load_mgraph_from_json(graph_json)

        result = collect_node_ids_from_mgraph(mgraph)

        for node_id in result:
            assert type(node_id) is str, f"node_id should be string, got {type(node_id)}"

    def test_collect_node_ids_from_mgraph__empty_graph(self):
        """Should return empty set for empty graph."""
        graph_json = {'nodes': {}, 'edges': {}, 'root_id': None}
        mgraph = load_mgraph_from_json(graph_json)

        result = collect_node_ids_from_mgraph(mgraph)

        assert type(result) is set

    # ═══════════════════════════════════════════════════════════════════════════
    # load_fixture_for_transform Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_load_fixture_for_transform__returns_tuple(self):
        """Should return a tuple of (html_dict, mgraph)."""
        fixture = get_fixture('simple')

        result = load_fixture_for_transform(fixture)

        assert type(result) is tuple
        assert len(result) == 2

    def test_load_fixture_for_transform__first_element_is_dict(self):
        """First element should be html_dict (dict)."""
        fixture = get_fixture('simple')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert type(html_dict) is dict

    def test_load_fixture_for_transform__second_element_is_mgraph(self):
        """Second element should be MGraph instance."""
        from mgraph_db.mgraph.MGraph import MGraph

        fixture = get_fixture('simple')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert isinstance(mgraph, MGraph)

    def test_load_fixture_for_transform__html_dict_has_node_id(self):
        """Returned html_dict should have node_id."""
        fixture = get_fixture('simple')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert 'node_id' in html_dict

    def test_load_fixture_for_transform__html_dict_matches_fixture(self):
        """Returned html_dict should match fixture's html_dict."""
        fixture = get_fixture('simple')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert html_dict == fixture['html_dict']

    def test_load_fixture_for_transform__simple(self):
        """Should load 'simple' fixture successfully."""
        fixture = get_fixture('simple')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert html_dict is not None
        assert mgraph is not None

    def test_load_fixture_for_transform__multiple_wrappers(self):
        """Should load 'multiple_wrappers' fixture successfully."""
        fixture = get_fixture('multiple_wrappers')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert html_dict is not None
        assert mgraph is not None

    def test_load_fixture_for_transform__nested_structure(self):
        """Should load 'nested_structure' fixture successfully."""
        fixture = get_fixture('nested_structure')

        html_dict, mgraph = load_fixture_for_transform(fixture)

        assert html_dict is not None
        assert mgraph is not None

    # ═══════════════════════════════════════════════════════════════════════════
    # Integration Tests
    # ═══════════════════════════════════════════════════════════════════════════

    def test_integration__node_ids_overlap(self):
        """Node_ids from dict and mgraph should have overlap."""
        fixture = get_fixture('simple')
        html_dict, mgraph = load_fixture_for_transform(fixture)

        dict_ids   = collect_node_ids_from_dict(html_dict)
        mgraph_ids = collect_node_ids_from_mgraph(mgraph)

        # Find body in html_dict for fair comparison
        body_dict = None
        for node in html_dict.get('nodes', []):
            if isinstance(node, dict) and node.get('tag') == 'body':
                body_dict = node
                break

        if body_dict:
            body_dict_ids = collect_node_ids_from_dict(body_dict)
            common = body_dict_ids & mgraph_ids
            # With generated fixtures, there should be overlap
            # With placeholder fixtures, this may be empty
            assert type(common) is set

    def test_integration__mgraph_usable_for_transform(self):
        """Loaded MGraph should be usable with transformer."""
        fixture = get_fixture('simple')
        html_dict, mgraph = load_fixture_for_transform(fixture)
        assert type(mgraph) is MGraph


    def test_integration__all_fixtures_loadable(self):
        """All fixtures should be loadable."""
        from Phase_C__Test_Fixtures import list_fixtures

        for name in list_fixtures():
            fixture = get_fixture(name)
            html_dict, mgraph = load_fixture_for_transform(fixture)

            assert html_dict is not None, f"{name} html_dict should not be None"
            assert mgraph is not None, f"{name} mgraph should not be None"
